import React from 'react';
import './IntensitySlider.css';

interface IntensitySliderProps {
  value: number;
  onChange: (value: number) => void;
  disabled?: boolean;
}

const INTENSITY_LEVELS = [
  {
    level: 1,
    label: 'Gentle Whisper',
    description: 'Subtle hints and mild unease',
    icon: '🌙',
  },
  {
    level: 2,
    label: 'Creeping Dread',
    description: 'Growing tension and ominous foreshadowing',
    icon: '👻',
  },
  {
    level: 3,
    label: 'Dark Shadows',
    description: 'Clear supernatural elements with moderate fear',
    icon: '🕷️',
  },
  {
    level: 4,
    label: 'Nightmare Fuel',
    description: 'Intense horror with psychological terror',
    icon: '💀',
  },
  {
    level: 5,
    label: 'Absolute Terror',
    description: 'Maximum horror intensity and existential dread',
    icon: '☠️',
  },
];

const IntensitySlider: React.FC<IntensitySliderProps> = ({ value, onChange, disabled = false }) => {
  const currentLevel = INTENSITY_LEVELS.find(level => level.level === value) || INTENSITY_LEVELS[2];

  const handleSliderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(event.target.value, 10);
    onChange(newValue);
  };

  const handleLevelClick = (level: number) => {
    if (!disabled) {
      onChange(level);
    }
  };

  return (
    <div className="intensity-slider">
      <div className="intensity-header">
        <h3 className="intensity-title">Horror Intensity</h3>
        <div className="intensity-current">
          <span className="intensity-icon">{currentLevel.icon}</span>
          <span className="intensity-label">{currentLevel.label}</span>
        </div>
      </div>

      <div className="intensity-description">
        {currentLevel.description}
      </div>

      <div className="intensity-control">
        <input
          type="range"
          min="1"
          max="5"
          step="1"
          value={value}
          onChange={handleSliderChange}
          disabled={disabled}
          className="intensity-range"
          aria-label="Horror intensity level"
        />
        <div className="intensity-markers">
          {INTENSITY_LEVELS.map((level) => (
            <button
              key={level.level}
              className={`intensity-marker ${value === level.level ? 'active' : ''}`}
              onClick={() => handleLevelClick(level.level)}
              disabled={disabled}
              aria-label={`Set intensity to ${level.label}`}
              title={level.label}
            >
              <span className="marker-icon">{level.icon}</span>
              <span className="marker-number">{level.level}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="intensity-preview">
        <div className="preview-label">Preview:</div>
        <div className={`preview-content intensity-${value}`}>
          {value === 1 && "A mysterious shadow flickered at the edge of your vision..."}
          {value === 2 && "The air grew cold as an unseen presence drew near, watching..."}
          {value === 3 && "Ghostly whispers echoed through the darkness, speaking your name..."}
          {value === 4 && "Terror gripped your soul as the nightmare manifested before you..."}
          {value === 5 && "Reality shattered as cosmic horrors beyond comprehension consumed all hope..."}
        </div>
      </div>
    </div>
  );
};

export default IntensitySlider;
