import { useEffect, useCallback, useState } from 'react';
import { soundManager } from '../services/SoundManager';
import type { SoundType } from '../services/SoundManager';

/**
 * React hook for managing sound effects in components
 * Provides easy access to sound playback and volume controls
 */
export function useSoundEffects() {
  const [isEnabled, setIsEnabled] = useState(soundManager.isEnabled());
  const [volume, setVolumeState] = useState(soundManager.getVolume());

  // Initialize sound manager on mount
  useEffect(() => {
    soundManager.initialize();

    return () => {
      // Cleanup is handled by the app-level component
    };
  }, []);

  /**
   * Play a sound effect
   */
  const playSound = useCallback((soundName: SoundType) => {
    soundManager.play(soundName);
  }, []);

  /**
   * Stop a specific sound
   */
  const stopSound = useCallback((soundName: SoundType) => {
    soundManager.stop(soundName);
  }, []);

  /**
   * Stop all sounds
   */
  const stopAllSounds = useCallback(() => {
    soundManager.stopAll();
  }, []);

  /**
   * Toggle sound effects on/off
   */
  const toggleSound = useCallback(() => {
    soundManager.toggle();
    setIsEnabled(soundManager.isEnabled());
  }, []);

  /**
   * Set volume level
   */
  const setVolume = useCallback((newVolume: number) => {
    soundManager.setVolume(newVolume);
    setVolumeState(newVolume);
  }, []);

  /**
   * Enable sound effects
   */
  const enableSound = useCallback(() => {
    soundManager.enable();
    setIsEnabled(true);
  }, []);

  /**
   * Disable sound effects
   */
  const disableSound = useCallback(() => {
    soundManager.disable();
    setIsEnabled(false);
  }, []);

  return {
    playSound,
    stopSound,
    stopAllSounds,
    toggleSound,
    setVolume,
    enableSound,
    disableSound,
    isEnabled,
    volume,
  };
}
