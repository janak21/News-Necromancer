import React, { createContext, useEffect } from 'react';
import type { ReactNode } from 'react';
import './DarkThemeProvider.css';

interface ThemeContextType {
  theme: 'dark';
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    accent: string;
    danger: string;
    success: string;
    warning: string;
  };
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface DarkThemeProviderProps {
  children: ReactNode;
}

const DarkThemeProvider: React.FC<DarkThemeProviderProps> = ({ children }) => {
  const value: ThemeContextType = {
    theme: 'dark',
    colors: {
      primary: 'var(--color-primary)',
      secondary: 'var(--color-secondary)',
      background: 'var(--color-background)',
      surface: 'var(--color-surface)',
      text: 'var(--color-text)',
      textSecondary: 'var(--color-text-secondary)',
      accent: 'var(--color-accent)',
      danger: 'var(--color-danger)',
      success: 'var(--color-success)',
      warning: 'var(--color-warning)',
    },
  };

  useEffect(() => {
    // Apply dark theme class to document root
    document.documentElement.classList.add('dark-theme');
    
    return () => {
      document.documentElement.classList.remove('dark-theme');
    };
  }, []);

  return (
    <ThemeContext.Provider value={value}>
      <div className="spooky-theme-root">
        {children}
      </div>
    </ThemeContext.Provider>
  );
};

export default DarkThemeProvider;
export { ThemeContext };
export type { ThemeContextType };