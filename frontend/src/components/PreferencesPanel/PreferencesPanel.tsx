import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import useUserPreferences from '../../hooks/useUserPreferences';
import { useSoundEffects } from '../../hooks';
import { ApiService } from '../../services/api';
import IntensitySlider from '../IntensitySlider';
import type { UserPreferences } from '../../types';
import './PreferencesPanel.css';

interface PreferencesPanelProps {
  compact?: boolean;
  onSave?: (preferences: UserPreferences) => void;
  className?: string;
}

const HORROR_TYPES = [
  { display: 'Gothic', value: 'gothic' },
  { display: 'Cosmic', value: 'cosmic' },
  { display: 'Psychological', value: 'psychological' },
  { display: 'Supernatural', value: 'supernatural' },
  { display: 'Folk', value: 'folk' },
];

const CONTENT_FILTERS = [
  'Violence',
  'Gore',
  'Jump Scares',
  'Religious',
  'Death',
  'Madness',
  'Occult'
];

const NOTIFICATION_SETTINGS = [
  { key: 'new_variants', label: 'New Variants', icon: '👻' },
  { key: 'processing_complete', label: 'Processing Done', icon: '⚡' },
  { key: 'error_alerts', label: 'Error Alerts', icon: '⚠️' },
  { key: 'daily_summary', label: 'Daily Summary', icon: '📊' }
];

