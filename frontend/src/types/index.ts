// Type definitions for the Spooky RSS System

export interface FeedItem {
  title: string;
  summary: string;
  link: string;
  published: string;
  source: string;
  metadata: Record<string, unknown>;
}

export interface SpookyVariant {
  original_item: FeedItem;
  haunted_title: string;
  haunted_summary: string;
  horror_themes: string[];
  supernatural_explanation: string;
  personalization_applied: boolean;
  generation_timestamp: string;
}

export interface UserPreferences {
  preferred_horror_types: string[];
  intensity_level: number; // 1-5 scale
  content_filters: string[];
  notification_settings: Record<string, boolean>;
  theme_customizations: Record<string, string>;
}

export interface ProcessingStats {
  feeds_processed: number;
  variants_generated: number;
  processing_time: number;
  success_rate: number;
  error_count: number;
}

export interface SpookyFeed {
  id: string;
  url: string;
  title: string;
  variants: SpookyVariant[];
  last_updated: string;
}