// Hook for managing feed data persistence
import { useState, useEffect, useCallback } from 'react';
import { StorageService } from '../services/storage';
import type { SpookyFeed } from '../types';

export const useFeedPersistence = () => {
  const [feeds, setFeedsState] = useState<SpookyFeed[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSync, setLastSync] = useState<string | null>(null);

  // Load feeds from localStorage on mount
  useEffect(() => {
    const storedFeeds = StorageService.loadFeeds();
    const syncTime = StorageService.getLastSyncTime();
    
    setFeedsState(storedFeeds);
    setLastSync(syncTime);
    setIsLoading(false);
  }, []);

  // Save feeds to localStorage
  const setFeeds = useCallback((newFeeds: SpookyFeed[] | ((prev: SpookyFeed[]) => SpookyFeed[])) => {
    setFeedsState(prev => {
      const updated = typeof newFeeds === 'function' ? newFeeds(prev) : newFeeds;
      StorageService.saveFeeds(updated);
      setLastSync(new Date().toISOString());
      return updated;
    });
  }, []);

  // Add a single feed
  const addFeed = useCallback((feed: SpookyFeed) => {
    setFeeds(prev => [feed, ...prev]);
  }, [setFeeds]);

  // Update a feed
  const updateFeed = useCallback((feedId: string, updates: Partial<SpookyFeed>) => {
    setFeeds(prev => 
      prev.map(feed => feed.id === feedId ? { ...feed, ...updates } : feed)
    );
  }, [setFeeds]);

  // Remove a feed
  const removeFeed = useCallback((feedId: string) => {
    setFeeds(prev => prev.filter(feed => feed.id !== feedId));
  }, [setFeeds]);

  // Clear all feeds
  const clearFeeds = useCallback(() => {
    StorageService.clearFeeds();
    setFeedsState([]);
    setLastSync(null);
  }, []);

  // Export feeds as JSON
  const exportFeeds = useCallback(() => {
    return StorageService.exportData();
  }, []);

  // Import feeds from JSON
  const importFeeds = useCallback((jsonData: string): boolean => {
    const success = StorageService.importData(jsonData);
    if (success) {
      const storedFeeds = StorageService.loadFeeds();
      setFeedsState(storedFeeds);
      setLastSync(StorageService.getLastSyncTime());
    }
    return success;
  }, []);

  return {
    feeds,
    setFeeds,
    addFeed,
    updateFeed,
    removeFeed,
    clearFeeds,
    exportFeeds,
    importFeeds,
    isLoading,
    lastSync,
  };
};
