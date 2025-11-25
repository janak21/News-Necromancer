import React, { useRef, useState } from 'react';

/**
 * Props for the ProgressBar component
 * Requirements: 3.2, 3.5
 */
export interface ProgressBarProps {
  currentTime: number;
  duration: number;
  onSeek: (time: number) => void;
  disabled?: boolean;
  className?: string;
}

/**
 * ProgressBar component for audio playback progress and seeking
 * 
 * Features:
 * - Visual progress indicator (Requirements: 3.2)
 * - Current time and total duration display (Requirements: 3.2)
 * - Click-to-seek interaction (Requirements: 3.5)
 * - Drag-to-seek functionality (Requirements: 3.5)
 * - Horror theme styling
 */
const ProgressBar: React.FC<ProgressBarProps> = ({
  currentTime,
  duration,
  onSeek,
  disabled = false,
  className = ''
}) => {
  const progressBarRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [hoverTime, setHoverTime] = useState<number | null>(null);

  /**
   * Format time in MM:SS format
   * Requirements: 3.2
   */
  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || seconds < 0) {
      return '0:00';
    }
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * Calculate time from mouse position
   */
  const getTimeFromPosition = (clientX: number): number => {
    if (!progressBarRef.current) return 0;
    
    const rect = progressBarRef.current.getBoundingClientRect();
    const position = (clientX - rect.left) / rect.width;
    const clampedPosition = Math.max(0, Math.min(1, position));
    
    return clampedPosition * duration;
  };

  /**
   * Handle click on progress bar to seek
   * Requirements: 3.5
   */
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (disabled || !duration) return;
    
    const newTime = getTimeFromPosition(e.clientX);
    onSeek(newTime);
  };

  /**
   * Handle mouse down to start dragging
   * Requirements: 3.5
   */
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (disabled || !duration) return;
    
    setIsDragging(true);
    const newTime = getTimeFromPosition(e.clientX);
    onSeek(newTime);
  };

  /**
   * Handle mouse move during drag
   * Requirements: 3.5
   */
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!duration) return;
    
    const time = getTimeFromPosition(e.clientX);
    setHoverTime(time);
    
    if (isDragging && !disabled) {
      onSeek(time);
    }
  };

  /**
   * Handle mouse up to end dragging
   */
  const handleMouseUp = () => {
    setIsDragging(false);
  };

  /**
   * Handle mouse leave
   */
  const handleMouseLeave = () => {
    setHoverTime(null);
    setIsDragging(false);
  };

  /**
   * Handle keyboard navigation
   * Requirements: 3.5
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (disabled || !duration) return;
    
    let newTime = currentTime;
    
    // Arrow left: seek backward 5 seconds
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      newTime = Math.max(0, currentTime - 5);
      onSeek(newTime);
    }
    // Arrow right: seek forward 5 seconds
    else if (e.key === 'ArrowRight') {
      e.preventDefault();
      newTime = Math.min(duration, currentTime + 5);
      onSeek(newTime);
    }
  };

  // Calculate progress percentage
  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;
  const hoverPercentage = hoverTime !== null && duration > 0 ? (hoverTime / duration) * 100 : null;

  const containerClasses = `progress-bar ${disabled ? 'progress-bar--disabled' : ''} ${className}`.trim();

  return (
    <div className={containerClasses}>
      {/* Current time display */}
      <span className="progress-bar__time progress-bar__time--current">
        {formatTime(currentTime)}
      </span>

      {/* Progress bar track */}
      <div
        ref={progressBarRef}
        className="progress-bar__track"
        onClick={handleClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onKeyDown={handleKeyDown}
        role="slider"
        aria-label="Seek audio position"
        aria-valuemin={0}
        aria-valuemax={duration}
        aria-valuenow={currentTime}
        aria-valuetext={`${formatTime(currentTime)} of ${formatTime(duration)}`}
        tabIndex={disabled ? -1 : 0}
      >
        {/* Progress fill */}
        <div
          className="progress-bar__fill"
          style={{ width: `${progressPercentage}%` }}
        />

        {/* Hover indicator */}
        {hoverPercentage !== null && !disabled && (
          <div
            className="progress-bar__hover"
            style={{ left: `${hoverPercentage}%` }}
          >
            <div className="progress-bar__hover-time">
              {formatTime(hoverTime!)}
            </div>
          </div>
        )}

        {/* Playhead */}
        <div
          className="progress-bar__playhead"
          style={{ left: `${progressPercentage}%` }}
        />
      </div>

      {/* Total duration display */}
      <span className="progress-bar__time progress-bar__time--duration">
        {formatTime(duration)}
      </span>
    </div>
  );
};

export default ProgressBar;
