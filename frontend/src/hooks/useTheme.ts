import { useContext } from 'react';
import { ThemeContext, type ThemeContextType } from '../components/DarkThemeProvider/DarkThemeProvider';

const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a DarkThemeProvider');
  }
  return context;
};

export default useTheme;