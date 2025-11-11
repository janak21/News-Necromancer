import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSoundEffects } from '../useSoundEffects';
import { soundManager } from '../../services/SoundManager';

// Mock the SoundManager
vi.mock('../../services/SoundManager', () => ({
  soundManager: {
    initialize: vi.fn(),
    play: vi.fn(),
    stop: vi.fn(),
    stopAll: vi.fn(),
    toggle: vi.fn(),
    setVolume: vi.fn(),
    enable: vi.fn(),
    disable: vi.fn(),
    isEnabled: vi.fn(() => true),
    getVolume: vi.fn(() => 0.5),
  },
}));

describe('useSoundEffects', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(soundManager.isEnabled).mockReturnValue(true);
    vi.mocked(soundManager.getVolume).mockReturnValue(0.5);
  });

  describe('Initialization', () => {
    it('should initialize sound manager on mount', () => {
      renderHook(() => useSoundEffects());
      expect(soundManager.initialize).toHaveBeenCalledTimes(1);
    });

    it('should return initial enabled state', () => {
      const { result } = renderHook(() => useSoundEffects());
      expect(result.current.isEnabled).toBe(true);
    });

    it('should return initial volume', () => {
      const { result } = renderHook(() => useSoundEffects());
      expect(result.current.volume).toBe(0.5);
    });
  });

  describe('Sound Playback', () => {
    it('should play whisper sound', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.playSound('whisper');
      });
      
      expect(soundManager.play).toHaveBeenCalledWith('whisper');
    });

    it('should play creak sound', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.playSound('creak');
      });
      
      expect(soundManager.play).toHaveBeenCalledWith('creak');
    });

    it('should play ambient sound', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.playSound('ambient');
      });
      
      expect(soundManager.play).toHaveBeenCalledWith('ambient');
    });

    it('should stop specific sound', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.stopSound('ambient');
      });
      
      expect(soundManager.stop).toHaveBeenCalledWith('ambient');
    });

    it('should stop all sounds', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.stopAllSounds();
      });
      
      expect(soundManager.stopAll).toHaveBeenCalledTimes(1);
    });
  });

  describe('Volume Controls', () => {
    it('should set volume', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.setVolume(0.7);
      });
      
      expect(soundManager.setVolume).toHaveBeenCalledWith(0.7);
    });

    it('should update volume state', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.setVolume(0.8);
      });
      
      expect(result.current.volume).toBe(0.8);
    });
  });

  describe('Enable/Disable Controls', () => {
    it('should toggle sound', () => {
      vi.mocked(soundManager.isEnabled).mockReturnValue(false);
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.toggleSound();
      });
      
      expect(soundManager.toggle).toHaveBeenCalledTimes(1);
    });

    it('should update enabled state after toggle', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      vi.mocked(soundManager.isEnabled).mockReturnValue(false);
      
      act(() => {
        result.current.toggleSound();
      });
      
      expect(result.current.isEnabled).toBe(false);
    });

    it('should enable sound', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.enableSound();
      });
      
      expect(soundManager.enable).toHaveBeenCalledTimes(1);
      expect(result.current.isEnabled).toBe(true);
    });

    it('should disable sound', () => {
      const { result } = renderHook(() => useSoundEffects());
      
      act(() => {
        result.current.disableSound();
      });
      
      expect(soundManager.disable).toHaveBeenCalledTimes(1);
      expect(result.current.isEnabled).toBe(false);
    });
  });

  describe('Hook Stability', () => {
    it('should maintain stable function references', () => {
      const { result, rerender } = renderHook(() => useSoundEffects());
      
      const firstPlaySound = result.current.playSound;
      const firstSetVolume = result.current.setVolume;
      const firstToggleSound = result.current.toggleSound;
      
      rerender();
      
      expect(result.current.playSound).toBe(firstPlaySound);
      expect(result.current.setVolume).toBe(firstSetVolume);
      expect(result.current.toggleSound).toBe(firstToggleSound);
    });
  });
});
