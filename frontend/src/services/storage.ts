// Storage service for persisting data using localStorage
import type { SpookyFeed, UserPreferences } from '../types';

const STORAGE_KEYS = {
  FEEDS: 'spooky_feeds',
  PREFERENCES: 'spooky_preferences',
  LAST_SYNC: 'spooky_last_sync',
  USER_ID: 'spooky_user_id',
} as const;

export class StorageService {
  // Feed Management
  static saveFeeds(feeds: SpookyFeed[]): void {
    try {
      localStorage.setItem(STORAGE_KEYS.FEEDS, JSON.stringify(feeds));
      localStorage.setItem(STORAGE_KEYS.LAST_SYNC, new Date().toISOString());
    } catch (error) {
      console.error('Failed to save feeds to localStorage:', error);
    }
  }

  static loadFeeds(): SpookyFeed[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.FEEDS);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to load feeds from localStorage:', error);
      return [];
    }
  }

  static addFeed(feed: SpookyFeed): void {
    const feeds = this.loadFeeds();
    const updatedFeeds = [feed, ...feeds];
    this.saveFeeds(updatedFeeds);
  }

  static updateFeed(feedId: string, updates: Partial<SpookyFeed>): void {
    const feeds = this.loadFeeds();
    const updatedFeeds = feeds.map(feed =>
      feed.id === feedId ? { ...feed, ...updates } : feed
    );
    this.saveFeeds(updatedFeeds);
  }

  static removeFeed(feedId: string): void {
    const feeds = this.loadFeeds();
    const updatedFeeds = feeds.filter(feed => feed.id !== feedId);
    this.saveFeeds(updatedFeeds);
  }

  static clearFeeds(): void {
    localStorage.removeItem(STORAGE_KEYS.FEEDS);
    localStorage.removeItem(STORAGE_KEYS.LAST_SYNC);
  }

  // Preferences Management
  static savePreferences(preferences: UserPreferences): void {
    try {
      localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(preferences));
    } catch (error) {
      console.error('Failed to save preferences to localStorage:', error);
    }
  }

  static loadPreferences(): UserPreferences | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.PREFERENCES);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Failed to load preferences from localStorage:', error);
      return null;
    }
  }

  // User ID Management
  static getUserId(): string {
    let userId = localStorage.getItem(STORAGE_KEYS.USER_ID);
    if (!userId) {
      userId = `ghost_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
    }
    return userId;
  }

  // Metadata
  static getLastSyncTime(): string | null {
    return localStorage.getItem(STORAGE_KEYS.LAST_SYNC);
  }

  // Clear all data
  static clearAll(): void {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  }

  // Export/Import functionality for backup
  static exportData(): string {
    const data = {
      feeds: this.loadFeeds(),
      preferences: this.loadPreferences(),
      lastSync: this.getLastSyncTime(),
      exportDate: new Date().toISOString(),
    };
    return JSON.stringify(data, null, 2);
  }

  static importData(jsonData: string): boolean {
    try {
      const data = JSON.parse(jsonData);
      if (data.feeds) this.saveFeeds(data.feeds);
      if (data.preferences) this.savePreferences(data.preferences);
      return true;
    } catch (error) {
      console.error('Failed to import data:', error);
      return false;
    }
  }
}
