// API service for communicating with the backend
import { StorageService } from './storage';
import type { SpookyVariant, UserPreferences, ProcessingStats, StoryContinuation } from '../types';
import type { NarrationRequest, NarrationStatus, VoiceStyleInfo } from '../types/narration';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    const config: RequestInit = {
      headers,
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        // Try to extract error message from response body
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = await response.json();
          
          // Handle different error response formats
          if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (errorData.error) {
            errorMessage = errorData.error;
          }
        } catch {
          // If response body is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        
        // Add context for specific status codes
        if (response.status === 429) {
          errorMessage = `Rate limit exceeded. ${errorMessage}`;
        } else if (response.status === 503) {
          errorMessage = `Service temporarily unavailable. ${errorMessage}`;
        } else if (response.status >= 500) {
          errorMessage = `Server error. ${errorMessage}`;
        } else if (response.status === 404) {
          errorMessage = `Resource not found. ${errorMessage}`;
        } else if (response.status === 401 || response.status === 403) {
          errorMessage = `Authentication error. ${errorMessage}`;
        }
        
        const error = new Error(errorMessage);
        (error as any).status = response.status;
        throw error;
      }
      
      return await response.json();
    } catch (error) {
      // Add context for network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        const networkError = new Error('Network error. Please check your internet connection.');
        console.error('API request failed:', networkError);
        throw networkError;
      }
      
      console.error('API request failed:', error);
      throw error;
    }
  }

  static async processFeeds(
    urls: string[], 
    preferences?: UserPreferences,
    intensity?: number,
    variantCount?: number
  ): Promise<{ 
    success: boolean;
    message: string; 
    processing_id: string;
    total_feeds: number;
    total_variants: number;
    processing_time: number;
    variants: any[];
  }> {
    const requestBody: any = { urls };
    
    if (preferences) {
      requestBody.user_preferences = preferences;
    }
    
    if (intensity !== undefined) {
      requestBody.intensity = intensity;
    }
    
    if (variantCount !== undefined) {
      requestBody.variant_count = variantCount;
    }
    
    return this.request('/feeds/process', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  static async getSpookyVariants(feedId: string): Promise<SpookyVariant[]> {
    return this.request(`/variants/${feedId}`);
  }

  static async updateUserPreferences(preferences: UserPreferences): Promise<{ status: string }> {
    // Get or generate user ID using StorageService
    const userId = StorageService.getUserId();
    
    // Format the request according to backend expectations
    const preferencesRequest = {
      user_id: userId,
      preferred_horror_types: preferences.preferred_horror_types,
      intensity_level: preferences.intensity_level,
      content_filters: preferences.content_filters,
      notification_settings: preferences.notification_settings,
      theme_customizations: preferences.theme_customizations,
    };
    
    return this.request('/preferences/', {
      method: 'POST',
      body: JSON.stringify(preferencesRequest),
    });
  }

  static async getHealthStatus(): Promise<ProcessingStats> {
    return this.request('/health');
  }

  static async continueStory(
    variantId: string,
    continuationLength: number = 500
  ): Promise<StoryContinuation> {
    const url = `${API_BASE_URL}/feeds/variants/${variantId}/continue?continuation_length=${continuationLength}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        const waitTime = retryAfter ? parseInt(retryAfter) : 60;
        throw new Error(`Rate limit exceeded. Please wait ${waitTime} seconds before trying again.`);
      }

      // Handle other HTTP errors
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Story variant not found. It may have been deleted.');
        }
        if (response.status === 400) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Invalid request. The story may be too short to continue.');
        }
        if (response.status >= 500) {
          throw new Error('Server error. Please try again in a moment.');
        }
        throw new Error(`Failed to continue story: ${response.statusText}`);
      }

      const data = await response.json();

      // Validate response structure
      if (!data.success || !data.continuation) {
        throw new Error('Invalid response from server. Please try again.');
      }

      const continuation = data.continuation;

      // Validate continuation content
      if (!continuation.continued_narrative || continuation.continued_narrative.trim().length === 0) {
        throw new Error('Received empty continuation. Please try again.');
      }

      if (continuation.continued_narrative.length < 100) {
        throw new Error('Continuation is too short. Please try again.');
      }

      return continuation;

    } catch (error) {
      clearTimeout(timeoutId);

      // Handle timeout
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timed out. The nightmare may be too dark to continue. Please try again.');
      }

      // Handle network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error. Please check your connection and try again.');
      }

      // Re-throw other errors
      throw error;
    }
  }

  static async getCachedContinuation(
    variantId: string,
    continuationLength: number = 500
  ): Promise<StoryContinuation | null> {
    try {
      const response = await this.request<{
        success: boolean;
        variant_id: string;
        continuation: StoryContinuation;
        cached: boolean;
      }>(`/feeds/variants/${variantId}/continuation?continuation_length=${continuationLength}`);
      
      return response.continuation;
    } catch (error) {
      // Return null if not found in cache
      return null;
    }
  }

  // Narration API methods
  // Requirements: 1.1, 5.1, 7.4

  /**
   * Generate voice narration for a spooky variant
   * Requirements: 1.1
   */
  static async generateNarration(request: NarrationRequest): Promise<{
    request_id: string;
    status: string;
    estimated_time?: number;
    queue_position?: number;
  }> {
    const requestBody = {
      variant_id: request.variantId,
      voice_style: request.voiceStyle,
      intensity_level: request.intensityLevel,
      priority: request.priority || 'normal',
      content: request.content
    };

    return this.request('/narration/generate', {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  /**
   * Get generation status and progress for a narration request
   * Requirements: 5.1
   */
  static async getNarrationStatus(requestId: string): Promise<NarrationStatus> {
    const response = await this.request<any>(`/narration/status/${requestId}`);
    
    // Transform snake_case to camelCase
    return {
      requestId: response.request_id,
      status: response.status,
      progress: response.progress,
      audioUrl: response.audio_url,
      duration: response.duration,
      error: response.error,
      createdAt: response.created_at,
      completedAt: response.completed_at
    };
  }

  /**
   * Get list of available voice styles with preview information
   * Requirements: 2.1
   */
  static async getVoiceStyles(): Promise<VoiceStyleInfo[]> {
    return this.request('/narration/voices');
  }

  /**
   * Cancel a queued or in-progress narration generation request
   * Requirements: 7.4
   */
  static async cancelNarration(requestId: string): Promise<{
    success: boolean;
    message: string;
    request_id: string;
  }> {
    return this.request(`/narration/cancel/${requestId}`, {
      method: 'DELETE',
    });
  }
}