import React, { useState } from 'react';

/**
 * Props for the PlaybackRateControl component
 * Requirements: 3.3
 */
export interface PlaybackRateControlProps {
  rate: number;
  onChange: (rate: number) => void;
  disabled?: boolean;
  className?: string;
}

/**
 * PlaybackRateControl component for adjusting audio playback speed
 * 
 * Features:
 * - Speed adjustment from 0.5x to 2.0x (Requirements: 3.3)
 * - Preset speed buttons for common rates
 * - Custom slider for fine-tuned control
 * - Current playback rate display
 * - Dark horror theme styling
 */
const PlaybackRateControl: React.FC<PlaybackRateControlProps> = ({
  rate,
  onChange,
  disabled = false,
  className = ''
}) => {
  const [showSlider, setShowSlider] = useState(false);

  // Preset speed options
  const presetRates = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0];

  /**
   * Handle preset button click
   * Requirements: 3.3
   */
  const handlePresetClick = (presetRate: number) => {
    onChange(presetRate);
  };

  /**
   * Handle slider change
   * Requirements: 3.3
   */
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newRate = parseFloat(e.target.value);
    onChange(newRate);
  };

  /**
   * Toggle slider visibility
   */
  const toggleSlider = () => {
    setShowSlider(!showSlider);
  };

  /**
   * Format rate for display
   */
  const formatRate = (rateValue: number): string => {
    return `${rateValue.toFixed(2)}x`;
  };

  const containerClasses = `playback-rate-control ${disabled ? 'playback-rate-control--disabled' : ''} ${className}`.trim();

  return (
    <div className={containerClasses}>
      {/* Current rate display and toggle */}
      <button
        className="playback-rate-control__display"
        onClick={toggleSlider}
        disabled={disabled}
        aria-label={`Playback speed: ${formatRate(rate)}`}
        aria-expanded={showSlider}
        title="Adjust playback speed"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        <span className="playback-rate-control__rate-text">
          {formatRate(rate)}
        </span>
      </button>

      {/* Dropdown panel with presets and slider */}
      {showSlider && !disabled && (
        <div className="playback-rate-control__panel">
          {/* Preset buttons */}
          <div className="playback-rate-control__presets">
            <div className="playback-rate-control__presets-label">
              Quick Select:
            </div>
            <div className="playback-rate-control__presets-buttons">
              {presetRates.map((presetRate) => (
                <button
                  key={presetRate}
                  className={`playback-rate-control__preset-button ${
                    Math.abs(rate - presetRate) < 0.01
                      ? 'playback-rate-control__preset-button--active'
                      : ''
                  }`}
                  onClick={() => handlePresetClick(presetRate)}
                  aria-label={`Set speed to ${formatRate(presetRate)}`}
                  aria-pressed={Math.abs(rate - presetRate) < 0.01}
                >
                  {formatRate(presetRate)}
                </button>
              ))}
            </div>
          </div>

          {/* Custom slider */}
          <div className="playback-rate-control__slider-container">
            <label
              htmlFor="playback-rate-slider"
              className="playback-rate-control__slider-label"
            >
              Custom Speed:
            </label>
            <div className="playback-rate-control__slider-wrapper">
              <span className="playback-rate-control__slider-min">0.5x</span>
              <input
                id="playback-rate-slider"
                type="range"
                className="playback-rate-control__slider"
                min="0.5"
                max="2.0"
                step="0.05"
                value={rate}
                onChange={handleSliderChange}
                aria-label="Custom playback speed"
                aria-valuemin={0.5}
                aria-valuemax={2.0}
                aria-valuenow={rate}
                aria-valuetext={formatRate(rate)}
              />
              <span className="playback-rate-control__slider-max">2.0x</span>
            </div>
            <div className="playback-rate-control__slider-value">
              {formatRate(rate)}
            </div>
          </div>

          {/* Reset button */}
          <button
            className="playback-rate-control__reset"
            onClick={() => handlePresetClick(1.0)}
            disabled={Math.abs(rate - 1.0) < 0.01}
            aria-label="Reset to normal speed"
          >
            Reset to Normal
          </button>
        </div>
      )}
    </div>
  );
};

export default PlaybackRateControl;
