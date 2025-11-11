import React from 'react';
import { useSoundEffects } from '../hooks';

/**
 * Temporary debugging component to test sound system
 * Add this to your app to test sounds manually
 * 
 * Usage: Import and add <SoundDebugger /> to your App.tsx
 */
export const SoundDebugger: React.FC = () => {
  const { playSound, stopSound, isEnabled, volume, toggleSound, setVolume } = useSoundEffects();

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'rgba(0, 0, 0, 0.9)',
      border: '2px solid #8b5cf6',
      borderRadius: '8px',
      padding: '16px',
      color: 'white',
      zIndex: 9999,
      minWidth: '250px',
      fontFamily: 'monospace',
      fontSize: '12px'
    }}>
      <h3 style={{ margin: '0 0 12px 0', color: '#8b5cf6' }}>🔊 Sound Debugger</h3>
      
      <div style={{ marginBottom: '12px' }}>
        <strong>Status:</strong> {isEnabled ? '✅ Enabled' : '❌ Disabled'}
        <br />
        <strong>Volume:</strong> {Math.round(volume * 100)}%
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <button
          onClick={toggleSound}
          style={{
            padding: '8px',
            background: isEnabled ? '#ef4444' : '#10b981',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {isEnabled ? '🔇 Disable' : '🔊 Enable'}
        </button>

        <button
          onClick={() => playSound('whisper')}
          disabled={!isEnabled}
          style={{
            padding: '8px',
            background: '#8b5cf6',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: isEnabled ? 'pointer' : 'not-allowed',
            opacity: isEnabled ? 1 : 0.5
          }}
        >
          👻 Play Whisper
        </button>

        <button
          onClick={() => playSound('creak')}
          disabled={!isEnabled}
          style={{
            padding: '8px',
            background: '#8b5cf6',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: isEnabled ? 'pointer' : 'not-allowed',
            opacity: isEnabled ? 1 : 0.5
          }}
        >
          🚪 Play Creak
        </button>

        <button
          onClick={() => playSound('ambient')}
          disabled={!isEnabled}
          style={{
            padding: '8px',
            background: '#8b5cf6',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: isEnabled ? 'pointer' : 'not-allowed',
            opacity: isEnabled ? 1 : 0.5
          }}
        >
          🎵 Play Ambient
        </button>

        <button
          onClick={() => stopSound('ambient')}
          disabled={!isEnabled}
          style={{
            padding: '8px',
            background: '#ef4444',
            border: 'none',
            borderRadius: '4px',
            color: 'white',
            cursor: isEnabled ? 'pointer' : 'not-allowed',
            opacity: isEnabled ? 1 : 0.5
          }}
        >
          ⏹️ Stop Ambient
        </button>

        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={(e) => setVolume(parseFloat(e.target.value))}
          disabled={!isEnabled}
          style={{
            width: '100%',
            cursor: isEnabled ? 'pointer' : 'not-allowed',
            opacity: isEnabled ? 1 : 0.5
          }}
        />
      </div>

      <div style={{ 
        marginTop: '12px', 
        padding: '8px', 
        background: 'rgba(139, 92, 246, 0.2)',
        borderRadius: '4px',
        fontSize: '10px'
      }}>
        <strong>💡 Tip:</strong> Check browser console (F12) for sound loading status
      </div>
    </div>
  );
};

export default SoundDebugger;
