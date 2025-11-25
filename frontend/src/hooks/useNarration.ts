import { useState, useEffect, useCallback, useRef } from 'react';
import { ApiService } from '../services/api';
import { GenerationStatus, VoiceStyle } from '../types/narration';
import type { NarrationRequest } from '../types/narration';

/**
 * Options for the useNarration hook
 * Requirements: 1.1, 1.5, 4.1, 4.2, 5.1, 5.2, 5.3, 7.4
 */
interface UseNarrationOptions {
  variantId: string;
  voiceStyle: VoiceStyle;
  intensity: number;
  content: string;
  autoGenerate?: boolean;
}

/**
 * State returned by the useNarration hook
 */
interface NarrationState {
  status: 'idle' | 'generating' | 'ready' | 'error';
  progress: number;
  audioUrl: string | null;
  error: string | null;
  requestId: string | null;
}

/**
 * Cache entry structure for localStorage
 * Requirements: 4.1, 4.2
 */
interface CacheEntry {
  audioUrl: string;
  timestamp: number;
}

const CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
const POLL_INTERVAL_MS = 1000; // 1 second

/**
 * Custom hook for managing AI voice narration generation and playback
 * 
 * Features:
 * - Automatic caching with 7-day TTL (Requirements: 4.1, 4.2)
 * - Status polling with 1-second intervals (Requirements: 5.1, 5.2, 5.3)
 * - Request cancellation support (Requirements: 7.4)
 * - Auto-generation option (Requirements: 1.1, 1.5)
 * 
 * @param options - Configuration options for narration generation
 * @returns Narration state and control functions
 */
