import React, { useState } from 'react';
import { motion } from 'framer-motion';
import useUserPreferences from '../hooks/useUserPreferences';
import { ApiService } from '../services/api';
import Button from '../components/Button/Button';
import './PreferencesPage.css';

const HORROR_TYPES = [
  { display: 'Gothic Horror', value: 'gothic' },
  { display: 'Cosmic Horror', value: 'cosmic' },
  { display: 'Psychological Horror', value: 'psychological' },
  { display: 'Supernatural Horror', value: 'supernatural' },
  { display: 'Folk Horror', value: 'folk' },
];

const CONTENT_FILTERS = [
  'Violence',
  'Gore',
  'Jump Scares',
  'Religious Themes',
  'Death',
  'Madness',
  'Occult'
];

const PreferencesPage: React.FC = () => {
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
      setSaveMessage('Your cursed preferences have been saved to the void...');
    } catch (err) {
      setSaveMessage('The spirits rejected your preferences. Try again...');
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
      <div className="preferences-page loading">
        <div className="loading-ghost">👻</div>
        <p>Summoning your preferences from the ethereal realm...</p>
      </div>
    );
  }

  return (
    <motion.div 
      className="preferences-page"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="preferences-container">
        <motion.h1 
          className="preferences-title"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          🎭 Cursed Preferences
        </motion.h1>
        
        <motion.p 
          className="preferences-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          Customize how the darkness haunts your RSS feeds...
        </motion.p>

        {error && (
          <div className="error-message">
            ⚠️ The spirits are restless: {error}
          </div>
        )}

        <div className="preferences-sections">
          {/* Horror Types Section */}
          <motion.section 
            className="preference-section"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h2>🦇 Preferred Horror Types</h2>
            <p className="section-description">
              Choose which types of horror shall curse your content...
            </p>
            <div className="horror-types-grid">
              {HORROR_TYPES.map((type, index) => (
                <motion.label
                  key={type.value}
                  className={`horror-type-option ${preferences.preferred_horror_types.includes(type.value) ? 'selected' : ''}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + index * 0.05 }}
                >
                  <input
                    type="checkbox"
                    checked={preferences.preferred_horror_types.includes(type.value)}
                    onChange={() => handleHorrorTypeToggle(type.value)}
                  />
                  <span className="checkmark">👻</span>
                  <span className="type-name">{type.display}</span>
                </motion.label>
              ))}
            </div>
          </motion.section>

          {/* Intensity Level Section */}
          <motion.section 
            className="preference-section"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h2>🌙 Horror Intensity</h2>
            <p className="section-description">
              How deeply should the darkness penetrate your soul?
            </p>
            <div className="intensity-selector">
              <div className="intensity-labels">
                <span>Gentle Whisper</span>
                <span>Absolute Terror</span>
              </div>
              <div className="intensity-slider-container">
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={preferences.intensity_level}
                  onChange={(e) => handleIntensityChange(parseInt(e.target.value))}
                  className="intensity-slider"
                />
                <div className="intensity-markers">
                  {[1, 2, 3, 4, 5].map(level => (
                    <div
                      key={level}
                      className={`intensity-marker ${preferences.intensity_level >= level ? 'active' : ''}`}
                    />
                  ))}
                </div>
              </div>
              <div className="current-intensity">
                Current: <strong>{getIntensityLabel(preferences.intensity_level)}</strong>
              </div>
            </div>
          </motion.section>

          {/* Content Filters Section */}
          <motion.section 
            className="preference-section"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
          >
            <h2>🚫 Content Filters</h2>
            <p className="section-description">
              Banish certain dark themes from your cursed content...
            </p>
            <div className="content-filters-grid">
              {CONTENT_FILTERS.map((filter, index) => (
                <motion.label
                  key={filter}
                  className={`filter-option ${preferences.content_filters.includes(filter) ? 'filtered' : ''}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 + index * 0.05 }}
                >
                  <input
                    type="checkbox"
                    checked={preferences.content_filters.includes(filter)}
                    onChange={() => handleContentFilterToggle(filter)}
                  />
                  <span className="filter-checkmark">🛡️</span>
                  <span className="filter-name">{filter}</span>
                </motion.label>
              ))}
            </div>
          </motion.section>

          {/* Notification Settings Section */}
          <motion.section 
            className="preference-section"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
          >
            <h2>🔔 Ghostly Notifications</h2>
            <p className="section-description">
              Configure how the spirits shall whisper to you...
            </p>
            <div className="notification-settings">
              {[
                { key: 'new_variants', label: 'New Spooky Variants', icon: '👻' },
                { key: 'processing_complete', label: 'Feed Processing Complete', icon: '⚡' },
                { key: 'error_alerts', label: 'Error Alerts', icon: '⚠️' },
                { key: 'daily_summary', label: 'Daily Horror Summary', icon: '📊' }
              ].map((setting, index) => (
                <motion.label
                  key={setting.key}
                  className={`notification-option ${preferences.notification_settings[setting.key] ? 'enabled' : ''}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 + index * 0.1 }}
                >
                  <input
                    type="checkbox"
                    checked={preferences.notification_settings[setting.key] || false}
                    onChange={() => handleNotificationToggle(setting.key)}
                  />
                  <span className="notification-icon">{setting.icon}</span>
                  <span className="notification-label">{setting.label}</span>
                </motion.label>
              ))}
            </div>
          </motion.section>
        </div>

        {/* Save Button */}
        <motion.div 
          className="save-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
        >
          <Button
            onClick={handleSavePreferences}
            disabled={saving}
            className="save-preferences-btn"
          >
            {saving ? '🌀 Binding to the Void...' : '💾 Save Cursed Preferences'}
          </Button>
          
          {saveMessage && (
            <motion.div
              className={`save-message ${saveMessage.includes('saved') ? 'success' : 'error'}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              {saveMessage}
            </motion.div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default PreferencesPage;