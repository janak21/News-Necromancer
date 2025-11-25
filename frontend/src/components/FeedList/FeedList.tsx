import React, { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SpookyCard from '../SpookyCard/SpookyCard';
import SpookySpinner from '../SpookySpinner/SpookySpinner';
import FilterResults from '../FilterResults/FilterResults';
import useLazyLoad from '../../hooks/useLazyLoad';
import type { SpookyVariant, SpookyFeed, StoryContinuation } from '../../types';
import './FeedList.css';

export interface FeedListProps {
  feeds: SpookyFeed[];
  onVariantSelect?: (variant: SpookyVariant) => void;
  onFeedDelete?: (feedId: string) => void;
  onContinueStory?: (variantId: string) => Promise<StoryContinuation>;
  showFilters?: boolean;
  compactView?: boolean;
  maxItemsPerFeed?: number;
}

type SortOption = 'newest' | 'oldest' | 'source' | 'themes';
type FilterOption = 'all' | 'personalized' | 'recent';

const FeedList: React.FC<FeedListProps> = ({
  feeds,
  onVariantSelect,
  onFeedDelete,
  onContinueStory,
  showFilters = true,
  compactView = false,
  maxItemsPerFeed = 5
}) => {
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [filterBy, setFilterBy] = useState<FilterOption>('all');
  const [selectedThemes, setSelectedThemes] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // Debounce search query
  useEffect(() => {
    setIsSearching(true);
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
      setIsSearching(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Extract all unique themes from variants
  const allThemes = useMemo(() => {
    const themes = new Set<string>();
    feeds.forEach(feed => {
      if (feed.variants && Array.isArray(feed.variants)) {
        feed.variants.forEach(variant => {
          if (variant.horror_themes && Array.isArray(variant.horror_themes)) {
            variant.horror_themes.forEach(theme => themes.add(theme));
          }
        });
      }
    });
    return Array.from(themes).sort();
  }, [feeds]);

  // Get all variants from all feeds with feed info
  const allVariants = useMemo(() => {
    const variants: (SpookyVariant & { feedId: string; feedTitle: string })[] = [];
    feeds.forEach(feed => {
      if (feed.variants && Array.isArray(feed.variants)) {
        const feedVariants = feed.variants.slice(0, maxItemsPerFeed);
        feedVariants.forEach(variant => {
          variants.push({
            ...variant,
            horror_themes: variant.horror_themes || [],
            feedId: feed.id,
            feedTitle: feed.title
          });
        });
      }
    });
    return variants;
  }, [feeds, maxItemsPerFeed]);

  // Filter and sort variants
  const filteredAndSortedVariants = useMemo(() => {
    let filtered = allVariants;

    // Apply search filter (using debounced query)
    if (debouncedSearchQuery.trim()) {
      const query = debouncedSearchQuery.toLowerCase();
      filtered = filtered.filter(variant =>
        variant.haunted_title.toLowerCase().includes(query) ||
        variant.haunted_summary.toLowerCase().includes(query) ||
        variant.original_item.source.toLowerCase().includes(query) ||
        variant.horror_themes.some(theme => theme.toLowerCase().includes(query))
      );
    }

    // Apply filter
    switch (filterBy) {
      case 'personalized':
        filtered = filtered.filter(variant => variant.personalization_applied);
        break;
      case 'recent':
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
        filtered = filtered.filter(variant => 
          new Date(variant.generation_timestamp) > oneDayAgo
        );
        break;
      default:
        // 'all' - no additional filtering
        break;
    }

    // Apply theme filter
    if (selectedThemes.length > 0) {
      filtered = filtered.filter(variant =>
        variant.horror_themes.some(theme => selectedThemes.includes(theme))
      );
    }

    // Sort variants
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => 
          new Date(b.original_item.published).getTime() - 
          new Date(a.original_item.published).getTime()
        );
        break;
      case 'oldest':
        filtered.sort((a, b) => 
          new Date(a.original_item.published).getTime() - 
          new Date(b.original_item.published).getTime()
        );
        break;
      case 'source':
        filtered.sort((a, b) => 
          a.original_item.source.localeCompare(b.original_item.source)
        );
        break;
      case 'themes':
        filtered.sort((a, b) => 
          a.horror_themes.length - b.horror_themes.length
        );
        break;
    }

    return filtered;
  }, [allVariants, sortBy, filterBy, selectedThemes, debouncedSearchQuery]);

  // Determine if filters are active
  const isFiltered = useMemo(() => {
    return debouncedSearchQuery.trim() !== '' || 
           filterBy !== 'all' || 
           selectedThemes.length > 0;
  }, [debouncedSearchQuery, filterBy, selectedThemes]);

  // Lazy load variants for better performance
  const { 
    displayedItems, 
    isLoadingMore, 
    hasMore, 
    sentinelRef 
  } = useLazyLoad({
    items: filteredAndSortedVariants,
    initialCount: 20,
    loadMoreCount: 10,
    threshold: 200
  });

  const handleThemeToggle = (theme: string) => {
    setSelectedThemes(prev => 
      prev.includes(theme)
        ? prev.filter(t => t !== theme)
        : [...prev, theme]
    );
  };

  const clearFilters = () => {
    setFilterBy('all');
    setSelectedThemes([]);
    setSearchQuery('');
    setSortBy('newest');
  };



  if (feeds.length === 0) {
    return (
      <motion.div 
        className="feed-list feed-list--empty"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div 
          className="feed-list__empty-state"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5, type: "spring" }}
        >
          <motion.span 
            className="feed-list__empty-icon"
            animate={{ 
              rotate: [0, -10, 10, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              repeatDelay: 3
            }}
          >
            👻
          </motion.span>
          <motion.h2 
            className="feed-list__empty-title"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.4 }}
          >
            No Spooky Content Yet
          </motion.h2>
          <motion.p 
            className="feed-list__empty-description"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.4 }}
          >
            Add some RSS feeds above to start generating haunted variants of your favorite content.
          </motion.p>
          <motion.div
            className="feed-list__empty-hint"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.4 }}
          >
            💡 Tip: Try one of the sample feeds to get started quickly!
          </motion.div>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className={`feed-list ${compactView ? 'feed-list--compact' : ''}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {showFilters && (
        <motion.div 
          className="feed-list__controls"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className={`feed-list__search ${isSearching ? 'feed-list__search--searching' : ''}`}>
            <input
              type="text"
              placeholder="Search spooky content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="feed-list__search-input"
              aria-label="Search through spooky content"
            />
            {isSearching && (
              <div className="feed-list__search-spinner">
                <SpookySpinner variant="spiral" size="small" />
              </div>
            )}
          </div>

          <div className="feed-list__filters">
            <div className="feed-list__filter-group">
              <label className="feed-list__filter-label">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                className="feed-list__filter-select"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="source">Source</option>
                <option value="themes">Theme Count</option>
              </select>
            </div>

            <div className="feed-list__filter-group">
              <label className="feed-list__filter-label">Filter:</label>
              <select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value as FilterOption)}
                className="feed-list__filter-select"
              >
                <option value="all">All Content</option>
                <option value="personalized">Personalized</option>
                <option value="recent">Recent (24h)</option>
              </select>
            </div>

            {(selectedThemes.length > 0 || searchQuery || filterBy !== 'all' || sortBy !== 'newest') && (
              <button
                onClick={clearFilters}
                className="feed-list__clear-filters"
                type="button"
              >
                Clear Filters
              </button>
            )}
          </div>

          {allThemes.length > 0 && (
            <div className="feed-list__theme-filters">
              <span className="feed-list__theme-label">Horror Themes:</span>
              <div className="feed-list__theme-tags">
                {allThemes.map(theme => (
                  <button
                    key={theme}
                    onClick={() => handleThemeToggle(theme)}
                    className={`feed-list__theme-tag ${
                      selectedThemes.includes(theme) ? 'feed-list__theme-tag--active' : ''
                    }`}
                    type="button"
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Filter Results Count */}
          <FilterResults
            totalCount={allVariants.length}
            filteredCount={filteredAndSortedVariants.length}
            isFiltered={isFiltered}
          />
        </motion.div>
      )}

      {/* Feed Management Section */}
      {onFeedDelete && feeds.length > 0 && (
        <motion.div 
          className="feed-list__feeds"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="feed-list__feeds-header">
            <h2 className="feed-list__feeds-title">📡 Your Feeds ({feeds.length})</h2>
            {feeds.length > 1 && (
              <button
                onClick={() => {
                  const totalVariants = feeds.reduce((sum, feed) => sum + feed.variants.length, 0);
                  const message = `⚠️ DELETE ALL FEEDS?\n\nThis will permanently remove:\n• ${feeds.length} feed${feeds.length !== 1 ? 's' : ''}\n• ${totalVariants} spooky variant${totalVariants !== 1 ? 's' : ''}\n• All associated data\n\nThis action cannot be undone!\n\nType "DELETE" to confirm.`;
                  const confirmation = prompt(message);
                  if (confirmation === 'DELETE') {
                    feeds.forEach(feed => onFeedDelete(feed.id));
                  } else if (confirmation !== null) {
                    alert('Deletion cancelled. You must type "DELETE" exactly to confirm.');
                  }
                }}
                className="feed-list__feeds-delete-all"
                title="Delete all feeds (requires confirmation)"
                type="button"
              >
                🗑️ Delete All
              </button>
            )}
          </div>
          <div className="feed-list__feeds-grid">
            <AnimatePresence mode="popLayout">
              {feeds.map((feed) => (
                <motion.div
                  key={feed.id}
                  className="feed-list__feed-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20, height: 0, marginBottom: 0 }}
                  transition={{ duration: 0.3 }}
                  layout
                >
                  <div className="feed-list__feed-info">
                    <span className="feed-list__feed-title">{feed.title}</span>
                    <span className="feed-list__feed-url">{feed.url}</span>
                    <span className="feed-list__feed-meta">
                      {feed.variants.length} variant{feed.variants.length !== 1 ? 's' : ''} • 
                      Updated {new Date(feed.last_updated).toLocaleDateString()}
                    </span>
                  </div>
                  <button
                    onClick={() => {
                      const variantCount = feed.variants.length;
                      const message = `Delete "${feed.title}"?\n\nThis will permanently remove:\n• ${variantCount} spooky variant${variantCount !== 1 ? 's' : ''}\n• All associated data\n\nThis action cannot be undone.`;
                      if (confirm(message)) {
                        onFeedDelete(feed.id);
                      }
                    }}
                    className="feed-list__feed-delete"
                    title="Delete this feed and all its variants"
                    type="button"
                  >
                    🗑️
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      )}

      <motion.div 
        className="feed-list__results"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <motion.div 
          className="feed-list__grid"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ staggerChildren: 0.1, delayChildren: 0.2 }}
        >
          <AnimatePresence mode="popLayout">
            {displayedItems.map((variant, index) => (
              <motion.div
                key={`${variant.original_item.link}-${index}`}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                layout
                layoutId={`card-${variant.original_item.link}-${index}`}
              >
                <SpookyCard
                  variant={variant}
                  onReadMore={onVariantSelect}
                  onContinueStory={onContinueStory}
                  compact={compactView}
                />
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Lazy loading sentinel */}
          {hasMore && (
            <div ref={sentinelRef} className="feed-list__sentinel">
              {isLoadingMore && (
                <motion.div
                  className="feed-list__loading-more"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <SpookySpinner 
                    variant="ghost" 
                    size="medium"
                    message="Loading more nightmares..."
                  />
                </motion.div>
              )}
            </div>
          )}
        </motion.div>

        <AnimatePresence>
          {filteredAndSortedVariants.length === 0 && (
            <motion.div 
              className="feed-list__no-results"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.5 }}
            >
              <motion.span 
                className="feed-list__no-results-icon"
                animate={{ 
                  rotate: [0, 10, -10, 0],
                  scale: [1, 1.1, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 2
                }}
              >
                🔍
              </motion.span>
              <motion.h2 
                className="feed-list__no-results-title"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.4 }}
              >
                No Matching Content
              </motion.h2>
              <motion.p 
                className="feed-list__no-results-description"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.4 }}
              >
                Try adjusting your filters or search terms to find more spooky content.
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

export default FeedList;