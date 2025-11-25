"""
Voice narration service for TTS API integration and audio generation.
"""

import os
import asyncio
import logging
import uuid
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta

import httpx
from elevenlabs import ElevenLabs, Voice, VoiceSettings
from elevenlabs.core import ApiError

from backend.narration.audio_cache import AudioCacheManager
from backend.narration.voice_configs import VoiceStyle

logger = logging.getLogger(__name__)


class TTSAPIError(Exception):
    """Base exception for TTS API errors."""
    pass


class RateLimitError(TTSAPIError):
    """Exception raised when TTS API rate limit is exceeded."""
    pass


class APIOutageError(TTSAPIError):
    """Exception raised when TTS API is experiencing an outage."""
    pass


@dataclass
class VoiceConfig:
    """Configuration for a specific voice style."""
    voice_id: str
    stability: float
    similarity_boost: float
    style: float
    speed: float


@dataclass
class NarrationRequest:
    """Request for generating voice narration."""
    content: str
    voice_style: VoiceStyle
    intensity_level: int  # 1-5
    variant_id: str


@dataclass
class NarrationResult:
    """Result of narration generation."""
    narration_id: str
    audio_url: str
    duration: float
    file_size: int
    cached: bool


class VoiceNarrationService:
    """Service for generating AI-powered voice narrations using TTS API."""
    
    def __init__(self, api_key: str, cache_manager: AudioCacheManager):
        """
        Initialize the voice narration service.
        
        Args:
            api_key: API key for TTS service (ElevenLabs)
            cache_manager: Audio cache manager instance
        """
        self.api_key = api_key
        self.cache_manager = cache_manager
        self.client = ElevenLabs(api_key=api_key)
        self.voice_configs = self._initialize_voice_configs()
        
        # Track API health and rate limiting
        self._api_healthy = True
        self._last_outage_check = datetime.now()
        self._consecutive_failures = 0
        self._rate_limit_reset_time: Optional[datetime] = None
        
        logger.info("VoiceNarrationService initialized with %d voice styles", len(self.voice_configs))
    
    def _initialize_voice_configs(self) -> Dict[VoiceStyle, VoiceConfig]:
        """
        Map voice styles to TTS API voice configurations.
        
        Loads voice configurations from voice_configs module to avoid circular imports.
        
        Returns:
            Dictionary mapping voice styles to their configurations
        """
        from backend.narration.voice_configs import VOICE_STYLE_CONFIGS
        
        configs = {}
        for voice_style, config_data in VOICE_STYLE_CONFIGS.items():
            configs[voice_style] = VoiceConfig(
                voice_id=config_data["voice_id"],
                stability=config_data["base_stability"],
                similarity_boost=config_data["base_similarity_boost"],
                style=config_data["base_style"],
                speed=config_data["base_speed"]
            )
        
        return configs
    
    async def generate_narration(
        self, 
        request: NarrationRequest
    ) -> NarrationResult:
        """
        Generate audio narration for content.
        
        This method:
        1. Checks cache for existing audio
        2. If not cached, calls TTS API to generate audio
        3. Stores generated audio in cache
        4. Returns result with audio URL and metadata
        
        Args:
            request: Narration generation request
            
        Returns:
            Result containing audio URL and metadata
            
        Raises:
            ValueError: If voice style is not configured or intensity is invalid
            RateLimitError: If API rate limit is exceeded
            APIOutageError: If API is experiencing an outage
            RuntimeError: If TTS API call fails after retries
        """
        # Validate voice style first (before logging)
        if request.voice_style not in self.voice_configs:
            error_msg = f"Voice style {request.voice_style} is not configured"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log request details for debugging
        logger.info(
            "Generating narration: variant_id=%s, voice_style=%s, intensity=%d, content_length=%d",
            request.variant_id,
            request.voice_style.value if hasattr(request.voice_style, 'value') else str(request.voice_style),
            request.intensity_level,
            len(request.content)
        )
        
        # Validate intensity level
        if not 1 <= request.intensity_level <= 5:
            error_msg = f"Intensity level must be between 1 and 5, got {request.intensity_level}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if we're currently rate limited
        if self._rate_limit_reset_time and datetime.now() < self._rate_limit_reset_time:
            wait_seconds = (self._rate_limit_reset_time - datetime.now()).total_seconds()
            error_msg = f"Rate limit exceeded. Please wait {wait_seconds:.0f} seconds before retrying."
            logger.warning(error_msg)
            raise RateLimitError(error_msg)
        
        # Check API health for extended outages
        if not self._api_healthy:
            time_since_check = (datetime.now() - self._last_outage_check).total_seconds()
            if time_since_check < 300:  # 5 minutes
                error_msg = "TTS API is currently experiencing an outage. Please try again later."
                logger.error(error_msg)
                raise APIOutageError(error_msg)
            else:
                # Reset health check after 5 minutes
                logger.info("Resetting API health check after cooldown period")
                self._api_healthy = True
                self._consecutive_failures = 0
        
        # Generate cache key
        cache_key = self.cache_manager.get_cache_key(
            request.variant_id,
            request.voice_style
        )
        
        # Check cache first
        cached_path = await self.cache_manager.get(cache_key)
        
        if cached_path:
            logger.info(
                "Cache hit for variant_id=%s, voice_style=%s",
                request.variant_id,
                request.voice_style.value
            )
            
            # Get file size and duration (approximate)
            file_size = cached_path.stat().st_size
            # Approximate duration: MP3 at 128kbps = ~16KB/second
            duration = file_size / (16 * 1024)
            
            narration_id = cache_key
            audio_url = f"/api/narration/audio/{narration_id}"
            
            return NarrationResult(
                narration_id=narration_id,
                audio_url=audio_url,
                duration=duration,
                file_size=file_size,
                cached=True
            )
        
        # Cache miss - generate new audio
        logger.info(
            "Cache miss for variant_id=%s, voice_style=%s - generating new audio",
            request.variant_id,
            request.voice_style.value
        )
        
        try:
            # Get base voice config and adjust for intensity
            base_config = self.voice_configs[request.voice_style]
            adjusted_config = self._adjust_voice_for_intensity(base_config, request.intensity_level)
            
            # Call TTS API
            audio_data = await self._call_tts_api(request.content, adjusted_config)
            
            # Reset failure tracking on success
            self._consecutive_failures = 0
            self._api_healthy = True
            
            # Store in cache
            narration_id = str(uuid.uuid4())
            metadata = {
                'narration_id': narration_id,
                'variant_id': request.variant_id,
                'voice_style': request.voice_style.value
            }
            
            file_path = await self.cache_manager.put(cache_key, audio_data, metadata)
            
            # Calculate metadata
            file_size = len(audio_data)
            duration = file_size / (16 * 1024)  # Approximate duration
            audio_url = f"/api/narration/audio/{cache_key}"
            
            logger.info(
                "Generated narration: id=%s, size=%d bytes, duration=%.2f seconds",
                narration_id,
                file_size,
                duration
            )
            
            return NarrationResult(
                narration_id=narration_id,
                audio_url=audio_url,
                duration=duration,
                file_size=file_size,
                cached=False
            )
            
        except RateLimitError:
            # Re-raise rate limit errors without modification
            raise
        except APIOutageError:
            # Re-raise outage errors without modification
            raise
        except Exception as e:
            # Track consecutive failures for outage detection
            self._consecutive_failures += 1
            
            logger.error(
                "Failed to generate narration for variant_id=%s: %s (consecutive failures: %d)",
                request.variant_id,
                str(e),
                self._consecutive_failures,
                exc_info=True
            )
            
            # Detect extended outage (5+ consecutive failures)
            if self._consecutive_failures >= 5:
                self._api_healthy = False
                self._last_outage_check = datetime.now()
                logger.error(
                    "Detected extended TTS API outage after %d consecutive failures",
                    self._consecutive_failures
                )
                raise APIOutageError(
                    "TTS API appears to be experiencing an extended outage. Please try again later."
                ) from e
            
            # Re-raise the original exception
            raise
    
    async def _call_tts_api(
        self, 
        text: str, 
        voice_config: VoiceConfig
    ) -> bytes:
        """
        Call ElevenLabs TTS API with streaming and exponential backoff retry logic.
        
        Implements retry logic with exponential backoff (3 attempts):
        - Attempt 1: immediate
        - Attempt 2: wait 2 seconds
        - Attempt 3: wait 4 seconds
        
        Detects and handles:
        - Rate limiting (429 status codes)
        - Network errors
        - API errors
        - Timeout errors
        
        Args:
            text: Text content to convert to speech
            voice_config: Voice configuration parameters
            
        Returns:
            Audio data as bytes (MP3 format)
            
        Raises:
            RateLimitError: If rate limit is exceeded
            RuntimeError: If all retry attempts fail
        """
        max_attempts = 3
        base_delay = 2  # seconds
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(
                    "Calling TTS API (attempt %d/%d) with voice_id=%s, text_length=%d",
                    attempt,
                    max_attempts,
                    voice_config.voice_id,
                    len(text)
                )
                
                # Create voice settings
                voice_settings = VoiceSettings(
                    stability=voice_config.stability,
                    similarity_boost=voice_config.similarity_boost,
                    style=voice_config.style,
                    use_speaker_boost=True
                )
                
                # Call ElevenLabs API with streaming
                # Note: The ElevenLabs SDK handles streaming internally
                # Using eleven_turbo_v2_5 which is free-tier compatible
                audio_generator = self.client.text_to_speech.convert(
                    voice_id=voice_config.voice_id,
                    text=text,
                    model_id="eleven_turbo_v2_5",
                    voice_settings=voice_settings,
                    output_format="mp3_44100_128"
                )
                
                # Collect audio chunks
                audio_chunks = []
                for chunk in audio_generator:
                    if chunk:
                        audio_chunks.append(chunk)
                
                audio_data = b''.join(audio_chunks)
                
                if not audio_data:
                    raise RuntimeError("TTS API returned empty audio data")
                
                logger.info(
                    "TTS API call successful, received %d bytes (attempt %d/%d)",
                    len(audio_data),
                    attempt,
                    max_attempts
                )
                
                return audio_data
                
            except ApiError as e:
                last_exception = e
                error_details = {
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "voice_id": voice_config.voice_id,
                    "text_length": len(text),
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                # Check for rate limiting (429 status code)
                if hasattr(e, 'status_code') and e.status_code == 429:
                    # Extract retry-after header if available
                    retry_after = 60  # Default to 60 seconds
                    if hasattr(e, 'headers') and 'retry-after' in e.headers:
                        try:
                            retry_after = int(e.headers['retry-after'])
                        except (ValueError, TypeError):
                            pass
                    
                    self._rate_limit_reset_time = datetime.now() + timedelta(seconds=retry_after)
                    
                    logger.error(
                        "Rate limit exceeded. Reset time: %s. Error details: %s",
                        self._rate_limit_reset_time.isoformat(),
                        error_details
                    )
                    
                    raise RateLimitError(
                        f"TTS API rate limit exceeded. Please wait {retry_after} seconds before retrying."
                    ) from e
                
                logger.warning(
                    "TTS API call failed with ApiError (attempt %d/%d): %s. Details: %s",
                    attempt,
                    max_attempts,
                    str(e),
                    error_details
                )
                
                if attempt < max_attempts:
                    # Exponential backoff
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.info("Retrying in %d seconds...", delay)
                    await asyncio.sleep(delay)
                    
            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
                last_exception = e
                error_details = {
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "voice_id": voice_config.voice_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                logger.warning(
                    "Network error during TTS API call (attempt %d/%d): %s. Details: %s",
                    attempt,
                    max_attempts,
                    str(e),
                    error_details
                )
                
                if attempt < max_attempts:
                    # Exponential backoff
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.info("Retrying in %d seconds...", delay)
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                last_exception = e
                error_details = {
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "voice_id": voice_config.voice_id,
                    "text_length": len(text),
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
                
                logger.error(
                    "Unexpected error during TTS API call (attempt %d/%d): %s. Details: %s",
                    attempt,
                    max_attempts,
                    str(e),
                    error_details,
                    exc_info=True
                )
                
                if attempt < max_attempts:
                    # Exponential backoff
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.info("Retrying in %d seconds...", delay)
                    await asyncio.sleep(delay)
        
        # All attempts failed
        error_msg = f"TTS API call failed after {max_attempts} attempts. Last error: {str(last_exception)}"
        logger.error(
            "All retry attempts exhausted. Final error: %s",
            error_msg,
            exc_info=True
        )
        raise RuntimeError(error_msg) from last_exception
    
    def get_api_health_status(self) -> Dict[str, Any]:
        """
        Get current API health status.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            "healthy": self._api_healthy,
            "consecutive_failures": self._consecutive_failures,
            "rate_limited": self._rate_limit_reset_time is not None and datetime.now() < self._rate_limit_reset_time,
            "rate_limit_reset_time": self._rate_limit_reset_time.isoformat() if self._rate_limit_reset_time else None,
            "last_outage_check": self._last_outage_check.isoformat()
        }
    
    def _adjust_voice_for_intensity(
        self, 
        base_config: VoiceConfig, 
        intensity: int
    ) -> VoiceConfig:
        """
        Modify voice parameters based on horror intensity.
        
        Applies intensity-specific modifiers from voice_configs to adjust:
        - Stability: Lower values create more variation (more unsettling)
        - Speed: Slower speeds increase tension
        - Style: Higher values emphasize the horror characteristics
        
        Args:
            base_config: Base voice configuration
            intensity: Horror intensity level (1-5)
            
        Returns:
            Adjusted voice configuration with intensity modifiers applied
        """
        from backend.narration.voice_configs import VOICE_STYLE_CONFIGS
        
        # Find the voice style that matches this config
        voice_style = None
        for style, config_data in VOICE_STYLE_CONFIGS.items():
            if config_data["voice_id"] == base_config.voice_id:
                voice_style = style
                break
        
        if not voice_style:
            logger.warning(
                "Could not find voice style for voice_id=%s, using base config",
                base_config.voice_id
            )
            return base_config
        
        # Get intensity modifiers
        config_data = VOICE_STYLE_CONFIGS[voice_style]
        intensity_modifiers = config_data.get("intensity_modifiers", {})
        
        if intensity not in intensity_modifiers:
            logger.warning(
                "No intensity modifiers for level %d, using base config",
                intensity
            )
            return base_config
        
        modifiers = intensity_modifiers[intensity]
        
        # Apply modifiers to create adjusted config
        adjusted_config = VoiceConfig(
            voice_id=base_config.voice_id,
            stability=modifiers.get("stability", base_config.stability),
            similarity_boost=base_config.similarity_boost,  # Keep constant
            style=modifiers.get("style", base_config.style),
            speed=modifiers.get("speed", base_config.speed)
        )
        
        logger.debug(
            "Adjusted voice config for intensity %d: stability=%.2f, style=%.2f, speed=%.2f",
            intensity,
            adjusted_config.stability,
            adjusted_config.style,
            adjusted_config.speed
        )
        
        return adjusted_config
