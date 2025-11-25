import React from 'react';
import type { VoiceStyleInfo } from '../../types/narration';

export interface VoiceStyleCardProps {
  voice: VoiceStyleInfo;
  selected: boolean;
  isPlaying: boolean;
  intensity: number;
  onSelect: () => void;
  onPreview: () => void;
}

/**
 * Individual Voice Style Card Component
 * Displays a single voice style with preview and selection functionality
 * Requirements: 2.1, 2.2, 2.3, 2.5
 */
const VoiceStyleCard: React.FC<VoiceStyleCardProps> = ({
  voice,
  selected,
  isPlaying,
  intensity,
  onSelect,
  onPreview
}) => {
  const cardClasses = [
    'voice-style-card',
    selected ? 'voice-style-card--selected' : '',
    isPlaying ? 'voice-style-card--playing' : ''
  ].filter(Boolean).join(' ');

  // Determine if this voice is recommended for current intensity
  const isRecommended = Math.abs(voice.recommendedIntensity - intensity) <= 1;

  return (
    <div
      className={cardClasses}
      role="radio"
      aria-checked={selected}
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect();
        }
      }}
    >
      {/* Selection indicator */}
      <div className="voice-style-card__indicator" aria-hidden="true">
        {selected && (
          <svg
            className="voice-style-card__check-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        )}
      </div>

      {/* Voice icon */}
      <div className="voice-style-card__icon" aria-hidden="true">
        {voice.icon}
      </div>

      {/* Voice info */}
      <div className="voice-style-card__content">
        <h4 className="voice-style-card__name">
          {voice.name}
          {isRecommended && (
            <span className="voice-style-card__badge" title="Recommended for current intensity">
              Recommended
            </span>
          )}
        </h4>
        <p className="voice-style-card__description">{voice.description}</p>
      </div>

      {/* Preview button */}
      <button
        className="voice-style-card__preview-button"
        onClick={(e) => {
          e.stopPropagation();
          onPreview();
        }}
        aria-label={`${isPlaying ? 'Stop' : 'Play'} preview for ${voice.name}`}
        title={`${isPlaying ? 'Stop' : 'Play'} preview`}
      >
        {isPlaying ? (
          <svg
            className="voice-style-card__preview-icon"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <rect x="6" y="4" width="4" height="16" rx="1" />
            <rect x="14" y="4" width="4" height="16" rx="1" />
          </svg>
        ) : (
          <svg
            className="voice-style-card__preview-icon"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </button>

      {/* Playing indicator */}
      {isPlaying && (
        <div className="voice-style-card__playing-indicator" aria-hidden="true">
          <span className="voice-style-card__wave"></span>
          <span className="voice-style-card__wave"></span>
          <span className="voice-style-card__wave"></span>
        </div>
      )}
    </div>
  );
};

export default VoiceStyleCard;
