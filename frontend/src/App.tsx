import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DarkThemeProvider from './components/DarkThemeProvider/DarkThemeProvider';
import { GhostNotificationProvider } from './contexts/GhostNotificationContext';
import { ParticleBackground } from './components';
import GhostNotificationContainer from './components/GhostNotification/GhostNotificationContainer';
import { HomePage, FeedsPage, PreferencesPage } from './pages';
import Navigation from './components/Navigation/Navigation';
import './App.css';

function App() {
  return (
    <DarkThemeProvider>
      <GhostNotificationProvider>
        <Router>
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
        </Router>
      </GhostNotificationProvider>
    </DarkThemeProvider>
  );
}

export default App;
