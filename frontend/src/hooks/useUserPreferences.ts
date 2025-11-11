import { useState, useEffect, useCallback } from 'react';
import { StorageService } from '../services/storage';
import type { UserPreferences } from '../types';

const DEFAULT_PREFERENCES: UserPreferences = {
  preferred_horror_types: ['gothic', 'supernatural'],
  intensity_level: 3,
  content_filters: [],
  notification_settings: {
    new_variants: true,
    processing_complete: true,
    error_alerts: true,
    daily_summary: false,
  },
  theme_customizations: {
    primary_color: '#8a2be2',
    accent_color: '#4b0082',
    fog_intensity: 'medium',
  },
};

const useUserPreferences = () => {
  const [preferences, setPreferencesState] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load preferences from localStorage on mount
  useEffect(() => {
    try {
      const stored = StorageService.loadPreferences();
      if (stored) {
        // Merge with defaults to ensure all properties exist
        setPreferencesState({
          ...DEFAULT_PREFERENCES,
          ...stored,
          notification_settings: {
            ...DEFAULT_PREFERENCES.notification_settings,
            ...stored.notification_settings,
          },
          theme_customizations: {
            ...DEFAULT_PREFERENCES.theme_customizations,
            ...stored.theme_customizations,
          },
        });
      }
    } catch (err) {
      console.error('Failed to load preferences from localStorage:', err);
      setError('Failed to load your cursed preferences from the ethereal storage');
    } finally {
      setLoading(false);
    }
  }, []);

  // Save preferences to localStorage whenever they change
  const setPreferences = useCallback((newPreferences: UserPreferences) => {
    try {
      setPreferencesState(newPreferences);
      StorageService.savePreferences(newPreferences);
      setError(null);
    } catch (err) {
      console.error('Failed to save preferences to localStorage:', err);
      setError('Failed to bind your preferences to the void');
    }
  }, []);

  // Update specific preference sections
  const updateHorrorTypes = useCallback((horrorTypes: string[]) => {
    setPreferences({
      ...preferences,
      preferred_horror_types: horrorTypes,
    });
  }, [preferences, setPreferences]);

  const updateIntensity = useCallback((intensity: number) => {
    setPreferences({
      ...preferences,
      intensity_level: Math.max(1, Math.min(5, intensity)),
    });
  }, [preferences, setPreferences]);

  const updateContentFilters = useCallback((filters: string[]) => {
    setPreferences({
      ...preferences,
      content_filters: filters,
    });
  }, [preferences, setPreferences]);

  const updateNotificationSettings = useCallback((settings: Record<string, boolean>) => {
    setPreferences({
      ...preferences,
      notification_settings: {
        ...preferences.notification_settings,
        ...settings,
      },
    });
  }, [preferences, setPreferences]);

  const updateThemeCustomizations = useCallback((customizations: Record<string, string>) => {
    setPreferences({
      ...preferences,
      theme_customizations: {
        ...preferences.theme_customizations,
        ...customizations,
      },
    });
  }, [preferences, setPreferences]);

  // Reset to defaults
  const resetPreferences = useCallback(() => {
    setPreferences(DEFAULT_PREFERENCES);
  }, [setPreferences]);

  // Check if preferences have been modified from defaults
  const isModified = useCallback(() => {
    return JSON.stringify(preferences) !== JSON.stringify(DEFAULT_PREFERENCES);
  }, [preferences]);

  return {
    preferences,
    loading,
    error,
    setPreferences,
    updateHorrorTypes,
    updateIntensity,
    updateContentFilters,
    updateNotificationSettings,
    updateThemeCustomizations,
    resetPreferences,
    isModified,
  };
};

export default useUserPreferences;