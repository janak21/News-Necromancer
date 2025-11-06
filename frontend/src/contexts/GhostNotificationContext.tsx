import React, { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { useGhostNotifications } from '../hooks/useGhostNotifications';
import type { GhostNotification } from '../hooks/useGhostNotifications';

interface GhostNotificationContextType {
  notifications: GhostNotification[];
  addNotification: (message: string, type?: GhostNotification['type'], duration?: number) => string;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  showSuccess: (message: string, duration?: number) => string;
  showError: (message: string, duration?: number) => string;
  showWarning: (message: string, duration?: number) => string;
  showInfo: (message: string, duration?: number) => string;
}

const GhostNotificationContext = createContext<GhostNotificationContextType | undefined>(undefined);

interface GhostNotificationProviderProps {
  children: ReactNode;
}

export const GhostNotificationProvider: React.FC<GhostNotificationProviderProps> = ({ children }) => {
  const ghostNotifications = useGhostNotifications();

  return (
    <GhostNotificationContext.Provider value={ghostNotifications}>
      {children}
    </GhostNotificationContext.Provider>
  );
};

export const useGhostNotificationContext = () => {
  const context = useContext(GhostNotificationContext);
  if (context === undefined) {
    throw new Error('useGhostNotificationContext must be used within a GhostNotificationProvider');
  }
  return context;
};