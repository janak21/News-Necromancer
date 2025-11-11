// API service for communicating with the backend
import { StorageService } from './storage';
import type { SpookyVariant, UserPreferences, ProcessingStats, StoryContinuation } from '../types';

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
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
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
    const response = await this.request<{
      success: boolean;
      variant_id: string;
      continuation: StoryContinuation;
    }>(`/feeds/variants/${variantId}/continue?continuation_length=${continuationLength}`, {
      method: 'POST',
    });
    
    return response.continuation;
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
}