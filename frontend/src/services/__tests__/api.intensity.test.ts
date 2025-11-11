import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ApiService } from '../api';
import type { UserPreferences } from '../../types';

describe('ApiService - Intensity Integration', () => {
  const mockFetch = vi.fn();
  
  beforeEach(() => {
    global.fetch = mockFetch;
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('processFeeds with Intensity', () => {
    it('includes intensity parameter in request body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      await ApiService.processFeeds(['https://example.com/feed'], undefined, 4);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/feeds/process'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            urls: ['https://example.com/feed'],
            intensity: 4,
          }),
        })
      );
    });

    it('sends minimum intensity level (1)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      await ApiService.processFeeds(['https://example.com/feed'], undefined, 1);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.intensity).toBe(1);
    });

    it('sends maximum intensity level (5)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      await ApiService.processFeeds(['https://example.com/feed'], undefined, 5);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.intensity).toBe(5);
    });

    it('omits intensity parameter when not provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      await ApiService.processFeeds(['https://example.com/feed']);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.intensity).toBeUndefined();
    });

    it('includes both preferences and intensity when both provided', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      const preferences: UserPreferences = {
        preferred_horror_types: ['gothic', 'psychological'],
        intensity_level: 4,
        content_filters: [],
        notification_settings: {},
        theme_customizations: {},
      };

      await ApiService.processFeeds(['https://example.com/feed'], preferences, 4);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.user_preferences).toEqual(preferences);
      expect(requestBody.intensity).toBe(4);
    });

    it('handles intensity with multiple feed URLs', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 3,
          total_variants: 15,
          processing_time: 3.5,
          variants: [],
        }),
      });

      const urls = [
        'https://example.com/feed1',
        'https://example.com/feed2',
        'https://example.com/feed3',
      ];

      await ApiService.processFeeds(urls, undefined, 3);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.urls).toEqual(urls);
      expect(requestBody.intensity).toBe(3);
    });
  });

  describe('updateUserPreferences with Intensity', () => {
    it('includes intensity_level in preferences update', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'success' }),
      });

      const preferences: UserPreferences = {
        preferred_horror_types: ['cosmic'],
        intensity_level: 5,
        content_filters: ['gore'],
        notification_settings: { new_variants: true },
        theme_customizations: { primary_color: '#8a2be2' },
      };

      await ApiService.updateUserPreferences(preferences);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.intensity_level).toBe(5);
    });

    it('updates intensity level independently', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'success' }),
      });

      const preferences: UserPreferences = {
        preferred_horror_types: ['gothic'],
        intensity_level: 2,
        content_filters: [],
        notification_settings: {},
        theme_customizations: {},
      };

      await ApiService.updateUserPreferences(preferences);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.intensity_level).toBe(2);
      expect(requestBody.preferred_horror_types).toEqual(['gothic']);
    });

    it('handles all intensity levels (1-5)', async () => {
      const intensityLevels = [1, 2, 3, 4, 5];

      for (const level of intensityLevels) {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'success' }),
        });

        const preferences: UserPreferences = {
          preferred_horror_types: [],
          intensity_level: level,
          content_filters: [],
          notification_settings: {},
          theme_customizations: {},
        };

        await ApiService.updateUserPreferences(preferences);

        const callArgs = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
        const requestBody = JSON.parse(callArgs[1].body);
        
        expect(requestBody.intensity_level).toBe(level);
      }
    });
  });

  describe('Error Handling with Intensity', () => {
    it('handles API errors when processing feeds with intensity', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(
        ApiService.processFeeds(['https://example.com/feed'], undefined, 4)
      ).rejects.toThrow();
    });

    it('handles network errors when updating intensity preferences', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const preferences: UserPreferences = {
        preferred_horror_types: [],
        intensity_level: 3,
        content_filters: [],
        notification_settings: {},
        theme_customizations: {},
      };

      await expect(
        ApiService.updateUserPreferences(preferences)
      ).rejects.toThrow('Network error');
    });
  });

  describe('Intensity Parameter Validation', () => {
    it('sends intensity as number type', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      await ApiService.processFeeds(['https://example.com/feed'], undefined, 3);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(typeof requestBody.intensity).toBe('number');
    });

    it('handles intensity value of 0 (edge case)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Feeds processed',
          processing_id: 'test-123',
          total_feeds: 1,
          total_variants: 5,
          processing_time: 1.5,
          variants: [],
        }),
      });

      await ApiService.processFeeds(['https://example.com/feed'], undefined, 0);

      const callArgs = mockFetch.mock.calls[0];
      const requestBody = JSON.parse(callArgs[1].body);
      
      expect(requestBody.intensity).toBe(0);
    });
  });
});
