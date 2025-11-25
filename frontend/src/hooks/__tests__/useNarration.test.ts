import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useNarration } from '../useNarration';
import { ApiService } from '../../services/api';
import { VoiceStyle, GenerationStatus } from '../../types/narration';

// Mock the ApiService
vi.mock('../../services/api', () => ({
  ApiService: {
    generateNarration: vi.fn(),
    getNarrationStatus: vi.fn(),
    cancelNarration: vi.fn(),
  },
}));

describe('useNarration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should initialize with idle state', () => {
    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    expect(result.current.status).toBe('idle');
    expect(result.current.progress).toBe(0);
    expect(result.current.audioUrl).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.requestId).toBeNull();
  });

  it('should return cached narration if available and valid', async () => {
    const cachedUrl = 'https://example.com/cached-audio.mp3';
    const cacheKey = 'narration_test-variant_ghostly_whisper';
    
    localStorage.setItem(
      cacheKey,
      JSON.stringify({
        audioUrl: cachedUrl,
        timestamp: Date.now(),
      })
    );

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    await result.current.generate();

    await waitFor(() => {
      expect(result.current.status).toBe('ready');
      expect(result.current.audioUrl).toBe(cachedUrl);
      expect(result.current.progress).toBe(100);
    });
  });

  it('should not use expired cache', async () => {
    const cachedUrl = 'https://example.com/cached-audio.mp3';
    const cacheKey = 'narration_test-variant_ghostly_whisper';
    
    // Set cache with timestamp older than 7 days
    const expiredTimestamp = Date.now() - (8 * 24 * 60 * 60 * 1000);
    localStorage.setItem(
      cacheKey,
      JSON.stringify({
        audioUrl: cachedUrl,
        timestamp: expiredTimestamp,
      })
    );

    vi.mocked(ApiService.generateNarration).mockResolvedValue({
      request_id: 'req-123',
      status: 'queued',
    });

    vi.mocked(ApiService.getNarrationStatus).mockResolvedValue({
      requestId: 'req-123',
      status: GenerationStatus.COMPLETED,
      progress: 100,
      audioUrl: 'https://example.com/new-audio.mp3',
      createdAt: new Date().toISOString(),
    });

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    await result.current.generate();

    await waitFor(() => {
      expect(result.current.status).toBe('generating');
    });
    
    expect(ApiService.generateNarration).toHaveBeenCalled();
  });

  it('should generate narration and poll for status', async () => {
    const requestId = 'req-123';
    const audioUrl = 'https://example.com/audio.mp3';

    vi.mocked(ApiService.generateNarration).mockResolvedValue({
      request_id: requestId,
      status: 'queued',
    });

    vi.mocked(ApiService.getNarrationStatus)
      .mockResolvedValueOnce({
        requestId,
        status: GenerationStatus.GENERATING,
        progress: 50,
        createdAt: new Date().toISOString(),
      })
      .mockResolvedValueOnce({
        requestId,
        status: GenerationStatus.COMPLETED,
        progress: 100,
        audioUrl,
        createdAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      });

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    await result.current.generate();

    await waitFor(() => {
      expect(result.current.status).toBe('generating');
      expect(result.current.requestId).toBe(requestId);
    });

    // Advance timers to trigger first poll
    await vi.advanceTimersByTimeAsync(1000);

    await waitFor(() => {
      expect(result.current.progress).toBe(50);
    });

    // Advance timers to trigger second poll
    await vi.advanceTimersByTimeAsync(1000);

    await waitFor(() => {
      expect(result.current.status).toBe('ready');
      expect(result.current.audioUrl).toBe(audioUrl);
      expect(result.current.progress).toBe(100);
    });
  });

  it('should handle generation errors', async () => {
    const errorMessage = 'API error';

    vi.mocked(ApiService.generateNarration).mockRejectedValue(
      new Error(errorMessage)
    );

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    await result.current.generate();

    await waitFor(() => {
      expect(result.current.status).toBe('error');
      expect(result.current.error).toBe(errorMessage);
    });
  });

  it('should cancel narration request', async () => {
    const requestId = 'req-123';

    vi.mocked(ApiService.generateNarration).mockResolvedValue({
      request_id: requestId,
      status: 'queued',
    });

    vi.mocked(ApiService.getNarrationStatus).mockResolvedValue({
      requestId,
      status: GenerationStatus.GENERATING,
      progress: 50,
      createdAt: new Date().toISOString(),
    });

    vi.mocked(ApiService.cancelNarration).mockResolvedValue({
      success: true,
      message: 'Cancelled',
      request_id: requestId,
    });

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    await result.current.generate();

    await waitFor(() => {
      expect(result.current.requestId).toBe(requestId);
    });

    await result.current.cancel();

    await waitFor(() => {
      expect(result.current.status).toBe('idle');
      expect(result.current.requestId).toBeNull();
    });

    expect(ApiService.cancelNarration).toHaveBeenCalledWith(requestId);
  });

  it('should auto-generate when autoGenerate is true', async () => {
    const cachedUrl = 'https://example.com/cached-audio.mp3';
    const cacheKey = 'narration_test-variant_ghostly_whisper';
    
    localStorage.setItem(
      cacheKey,
      JSON.stringify({
        audioUrl: cachedUrl,
        timestamp: Date.now(),
      })
    );

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
        autoGenerate: true,
      })
    );

    await waitFor(() => {
      expect(result.current.status).toBe('ready');
      expect(result.current.audioUrl).toBe(cachedUrl);
    });
  });

  it('should cache generated narration', async () => {
    const requestId = 'req-123';
    const audioUrl = 'https://example.com/audio.mp3';
    const cacheKey = 'narration_test-variant_ghostly_whisper';

    vi.mocked(ApiService.generateNarration).mockResolvedValue({
      request_id: requestId,
      status: 'queued',
    });

    vi.mocked(ApiService.getNarrationStatus).mockResolvedValue({
      requestId,
      status: GenerationStatus.COMPLETED,
      progress: 100,
      audioUrl,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
    });

    const { result } = renderHook(() =>
      useNarration({
        variantId: 'test-variant',
        voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
        intensity: 3,
        content: 'Test spooky content',
      })
    );

    await result.current.generate();

    // Advance timer to trigger poll
    await vi.advanceTimersByTimeAsync(1000);

    await waitFor(() => {
      expect(result.current.status).toBe('ready');
    });

    // Check that the audio URL was cached
    const cached = localStorage.getItem(cacheKey);
    expect(cached).toBeTruthy();
    
    if (cached) {
      const entry = JSON.parse(cached);
      expect(entry.audioUrl).toBe(audioUrl);
      expect(entry.timestamp).toBeLessThanOrEqual(Date.now());
    }
  });
});
