import React from 'react';
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
  const sizeMap = {
    small: 40,
    medium: 60,
    large: 80
  };

  const spinnerSize = sizeMap[size];

  const renderSpinner = () => {
    switch (variant) {
      case 'ghost':
        return (
          <motion.div
            className="spooky-spinner__ghost"
            animate={{
              y: [0, -10, 0],
              opacity: [0.6, 1, 0.6]
            }}
            transition={{
              duration: 2,
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
                  scale: [1, 1.05, 1]
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              />
              <circle cx="40" cy="45" r="5" fill="#1f2937" />
              <circle cx="60" cy="45" r="5" fill="#1f2937" />
              <motion.path
                d="M40 60 Q50 65, 60 60"
                stroke="#1f2937"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
                animate={{
                  d: [
                    'M40 60 Q50 65, 60 60',
                    'M40 60 Q50 55, 60 60',
                    'M40 60 Q50 65, 60 60'
                  ]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              />
            </svg>
          </motion.div>
        );

      case 'skull':
        return (
          <motion.div
            className="spooky-spinner__skull"
            animate={{
              rotate: [0, 360]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'linear'
            }}
            style={{ width: spinnerSize, height: spinnerSize }}
          >
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="50" cy="45" rx="30" ry="35" fill="currentColor" />
              <rect x="35" y="50" width="10" height="15" rx="2" fill="#1f2937" />
              <rect x="55" y="50" width="10" height="15" rx="2" fill="#1f2937" />
              <path d="M45 75 L48 80 L50 75 L52 80 L55 75" stroke="#1f2937" strokeWidth="2" fill="none" />
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
                  scale: [1, 1.2, 1]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'linear',
                  delay: i * 0.2
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
    <div className={`spooky-spinner spooky-spinner--${size} ${className}`}>
      <div className="spooky-spinner__animation">
        {renderSpinner()}
      </div>
      
      {message && (
        <motion.p
          className="spooky-spinner__message"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{
            duration: 2,
            repeat: Infinity,
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
