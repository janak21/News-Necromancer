import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './GhostNotification.css';

interface GhostNotificationProps {
  message: string;
  isVisible: boolean;
  onClose?: () => void;
  type?: 'info' | 'success' | 'warning' | 'error';
  duration?: number;
}

const GhostNotification: React.FC<GhostNotificationProps> = ({
  message,
  isVisible,
  onClose,
  type = 'info',
  duration = 4000
}) => {
  const [shouldShow, setShouldShow] = useState(isVisible);

  useEffect(() => {
    setShouldShow(isVisible);
    
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        setShouldShow(false);
        onClose?.();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);



  return (
    <AnimatePresence>
      {shouldShow && (
        <motion.div
          className={`ghost-notification ghost-notification--${type}`}
          initial={{ opacity: 0, y: -50, scale: 0.8, rotate: -10 }}
          animate={{ 
            opacity: 1, 
            y: [0, -8, 0], 
            scale: 1, 
            rotate: [-2, 2, -2] 
          }}
          exit={{ opacity: 0, y: -30, scale: 0.9, rotate: 5 }}
          transition={{ 
            duration: 0.6,
            y: { duration: 3, repeat: Infinity },
            rotate: { duration: 3, repeat: Infinity }
          }}
          onClick={() => {
            setShouldShow(false);
            onClose?.();
          }}
        >
          {/* Glow effect background */}
          <motion.div
            className="ghost-notification__glow"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ 
              opacity: [0.3, 0.7, 0.3],
              scale: [0.8, 1.2, 0.8]
            }}
            transition={{
              duration: 2,
              repeat: Infinity
            }}
          />
          
          {/* Ghost body */}
          <div className="ghost-notification__body">
            {/* Ghost face */}
            <div className="ghost-notification__face">
              <div className="ghost-notification__eyes">
                <motion.div 
                  className="ghost-notification__eye"
                  animate={{
                    scaleY: [1, 0.1, 1],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    repeatDelay: 2
                  }}
                />
                <motion.div 
                  className="ghost-notification__eye"
                  animate={{
                    scaleY: [1, 0.1, 1],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    repeatDelay: 2,
                    delay: 0.1
                  }}
                />
              </div>
              <div className="ghost-notification__mouth" />
            </div>
            
            {/* Message content */}
            <div className="ghost-notification__content">
              <p className="ghost-notification__message">{message}</p>
            </div>
          </div>
          
          {/* Floating particles */}
          <div className="ghost-notification__particles">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="ghost-notification__particle"
                animate={{
                  y: [0, -20, 0],
                  x: [0, Math.sin(i) * 10, 0],
                  opacity: [0.3, 0.8, 0.3],
                }}
                transition={{
                  duration: 2 + i * 0.3,
                  repeat: Infinity,
                  delay: i * 0.2,
                  ease: "easeInOut"
                }}
              />
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default GhostNotification;