// Type definitions for AI Voice Narration feature

/**
 * Available horror voice styles for narration
 * Requirements: 2.1
 */
export const VoiceStyle = {
  GHOSTLY_WHISPER: 'ghostly_whisper',
  DEMONIC_GROWL: 'demonic_growl',
  EERIE_NARRATOR: 'eerie_narrator',
  POSSESSED_CHILD: 'possessed_child',
  ANCIENT_ENTITY: 'ancient_entity'
} as const;

export type VoiceStyle = typeof VoiceStyle[keyof typeof VoiceStyle];

/**
 * Status of narration generation process
 * Requirements: 5.1
 */
export const GenerationStatus = {
  QUEUED: 'queued',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
} as const;

export type GenerationStatus = typeof GenerationStatus[keyof typeof GenerationStatus];

/**
 * Request payload for generating narration
 * Requirements: 2.1
 */
export interface NarrationRequest {
  variantId: string;
  voiceStyle: VoiceStyle;
  intensityLevel: number; // 1-5 scale
  content: string;
  priority?: 'high' | 'normal' | 'low';
}

/**
 * Status response for narration generation
 * Requirements: 5.1
 */
export interface NarrationStatus {
  requestId: string;
  status: GenerationStatus;
  progress: number; // 0-100
  audioUrl?: string;
  duration?: number; // in seconds
  error?: string;
  createdAt: string;
  completedAt?: string;
}

/**
 * Information about available voice styles
 * Requirements: 2.1
 */
export interface VoiceStyleInfo {
  id: string;
  name: string;
  description: string;
  previewUrl: string;
  icon: string;
  recommendedIntensity: number; // 1-5 scale
}
