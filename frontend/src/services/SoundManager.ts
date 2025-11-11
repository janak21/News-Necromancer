import { Howl, Howler } from 'howler';

export type SoundType = 'whisper' | 'creak' | 'ambient';

interface SoundConfig {
  src: string[];
  volume?: number;
  loop?: boolean;
  sprite?: Record<string, [number, number]>;
}

/**
 * Centralized audio management system for spooky sound effects
 * Handles loading, playing, and controlling all audio in the application
 */
class SoundManager {
  private sounds: Map<SoundType, Howl> = new Map();
  private enabled: boolean = true;
  private globalVolume: number = 0.5;
  private initialized: boolean = false;

  constructor() {
    // Set initial global volume
    Howler.volume(this.globalVolume);
  }

  /**
   * Initialize and preload all sound effects
   * Should be called once during app initialization
   */
  initialize(): void {
    if (this.initialized) return;

    // Define sound configurations
    const soundConfigs: Record<SoundType, SoundConfig> = {
      whisper: {
        src: ['/sounds/whisper.mp3', '/sounds/whisper.webm'],
        volume: 0.3,
        loop: false,
      },
      creak: {
        src: ['/sounds/creak.mp3', '/sounds/creak.webm', '/sounds/creak.wav'],
        volume: 0.4,
        loop: false,
      },
      ambient: {
        src: ['/sounds/ambient.mp3', '/sounds/ambient.webm'],
        volume: 0.2,
        loop: true,
      },
    };

    // Load all sounds
    Object.entries(soundConfigs).forEach(([name, config]) => {
      const sound = new Howl({
        src: config.src,
        volume: config.volume,
        loop: config.loop,
        preload: true,
        html5: name === 'ambient', // Use HTML5 Audio for streaming ambient sounds
        onload: () => {
          console.log(`✅ Sound loaded: ${name}`);
        },
        onloaderror: (_id, error) => {
          console.warn(`⚠️ Failed to load sound: ${name}`, error);
          console.info(`💡 Add ${name}.mp3 to frontend/public/sounds/ directory`);
        },
      });

      this.sounds.set(name as SoundType, sound);
    });

    this.initialized = true;
  }

  /**
   * Play a specific sound effect
   * @param soundName - The name of the sound to play
   */
  play(soundName: SoundType): void {
    if (!this.enabled || !this.initialized) return;

    const sound = this.sounds.get(soundName);
    if (sound) {
      // Stop previous instance if not looping
      if (!sound.loop()) {
        sound.stop();
      }
      sound.play();
    }
  }

  /**
   * Stop a specific sound
   * @param soundName - The name of the sound to stop
   */
  stop(soundName: SoundType): void {
    const sound = this.sounds.get(soundName);
    if (sound) {
      sound.stop();
    }
  }

  /**
   * Stop all currently playing sounds
   */
  stopAll(): void {
    this.sounds.forEach((sound) => sound.stop());
  }

  /**
   * Set the global volume for all sounds
   * @param volume - Volume level between 0 and 1
   */
  setVolume(volume: number): void {
    this.globalVolume = Math.max(0, Math.min(1, volume));
    Howler.volume(this.globalVolume);
  }

  /**
   * Get the current global volume
   */
  getVolume(): number {
    return this.globalVolume;
  }

  /**
   * Toggle sound effects on/off
   */
  toggle(): void {
    this.enabled = !this.enabled;
    if (!this.enabled) {
      this.stopAll();
    }
  }

  /**
   * Enable sound effects
   */
  enable(): void {
    this.enabled = true;
  }

  /**
   * Disable sound effects
   */
  disable(): void {
    this.enabled = false;
    this.stopAll();
  }

  /**
   * Check if sound effects are enabled
   */
  isEnabled(): boolean {
    return this.enabled;
  }

  /**
   * Unload all sounds and clean up resources
   */
  cleanup(): void {
    this.sounds.forEach((sound) => {
      sound.unload();
    });
    this.sounds.clear();
    this.initialized = false;
  }
}

// Export singleton instance
export const soundManager = new SoundManager();
