import React, { useState, useEffect, useRef } from 'react';
import type { VoiceStyleInfo } from '../../types/narration';
import { ApiService } from '../../services/api';
import VoiceStyleCard from './VoiceStyleCard.tsx';
import './VoiceStyleSelector.css';

export interface VoiceStyleSelectorProps {
  selectedStyle: string;
  onStyleChange: (styleId: string) => void;
  intensity?: number;
  className?: string;
}

/**
 * Voice Style Selector Component
 * Displays available horror voice styles with preview functionality
 * Requirements: 2.1, 2.2, 2.3, 2.5, 6.5
 */
const VoiceStyleSelector: React.FC<VoiceStyleSelectorProps> = ({
  selectedStyle,
  onStyleChange,
  intensity = 3,
  className = ''
}) => {
  const [voices, setVoices] = useState<VoiceStyleInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playingPreview, setPlayingPreview] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Fetch available voice styles on mount
  // Requirements: 2.1
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        setLoading(true);
        setError(null);
        const voiceStyles = await ApiService.getVoiceStyles();
        setVoices(voiceStyles);
      } catch (err) {
        console.error('Failed to fetch voice styles:', err);
        setError('Failed to load voice styles. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchVoices();
  }, []);

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  /**
   * Play preview sample for a voice style
   * Requirements: 2.2, 2.3
   */
  const playPreview = (voiceId: string, previewUrl: string) => {
    // Stop current preview if playing
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    // If clicking the same voice, just stop
    if (playingPreview === voiceId) {
      setPlayingPreview(null);
      return;
    }

    // Create and play new audio
    const audio = new Audio(previewUrl);
    audioRef.current = audio;
    setPlayingPreview(voiceId);

    audio.play().catch(err => {
      console.error('Failed to play preview:', err);
      setPlayingPreview(null);
    });

    // Handle audio end
    audio.addEventListener('ended', () => {
      setPlayingPreview(null);
      audioRef.current = null;
    });

    // Handle audio error
    audio.addEventListener('error', () => {
      console.error('Audio preview error');
      setPlayingPreview(null);
      audioRef.current = null;
    });
  };

  /**
   * Handle voice style selection
   * Requirements: 2.3, 2.5
   */
  const handleStyleSelect = (styleId: string) => {
    onStyleChange(styleId);
  };

  const containerClasses = [
    'voice-style-selector',
    className
  ].filter(Boolean).join(' ');

  if (loading) {
    return (
      <div className={containerClasses}>
        <div className="voice-style-selector__loading">
          <div className="voice-style-selector__spinner" aria-label="Loading voice styles">
            <svg className="voice-style-selector__spinner-icon" viewBox="0 0 24 24">
              <circle
                className="voice-style-selector__spinner-circle"
                cx="12"
                cy="12"
                r="10"
                fill="none"
                strokeWidth="2"
              />
            </svg>
          </div>
          <p className="voice-style-selector__loading-text">Summoning voices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={containerClasses}>
        <div className="voice-style-selector__error">
          <p className="voice-style-selector__error-text">{error}</p>
          <button
            className="voice-style-selector__retry-button"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={containerClasses}>
      <div className="voice-style-selector__header">
        <h3 className="voice-style-selector__title">Choose Your Horror Voice</h3>
        <p className="voice-style-selector__subtitle">
          Select a voice style that matches your preferred horror aesthetic
        </p>
      </div>

      <div className="voice-style-selector__grid" role="radiogroup" aria-label="Voice style selection">
        {voices.map(voice => (
          <VoiceStyleCard
            key={voice.id}
            voice={voice}
            selected={selectedStyle === voice.id}
            isPlaying={playingPreview === voice.id}
            intensity={intensity}
            onSelect={() => handleStyleSelect(voice.id)}
            onPreview={() => playPreview(voice.id, voice.previewUrl)}
          />
        ))}
      </div>

      {voices.length === 0 && (
        <div className="voice-style-selector__empty">
          <p>No voice styles available at the moment.</p>
        </div>
      )}
    </div>
  );
};

export default VoiceStyleSelector;
