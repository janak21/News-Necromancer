import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './SupernaturalReveal.css';

export interface SupernaturalRevealProps {
  explanation: string;
  isExpanded?: boolean;
  onToggle?: (expanded: boolean) => void;
}

const SupernaturalReveal: React.FC<SupernaturalRevealProps> = ({
  explanation,
  isExpanded: controlledExpanded,
  onToggle
}) => {
  const [internalExpanded, setInternalExpanded] = useState(false);
  
  const isExpanded = controlledExpanded !== undefined ? controlledExpanded : internalExpanded;
  
  const handleToggle = () => {
    const newExpanded = !isExpanded;
    if (onToggle) {
      onToggle(newExpanded);
    } else {
      setInternalExpanded(newExpanded);
    }
  };

  // Split explanation into words for staggered animation
  // Handle edge case where text has no spaces by inserting spaces
  let processedExplanation = explanation || '';
  
  // Check if text has very few spaces (likely a parsing issue)
  const spaceCount = (processedExplanation.match(/ /g) || []).length;
  const wordEstimate = processedExplanation.length / 5; // Average word length
  
  if (spaceCount < wordEstimate * 0.3 && processedExplanation.length > 50) {
    // Text has too few spaces - insert spaces before capital letters
    // This handles cases like "ThegroupsformedonAmazonMusic..."
    processedExplanation = processedExplanation
      // Add space before capital letters that follow lowercase letters
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      // Add space before capital letters that follow numbers
      .replace(/([0-9])([A-Z])/g, '$1 $2')
      // Clean up any double spaces
      .replace(/\s+/g, ' ')
      .trim();
  }
  
  const words = processedExplanation.split(' ').filter(word => word.length > 0);

  return (
    <div className="supernatural-reveal">
      <motion.button
        className="supernatural-reveal__trigger"
        onClick={handleToggle}
        whileHover={{ 
          scale: 1.02,
          textShadow: "0 0 12px rgba(139, 92, 246, 0.8)"
        }}
        whileTap={{ scale: 0.98 }}
        type="button"
      >
        <motion.span
          animate={isExpanded ? { rotate: 90 } : { rotate: 0 }}
          transition={{ duration: 0.3 }}
          className="supernatural-reveal__icon"
        >
          ▶
        </motion.span>
        <span className="supernatural-reveal__title">
          Supernatural Explanation
        </span>
      </motion.button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="supernatural-reveal__container"
            initial={{ opacity: 0, height: 0 }}
            animate={{ 
              opacity: 1, 
              height: 'auto',
            }}
            exit={{ 
              opacity: 0, 
              height: 0,
            }}
            transition={{ 
              duration: 0.6,
              ease: 'easeOut'
            }}
          >
            <motion.div
              className="supernatural-reveal__glow"
              initial={{ opacity: 0 }}
              animate={{ 
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            />
            
            <motion.div 
              className="supernatural-reveal__content"
              initial={{ y: 20 }}
              animate={{ y: 0 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              <p className="supernatural-reveal__text">
                {words.map((word, index) => (
                  <motion.span
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      delay: 0.3 + (index * 0.03),
                      duration: 0.3
                    }}
                    className="supernatural-reveal__word"
                  >
                    {word}{' '}
                  </motion.span>
                ))}
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SupernaturalReveal;
