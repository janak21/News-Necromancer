import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DarkThemeProvider from './components/DarkThemeProvider/DarkThemeProvider';
import { GhostNotificationProvider } from './contexts/GhostNotificationContext';
import { ParticleBackground } from './components';
import GhostNotificationContainer from './components/GhostNotification/GhostNotificationContainer';
import { HomePage, FeedsPage, PreferencesPage } from './pages';
import Navigation from './components/Navigation/Navigation';
import { useSoundEffects } from './hooks';
import './App.css';

const AMBIENT_PREFERENCE_KEY = 'spooky_ambient_enabled';

function AppContent() {
  const { playSound, isEnabled } = useSoundEffects();
  const [ambientStarted, setAmbientStarted] = useState(false);

  useEffect(() => {
    // Check if ambient should be enabled by default
    const savedPreference = localStorage.getItem(AMBIENT_PREFERENCE_KEY);
    const shouldEnableAmbient = savedPreference === null ? true : savedPreference === 'true';
    
    if (shouldEnableAmbient) {
      localStorage.setItem(AMBIENT_PREFERENCE_KEY, 'true');
    }

    // Try to start ambient sound after first user interaction
    const startAmbient = () => {
      if (!ambientStarted && isEnabled && shouldEnableAmbient) {
        // Only play ambient sound, not any other sounds
        playSound('ambient');
        setAmbientStarted(true);
        // Remove listeners after first interaction
        document.removeEventListener('click', startAmbient as EventListener);
        document.removeEventListener('keydown', startAmbient as EventListener);
        document.removeEventListener('touchstart', startAmbient as EventListener);
      }
    };

    // Listen for user interactions to start ambient sound
    // Use capture phase to ensure we get the event first
    document.addEventListener('click', startAmbient as EventListener, { once: true, capture: true });
    document.addEventListener('keydown', startAmbient as EventListener, { once: true, capture: true });
    document.addEventListener('touchstart', startAmbient as EventListener, { once: true, capture: true });

    return () => {
      document.removeEventListener('click', startAmbient as EventListener, { capture: true } as any);
      document.removeEventListener('keydown', startAmbient as EventListener, { capture: true } as any);
      document.removeEventListener('touchstart', startAmbient as EventListener, { capture: true } as any);
    };
  }, [playSound, isEnabled, ambientStarted]);

  return (
    <div className="app">
      {/* Atmospheric particle background */}
      <ParticleBackground particleCount={40} />
      
      <Navigation />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/feeds" element={<FeedsPage />} />
          <Route path="/preferences" element={<PreferencesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      
      {/* Ghost notification system */}
      <GhostNotificationContainer />
    </div>
  );
}

function App() {
  return (
    <DarkThemeProvider>
      <GhostNotificationProvider>
        <Router>
          <AppContent />
        </Router>
      </GhostNotificationProvider>
    </DarkThemeProvider>
  );
}

export default App;
