import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './SpookySpinner.css';

export interface SpookySpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'ghost' | 'skull' | 'spiral';
  className?: string;
}

const SpookySpinner: React.FC<SpookySpinnerProps> = ({
  message,
  size = 'medium',
  variant = 'ghost',
  className = ''
}) => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const sizeMap = {
    small: 40,
    medium: 60,
    large: 80
  };

  const spinnerSize = sizeMap[size];

  const renderSpinner = () => {
    // Reduced motion fallback - simple static or minimal animation
    if (prefersReducedMotion) {
      return (
        <div
          className={`spooky-spinner__${variant} spooky-spinner--reduced-motion`}
          style={{ width: spinnerSize, height: spinnerSize }}
        >
          {variant === 'ghost' && (
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M50 10 C30 10, 20 25, 20 45 C20 65, 20 80, 20 90 L30 85 L40 90 L50 85 L60 90 L70 85 L80 90 C80 80, 80 65, 80 45 C80 25, 70 10, 50 10 Z"
                fill="currentColor"
              />
              <circle cx="40" cy="45" r="5" fill="#0a0a0f" />
              <circle cx="60" cy="45" r="5" fill="#0a0a0f" />
              <path d="M40 60 Q50 65, 60 60" stroke="#0a0a0f" strokeWidth="3" strokeLinecap="round" fill="none" />
            </svg>
          )}
          {variant === 'skull' && (
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="50" cy="45" rx="30" ry="35" fill="currentColor" />
              <rect x="35" y="50" width="10" height="15" rx="2" fill="#0a0a0f" />
              <rect x="55" y="50" width="10" height="15" rx="2" fill="#0a0a0f" />
              <path d="M45 75 L48 80 L50 75 L52 80 L55 75" stroke="#0a0a0f" strokeWidth="2" fill="none" />
            </svg>
          )}
          {variant === 'spiral' && (
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="50" r="35" stroke="currentColor" strokeWidth="3" fill="none" opacity="0.8" />
              <circle cx="50" cy="50" r="25" stroke="currentColor" strokeWidth="3" fill="none" opacity="0.6" />
              <circle cx="50" cy="50" r="15" stroke="currentColor" strokeWidth="3" fill="none" opacity="0.4" />
            </svg>
          )}
        </div>
      );
    }

    switch (variant) {
      case 'ghost':
        return (
          <motion.div
            className="spooky-spinner__ghost"
            animate={{
              y: [0, -15, 0],
              opacity: [0.7, 1, 0.7]
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
            style={{ width: spinnerSize, height: spinnerSize }}
          >
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <motion.path
                d="M50 10 C30 10, 20 25, 20 45 C20 65, 20 80, 20 90 L30 85 L40 90 L50 85 L60 90 L70 85 L80 90 C80 80, 80 65, 80 45 C80 25, 70 10, 50 10 Z"
                fill="currentColor"
                animate={{
                  scale: [1, 1.08, 1]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              />
              <motion.circle
                cx="40"
                cy="45"
                r="5"
                fill="#0a0a0f"
                animate={{
                  scale: [1, 1.2, 1]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: 0.2
                }}
              />
              <motion.circle
                cx="60"
                cy="45"
                r="5"
                fill="#0a0a0f"
                animate={{
                  scale: [1, 1.2, 1]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: 0.2
                }}
              />
              <path
                d="M40 60 Q50 65, 60 60"
                stroke="#0a0a0f"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
              />
            </svg>
          </motion.div>
        );

      case 'skull':
        return (
          <motion.div
            className="spooky-spinner__skull"
            animate={{
              rotate: [0, 360],
              scale: [1, 1.1, 1]
            }}
            transition={{
              rotate: {
                duration: 3,
                repeat: Infinity,
                ease: 'linear'
              },
              scale: {
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }
            }}
            style={{ width: spinnerSize, height: spinnerSize }}
          >
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <motion.ellipse
                cx="50"
                cy="45"
                rx="30"
                ry="35"
                fill="currentColor"
                animate={{
                  opacity: [0.9, 1, 0.9]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              />
              <motion.rect
                x="35"
                y="50"
                width="10"
                height="15"
                rx="2"
                fill="#0a0a0f"
                animate={{
                  height: [15, 18, 15]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: 0.3
                }}
              />
              <motion.rect
                x="55"
                y="50"
                width="10"
                height="15"
                rx="2"
                fill="#0a0a0f"
                animate={{
                  height: [15, 18, 15]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: 0.3
                }}
              />
              <motion.path
                d="M45 75 L48 80 L50 75 L52 80 L55 75"
                stroke="#0a0a0f"
                strokeWidth="2"
                fill="none"
                animate={{
                  strokeWidth: [2, 3, 2]
                }}
                transition={{
                  duration: 1.8,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              />
            </svg>
          </motion.div>
        );

      case 'spiral':
        return (
          <motion.div
            className="spooky-spinner__spiral"
            style={{ width: spinnerSize, height: spinnerSize }}
          >
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="spooky-spinner__spiral-ring"
                animate={{
                  rotate: [0, 360],
                  scale: [1, 1.15, 1],
                  opacity: [0.4 + i * 0.2, 0.8 + i * 0.1, 0.4 + i * 0.2]
                }}
                transition={{
                  rotate: {
                    duration: 2.5 - i * 0.3,
                    repeat: Infinity,
                    ease: 'linear'
                  },
                  scale: {
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: i * 0.15
                  },
                  opacity: {
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                    delay: i * 0.15
                  }
                }}
                style={{
                  width: spinnerSize - i * 15,
                  height: spinnerSize - i * 15
                }}
              />
            ))}
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div 
      className={`spooky-spinner spooky-spinner--${size} spooky-spinner--${variant} ${className}`}
      role="status"
      aria-live="polite"
      aria-label={message || 'Loading'}
    >
      <div className="spooky-spinner__animation">
        {renderSpinner()}
      </div>
      
      {message && (
        <motion.p
          className="spooky-spinner__message"
          initial={{ opacity: 0 }}
          animate={prefersReducedMotion ? { opacity: 1 } : { opacity: [0.6, 1, 0.6] }}
          transition={{
            duration: prefersReducedMotion ? 0 : 2.5,
            repeat: prefersReducedMotion ? 0 : Infinity,
            ease: 'easeInOut'
          }}
        >
          {message}
        </motion.p>
      )}
    </div>
  );
};

export default SpookySpinner;
