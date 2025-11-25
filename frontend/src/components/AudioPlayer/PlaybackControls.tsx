import React from 'react';

/**
 * Props for the PlaybackControls component
 * Requirements: 3.1, 8.1, 8.4
 */
export interface PlaybackControlsProps {
  isPlaying: boolean;
  onPlay: () => void;
  onPause: () => void;
  disabled?: boolean;
  className?: string;
}

/**
 * PlaybackControls component for play/pause functionality
 * 
 * Features:
 * - Play/pause toggle button (Requirements: 3.1)
 * - ARIA labels for accessibility (Requirements: 8.1, 8.4)
 * - Keyboard support (spacebar) (Requirements: 8.1)
 * - Dark theme styling
 */
const PlaybackControls: React.FC<PlaybackControlsProps> = ({
  isPlaying,
  onPlay,
  onPause,
  disabled = false,
  className = ''
}) => {
  /**
   * Handle play/pause toggle
   * Requirements: 3.1
   */
  const handleToggle = () => {
    if (isPlaying) {
      onPause();
    } else {
      onPlay();
    }
  };

  /**
   * Handle keyboard events
   * Requirements: 8.1
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    // Spacebar toggles play/pause
    if (e.key === ' ' || e.key === 'Spacebar') {
      e.preventDefault();
      handleToggle();
    }
  };

  const buttonClasses = `playback-controls__button ${className}`.trim();

  return (
    <div className="playback-controls">
      <button
        className={buttonClasses}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        aria-label={isPlaying ? 'Pause narration' : 'Play narration'}
        aria-pressed={isPlaying}
        title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
      >
        {isPlaying ? (
          // Pause icon
          <svg 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="currentColor"
            aria-hidden="true"
          >
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
          </svg>
        ) : (
          // Play icon
          <svg 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default PlaybackControls;
