import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../Card/Card';
import type { SpookyVariant } from '../../types';
import './SpookyCard.css';

export interface SpookyCardProps {
  variant: SpookyVariant;
  onReadMore?: (variant: SpookyVariant) => void;
  showThemes?: boolean;
  compact?: boolean;
}

const SpookyCard: React.FC<SpookyCardProps> = ({
  variant,
  onReadMore,
  showThemes = true,
  compact = false
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
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



  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      whileHover={{ y: -8, scale: 1.02 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
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
            className="spooky-content-card__explanation"
            initial={{ opacity: 0, height: 0 }}
            animate={{ 
              opacity: isExpanded ? 1 : 0.7, 
              height: "auto" 
            }}
            transition={{ delay: 0.6, duration: 0.4 }}
          >
            <motion.h4 
              className="spooky-content-card__explanation-title"
              whileHover={{ 
                color: "var(--color-primary)",
                transition: { duration: 0.2 }
              }}
              onClick={() => setIsExpanded(!isExpanded)}
              style={{ cursor: 'pointer' }}
            >
              Supernatural Explanation {isExpanded ? '▼' : '▶'}
            </motion.h4>
            <AnimatePresence>
              {isExpanded && (
                <motion.p 
                  className="spooky-content-card__explanation-text"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {variant.supernatural_explanation}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {showThemes && variant.horror_themes.length > 0 && (
          <motion.div 
            className="spooky-content-card__themes"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.4 }}
          >
            {variant.horror_themes.map((theme, index) => (
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
      </motion.div>

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