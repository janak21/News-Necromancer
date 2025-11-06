import React, { useState } from 'react';
import { motion } from 'framer-motion';
import useUserPreferences from '../../hooks/useUserPreferences';
import { ApiService } from '../../services/api';
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
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

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

  const getIntensityLabel = (level: number) => {
    const labels = ['Whisper', 'Murmur', 'Haunt', 'Terror', 'Nightmare'];
    return labels[level - 1] || 'Unknown';
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
          <h3>🌙 Horror Intensity</h3>
          <p className="preference-section-description">
            How deeply should darkness penetrate?
          </p>
          <div className="intensity-compact">
            <div className="intensity-labels-compact">
              <span>Gentle</span>
              <span>Terror</span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              value={preferences.intensity_level}
              onChange={(e) => handleIntensityChange(parseInt(e.target.value))}
              className="intensity-slider-compact"
            />
            <div className="current-intensity-compact">
              {getIntensityLabel(preferences.intensity_level)}
            </div>
          </div>
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