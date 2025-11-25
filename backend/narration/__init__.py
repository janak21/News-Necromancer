"""
Voice narration module for generating AI-powered horror-themed audio narrations.

This module provides:
- Voice narration service with TTS API integration
- Audio caching with LRU eviction
- Generation queue management with prioritization
"""

from backend.narration.voice_service import VoiceNarrationService
from backend.narration.audio_cache import AudioCacheManager
from backend.narration.queue_manager import GenerationQueueManager

__all__ = [
    'VoiceNarrationService',
    'AudioCacheManager',
    'GenerationQueueManager',
]
