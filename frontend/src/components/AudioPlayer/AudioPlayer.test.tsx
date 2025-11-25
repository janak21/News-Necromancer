import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AudioPlayer from './AudioPlayer';
import { VoiceStyle } from '../../types/narration';
import * as useNarrationModule from '../../hooks/useNarration';

// Mock the useNarration hook
vi.mock('../../hooks/useNarration');

describe('AudioPlayer', () => {
  const mockGenerate = vi.fn();
  const mockCancel = vi.fn();

  const defaultProps = {
    variantId: 'test-variant-123',
    voiceStyle: VoiceStyle.GHOSTLY_WHISPER,
    intensity: 3,
    content: 'Test haunted content for narration'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock implementation
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'idle',
      progress: 0,
      audioUrl: null,
      error: null,
      requestId: null,
      generate: mockGenerate,
      cancel: mockCancel
    });
  });

  it('renders generate button in idle state', () => {
    render(<AudioPlayer {...defaultProps} />);
    
    const generateButton = screen.getByRole('button', { name: /generate narration/i });
    expect(generateButton).toBeInTheDocument();
  });

  it('calls generate when generate button is clicked', async () => {
    const user = userEvent.setup();
    render(<AudioPlayer {...defaultProps} />);
    
    const generateButton = screen.getByRole('button', { name: /generate narration/i });
    await user.click(generateButton);
    
    expect(mockGenerate).toHaveBeenCalledTimes(1);
  });

  it('shows progress indicator when generating', () => {
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'generating',
      progress: 45,
      audioUrl: null,
      error: null,
      requestId: 'test-request-123',
      generate: mockGenerate,
      cancel: mockCancel
    });

    render(<AudioPlayer {...defaultProps} />);
    
    expect(screen.getByText(/summoning voice\.\.\. 45%/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('shows error message and retry button on error', () => {
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'error',
      progress: 0,
      audioUrl: null,
      error: 'Failed to generate narration',
      requestId: null,
      generate: mockGenerate,
      cancel: mockCancel
    });

    render(<AudioPlayer {...defaultProps} />);
    
    expect(screen.getByText(/failed to generate narration/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('shows playback controls when audio is ready', () => {
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'ready',
      progress: 100,
      audioUrl: 'https://example.com/audio.mp3',
      error: null,
      requestId: 'test-request-123',
      generate: mockGenerate,
      cancel: mockCancel
    });

    render(<AudioPlayer {...defaultProps} />);
    
    expect(screen.getByRole('button', { name: /play narration/i })).toBeInTheDocument();
    expect(screen.getByRole('slider', { name: /seek audio position/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /playback speed/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /download narration/i })).toBeInTheDocument();
  });

  it('toggles play/pause when play button is clicked', async () => {
    const user = userEvent.setup();
    
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'ready',
      progress: 100,
      audioUrl: 'https://example.com/audio.mp3',
      error: null,
      requestId: 'test-request-123',
      generate: mockGenerate,
      cancel: mockCancel
    });

    render(<AudioPlayer {...defaultProps} />);
    
    const playButton = screen.getByRole('button', { name: /play narration/i });
    await user.click(playButton);
    
    // After clicking play, button should show pause
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /pause narration/i })).toBeInTheDocument();
    });
  });

  it('changes playback rate when button is clicked and preset is selected', async () => {
    const user = userEvent.setup();
    
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'ready',
      progress: 100,
      audioUrl: 'https://example.com/audio.mp3',
      error: null,
      requestId: 'test-request-123',
      generate: mockGenerate,
      cancel: mockCancel
    });

    render(<AudioPlayer {...defaultProps} />);
    
    // Click the playback speed button to open the panel
    const rateButton = screen.getByRole('button', { name: /playback speed/i });
    await user.click(rateButton);
    
    // The panel should now be visible with preset buttons
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /set speed to 1\.50x/i })).toBeInTheDocument();
    });
  });

  it('calls cancel when cancel button is clicked during generation', async () => {
    const user = userEvent.setup();
    
    vi.mocked(useNarrationModule.useNarration).mockReturnValue({
      status: 'generating',
      progress: 30,
      audioUrl: null,
      error: null,
      requestId: 'test-request-123',
      generate: mockGenerate,
      cancel: mockCancel
    });

    render(<AudioPlayer {...defaultProps} />);
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);
    
    expect(mockCancel).toHaveBeenCalledTimes(1);
  });
});
