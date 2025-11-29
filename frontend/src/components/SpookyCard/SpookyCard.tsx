import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Card from '../Card/Card';
import SupernaturalReveal from '../SupernaturalReveal';
import StoryContinuation from '../StoryContinuation';
import AudioPlayer from '../AudioPlayer/AudioPlayer';
import type { SpookyVariant, StoryContinuation as StoryContinuationType } from '../../types';
import { VoiceStyle } from '../../types/narration';
import { useSoundEffects } from '../../hooks';
import './SpookyCard.css';

export interface SpookyCardProps {
  variant: SpookyVariant;
  onReadMore?: (variant: SpookyVariant) => void;
  onContinueStory?: (variantId: string) => Promise<StoryContinuationType>;
  showThemes?: boolean;
  compact?: boolean;
}

const SpookyCard: React.FC<SpookyCardProps> = ({
  variant,
  onReadMore,
  onContinueStory,
  showThemes = true,
  compact = false
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAudioPlayer, setShowAudioPlayer] = useState(false);
  const { playSound } = useSoundEffects();
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown date';
    }
  };

  const handleReadMore = () => {
    if (onReadMore) {
      onReadMore(variant);
    } else {
      // Fallback to opening original link
      window.open(variant.original_item.link, '_blank', 'noopener,noreferrer');
    }
  };



  const handleHoverStart = () => {
    setIsHovered(true);
    playSound('whisper');
  };

  const handleHoverEnd = () => {
    setIsHovered(false);
  };

  const handleExpansionToggle = (expanded: boolean) => {
    // Only play sound if state is actually changing
    if (expanded !== isExpanded) {
      setIsExpanded(expanded);
      if (expanded) {
        playSound('creak');
      }
    }
  };

  const handleAudioPlayerToggle = () => {
    setShowAudioPlayer(!showAudioPlayer);
    if (!showAudioPlayer) {
      playSound('whisper');
    }
  };

  // Get default voice style - always use Demonic Growl
  const getDefaultVoiceStyle = (): VoiceStyle => {
    return VoiceStyle.DEMONIC_GROWL;
  };

  // Get intensity level (default to 3 if not available)
  const getIntensityLevel = (): number => {
    // Could be derived from user preferences or variant metadata
    // For now, use a default of 3 (medium intensity)
    return 3;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      whileHover={{ y: -8, scale: 1.02 }}
      onHoverStart={handleHoverStart}
      onHoverEnd={handleHoverEnd}
      className={`spooky-card-wrapper ${compact ? 'spooky-card-wrapper--compact' : ''}`}
      transition={{ duration: 0.5 }}
    >
      {/* Animated glow effect */}
      <motion.div
        className="spooky-card__glow"
        initial={{ opacity: 0 }}
        animate={isHovered ? { 
          opacity: [0.3, 0.6, 0.3]
        } : { opacity: 0 }}
        transition={{
          duration: 2,
          repeat: isHovered ? Infinity : 0
        }}
      />
      
      <Card 
        variant="ghost" 
        hover={false} 
        glow={false}
        className={`spooky-content-card ${compact ? 'spooky-content-card--compact' : ''}`}
      >
      <motion.div 
        className="spooky-content-card__header"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
      >
        <motion.h3 
          className="spooky-content-card__title"
          whileHover={{ 
            textShadow: "0 0 8px rgba(139, 92, 246, 0.6)",
            transition: { duration: 0.3 }
          }}
        >
          {variant.haunted_title}
        </motion.h3>
        <motion.div 
          className="spooky-content-card__meta"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.3 }}
        >
          <span className="spooky-content-card__source">
            {variant.original_item.source}
          </span>
          <span className="spooky-content-card__date">
            {formatDate(variant.original_item.published)}
          </span>
        </motion.div>
      </motion.div>

      <motion.div 
        className="spooky-content-card__body"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        <motion.p 
          className="spooky-content-card__summary"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          {variant.haunted_summary}
        </motion.p>
        
        {!compact && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.4 }}
          >
            <SupernaturalReveal
              explanation={variant.supernatural_explanation}
              isExpanded={isExpanded}
              onToggle={handleExpansionToggle}
            />
          </motion.div>
        )}

        {showThemes && Array.isArray(variant.horror_themes) && variant.horror_themes.length > 0 && (
          <motion.div 
            className="spooky-content-card__themes"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.4 }}
          >
            {(Array.isArray(variant.horror_themes) 
              ? variant.horror_themes 
              : (typeof variant.horror_themes === 'string' ? [variant.horror_themes] : [])
            ).map((theme, index) => (
              <motion.span 
                key={index} 
                className="spooky-content-card__theme-tag"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                whileHover={{ scale: 1.1 }}
                transition={{ 
                  delay: index * 0.1, 
                  duration: 0.3,
                  type: "spring",
                  stiffness: 400
                }}
              >
                {theme}
              </motion.span>
            ))}
          </motion.div>
        )}

        {!compact && onContinueStory && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.4 }}
          >
            <StoryContinuation
              variant={variant}
              onContinue={onContinueStory}
            />
          </motion.div>
        )}
      </motion.div>

      {/* Audio Player Section */}
      {!compact && (
        <motion.div
          className="spooky-content-card__audio-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.85, duration: 0.4 }}
        >
          <motion.button
            className="spooky-content-card__audio-toggle"
            onClick={handleAudioPlayerToggle}
            type="button"
            whileHover={{ 
              scale: 1.05,
              transition: { duration: 0.2 }
            }}
            whileTap={{ 
              scale: 0.95,
              transition: { duration: 0.1 }
            }}
            aria-expanded={showAudioPlayer}
            aria-label={showAudioPlayer ? "Hide audio player" : "Show audio player"}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            {showAudioPlayer ? 'Hide Narration' : 'Listen to Narration'}
          </motion.button>

          {showAudioPlayer && (
            <motion.div
              className="spooky-content-card__audio-player-container"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <AudioPlayer
                variantId={variant.variant_id || `${variant.original_item.source}-${variant.generation_timestamp}`}
                voiceStyle={getDefaultVoiceStyle()}
                intensity={getIntensityLevel()}
                content={variant.haunted_summary}
                autoPlay={false}
                className="spooky-content-card__audio-player"
              />
            </motion.div>
          )}
        </motion.div>
      )}

      <motion.div 
        className="spooky-content-card__footer"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.4 }}
      >
        <div className="spooky-content-card__indicators">
          {variant.personalization_applied && (
            <motion.span 
              className="spooky-content-card__personalized"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ 
                delay: 0.9, 
                duration: 0.5, 
                type: "spring",
                stiffness: 200 
              }}
              whileHover={{ 
                scale: 1.1,
                rotate: [0, -10, 10, 0],
                transition: { duration: 0.5 }
              }}
            >
              👻 Personalized
            </motion.span>
          )}
          <motion.span 
            className="spooky-content-card__generated"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.3 }}
          >
            Generated {formatDate(variant.generation_timestamp)}
          </motion.span>
        </div>
        
        <motion.button 
          className="spooky-content-card__read-more"
          onClick={handleReadMore}
          type="button"
          whileHover={{ 
            scale: 1.05,
            boxShadow: "0 0 20px rgba(139, 92, 246, 0.4)",
            transition: { duration: 0.2 }
          }}
          whileTap={{ 
            scale: 0.95,
            transition: { duration: 0.1 }
          }}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.1, duration: 0.3 }}
        >
          Read Original 🔗
        </motion.button>
      </motion.div>
    </Card>
    </motion.div>
  );
};

export default SpookyCard;