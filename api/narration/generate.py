"""
Narration generation serverless function for Vercel deployment.

This endpoint handles AI voice narration generation with queue management.
"""

from mangum import Mangum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from enum import Enum
import logging
from datetime import datetime

# Configure logging for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for narration generation
app = FastAPI()


# Enums and models
class VoiceStyleEnum(str, Enum):
    """Available voice styles for narration"""
    ETHEREAL_WHISPER = "ethereal_whisper"
    GOTHIC_NARRATOR = "gothic_narrator"
    SINISTER_STORYTELLER = "sinister_storyteller"
    HAUNTED_VOICE = "haunted_voice"
    CRYPTIC_ORACLE = "cryptic_oracle"


class GenerationStatus(str, Enum):
    """Status of narration generation"""
    QUEUED = "queued"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NarrationGenerateRequest(BaseModel):
    """Request model for narration generation"""
    variant_id: str
    content: str
    voice_style: VoiceStyleEnum
    intensity_level: int = 3
    priority: str = "normal"


class NarrationGenerateResponse(BaseModel):
    """Response model for narration generation"""
    request_id: str
    status: GenerationStatus
    estimated_time: int
    queue_position: Optional[int] = None


class NarrationStatusResponse(BaseModel):
    """Response model for narration status"""
    request_id: str
    status: GenerationStatus
    progress: int
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


@app.post("/", response_model=NarrationGenerateResponse)
async def generate_narration(request: NarrationGenerateRequest):
    """
    Generate voice narration for content.
    
    This is a serverless-optimized version that queues requests and
    returns immediately with a request_id for status polling.
    
    Args:
        request: Narration generation request
        
    Returns:
        Response with request_id for status polling
    """
    try:
        logger.info(
            f"🎙️ Narration request: variant={request.variant_id}, "
            f"voice={request.voice_style.value}, intensity={request.intensity_level}"
        )
        
        # Import backend modules (lazy import for faster cold starts)
        from backend.narration.voice_service import VoiceNarrationService, NarrationRequest as ServiceRequest
        from backend.narration.queue_manager import GenerationQueueManager, Priority
        from backend.narration.voice_configs import VoiceStyle
        from backend.config.settings import get_settings
        
        # Get settings
        settings = get_settings()
        
        # Initialize services
        voice_service = VoiceNarrationService(
            api_key=settings.elevenlabs_api_key
        )
        queue_manager = GenerationQueueManager(
            max_concurrent=settings.narration_max_concurrent
        )
        
        # Map priority
        priority_map = {
            "high": Priority.HIGH,
            "normal": Priority.NORMAL,
            "low": Priority.LOW
        }
        priority = priority_map.get(request.priority.lower(), Priority.NORMAL)
        
        # Convert voice style
        voice_style = VoiceStyle(request.voice_style.value)
        
        # Create service request
        service_request = ServiceRequest(
            content=request.content,
            voice_style=voice_style,
            intensity_level=request.intensity_level,
            variant_id=request.variant_id
        )
        
        # Define generation callback
        async def generation_callback(req):
            return await voice_service.generate_narration(req)
        
        # Enqueue request
        request_id = await queue_manager.enqueue(
            request=service_request,
            priority=priority,
            generation_callback=generation_callback
        )
        
        # Get queue position
        queue_position = queue_manager.get_queue_position(request_id)
        estimated_time = 10 + (queue_position * 10) if queue_position >= 0 else 10
        
        logger.info(f"✅ Enqueued: request_id={request_id}, position={queue_position}")
        
        return NarrationGenerateResponse(
            request_id=request_id,
            status=GenerationStatus.QUEUED,
            estimated_time=estimated_time,
            queue_position=queue_position if queue_position >= 0 else None
        )
        
    except Exception as e:
        logger.error(f"💀 Error generating narration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate narration: {str(e)}"
        )


@app.get("/status/{request_id}", response_model=NarrationStatusResponse)
async def get_narration_status(request_id: str):
    """
    Get generation status for a narration request.
    
    Args:
        request_id: ID of the narration request
        
    Returns:
        Status response with progress and audio_url if completed
    """
    try:
        # Import backend modules
        from backend.narration.queue_manager import GenerationQueueManager
        
        # Initialize queue manager
        queue_manager = GenerationQueueManager()
        
        # Get status
        status_info = queue_manager.get_status(request_id)
        
        if status_info.get("status") == "not_found":
            raise HTTPException(
                status_code=404,
                detail=f"Request {request_id} not found"
            )
        
        # Map status
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
        
        return NarrationStatusResponse(
            request_id=request_id,
            status=status,
            progress=progress,
            audio_url=audio_url,
            duration=duration,
            error=status_info.get("error"),
            created_at=status_info["created_at"],
            completed_at=status_info.get("completed_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error getting status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get narration status: {str(e)}"
        )


# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
