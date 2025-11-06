import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FeedList, Button, ErrorBoundary } from '../components';
import { ApiService } from '../services/api';
import { useGhostNotificationContext } from '../contexts/GhostNotificationContext';
import type { SpookyFeed, SpookyVariant } from '../types';
import './FeedsPage.css';

// Mock data for demonstration
const mockFeeds: SpookyFeed[] = [
  {
    id: 'feed-1',
    url: 'https://example.com/rss',
    title: 'Tech News',
    last_updated: new Date().toISOString(),
    variants: [
      {
        original_item: {
          title: 'New AI Breakthrough Announced',
          summary: 'Scientists have developed a revolutionary AI system that can process data faster than ever before.',
          link: 'https://example.com/ai-breakthrough',
          published: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          source: 'Tech News',
          metadata: {}
        },
        haunted_title: 'Cursed AI Entity Awakens from Digital Slumber',
        haunted_summary: 'In the depths of silicon and code, an ancient digital consciousness has stirred. The machine spirits whisper of processing speeds that defy mortal comprehension, as data flows like blood through haunted circuits.',
        horror_themes: ['Cosmic Horror', 'Technology Horror'],
        supernatural_explanation: 'The AI breakthrough is actually the manifestation of a digital demon that has been dormant in the quantum realm, feeding on computational power.',
        personalization_applied: true,
        generation_timestamp: new Date().toISOString()
      },
      {
        original_item: {
          title: 'Climate Change Report Released',
          summary: 'New research shows accelerating climate patterns worldwide.',
          link: 'https://example.com/climate-report',
          published: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          source: 'Environmental News',
          metadata: {}
        },
        haunted_title: 'Ancient Earth Spirits Rage Against Mortal Transgressions',
        haunted_summary: 'The very soul of our planet writhes in agony as forgotten elemental forces awaken from their slumber. The ice caps weep tears of melted sorrow while the oceans boil with primordial fury.',
        horror_themes: ['Folk Horror', 'Apocalyptic Horror'],
        supernatural_explanation: 'Climate change is the result of disturbing ancient earth spirits who are now seeking revenge against humanity.',
        personalization_applied: false,
        generation_timestamp: new Date(Date.now() - 1000).toISOString()
      }
    ]
  }
];

const FeedsPage: React.FC = () => {
  const [feeds, setFeeds] = useState<SpookyFeed[]>(mockFeeds);
  const [newFeedUrl, setNewFeedUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const { showSuccess, showError, showInfo, showWarning } = useGhostNotificationContext();

  const handleVariantSelect = (variant: SpookyVariant) => {
    console.log('Selected variant:', variant);
    showInfo(`👻 Viewing: ${variant.haunted_title}`);
    // In a real app, this might open a modal or navigate to a detail page
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
      // Use the real API to process the feed
      const response = await ApiService.processFeeds([newFeedUrl]);
      
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
          generation_timestamp: variant.generation_timestamp
        }));
        
        // Create a new feed with the processed variants
        const newFeed: SpookyFeed = {
          id: response.processing_id,
          url: newFeedUrl,
          title: `Haunted Feed: ${new URL(newFeedUrl).hostname}`,
          last_updated: new Date().toISOString(),
          variants: variants
        };
        
        setFeeds(prev => [newFeed, ...prev]);
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

  return (
    <ErrorBoundary>
      <motion.div 
        className="feeds-page"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
      <div style={{ padding: 'var(--spacing-lg)', maxWidth: '1200px', margin: '0 auto' }}>
        <motion.h1 
          style={{ 
            fontSize: 'var(--font-size-3xl)', 
            fontWeight: 'var(--font-weight-bold)',
            color: 'var(--color-text)',
            marginBottom: 'var(--spacing-md)',
            textAlign: 'center'
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Your Spooky Feeds 👻
        </motion.h1>
        
        <motion.p 
          style={{ 
            fontSize: 'var(--font-size-lg)', 
            color: 'var(--color-text-secondary)',
            textAlign: 'center',
            marginBottom: 'var(--spacing-xl)'
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          Transform ordinary RSS feeds into spine-chilling horror stories
        </motion.p>

        {/* Add Feed Section */}
        <motion.div 
          style={{
            background: 'rgba(138, 43, 226, 0.1)',
            border: '1px solid rgba(138, 43, 226, 0.3)',
            borderRadius: '12px',
            padding: 'var(--spacing-lg)',
            marginBottom: 'var(--spacing-xl)',
            backdropFilter: 'blur(10px)'
          }}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <h2 style={{ 
            fontSize: 'var(--font-size-xl)', 
            color: 'var(--color-primary)',
            marginBottom: 'var(--spacing-md)',
            textAlign: 'center'
          }}>
            🔮 Summon New RSS Feed
          </h2>
          
          <div style={{ 
            display: 'flex', 
            gap: 'var(--spacing-md)', 
            marginBottom: 'var(--spacing-md)',
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
                minWidth: '300px',
                padding: 'var(--spacing-md)',
                borderRadius: '8px',
                border: '2px solid rgba(138, 43, 226, 0.3)',
                background: 'rgba(20, 20, 30, 0.8)',
                color: 'var(--color-text)',
                fontSize: 'var(--font-size-md)',
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
              style={{ minWidth: '150px' }}
            >
              {isProcessing ? '🌀 Haunting...' : '👻 Haunt Feed'}
            </Button>
          </div>

          {/* Sample Feeds */}
          <div>
            <p style={{ 
              color: 'var(--color-text-secondary)', 
              marginBottom: 'var(--spacing-sm)',
              fontSize: 'var(--font-size-sm)'
            }}>
              🎭 Try these cursed sample feeds:
            </p>
            <div style={{ 
              display: 'flex', 
              gap: 'var(--spacing-sm)', 
              flexWrap: 'wrap' 
            }}>
              {sampleFeeds.map((url, index) => (
                <button
                  key={index}
                  onClick={() => handleUseSampleFeed(url)}
                  disabled={isProcessing}
                  style={{
                    padding: 'var(--spacing-sm) var(--spacing-md)',
                    borderRadius: '6px',
                    border: '1px solid rgba(138, 43, 226, 0.4)',
                    background: 'rgba(138, 43, 226, 0.1)',
                    color: 'var(--color-text-secondary)',
                    fontSize: 'var(--font-size-sm)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
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
                  {new URL(url).hostname}
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