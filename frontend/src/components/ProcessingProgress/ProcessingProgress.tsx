import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SpookySpinner from '../SpookySpinner';
import './ProcessingProgress.css';

export interface ProcessingProgressProps {
  isProcessing: boolean;
  processingId?: string | null;
  className?: string;
}

const processingSteps = [
  { icon: '🕷️', message: 'Summoning dark forces...' },
  { icon: '🌙', message: 'Weaving supernatural threads...' },
  { icon: '👻', message: 'Channeling ghostly energies...' },
  { icon: '🔮', message: 'Transforming reality into nightmare...' },
  { icon: '⚡', message: 'Infusing horror into every word...' },
  { icon: '🎭', message: 'Crafting spine-chilling narratives...' }
];

const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  isProcessing,
  processingId,
  className = ''
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isProcessing) {
      setCurrentStep(0);
      setProgress(0);
      return;
    }

    // Cycle through processing steps
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % processingSteps.length);
    }, 2500);

    // Simulate progress (since we don't have real progress from backend)
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) return prev; // Cap at 95% until complete
        return prev + Math.random() * 5;
      });
    }, 300);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, [isProcessing]);

  if (!isProcessing) return null;

  const step = processingSteps[currentStep];

  return (
    <AnimatePresence>
      <motion.div
        className={`processing-progress ${className}`}
        initial={{ opacity: 0, y: -20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.95 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <div className="processing-progress__content">
          {/* Animated Spinner */}
          <div className="processing-progress__spinner">
            <SpookySpinner variant="spiral" size="medium" />
          </div>

          {/* Processing Steps */}
          <div className="processing-progress__steps">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                className="processing-progress__step"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <span className="processing-progress__icon">{step.icon}</span>
                <span className="processing-progress__message">{step.message}</span>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Progress Bar */}
          <div className="processing-progress__bar-container">
            <motion.div
              className="processing-progress__bar"
              initial={{ width: '0%' }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
            />
            <motion.div
              className="processing-progress__bar-glow"
              animate={{
                opacity: [0.5, 1, 0.5],
                scale: [1, 1.02, 1]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            />
          </div>

          {/* Processing ID */}
          {processingId && (
            <motion.div
              className="processing-progress__id"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <span className="processing-progress__id-label">Processing ID:</span>
              <code className="processing-progress__id-value">{processingId}</code>
            </motion.div>
          )}

          {/* Floating Particles */}
          <div className="processing-progress__particles">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="processing-progress__particle"
                animate={{
                  y: [-20, -60],
                  x: [0, (Math.random() - 0.5) * 40],
                  opacity: [0, 1, 0],
                  scale: [0, 1, 0]
                }}
                transition={{
                  duration: 2 + Math.random() * 2,
                  repeat: Infinity,
                  delay: i * 0.3,
                  ease: 'easeOut'
                }}
                style={{
                  left: `${15 + i * 15}%`
                }}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ProcessingProgress;
