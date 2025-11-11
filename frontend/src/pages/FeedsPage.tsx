import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FeedList, Button, ErrorBoundary } from '../components';
import { ApiService } from '../services/api';
import { useFeedPersistence } from '../hooks/useFeedPersistence';
import { useGhostNotificationContext } from '../contexts/GhostNotificationContext';
import useUserPreferences from '../hooks/useUserPreferences';
import type { SpookyFeed, SpookyVariant, StoryContinuation } from '../types';
import './FeedsPage.css';

const FeedsPage: React.FC = () => {
  const { feeds, addFeed, removeFeed, isLoading, lastSync } = useFeedPersistence();
  const { preferences } = useUserPreferences();
  const [newFeedUrl, setNewFeedUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const { showSuccess, showError, showInfo, showWarning } = useGhostNotificationContext();

  // Show restoration message on mount
  useEffect(() => {
    if (!isLoading && feeds.length > 0 && lastSync) {
      const syncDate = new Date(lastSync).toLocaleString();
      showInfo(`👻 Restored ${feeds.length} haunted feed(s) from ${syncDate}`);
    }
  }, [isLoading]);

  const handleVariantSelect = (variant: SpookyVariant) => {
    // Open the original article in a new tab
    window.open(variant.original_item.link, '_blank', 'noopener,noreferrer');
  };

  const handleFeedDelete = (feedId: string) => {
    const feed = feeds.find(f => f.id === feedId);
    if (feed) {
      removeFeed(feedId);
      showSuccess(`🗑️ Deleted "${feed.title}" and all its spooky variants`);
    }
  };

  const handleAddFeed = async () => {
    if (!newFeedUrl.trim()) {
      showWarning('🔮 Please enter a cursed RSS URL to haunt...');
      return;
    }

    // Basic URL validation
    try {
      new URL(newFeedUrl);
    } catch {
      showError('💀 That URL appears to be from a realm beyond comprehension...');
      return;
    }

    setIsProcessing(true);
    showInfo('🕷️ Summoning dark forces to process your feed...');

    try {
      // Use the real API to process the feed with user preferences and intensity
      // Generate only 1 variant per feed item to avoid duplicates
      const response = await ApiService.processFeeds(
        [newFeedUrl], 
        preferences,
        preferences.intensity_level,
        1  // Only generate 1 variant per item
      );
      
      if (response.success) {
        setProcessingId(response.processing_id);
        showSuccess(`👻 Successfully processed ${response.total_feeds} feed(s) and generated ${response.total_variants} spooky variants!`);
        
        // Convert the API response variants to SpookyVariant format
        const variants: SpookyVariant[] = response.variants.map((variant: any) => ({
          original_item: variant.original_item,
          haunted_title: variant.haunted_title,
          haunted_summary: variant.haunted_summary,
          horror_themes: variant.horror_themes,
          supernatural_explanation: variant.supernatural_explanation,
          personalization_applied: variant.personalization_applied,
          generation_timestamp: variant.generation_timestamp,
          variant_id: variant.variant_id
        }));
        
        // Create a new feed with the processed variants
        const newFeed: SpookyFeed = {
          id: response.processing_id,
          url: newFeedUrl,
          title: `Haunted Feed: ${new URL(newFeedUrl).hostname}`,
          last_updated: new Date().toISOString(),
          variants: variants
        };
        
        addFeed(newFeed);
        setNewFeedUrl('');
        showInfo(`⚡ Processing completed in ${response.processing_time.toFixed(2)} seconds`);
      } else {
        showError(`💀 The dark ritual failed: ${response.message}`);
      }
      
    } catch (error) {
      console.error('Error processing feed:', error);
      showError('💀 The dark ritual failed. The RSS spirits reject your offering...');
    } finally {
      setIsProcessing(false);
      setProcessingId(null);
    }
  };

  const sampleFeeds = [
    'https://www.forbes.com/business/feed/',
    'https://feeds.bbci.co.uk/news/rss.xml',
    'https://rss.cnn.com/rss/edition.rss',
    'https://feeds.reuters.com/reuters/topNews',
    'https://techcrunch.com/feed/',
    'https://www.theverge.com/rss/index.xml'
  ];

  const handleUseSampleFeed = (url: string) => {
    setNewFeedUrl(url);
    showInfo('🔮 Sample feed URL has been summoned to the input field...');
  };

  const handleContinueStory = async (variantId: string): Promise<StoryContinuation> => {
    try {
      showInfo('🌙 Summoning darker forces to continue the nightmare...');
      const continuation = await ApiService.continueStory(variantId);
      showSuccess('✨ The nightmare continues...');
      return continuation;
    } catch (error) {
      console.error('Error continuing story:', error);
      showError('💀 Failed to continue the nightmare. The spirits are restless...');
      throw error;
    }
  };

  return (
    <ErrorBoundary>
      <motion.div 
        className="feeds-page"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
      <div style={{ padding: 'var(--spacing-md)', maxWidth: '1200px', margin: '0 auto' }}>
        <motion.div
          style={{ textAlign: 'center', marginBottom: 'var(--spacing-md)' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h1 
            style={{ 
              fontSize: 'clamp(1.75rem, 4vw, 2.25rem)', 
              fontWeight: 'var(--font-weight-bold)',
              color: 'var(--color-text)',
              marginBottom: 'var(--spacing-xs)',
              lineHeight: 1.2
            }}
          >
            Your Spooky Feeds 👻
          </h1>
          
          <p 
            style={{ 
              fontSize: 'clamp(0.875rem, 1.5vw, 1rem)', 
              color: 'var(--color-text-secondary)',
              margin: 0,
              lineHeight: 1.3
            }}
          >
            Transform ordinary RSS feeds into spine-chilling horror stories
          </p>
        </motion.div>

        {/* Add Feed Section - Compact */}
        <motion.div 
          style={{
            background: 'rgba(138, 43, 226, 0.1)',
            border: '1px solid rgba(138, 43, 226, 0.3)',
            borderRadius: '10px',
            padding: 'var(--spacing-md)',
            marginBottom: 'var(--spacing-lg)',
            backdropFilter: 'blur(10px)'
          }}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h2 style={{ 
            fontSize: 'clamp(1.125rem, 2vw, 1.25rem)', 
            color: 'var(--color-primary)',
            marginBottom: 'var(--spacing-sm)',
            textAlign: 'center',
            lineHeight: 1.2
          }}>
            🔮 Summon New RSS Feed
          </h2>
          
          <div style={{ 
            display: 'flex', 
            gap: 'var(--spacing-sm)', 
            marginBottom: 'var(--spacing-sm)',
            flexWrap: 'wrap'
          }}>
            <input
              type="url"
              value={newFeedUrl}
              onChange={(e) => setNewFeedUrl(e.target.value)}
              placeholder="Enter RSS feed URL to haunt..."
              disabled={isProcessing}
              style={{
                flex: 1,
                minWidth: '250px',
                padding: 'var(--spacing-sm)',
                borderRadius: '8px',
                border: '2px solid rgba(138, 43, 226, 0.3)',
                background: 'rgba(20, 20, 30, 0.8)',
                color: 'var(--color-text)',
                fontSize: 'clamp(0.875rem, 1.5vw, 1rem)',
                outline: 'none',
                transition: 'border-color 0.3s ease'
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--color-primary)'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(138, 43, 226, 0.3)'}
            />
            <Button
              variant="primary"
              onClick={handleAddFeed}
              disabled={isProcessing}
              style={{ minWidth: '140px', whiteSpace: 'nowrap' }}
            >
              {isProcessing ? '🌀 Haunting...' : '👻 Haunt Feed'}
            </Button>
          </div>

          {/* Sample Feeds - Compact */}
          <div>
            <p style={{ 
              color: 'var(--color-text-secondary)', 
              marginBottom: 'var(--spacing-xs)',
              fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)'
            }}>
              🎭 Try sample feeds:
            </p>
            <div style={{ 
              display: 'flex', 
              gap: 'var(--spacing-xs)', 
              flexWrap: 'wrap' 
            }}>
              {sampleFeeds.map((url, index) => (
                <button
                  key={index}
                  onClick={() => handleUseSampleFeed(url)}
                  disabled={isProcessing}
                  style={{
                    padding: '0.375rem 0.75rem',
                    borderRadius: '6px',
                    border: '1px solid rgba(138, 43, 226, 0.4)',
                    background: 'rgba(138, 43, 226, 0.1)',
                    color: 'var(--color-text-secondary)',
                    fontSize: 'clamp(0.75rem, 1.2vw, 0.875rem)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    whiteSpace: 'nowrap'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(138, 43, 226, 0.2)';
                    e.currentTarget.style.color = 'var(--color-text)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(138, 43, 226, 0.1)';
                    e.currentTarget.style.color = 'var(--color-text-secondary)';
                  }}
                >
                  {new URL(url).hostname.replace('www.', '')}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Processing Status */}
        {isProcessing && processingId && (
          <motion.div
            style={{
              background: 'rgba(75, 0, 130, 0.2)',
              border: '1px solid rgba(75, 0, 130, 0.4)',
              borderRadius: '8px',
              padding: 'var(--spacing-md)',
              marginBottom: 'var(--spacing-lg)',
              textAlign: 'center'
            }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p style={{ color: 'var(--color-primary)', margin: 0 }}>
              🌀 Processing ID: {processingId} - The spirits are weaving dark magic...
            </p>
          </motion.div>
        )}
        
        {/* Feed List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <FeedList 
            feeds={feeds}
            onVariantSelect={handleVariantSelect}
            onFeedDelete={handleFeedDelete}
            onContinueStory={handleContinueStory}
            showFilters={true}
            compactView={false}
          />
        </motion.div>
      </div>
    </motion.div>
    </ErrorBoundary>
  );
};

export default FeedsPage;