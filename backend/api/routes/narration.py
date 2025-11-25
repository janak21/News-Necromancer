"""
Narration API endpoints for AI voice generation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import logging
from pathlib import Path

from backend.models.narration_models import (
    NarrationGenerateRequest,
    NarrationGenerateResponse,
    NarrationStatusResponse,
    VoiceStyleInfo,
    VoiceStyleEnum,
    GenerationStatus
)
from backend.narration.voice_service import VoiceNarrationService, NarrationRequest as ServiceNarrationRequest
from backend.narration.queue_manager import GenerationQueueManager, Priority
from backend.narration.audio_cache import AudioCacheManager
from backend.narration.voice_configs import VOICE_STYLE_CONFIGS, VoiceStyle

router = APIRouter()
logger = logging.getLogger(__name__)

# Global instances (will be initialized via dependencies)
_voice_service: VoiceNarrationService = None
_queue_manager: GenerationQueueManager = None
_audio_cache: AudioCacheManager = None


def get_voice_service() -> VoiceNarrationService:
    """Get or create voice narration service instance."""
    global _voice_service, _audio_cache
    
    if _voice_service is None:
        from backend.config.settings import get_settings
        
        settings = get_settings()
        
        api_key = settings.elevenlabs_api_key
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        
        # Initialize cache manager if not already done
        if _audio_cache is None:
            cache_dir = Path(settings.narration_cache_dir)
            max_size_mb = settings.narration_cache_max_size_mb
            ttl_days = settings.narration_cache_ttl_days
            
            _audio_cache = AudioCacheManager(
                cache_dir=cache_dir,
                max_size_mb=max_size_mb,
                ttl_days=ttl_days
            )
        
        _voice_service = VoiceNarrationService(
            api_key=api_key,
            cache_manager=_audio_cache
        )
        
        logger.info("Initialized VoiceNarrationService")
    
    return _voice_service


def get_queue_manager() -> GenerationQueueManager:
    """Get or create generation queue manager instance."""
    global _queue_manager
    
    if _queue_manager is None:
        from backend.config.settings import get_settings
        
        settings = get_settings()
        
        max_concurrent = settings.narration_max_concurrent
        _queue_manager = GenerationQueueManager(max_concurrent=max_concurrent)
        
        logger.info(f"Initialized GenerationQueueManager with max_concurrent={max_concurrent}")
    
    return _queue_manager


def get_audio_cache() -> AudioCacheManager:
    """Get or create audio cache manager instance."""
    global _audio_cache
    
    if _audio_cache is None:
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        cache_dir = Path(os.getenv('NARRATION_CACHE_DIR', '/tmp/spooky-rss/narration'))
        max_size_mb = int(os.getenv('NARRATION_CACHE_MAX_SIZE_MB', '500'))
        ttl_days = int(os.getenv('NARRATION_CACHE_TTL_DAYS', '7'))
        
        _audio_cache = AudioCacheManager(
            cache_dir=cache_dir,
            max_size_mb=max_size_mb,
            ttl_days=ttl_days
        )
        
        logger.info(f"Initialized AudioCacheManager at {cache_dir}")
    
    return _audio_cache


@router.post("/generate", response_model=NarrationGenerateResponse)
async def generate_narration(
    request: NarrationGenerateRequest,
    background_tasks: BackgroundTasks,
    voice_service: VoiceNarrationService = Depends(get_voice_service),
    queue_manager: GenerationQueueManager = Depends(get_queue_manager)
):
    """
    Generate voice narration for a spooky variant.
    
    This endpoint accepts a narration request and queues it for processing.
    Returns a request_id that can be used to poll for status.
    
    Args:
        request: Narration generation request with variant_id, voice_style, intensity, etc.
        background_tasks: FastAPI background tasks
        voice_service: Voice narration service instance
        queue_manager: Generation queue manager instance
        
    Returns:
        Response with request_id for status polling
        
    Raises:
        HTTPException: If request validation fails or service is unavailable
    """
    try:
        logger.info(
            f"🎙️ Received narration request: variant_id={request.variant_id}, "
            f"voice_style={request.voice_style.value}, intensity={request.intensity_level}"
        )
        
        # Validate content is provided
        if not request.content:
            raise HTTPException(
                status_code=400,
                detail="Content is required for narration generation"
            )
        
        # Map priority string to Priority enum
        priority_map = {
            "high": Priority.HIGH,
            "normal": Priority.NORMAL,
            "low": Priority.LOW
        }
        priority = priority_map.get(request.priority.lower(), Priority.NORMAL)
        
        # Convert VoiceStyleEnum to VoiceStyle
        voice_style = VoiceStyle(request.voice_style.value)
        
        # Create service narration request
        service_request = ServiceNarrationRequest(
            content=request.content,
            voice_style=voice_style,
            intensity_level=request.intensity_level,
            variant_id=request.variant_id
        )
        
        # Define generation callback
        async def generation_callback(req):
            return await voice_service.generate_narration(req)
        
        # Enqueue the request
        request_id = await queue_manager.enqueue(
            request=service_request,
            priority=priority,
            generation_callback=generation_callback
        )
        
        # Get queue position
        queue_position = queue_manager.get_queue_position(request_id)
        
        # Estimate time (rough estimate: 10 seconds per request + queue wait)
        estimated_time = 10 + (queue_position * 10) if queue_position >= 0 else 10
        
        logger.info(
            f"✅ Enqueued narration request: request_id={request_id}, "
            f"queue_position={queue_position}, estimated_time={estimated_time}s"
        )
        
        return NarrationGenerateResponse(
            request_id=request_id,
            status=GenerationStatus.QUEUED,
            estimated_time=estimated_time,
            queue_position=queue_position if queue_position >= 0 else None
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"💀 Error generating narration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate narration: {str(e)}"
        )


@router.get("/status/{request_id}", response_model=NarrationStatusResponse)
async def get_narration_status(
    request_id: str,
    queue_manager: GenerationQueueManager = Depends(get_queue_manager)
):
    """
    Get generation status and progress for a narration request.
    
    Args:
        request_id: ID of the narration request
        queue_manager: Generation queue manager instance
        
    Returns:
        Status response with progress, audio_url (if completed), and error info
        
    Raises:
        HTTPException: If request_id is not found
    """
    try:
        status_info = queue_manager.get_status(request_id)
        
        if status_info.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Request {request_id} not found"
            )
        
        # Map internal status to GenerationStatus enum
        status_map = {
            "queued": GenerationStatus.QUEUED,
            "generating": GenerationStatus.GENERATING,
            "completed": GenerationStatus.COMPLETED,
            "failed": GenerationStatus.FAILED,
            "cancelled": GenerationStatus.CANCELLED
        }
        
        status = status_map.get(status_info["status"], GenerationStatus.QUEUED)
        progress = status_info.get("progress", 0)
        
        # Extract result if completed
        audio_url = None
        duration = None
        if status == GenerationStatus.COMPLETED and status_info.get("result"):
            result = status_info["result"]
            audio_url = result.audio_url
            duration = result.duration
        
        response = NarrationStatusResponse(
            request_id=request_id,
            status=status,
            progress=progress,
            audio_url=audio_url,
            duration=duration,
            error=status_info.get("error"),
            created_at=status_info["created_at"],
            completed_at=status_info.get("completed_at")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error getting narration status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get narration status: {str(e)}"
        )


@router.get("/audio/{narration_id}")
async def get_audio_file(
    narration_id: str,
    audio_cache: AudioCacheManager = Depends(get_audio_cache)
):
    """
    Serve generated audio file.
    
    This endpoint serves the MP3 audio file with appropriate headers for
    streaming and download.
    
    Args:
        narration_id: ID of the narration (cache key)
        audio_cache: Audio cache manager instance
        
    Returns:
        FileResponse with MP3 audio file
        
    Raises:
        HTTPException: If audio file is not found
    """
    try:
        # Get audio file from cache
        audio_path = await audio_cache.get(narration_id)
        
        if not audio_path or not audio_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Audio file not found for narration {narration_id}"
            )
        
        logger.info(f"🎵 Serving audio file: {audio_path}")
        
        # Return file with appropriate headers
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'inline; filename="narration-{narration_id}.mp3"',
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=604800"  # Cache for 7 days
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error serving audio file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to serve audio file: {str(e)}"
        )


@router.get("/voices", response_model=List[VoiceStyleInfo])
async def list_voice_styles():
    """
    List available voice styles with preview samples.
    
    Returns information about all available horror voice styles including
    descriptions, preview URLs, and recommended intensity levels.
    
    Returns:
        List of voice style information objects
    """
    try:
        voice_styles = []
        
        for voice_style, config in VOICE_STYLE_CONFIGS.items():
            # Create voice style info
            voice_info = VoiceStyleInfo(
                id=voice_style.value,
                name=config["name"],
                description=config["description"],
                preview_url=config.get("preview_url", f"/api/narration/preview/{voice_style.value}"),
                icon=config.get("icon", "🎭"),
                recommended_intensity=config.get("recommended_intensity", 3)
            )
            voice_styles.append(voice_info)
        
        logger.info(f"📋 Returning {len(voice_styles)} voice styles")
        
        return voice_styles
        
    except Exception as e:
        logger.error(f"💀 Error listing voice styles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list voice styles: {str(e)}"
        )


@router.delete("/cancel/{request_id}")
async def cancel_generation(
    request_id: str,
    queue_manager: GenerationQueueManager = Depends(get_queue_manager)
):
    """
    Cancel a queued or in-progress generation request.
    
    Args:
        request_id: ID of the request to cancel
        queue_manager: Generation queue manager instance
        
    Returns:
        Cancellation confirmation
        
    Raises:
        HTTPException: If request is not found or already completed
    """
    try:
        # Check if request exists
        status_info = queue_manager.get_status(request_id)
        
        if status_info.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Request {request_id} not found"
            )
        
        # Check if request can be cancelled
        current_status = status_info["status"]
        if current_status in ["completed", "failed", "cancelled"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel request in {current_status} state"
            )
        
        # Cancel the request
        await queue_manager.cancel_request(request_id)
        
        logger.info(f"🚫 Cancelled narration request: {request_id}")
        
        return {
            "success": True,
            "message": f"Request {request_id} has been cancelled",
            "request_id": request_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error cancelling request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel request: {str(e)}"
        )


@router.get("/cleanup/stats")
async def get_cleanup_stats():
    """
    Get statistics about the cleanup service.
    
    Returns information about cache size, request counts, and cleanup status.
    
    Returns:
        Dictionary containing cleanup statistics
        
    Raises:
        HTTPException: If cleanup service is not available
    """
    try:
        from backend.api.main import app
        
        if not hasattr(app.state, 'cleanup_service') or not app.state.cleanup_service:
            raise HTTPException(
                status_code=503,
                detail="Cleanup service is not available"
            )
        
        stats = await app.state.cleanup_service.get_cleanup_stats()
        
        logger.info("📊 Retrieved cleanup statistics")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error getting cleanup stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cleanup stats: {str(e)}"
        )


@router.post("/cleanup/run")
async def run_cleanup_now():
    """
    Manually trigger cleanup tasks immediately.
    
    This endpoint allows administrators to run cleanup tasks on-demand
    instead of waiting for the scheduled interval.
    
    Returns:
        Confirmation of cleanup execution
        
    Raises:
        HTTPException: If cleanup service is not available or cleanup fails
    """
    try:
        from backend.api.main import app
        
        if not hasattr(app.state, 'cleanup_service') or not app.state.cleanup_service:
            raise HTTPException(
                status_code=503,
                detail="Cleanup service is not available"
            )
        
        logger.info("🧹 Manually triggering cleanup tasks")
        
        await app.state.cleanup_service.run_cleanup()
        
        # Get updated stats after cleanup
        stats = await app.state.cleanup_service.get_cleanup_stats()
        
        return {
            "success": True,
            "message": "Cleanup tasks completed successfully",
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error running cleanup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run cleanup: {str(e)}"
        )
