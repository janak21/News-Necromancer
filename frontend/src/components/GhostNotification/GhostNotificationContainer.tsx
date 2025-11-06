import React from 'react';
import { AnimatePresence } from 'framer-motion';
import GhostNotification from './GhostNotification';
import { useGhostNotificationContext } from '../../contexts/GhostNotificationContext';
import './GhostNotificationContainer.css';

const GhostNotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useGhostNotificationContext();

  return (
    <div className="ghost-notification-container">
      <AnimatePresence mode="popLayout">
        {notifications.map((notification) => (
          <GhostNotification
            key={notification.id}
            message={notification.message}
            type={notification.type}
            isVisible={true}
            duration={notification.duration}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

export default GhostNotificationContainer;