export const useNarration = ({
  variantId,
  voiceStyle,
  intensity,
  content,
  autoGenerate = false
}: UseNarrationOptions) => {
  const [state, setState] = useState<NarrationState>({
    status: 'idle',
    progress: 0,
    audioUrl: null,
    error: null,
    requestId: null
  });

  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isMountedRef = useRef(true);

  /**
   * Generate cache key for localStorage
   * Requirements: 4.1
   */
  const getCacheKey = useCallback((): string => {
    return `narration_${variantId}_${voiceStyle}`;
  }, [variantId, voiceStyle]);

  /**
   * Check if cached entry is still valid (within TTL)
   * Requirements: 4.2
   */
  const isCacheValid = useCallback((entry: CacheEntry): boolean => {
    const age = Date.now() - entry.timestamp;
    return age < CACHE_TTL_MS;
  }, []);

  /**
   * Get cached narration from localStorage
   * Requirements: 4.1, 4.2
   */
  const getCachedNarration = useCallback((): string | null => {
    try {
      const cacheKey = getCacheKey();
      const cached = localStorage.getItem(cacheKey);
      
      if (cached) {
        const entry: CacheEntry = JSON.parse(cached);
        
        if (isCacheValid(entry)) {
          return entry.audioUrl;
        } else {
          // Remove expired cache entry
          localStorage.removeItem(cacheKey);
        }
      }
    } catch (error) {
      console.error('Failed to retrieve cached narration:', error);
    }
    
    return null;
  }, [getCacheKey, isCacheValid]);

  /**
   * Save narration to localStorage cache
   * Requirements: 4.1, 4.2
   */
  const cacheNarration = useCallback((audioUrl: string): void => {
    try {
      const cacheKey = getCacheKey();
      const entry: CacheEntry = {
        audioUrl,
        timestamp: Date.now()
      };
      
      localStorage.setItem(cacheKey, JSON.stringify(entry));
    } catch (error) {
      console.error('Failed to cache narration:', error);
    }
  }, [getCacheKey]);

  /**
   * Stop polling for generation status
   */
  const stopPolling = useCallback((): void => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  /**
   * Poll for narration generation status
   * Requirements: 5.1, 5.2, 5.3
   */
  const pollGenerationStatus = useCallback(async (requestId: string): Promise<void> => {
    stopPolling();

    console.log('📊 Setting up polling interval for:', requestId);

    pollingIntervalRef.current = setInterval(async () => {
      if (!isMountedRef.current) {
        stopPolling();
        return;
      }

      try {
        console.log('🔍 Polling status for:', requestId);
        const status = await ApiService.getNarrationStatus(requestId);
        console.log('📈 Status received:', status);

        if (!isMountedRef.current) {
          stopPolling();
          return;
        }

        if (status.status === GenerationStatus.COMPLETED) {
          stopPolling();
          
          if (status.audioUrl) {
            // Cache the generated audio URL
            cacheNarration(status.audioUrl);
            
            setState({
              status: 'ready',
              progress: 100,
              audioUrl: status.audioUrl,
              error: null,
              requestId
            });
          } else {
            setState(prev => ({
              ...prev,
              status: 'error',
              error: 'Audio URL not provided in completed response'
            }));
          }
        } else if (status.status === GenerationStatus.FAILED) {
          stopPolling();
          
          setState(prev => ({
            ...prev,
            status: 'error',
            error: status.error || 'Narration generation failed'
          }));
        } else if (status.status === GenerationStatus.CANCELLED) {
          stopPolling();
          
          setState({
            status: 'idle',
            progress: 0,
            audioUrl: null,
            error: null,
            requestId: null
          });
        } else {
          // Update progress for QUEUED or GENERATING status
          setState(prev => ({
            ...prev,
            progress: status.progress
          }));
        }
      } catch (error) {
        if (!isMountedRef.current) {
          stopPolling();
          return;
        }

        stopPolling();
        
        setState(prev => ({
          ...prev,
          status: 'error',
          error: error instanceof Error ? error.message : 'Failed to check generation status'
        }));
      }
    }, POLL_INTERVAL_MS);
  }, [stopPolling, cacheNarration]);

  /**
   * Generate narration for the current variant
   * Requirements: 1.1, 1.5, 4.1, 4.2
   */
  const generate = useCallback(async (): Promise<void> => {
    console.log('🚀 Generate function called');
    
    // Check cache first
    const cachedUrl = getCachedNarration();
    console.log('💾 Cache check result:', cachedUrl);
    
    if (cachedUrl) {
      setState({
        status: 'ready',
        progress: 100,
        audioUrl: cachedUrl,
        error: null,
        requestId: null
      });
      return;
    }

    // Generate new narration
    setState(prev => ({
      ...prev,
      status: 'generating',
      progress: 0,
      error: null
    }));

    try {
      const request: NarrationRequest = {
        variantId,
        voiceStyle,
        intensityLevel: intensity,
        content,
        priority: 'normal'
      };

      console.log('📤 Sending narration request:', request);
      const response = await ApiService.generateNarration(request);
      console.log('📥 Received response:', response);

      // Don't check isMountedRef here - we want to continue even if remounted
      console.log('🎙️ Narration request created:', response.request_id);

      setState(prev => ({
        ...prev,
        requestId: response.request_id
      }));

      // Start polling for status
      console.log('🔄 Starting status polling for:', response.request_id);
      await pollGenerationStatus(response.request_id);
    } catch (error) {
      if (!isMountedRef.current) {
        return;
      }

      setState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to generate narration'
      }));
    }
  }, [variantId, voiceStyle, intensity, content, getCachedNarration, pollGenerationStatus]);

  /**
   * Cancel the current narration generation request
   * Requirements: 7.4
   */
  const cancel = useCallback(async (): Promise<void> => {
    if (!state.requestId) {
      return;
    }

    stopPolling();

    try {
      await ApiService.cancelNarration(state.requestId);

      if (!isMountedRef.current) {
        return;
      }

      setState({
        status: 'idle',
        progress: 0,
        audioUrl: null,
        error: null,
        requestId: null
      });
    } catch (error) {
      if (!isMountedRef.current) {
        return;
      }

      console.error('Failed to cancel narration:', error);
      
      // Still reset state even if cancellation fails
      setState({
        status: 'idle',
        progress: 0,
        audioUrl: null,
        error: null,
        requestId: null
      });
    }
  }, [state.requestId, stopPolling]);

  /**
   * Auto-generate narration on mount if enabled
   * Requirements: 1.1, 1.5
   */
  useEffect(() => {
    if (autoGenerate) {
      generate();
    }
  }, [autoGenerate, generate]);

  /**
   * Set mounted state
   */
  useEffect(() => {
    isMountedRef.current = true;
    
    return () => {
      isMountedRef.current = false;
      stopPolling();
    };
  }, [stopPolling]);

  return {
    ...state,
    generate,
    cancel
  };
};

export default useNarration;
