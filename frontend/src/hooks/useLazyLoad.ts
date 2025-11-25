import { useState, useEffect, useRef } from 'react';

interface UseLazyLoadOptions<T> {
  items: T[];
  initialCount?: number;
  loadMoreCount?: number;
  threshold?: number;
}

interface UseLazyLoadReturn<T> {
  displayedItems: T[];
  isLoadingMore: boolean;
  hasMore: boolean;
  sentinelRef: React.RefObject<HTMLDivElement | null>;
}

/**
 * Custom hook for lazy loading items with IntersectionObserver
 * @param items - Array of items to lazy load
 * @param initialCount - Number of items to show initially (default: 20)
 * @param loadMoreCount - Number of items to load when scrolling (default: 10)
 * @param threshold - Distance in pixels from bottom to trigger load (default: 200)
 */
function useLazyLoad<T>({
  items,
  initialCount = 20,
  loadMoreCount = 10,
  threshold = 200
}: UseLazyLoadOptions<T>): UseLazyLoadReturn<T> {
  const [displayCount, setDisplayCount] = useState(initialCount);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // Reset display count when items change
  useEffect(() => {
    setDisplayCount(initialCount);
  }, [items, initialCount]);

  // Set up IntersectionObserver
  useEffect(() => {
    // Clean up previous observer
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    // Create new observer
    observerRef.current = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        
        // Load more when sentinel is visible and there are more items
        if (entry.isIntersecting && displayCount < items.length && !isLoadingMore) {
          setIsLoadingMore(true);
          
          // Simulate loading delay for smooth UX
          setTimeout(() => {
            setDisplayCount(prev => Math.min(prev + loadMoreCount, items.length));
            setIsLoadingMore(false);
          }, 300);
        }
      },
      { 
        rootMargin: `${threshold}px`,
        threshold: 0.1
      }
    );

    // Observe the sentinel element
    if (sentinelRef.current) {
      observerRef.current.observe(sentinelRef.current);
    }

    // Cleanup on unmount
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [displayCount, items.length, loadMoreCount, threshold, isLoadingMore]);

  return {
    displayedItems: items.slice(0, displayCount),
    isLoadingMore,
    hasMore: displayCount < items.length,
    sentinelRef
  };
}

export default useLazyLoad;
