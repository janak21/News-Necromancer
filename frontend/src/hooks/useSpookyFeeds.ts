import { useState, useEffect } from 'react';
import type { SpookyFeed } from '../types';

const useSpookyFeeds = () => {
  const [feeds, setFeeds] = useState<SpookyFeed[]>([]);
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);

  // Placeholder implementation - to be enhanced later
  useEffect(() => {
    // This will be implemented when we integrate with the API
  }, []);

  return {
    feeds,
    loading,
    error,
    setFeeds,
  };
};

export default useSpookyFeeds;