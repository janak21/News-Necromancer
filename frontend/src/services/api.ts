// API service for communicating with the backend
import type { SpookyVariant, UserPreferences, ProcessingStats } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
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

  static async processFeeds(urls: string[]): Promise<{ 
    success: boolean;
    message: string; 
    processing_id: string;
    total_feeds: number;
    total_variants: number;
    processing_time: number;
    variants: any[];
  }> {
    return this.request('/feeds/process', {
      method: 'POST',
      body: JSON.stringify({ urls }),
    });
  }

  static async getSpookyVariants(feedId: string): Promise<SpookyVariant[]> {
    return this.request(`/variants/${feedId}`);
  }

  static async updateUserPreferences(preferences: UserPreferences): Promise<{ status: string }> {
    // Generate a simple user ID for demo purposes (in production, this would come from auth)
    const userId = localStorage.getItem('spooky_user_id') || 'default_ghost_user';
    
    // Store the user ID for future requests
    localStorage.setItem('spooky_user_id', userId);
    
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
}