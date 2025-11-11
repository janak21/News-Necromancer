import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useUserPreferences from '../useUserPreferences';
import { StorageService } from '../../services/storage';

// Mock the StorageService
vi.mock('../../services/storage', () => ({
  StorageService: {
    loadPreferences: vi.fn(),
    savePreferences: vi.fn(),
  },
}));

describe('useUserPreferences - Intensity System', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset localStorage mock
    (StorageService.loadPreferences as any).mockReturnValue(null);
  });

  describe('Initial State', () => {
    it('initializes with default intensity level of 3', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      expect(result.current.preferences.intensity_level).toBe(3);
    });

    it('loads saved intensity level from storage', () => {
      const savedPreferences = {
        preferred_horror_types: ['gothic'],
        intensity_level: 5,
        content_filters: [],
        notification_settings: {},
        theme_customizations: {},
      };
      
      (StorageService.loadPreferences as any).mockReturnValue(savedPreferences);
      
      const { result } = renderHook(() => useUserPreferences());
      
      expect(result.current.preferences.intensity_level).toBe(5);
    });
  });

  describe('updateIntensity Function', () => {
    it('updates intensity level correctly', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(4);
      });
      
      expect(result.current.preferences.intensity_level).toBe(4);
    });

    it('clamps intensity to minimum value of 1', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(0);
      });
      
      expect(result.current.preferences.intensity_level).toBe(1);
    });

    it('clamps intensity to maximum value of 5', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(10);
      });
      
      expect(result.current.preferences.intensity_level).toBe(5);
    });

    it('handles negative intensity values', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(-5);
      });
      
      expect(result.current.preferences.intensity_level).toBe(1);
    });

    it('preserves other preferences when updating intensity', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      const originalHorrorTypes = result.current.preferences.preferred_horror_types;
      const originalFilters = result.current.preferences.content_filters;
      
      act(() => {
        result.current.updateIntensity(5);
      });
      
      expect(result.current.preferences.preferred_horror_types).toEqual(originalHorrorTypes);
      expect(result.current.preferences.content_filters).toEqual(originalFilters);
    });
  });

  describe('Persistence', () => {
    it('saves intensity changes to storage', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(4);
      });
      
      expect(StorageService.savePreferences).toHaveBeenCalledWith(
        expect.objectContaining({
          intensity_level: 4,
        })
      );
    });

    it('saves intensity changes immediately', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(2);
      });
      
      expect(StorageService.savePreferences).toHaveBeenCalledTimes(1);
    });

    it('persists multiple intensity changes', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(1);
      });
      
      act(() => {
        result.current.updateIntensity(3);
      });
      
      act(() => {
        result.current.updateIntensity(5);
      });
      
      expect(StorageService.savePreferences).toHaveBeenCalledTimes(3);
      expect(result.current.preferences.intensity_level).toBe(5);
    });
  });

  describe('Integration with setPreferences', () => {
    it('updates intensity through setPreferences', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      const newPreferences = {
        ...result.current.preferences,
        intensity_level: 4,
      };
      
      act(() => {
        result.current.setPreferences(newPreferences);
      });
      
      expect(result.current.preferences.intensity_level).toBe(4);
    });

    it('saves to storage when using setPreferences', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      const newPreferences = {
        ...result.current.preferences,
        intensity_level: 5,
      };
      
      act(() => {
        result.current.setPreferences(newPreferences);
      });
      
      expect(StorageService.savePreferences).toHaveBeenCalledWith(
        expect.objectContaining({
          intensity_level: 5,
        })
      );
    });
  });

  describe('Reset Functionality', () => {
    it('resets intensity to default value of 3', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(5);
      });
      
      expect(result.current.preferences.intensity_level).toBe(5);
      
      act(() => {
        result.current.resetPreferences();
      });
      
      expect(result.current.preferences.intensity_level).toBe(3);
    });
  });

  describe('Error Handling', () => {
    it('handles storage save errors gracefully', () => {
      (StorageService.savePreferences as any).mockImplementation(() => {
        throw new Error('Storage error');
      });
      
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(4);
      });
      
      expect(result.current.error).toBeTruthy();
    });

    it('continues to update state even when storage fails', () => {
      (StorageService.savePreferences as any).mockImplementation(() => {
        throw new Error('Storage error');
      });
      
      const { result } = renderHook(() => useUserPreferences());
      
      act(() => {
        result.current.updateIntensity(4);
      });
      
      expect(result.current.preferences.intensity_level).toBe(4);
    });
  });

  describe('State Management', () => {
    it('maintains intensity state across multiple updates', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      const intensityLevels = [1, 2, 3, 4, 5, 3, 1, 5];
      
      intensityLevels.forEach(level => {
        act(() => {
          result.current.updateIntensity(level);
        });
        expect(result.current.preferences.intensity_level).toBe(level);
      });
    });

    it('detects modifications when intensity changes', () => {
      const { result } = renderHook(() => useUserPreferences());
      
      expect(result.current.isModified()).toBe(false);
      
      act(() => {
        result.current.updateIntensity(5);
      });
      
      expect(result.current.isModified()).toBe(true);
    });
  });
});
