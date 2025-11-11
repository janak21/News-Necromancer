import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { Howler } from 'howler';

// Store mock instances
let mockHowlInstances: any[] = [];

// Mock Howler.js
vi.mock('howler', () => {
  class MockHowl {
    play = vi.fn();
    stop = vi.fn();
    unload = vi.fn();
    loop = vi.fn(() => false);
    
    constructor() {
      mockHowlInstances.push(this);
    }
  }

  return {
    Howl: MockHowl,
    Howler: {
      volume: vi.fn(),
    },
  };
});

// Import after mocking
const { soundManager } = await import('../SoundManager');

describe('SoundManager', () => {
  beforeEach(() => {
    mockHowlInstances = [];
    vi.clearAllMocks();
    // Reset sound manager state
    soundManager.cleanup();
    soundManager.enable(); // Re-enable after cleanup
  });

  afterEach(() => {
    soundManager.cleanup();
  });

  describe('Initialization', () => {
    it('should initialize with default volume', () => {
      expect(soundManager.getVolume()).toBe(0.5);
    });

    it('should be enabled by default', () => {
      expect(soundManager.isEnabled()).toBe(true);
    });

    it('should initialize sounds only once', () => {
      soundManager.initialize();
      const firstCallCount = vi.mocked(Howler.volume).mock.calls.length;
      
      soundManager.initialize();
      const secondCallCount = vi.mocked(Howler.volume).mock.calls.length;
      
      expect(secondCallCount).toBe(firstCallCount);
    });
  });

  describe('Sound Playback', () => {
    beforeEach(() => {
      soundManager.initialize();
    });

    it('should play whisper sound when enabled', () => {
      soundManager.play('whisper');
      // Verify that play was called on at least one sound instance
      const playCallCount = mockHowlInstances.reduce((count, instance) => 
        count + instance.play.mock.calls.length, 0);
      expect(playCallCount).toBeGreaterThan(0);
    });

    it('should play creak sound when enabled', () => {
      soundManager.play('creak');
      const playCallCount = mockHowlInstances.reduce((count, instance) => 
        count + instance.play.mock.calls.length, 0);
      expect(playCallCount).toBeGreaterThan(0);
    });

    it('should play ambient sound when enabled', () => {
      soundManager.play('ambient');
      const playCallCount = mockHowlInstances.reduce((count, instance) => 
        count + instance.play.mock.calls.length, 0);
      expect(playCallCount).toBeGreaterThan(0);
    });

    it('should not play sounds when disabled', () => {
      soundManager.disable();
      mockHowlInstances.forEach(instance => instance.play.mockClear());
      
      soundManager.play('whisper');
      // No play calls should be made after disabling
      const playCallCount = mockHowlInstances.reduce((count, instance) => 
        count + instance.play.mock.calls.length, 0);
      expect(playCallCount).toBe(0);
    });

    it('should not play sounds before initialization', () => {
      soundManager.cleanup();
      soundManager.enable();
      mockHowlInstances = [];
      
      soundManager.play('whisper');
      expect(mockHowlInstances.length).toBe(0);
    });
  });

  describe('Volume Controls', () => {
    it('should set volume within valid range', () => {
      soundManager.setVolume(0.7);
      expect(soundManager.getVolume()).toBe(0.7);
      expect(Howler.volume).toHaveBeenCalledWith(0.7);
    });

    it('should clamp volume to maximum of 1', () => {
      soundManager.setVolume(1.5);
      expect(soundManager.getVolume()).toBe(1);
      expect(Howler.volume).toHaveBeenCalledWith(1);
    });

    it('should clamp volume to minimum of 0', () => {
      soundManager.setVolume(-0.5);
      expect(soundManager.getVolume()).toBe(0);
      expect(Howler.volume).toHaveBeenCalledWith(0);
    });

    it('should update global volume through Howler', () => {
      soundManager.setVolume(0.3);
      expect(Howler.volume).toHaveBeenCalledWith(0.3);
    });
  });

  describe('Mute Functionality', () => {
    beforeEach(() => {
      soundManager.initialize();
    });

    it('should toggle sound on and off', () => {
      expect(soundManager.isEnabled()).toBe(true);
      
      soundManager.toggle();
      expect(soundManager.isEnabled()).toBe(false);
      
      soundManager.toggle();
      expect(soundManager.isEnabled()).toBe(true);
    });

    it('should enable sounds', () => {
      soundManager.disable();
      expect(soundManager.isEnabled()).toBe(false);
      
      soundManager.enable();
      expect(soundManager.isEnabled()).toBe(true);
    });

    it('should disable sounds', () => {
      soundManager.enable();
      expect(soundManager.isEnabled()).toBe(true);
      
      soundManager.disable();
      expect(soundManager.isEnabled()).toBe(false);
    });
  });

  describe('Memory Management', () => {
    it('should cleanup all sounds', () => {
      soundManager.initialize();
      const instanceCount = mockHowlInstances.length;
      
      soundManager.cleanup();
      
      // Verify unload was called on all instances
      mockHowlInstances.slice(0, instanceCount).forEach(instance => {
        expect(instance.unload).toHaveBeenCalled();
      });
    });

    it('should allow re-initialization after cleanup', () => {
      soundManager.initialize();
      soundManager.cleanup();
      soundManager.enable();
      
      mockHowlInstances = [];
      soundManager.initialize();
      
      // Should be able to play sounds again
      soundManager.play('whisper');
      const playCallCount = mockHowlInstances.reduce((count, instance) => 
        count + instance.play.mock.calls.length, 0);
      expect(playCallCount).toBeGreaterThan(0);
    });
  });

  describe('User Preferences', () => {
    beforeEach(() => {
      soundManager.initialize();
    });

    it('should persist enabled state across operations', () => {
      soundManager.disable();
      soundManager.setVolume(0.8);
      
      expect(soundManager.isEnabled()).toBe(false);
      expect(soundManager.getVolume()).toBe(0.8);
    });

    it('should maintain volume when toggling enabled state', () => {
      soundManager.setVolume(0.6);
      soundManager.toggle();
      
      expect(soundManager.getVolume()).toBe(0.6);
    });
  });
});
