import React, { useRef, useState, useEffect } from 'react';
import { useNarration } from '../../hooks/useNarration';
import { VoiceStyle } from '../../types/narration';
import SpookySpinner from '../SpookySpinner/SpookySpinner';
import Button from '../Button/Button';
import PlaybackControls from './PlaybackControls';
import ProgressBar from './ProgressBar';
import PlaybackRateControl from './PlaybackRateControl';
import './AudioPlayer.css';
import './PlaybackControls.css';
import './ProgressBar.css';
import './PlaybackRateControl.css';

/**
 * Props for the AudioPlayer component
 * Requirements: 1.1, 1.5, 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5, 9.1, 9.2, 9.3, 9.4, 9.5
 */
export interface AudioPlayerProps {
  variantId: string;
  voiceStyle: VoiceStyle;
  intensity: number;
  content: string;
  autoPlay?: boolean;
  className?: string;
}

/**
 * AudioPlayer component for controlling AI voice narration playback
 * 
 * Features:
 * - Generate narration with progress tracking (Requirements: 1.1, 5.1, 5.2, 5.3)
 * - Playback controls: play, pause, seek (Requirements: 3.1, 3.2)
 * - Speed adjustment (0.5x to 2.0x) (Requirements: 3.3)
 * - Background playback support (Requirements: 3.4)
 * - Download functionality (Requirements: 9.1, 9.2, 9.3, 9.4, 9.5)
 * - Error handling with retry (Requirements: 5.4, 5.5)
 * - Loading states with progress indicator (Requirements: 5.2, 5.3)
 */