const PreferencesPanel: React.FC<PreferencesPanelProps> = ({ 
  compact = false, 
  onSave,
  className = ''
}) => {
  const { preferences, setPreferences, loading, error } = useUserPreferences();
  const { playSound, stopSound, toggleSound, setVolume, isEnabled, volume } = useSoundEffects();
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isAmbientPlaying, setIsAmbientPlaying] = useState(false);
  const [voiceStyles, setVoiceStyles] = useState<Array<{ id: string; name: string; description: string }>>([]);

  // Play ambient sound when enabled
  useEffect(() => {
    if (isAmbientPlaying && isEnabled) {
      playSound('ambient');
    } else {
      stopSound('ambient');
    }
  }, [isAmbientPlaying, isEnabled, playSound, stopSound]);

  // Fetch available voice styles
  useEffect(() => {
    const fetchVoiceStyles = async () => {
      try {
        const styles = await ApiService.getVoiceStyles();
        setVoiceStyles(styles.map(style => ({
          id: style.id,
          name: style.name,
          description: style.description
        })));
      } catch (err) {
        console.error('Failed to fetch voice styles:', err);
        // Use fallback voice styles if API fails
        setVoiceStyles([
          { id: 'ghostly_whisper', name: 'Ghostly Whisper', description: 'Ethereal and haunting' },
          { id: 'demonic_growl', name: 'Demonic Growl', description: 'Deep and menacing' },
          { id: 'eerie_narrator', name: 'Eerie Narrator', description: 'Classic horror storytelling' },
          { id: 'possessed_child', name: 'Possessed Child', description: 'Innocent yet sinister' },
          { id: 'ancient_entity', name: 'Ancient Entity', description: 'Timeless and otherworldly' }
        ]);
      }
    };
    fetchVoiceStyles();
  }, []);

  const handleHorrorTypeToggle = (horrorTypeValue: string) => {
    const updatedTypes = preferences.preferred_horror_types.includes(horrorTypeValue)
      ? preferences.preferred_horror_types.filter(type => type !== horrorTypeValue)
      : [...preferences.preferred_horror_types, horrorTypeValue];
    
    setPreferences({
      ...preferences,
      preferred_horror_types: updatedTypes
    });
  };

  const handleContentFilterToggle = (filter: string) => {
    const updatedFilters = preferences.content_filters.includes(filter)
      ? preferences.content_filters.filter(f => f !== filter)
      : [...preferences.content_filters, filter];
    
    setPreferences({
      ...preferences,
      content_filters: updatedFilters
    });
  };

  const handleIntensityChange = (intensity: number) => {
    setPreferences({
      ...preferences,
      intensity_level: intensity
    });
  };

  const handleNotificationToggle = (setting: string) => {
    setPreferences({
      ...preferences,
      notification_settings: {
        ...preferences.notification_settings,
        [setting]: !preferences.notification_settings[setting]
      }
    });
  };

  const handleVoiceStyleChange = (voiceStyle: string) => {
    setPreferences({
      ...preferences,
      voice_settings: {
        ...preferences.voice_settings,
        preferred_voice_style: voiceStyle
      }
    });
  };

  const handleAutoMatchIntensityToggle = () => {
    setPreferences({
      ...preferences,
      voice_settings: {
        ...preferences.voice_settings,
        auto_match_intensity: !preferences.voice_settings?.auto_match_intensity
      }
    });
  };

  const handleSavePreferences = async () => {
    setSaving(true);
    setSaveMessage(null);
    
    try {
      await ApiService.updateUserPreferences(preferences);
      setSaveMessage('Preferences saved to the void...');
      if (onSave) {
        onSave(preferences);
      }
    } catch {
      setSaveMessage('The spirits rejected your preferences...');
    } finally {
      setSaving(false);
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };



  if (loading) {
    return (
      <div className={`preferences-panel loading ${className}`}>
        <div className="loading-ghost-compact">👻</div>
        <p>Summoning preferences...</p>
      </div>
    );
  }

  return (
    <motion.div 
      className={`preferences-panel ${compact ? 'compact' : ''} ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="preferences-panel-header">
        <div>
          <h2 className="preferences-panel-title">
            🎭 Cursed Preferences
          </h2>
          <p className="preferences-panel-subtitle">
            Customize how darkness haunts your feeds...
          </p>
        </div>
      </div>

      {error && (
        <div className="preferences-error">
          ⚠️ {error}
        </div>
      )}

      <div className="preferences-sections">
        {/* Horror Types Section */}
        <div className="preference-section">
          <h3>🦇 Horror Types</h3>
          <p className="preference-section-description">
            Choose which horrors shall curse your content...
          </p>
          <div className="horror-types-compact">
            {HORROR_TYPES.map((type) => (
              <label
                key={type.value}
                className={`horror-type-compact ${preferences.preferred_horror_types.includes(type.value) ? 'selected' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={preferences.preferred_horror_types.includes(type.value)}
                  onChange={() => handleHorrorTypeToggle(type.value)}
                />
                <span className="checkmark">👻</span>
                <span>{type.display}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Intensity Level Section */}
        <div className="preference-section">
          <IntensitySlider
            value={preferences.intensity_level}
            onChange={handleIntensityChange}
            disabled={saving}
          />
        </div>

        {/* Content Filters Section */}
        <div className="preference-section">
          <h3>🚫 Content Filters</h3>
          <p className="preference-section-description">
            Banish certain themes from your content...
          </p>
          <div className="content-filters-compact">
            {CONTENT_FILTERS.map((filter) => (
              <label
                key={filter}
                className={`filter-compact ${preferences.content_filters.includes(filter) ? 'filtered' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={preferences.content_filters.includes(filter)}
                  onChange={() => handleContentFilterToggle(filter)}
                />
                <span className="filter-icon">🛡️</span>
                <span>{filter}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Notification Settings Section */}
        <div className="preference-section">
          <h3>🔔 Notifications</h3>
          <p className="preference-section-description">
            Configure how spirits whisper to you...
          </p>
          <div className="notifications-compact">
            {NOTIFICATION_SETTINGS.map((setting) => (
              <label
                key={setting.key}
                className={`notification-compact ${preferences.notification_settings[setting.key] ? 'enabled' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={preferences.notification_settings[setting.key] || false}
                  onChange={() => handleNotificationToggle(setting.key)}
                />
                <span className="notification-icon">{setting.icon}</span>
                <span>{setting.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Sound Settings Section */}
        <div className="preference-section">
          <h3>🔊 Sound Effects</h3>
          <p className="preference-section-description">
            Control the whispers from beyond...
          </p>
          <div className="sound-settings-compact">
            <label className={`sound-toggle-compact ${isEnabled ? 'enabled' : ''}`}>
              <input
                type="checkbox"
                checked={isEnabled}
                onChange={toggleSound}
              />
              <span className="sound-icon">{isEnabled ? '🔊' : '🔇'}</span>
              <span>Enable Sound Effects</span>
            </label>

            {isEnabled && (
              <>
                <div className="volume-control-compact">
                  <span className="volume-label">Volume</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={volume}
                    onChange={(e) => setVolume(parseFloat(e.target.value))}
                    className="volume-slider-compact"
                  />
                  <span className="volume-value">{Math.round(volume * 100)}%</span>
                </div>

                <label className={`ambient-toggle-compact ${isAmbientPlaying ? 'playing' : ''}`}>
                  <input
                    type="checkbox"
                    checked={isAmbientPlaying}
                    onChange={() => setIsAmbientPlaying(!isAmbientPlaying)}
                  />
                  <span className="ambient-icon">🎵</span>
                  <span>Ambient Horror Loop</span>
                </label>
              </>
            )}
          </div>
        </div>

        {/* Voice Narration Settings Section */}
        <div className="preference-section">
          <h3>🎙️ Voice Narration</h3>
          <p className="preference-section-description">
            Choose your preferred horror voice for AI narration...
          </p>
          <div className="voice-settings-compact">
            <div className="voice-style-selection">
              <label className="voice-setting-label">Preferred Voice Style</label>
              <select
                className="voice-style-select"
                value={preferences.voice_settings?.preferred_voice_style || 'eerie_narrator'}
                onChange={(e) => handleVoiceStyleChange(e.target.value)}
              >
                {voiceStyles.map((style) => (
                  <option key={style.id} value={style.id}>
                    {style.name} - {style.description}
                  </option>
                ))}
              </select>
            </div>

            <label className={`auto-match-toggle ${preferences.voice_settings?.auto_match_intensity ? 'enabled' : ''}`}>
              <input
                type="checkbox"
                checked={preferences.voice_settings?.auto_match_intensity ?? true}
                onChange={handleAutoMatchIntensityToggle}
              />
              <span className="toggle-icon">🎭</span>
              <span>Auto-match voice intensity to content</span>
              <span className="toggle-description">
                Automatically adjust voice characteristics based on horror intensity level
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Save Section */}
      <div className="preferences-save-section">
        <button
          onClick={handleSavePreferences}
          disabled={saving}
          className="save-preferences-compact"
        >
          {saving ? '🌀 Binding...' : '💾 Save Preferences'}
        </button>
        
        {saveMessage && (
          <motion.div
            className={`save-message-compact ${saveMessage.includes('saved') ? 'success' : 'error'}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            {saveMessage}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default PreferencesPanel;