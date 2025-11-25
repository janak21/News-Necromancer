import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { SpookyVariant, StoryContinuation as StoryContinuationType } from '../../types';
import { useSoundEffects } from '../../hooks';
import SpookySpinner from '../SpookySpinner/SpookySpinner';
import './StoryContinuation.css';

export interface StoryContinuationProps {
  variant: SpookyVariant;
  onContinue: (variantId: string) => Promise<StoryContinuationType>;
}

const MAX_RETRY_ATTEMPTS = 3;
const BASE_RETRY_DELAY = 1000; // 1 second

const StoryContinuation: React.FC<StoryContinuationProps> = ({
  variant,
  onContinue
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [continuation, setContinuation] = useState<StoryContinuationType | null>(
    variant.continuation || null
  );
  const [error, setError] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false); // Prevent duplicate requests
  const [retryCount, setRetryCount] = useState(0);
  const [retryDelay, setRetryDelay] = useState(0);
  const { playSound } = useSoundEffects();

  // Format narrative text with proper spacing
  const formatNarrativeText = (text: string): string => {
    if (!text) return '';
    
    let formatted = text;
    
    // Check if text has very few spaces (likely a parsing issue)
    const spaceCount = (formatted.match(/ /g) || []).length;
    const wordEstimate = formatted.length / 5; // Average word length
    
    if (spaceCount < wordEstimate * 0.3 && formatted.length > 50) {
      // Text has too few spaces - insert spaces before capital letters
      formatted = formatted
        // Add space before capital letters that follow lowercase letters
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        // Add space before capital letters that follow numbers
        .replace(/([0-9])([A-Z])/g, '$1 $2')
        // Add space after periods if missing
        .replace(/\.([A-Z])/g, '. $1')
        // Clean up any double spaces
        .replace(/\s+/g, ' ')
        .trim();
    }
    
    return formatted;
  };

  // Check if continuation is available
  const canContinue = () => {
    if (!variant.variant_id) return false;
    if (continuation) return false;
    if (variant.haunted_summary.length < 50) return false;
    return true;
  };

  // Get reason why continuation is unavailable
  const getUnavailableReason = () => {
    if (!variant.variant_id) return "This variant doesn't support continuation";
    if (continuation) return "Story already continued";
    if (variant.haunted_summary.length < 50) return "Original story is too short to continue";
    return null;
  };

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const shouldRetry = (error: Error): boolean => {
    // Don't retry for these errors
    if (error.message.includes('Rate limit')) return false;
    if (error.message.includes('too short')) return false;
    if (error.message.includes('not found')) return false;
    
    // Retry for these errors
    if (error.message.includes('timeout')) return true;
    if (error.message.includes('Network error')) return true;
    if (error.message.includes('Server error')) return true;
    if (error.message.includes('Invalid')) return true;
    
    return true; // Default to retry
  };

  const handleContinue = async (isRetry: boolean = false) => {
    // Prevent multiple simultaneous requests
    if (isProcessing || isLoading) {
      return;
    }

    if (!canContinue()) {
      const reason = getUnavailableReason();
      if (reason) {
        setError(reason);
      }
      return;
    }

    // Reset retry count if this is a fresh attempt (not a retry)
    if (!isRetry) {
      setRetryCount(0);
    }

    setIsProcessing(true);
    setIsLoading(true);
    setError(null);
    setRetryDelay(0);
    playSound('whisper');

    let lastError: Error | null = null;
    let currentAttempt = isRetry ? retryCount : 0;

    // Retry loop with exponential backoff
    while (currentAttempt <= MAX_RETRY_ATTEMPTS) {
      try {
        // Add delay for retries (exponential backoff)
        if (currentAttempt > 0) {
          const delay = BASE_RETRY_DELAY * Math.pow(2, currentAttempt - 1);
          setRetryDelay(delay);
          await sleep(delay);
          setRetryDelay(0);
        }

        const result = await onContinue(variant.variant_id!);
        
        // Validate the result
        if (!result || !result.continued_narrative) {
          throw new Error('Received invalid continuation data');
        }

        // Success! Reset retry count and set continuation
        setRetryCount(0);
        setContinuation(result);
        playSound('creak');
        setIsLoading(false);
        setIsProcessing(false);
        return;

      } catch (err) {
        lastError = err instanceof Error ? err : new Error('Unknown error');
        
        // Check if we should retry
        if (currentAttempt < MAX_RETRY_ATTEMPTS && shouldRetry(lastError)) {
          currentAttempt++;
          setRetryCount(currentAttempt);
          console.log(`Retry attempt ${currentAttempt}/${MAX_RETRY_ATTEMPTS}`);
          continue;
        }
        
        // Max retries reached or non-retryable error
        break;
      }
    }

    // Handle final error after all retries
    if (lastError) {
      let errorMessage = 'Failed to continue the nightmare';
      
      if (lastError.message.includes('Rate limit')) {
        const match = lastError.message.match(/(\d+)\s+seconds?/);
        const waitTime = match ? match[1] : '60';
        errorMessage = `⏱️ Too many requests. Please wait ${waitTime} seconds before trying again.`;
      } else if (lastError.message.includes('timeout') || lastError.message.includes('timed out')) {
        errorMessage = `⏳ Request timed out after ${currentAttempt} attempt${currentAttempt > 1 ? 's' : ''}. The nightmare may be too dark to continue.`;
      } else if (lastError.message.includes('Network error') || lastError.message.includes('fetch')) {
        errorMessage = `🌐 Network error after ${currentAttempt} attempt${currentAttempt > 1 ? 's' : ''}. Please check your connection.`;
      } else if (lastError.message.includes('too short')) {
        errorMessage = '📏 The original story is too short to continue meaningfully.';
      } else if (lastError.message.includes('empty') || lastError.message.includes('Invalid')) {
        errorMessage = `❌ Received invalid response after ${currentAttempt} attempt${currentAttempt > 1 ? 's' : ''}.`;
      } else if (lastError.message.includes('Server error')) {
        errorMessage = `🔧 Server error after ${currentAttempt} attempt${currentAttempt > 1 ? 's' : ''}. Please try again later.`;
      } else if (lastError.message.includes('not found')) {
        errorMessage = '🔍 Story variant not found. It may have been deleted.';
      }
      
      setError(errorMessage);
      console.error('Story continuation error:', lastError);
    }

    setIsLoading(false);
    setIsProcessing(false);
  };

  return (
    <div className="story-continuation">
      <AnimatePresence mode="wait">
        {!continuation && !isLoading && (
          <>
            <div className="story-continuation__controls">
              <motion.button
                key="continue-button"
                className="story-continuation__button"
                onClick={() => handleContinue(false)}
                disabled={!canContinue()}
                aria-label="Generate AI continuation of this horror story"
                aria-describedby="continuation-tooltip"
                aria-busy={isLoading}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                whileHover={{ 
                  scale: canContinue() ? 1.05 : 1,
                  boxShadow: canContinue() ? "0 0 20px rgba(220, 38, 38, 0.4)" : "none",
                  transition: { duration: 0.2 }
                }}
                whileTap={{ 
                  scale: canContinue() ? 0.95 : 1,
                  transition: { duration: 0.1 }
                }}
                transition={{ duration: 0.3 }}
              >
                <motion.span
                  animate={canContinue() ? {
                    textShadow: [
                      "0 0 4px rgba(220, 38, 38, 0.3)",
                      "0 0 8px rgba(220, 38, 38, 0.6)",
                      "0 0 4px rgba(220, 38, 38, 0.3)"
                    ]
                  } : {}}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                >
                  {canContinue() ? '🌙 Continue the Nightmare...' : '🔒 Continuation Unavailable'}
                </motion.span>
              </motion.button>
              
              <motion.button
                className="story-continuation__help"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                onFocus={() => setShowTooltip(true)}
                onBlur={() => setShowTooltip(false)}
                aria-label="Learn about story continuation feature"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                ❓
              </motion.button>
            </div>

            <AnimatePresence>
              {showTooltip && (
                <motion.div
                  className="story-continuation__tooltip"
                  id="continuation-tooltip"
                  role="tooltip"
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                >
                  <p className="story-continuation__tooltip-title">
                    <strong>🌙 Continue the Nightmare</strong>
                  </p>
                  <p className="story-continuation__tooltip-description">
                    Uses AI to extend your horror story with 300-500 words of additional narrative 
                    that maintains the same themes, intensity, and supernatural elements.
                  </p>
                  {!canContinue() && (
                    <p className="story-continuation__tooltip-reason">
                      <em>⚠️ {getUnavailableReason()}</em>
                    </p>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {!canContinue() && (
              <motion.p
                key="unavailable-message"
                className="story-continuation__unavailable-message"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {getUnavailableReason()}
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
            <SpookySpinner 
              variant="skull" 
              size="medium" 
              message={
                retryCount > 0 
                  ? `Retry attempt ${retryCount}/${MAX_RETRY_ATTEMPTS}...` 
                  : retryDelay > 0
                  ? `Waiting ${Math.ceil(retryDelay / 1000)}s before retry...`
                  : "Summoning darker forces..."
              }
            />
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
              className="story-continuation__divider"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ delay: 0.1, duration: 0.5 }}
            >
              <span className="story-continuation__divider-text">✦ New Content Begins ✦</span>
            </motion.div>

            <motion.div
              className="story-continuation__header"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <span className="story-continuation__icon">📖</span>
              <p className="story-continuation__title" style={{ fontWeight: 'var(--font-weight-bold)', fontSize: '1.125rem', margin: 0 }}>The Nightmare Continues...</p>
            </motion.div>

            <motion.div
              className="story-continuation__narrative"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              {formatNarrativeText(continuation.continued_narrative)
                .split(/\n\n+/)
                .filter(p => p.trim().length > 0)
                .map((paragraph, index) => (
                  <motion.p
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ 
                      delay: 0.5 + (index * 0.1), 
                      duration: 0.5 
                    }}
                  >
                    {paragraph.trim()}
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
            role="alert"
            aria-live="polite"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <span className="story-continuation__error-icon">⚠️</span>
            <p className="story-continuation__error-message">{error}</p>
            {!error.includes('too short') && !error.includes('not found') && retryCount < MAX_RETRY_ATTEMPTS && (
              <button
                className="story-continuation__retry"
                onClick={() => handleContinue(true)}
                disabled={isProcessing || isLoading}
                aria-label="Retry story continuation"
              >
                {isProcessing ? 'Retrying...' : 'Try Again'}
              </button>
            )}
            {retryCount >= MAX_RETRY_ATTEMPTS && (
              <p className="story-continuation__max-retries">
                Maximum retry attempts reached. Please try again later.
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StoryContinuation;