const AudioPlayer: React.FC<AudioPlayerProps> = ({
  variantId,
  voiceStyle,
  intensity,
  content,
  autoPlay = false,
  className = ''
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  
  // Use narration hook for generation and status management
  const {
    status,
    progress,
    audioUrl,
    error,
    generate,
    cancel
  } = useNarration({
    variantId,
    voiceStyle,
    intensity,
    content,
    autoGenerate: false
  });

  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [isDownloading, setIsDownloading] = useState(false);
  
  // Error handling state
  const [retryCount, setRetryCount] = useState(0);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  /**
   * Generate narration with exponential backoff retry
   * Requirements: 1.1, 5.1, 5.4, 5.5
   */
  const generateNarration = async () => {
    // Check if offline
    if (!navigator.onLine) {
      setErrorDetails('You appear to be offline. Please check your internet connection and try again.');
      return;
    }
    
    try {
      // Clear previous error details
      setErrorDetails(null);
      
      await generate();
      
      // Reset retry count on success
      setRetryCount(0);
      
    } catch (err) {
      // Log error for analytics
      console.error('Narration generation failed:', {
        variantId,
        voiceStyle,
        intensity,
        retryCount,
        error: err
      });
      
      // Extract user-friendly error message
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setErrorDetails(errorMessage);
      
      // Increment retry count for exponential backoff
      setRetryCount(prev => prev + 1);
    }
  };
  
  /**
   * Retry with exponential backoff
   * Requirements: 5.4, 5.5
   */
  const retryWithBackoff = async () => {
    // Calculate delay: 2^retryCount seconds (max 32 seconds)
    const delay = Math.min(Math.pow(2, retryCount) * 1000, 32000);
    
    if (delay > 1000) {
      // Show delay message to user
      setErrorDetails(`Retrying in ${delay / 1000} seconds...`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    await generateNarration();
  };

  /**
   * Play audio
   * Requirements: 3.1
   */
  const play = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  /**
   * Pause audio
   * Requirements: 3.1
   */
  const pause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  /**
   * Seek to specific time position
   * Requirements: 3.2, 3.5
   */
  const seek = (time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  /**
   * Adjust playback speed
   * Requirements: 3.3
   */
  const handlePlaybackRateChange = (rate: number) => {
    if (audioRef.current) {
      audioRef.current.playbackRate = rate;
      setPlaybackRate(rate);
    }
  };

  /**
   * Download narration as MP3
   * Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
   */
  const download = async () => {
    if (!audioUrl || isDownloading) {
      return;
    }
    
    // Check if offline
    if (!navigator.onLine) {
      setErrorDetails('Cannot download while offline. Please check your internet connection.');
      return;
    }

    setIsDownloading(true);

    try {
      // Fetch the audio file
      const response = await fetch(audioUrl);
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }
      
      const blob = await response.blob();
      
      if (blob.size === 0) {
        throw new Error('Downloaded file is empty');
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate descriptive filename with variant ID and voice style
      // Requirements: 9.4
      const filename = `narration-${variantId}-${voiceStyle}.mp3`;
      link.download = filename;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      // Log successful download for analytics
      console.log('Narration downloaded successfully:', {
        variantId,
        voiceStyle,
        filename,
        size: blob.size
      });
      
    } catch (error) {
      console.error('Failed to download narration:', {
        variantId,
        voiceStyle,
        error
      });
      
      // Show user-friendly error message
      const errorMessage = error instanceof Error ? error.message : 'Download failed';
      setErrorDetails(`Download failed: ${errorMessage}`);
      
      // Clear error after 5 seconds
      setTimeout(() => {
        setErrorDetails(null);
      }, 5000);
    } finally {
      setIsDownloading(false);
    }
  };

  /**
   * Handle audio time update
   * Requirements: 3.2
   */
  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  /**
   * Handle audio metadata loaded
   * Requirements: 3.2
   */
  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  /**
   * Handle audio ended
   * Requirements: 3.1
   */
  const handleEnded = () => {
    setIsPlaying(false);
  };

  /**
   * Auto-play when audio is ready
   * Requirements: 1.5
   */
  useEffect(() => {
    if (status === 'ready' && audioUrl && autoPlay) {
      play();
    }
  }, [status, audioUrl, autoPlay]);

  /**
   * Monitor online/offline status
   * Requirements: 5.4
   */
  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      console.log('Connection restored');
    };
    
    const handleOffline = () => {
      setIsOffline(true);
      setErrorDetails('Connection lost. Please check your internet connection.');
      console.log('Connection lost');
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const containerClasses = `audio-player ${className}`.trim();

  // Convert relative audio URL to absolute URL
  // Support data URLs (base64), http URLs, and relative paths
  const absoluteAudioUrl = audioUrl 
    ? (audioUrl.startsWith('http') || audioUrl.startsWith('data:') 
        ? audioUrl 
        : `${window.location.origin}${audioUrl}`)
    : undefined;

  return (
    <div className={containerClasses}>
      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        src={absoluteAudioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />

      {/* Idle state - show generate button */}
      {status === 'idle' && (
        <div className="audio-player__idle">
          <Button
            variant="primary"
            size="md"
            onClick={generateNarration}
            leftIcon={
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            }
          >
            Generate Narration
          </Button>
        </div>
      )}

      {/* Generating state - show progress */}
      {status === 'generating' && (
        <div className="audio-player__generating">
          <SpookySpinner
            variant="ghost"
            size="medium"
            message={`Summoning voice... ${progress}%`}
          />
          <div className="audio-player__progress-bar">
            <div
              className="audio-player__progress-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={cancel}
          >
            Cancel
          </Button>
        </div>
      )}

      {/* Error state - show error message and retry */}
      {status === 'error' && (
        <div className="audio-player__error">
          <div className="audio-player__error-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth={2} />
              <line x1="12" y1="8" x2="12" y2="12" strokeWidth={2} strokeLinecap="round" />
              <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth={2} strokeLinecap="round" />
            </svg>
          </div>
          
          {/* Offline indicator */}
          {isOffline && (
            <div className="audio-player__offline-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3" />
              </svg>
              <span>Offline</span>
            </div>
          )}
          
          {/* Primary error message */}
          <p className="audio-player__error-message">
            {error || 'Failed to generate narration'}
          </p>
          
          {/* Additional error details */}
          {errorDetails && errorDetails !== error && (
            <p className="audio-player__error-details">
              {errorDetails}
            </p>
          )}
          
          {/* Retry count indicator */}
          {retryCount > 0 && (
            <p className="audio-player__retry-info">
              Retry attempt: {retryCount}
            </p>
          )}
          
          {/* Retry button with exponential backoff */}
          <div className="audio-player__error-actions">
            <Button
              variant="primary"
              size="md"
              onClick={retryWithBackoff}
              disabled={isOffline}
            >
              {retryCount > 0 ? 'Retry Again' : 'Retry'}
            </Button>
            
            {retryCount > 2 && (
              <Button
                variant="ghost"
                size="md"
                onClick={() => {
                  setRetryCount(0);
                  setErrorDetails(null);
                }}
              >
                Reset
              </Button>
            )}
          </div>
          
          {/* Help text for persistent errors */}
          {retryCount >= 3 && (
            <p className="audio-player__help-text">
              If the problem persists, the service may be temporarily unavailable. Please try again later.
            </p>
          )}
        </div>
      )}

      {/* Ready/Playing state - show full player controls */}
      {(status === 'ready' || isPlaying) && audioUrl && (
        <div className="audio-player__controls">
          {/* Play/Pause button using PlaybackControls component */}
          <PlaybackControls
            isPlaying={isPlaying}
            onPlay={play}
            onPause={pause}
          />

          {/* Progress bar with seek functionality using ProgressBar component */}
          <ProgressBar
            currentTime={currentTime}
            duration={duration}
            onSeek={seek}
          />

          {/* Playback rate control using PlaybackRateControl component */}
          <PlaybackRateControl
            rate={playbackRate}
            onChange={handlePlaybackRateChange}
          />

          {/* Download button */}
          <button
            className="audio-player__download-button"
            onClick={download}
            disabled={isDownloading}
            aria-label="Download narration"
            title="Download narration"
          >
            {isDownloading ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="audio-player__spinner">
                <circle cx="12" cy="12" r="10" strokeWidth={2} />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default AudioPlayer;
