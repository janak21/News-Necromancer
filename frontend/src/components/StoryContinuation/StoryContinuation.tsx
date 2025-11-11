import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { SpookyVariant, StoryContinuation as StoryContinuationType } from '../../types';
import { useSoundEffects } from '../../hooks';
import './StoryContinuation.css';

export interface StoryContinuationProps {
  variant: SpookyVariant;
  onContinue: (variantId: string) => Promise<StoryContinuationType>;
}

const StoryContinuation: React.FC<StoryContinuationProps> = ({
  variant,
  onContinue
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [continuation, setContinuation] = useState<StoryContinuationType | null>(
    variant.continuation || null
  );
  const [error, setError] = useState<string | null>(null);
  const { playSound } = useSoundEffects();

  const handleContinue = async () => {
    if (!variant.variant_id) {
      setError('Cannot continue story: variant ID is missing');
      return;
    }

    if (isLoading || continuation) return;

    setIsLoading(true);
    setError(null);
    playSound('whisper');

    try {
      const result = await onContinue(variant.variant_id);
      setContinuation(result);
      playSound('creak');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to continue the nightmare';
      setError(errorMessage);
      console.error('Story continuation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="story-continuation">
      <AnimatePresence mode="wait">
        {!continuation && !isLoading && (
          <>
            <motion.button
              key="continue-button"
              className="story-continuation__button"
              onClick={handleContinue}
              disabled={isLoading || !variant.variant_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              whileHover={{ 
                scale: !variant.variant_id ? 1 : 1.05,
                boxShadow: !variant.variant_id ? "none" : "0 0 20px rgba(220, 38, 38, 0.4)",
                transition: { duration: 0.2 }
              }}
              whileTap={{ 
                scale: !variant.variant_id ? 1 : 0.95,
                transition: { duration: 0.1 }
              }}
              transition={{ duration: 0.3 }}
            >
              <motion.span
                animate={!variant.variant_id ? {} : {
                  textShadow: [
                    "0 0 4px rgba(220, 38, 38, 0.3)",
                    "0 0 8px rgba(220, 38, 38, 0.6)",
                    "0 0 4px rgba(220, 38, 38, 0.3)"
                  ]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                {!variant.variant_id ? '🔒 Continuation Unavailable' : '🌙 Continue the Nightmare...'}
              </motion.span>
            </motion.button>
            {!variant.variant_id && (
              <motion.p
                key="no-variant-id"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                  textAlign: 'center',
                  marginTop: '0.5rem',
                  fontStyle: 'italic'
                }}
              >
                This variant doesn't support continuation
              </motion.p>
            )}
          </>
        )}

        {isLoading && (
          <motion.div
            key="loading"
            className="story-continuation__loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="story-continuation__spinner"
              animate={{ rotate: 360 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear"
              }}
            >
              👻
            </motion.div>
            <motion.p
              animate={{
                opacity: [0.5, 1, 0.5]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              Summoning darker forces...
            </motion.p>
          </motion.div>
        )}

        {continuation && (
          <motion.div
            key="continuation-content"
            className="story-continuation__content"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            <motion.div
              className="story-continuation__header"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              <span className="story-continuation__icon">📖</span>
              <h4 className="story-continuation__title">The Nightmare Continues...</h4>
            </motion.div>

            <motion.div
              className="story-continuation__narrative"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              {continuation.continued_narrative.split('\n\n').map((paragraph, index) => (
                <motion.p
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ 
                    delay: 0.5 + (index * 0.1), 
                    duration: 0.5 
                  }}
                >
                  {paragraph}
                </motion.p>
              ))}
            </motion.div>

            {continuation.maintains_intensity && (
              <motion.div
                className="story-continuation__badge"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ 
                  delay: 0.8, 
                  duration: 0.4,
                  type: "spring",
                  stiffness: 200
                }}
              >
                ⚡ Intensity Maintained
              </motion.div>
            )}
          </motion.div>
        )}

        {error && (
          <motion.div
            key="error"
            className="story-continuation__error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <span className="story-continuation__error-icon">⚠️</span>
            <p>{error}</p>
            <button
              className="story-continuation__retry"
              onClick={handleContinue}
            >
              Try Again
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StoryContinuation;
