"""
Pydantic models for AI voice narration feature
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class VoiceStyleEnum(str, Enum):
    """Available horror voice styles for narration"""
    GHOSTLY_WHISPER = "ghostly_whisper"
    DEMONIC_GROWL = "demonic_growl"
    EERIE_NARRATOR = "eerie_narrator"
    POSSESSED_CHILD = "possessed_child"
    ANCIENT_ENTITY = "ancient_entity"


class GenerationStatus(str, Enum):
    """Status of narration generation request"""
    QUEUED = "queued"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NarrationGenerateRequest(BaseModel):
    """Request model for generating voice narration"""
    variant_id: str = Field(..., description="ID of the spooky variant to narrate")
    voice_style: VoiceStyleEnum = Field(..., description="Horror voice style to use")
    intensity_level: int = Field(..., ge=1, le=5, description="Horror intensity level (1-5)")
    priority: str = Field(default="normal", description="Request priority (high, normal, low)")
    content: Optional[str] = Field(
        None, 
        description="Text content to narrate"
    )
    
    @field_validator('content')
    @classmethod
    def validate_content_length(cls, v: Optional[str]) -> Optional[str]:
        """Validate content length does not exceed configured maximum"""
        if v is not None:
            from backend.config.settings import get_settings
            settings = get_settings()
            max_length = settings.narration_max_content_length
            
            if len(v) > max_length:
                raise ValueError(f"Content length must not exceed {max_length} characters")
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority is one of the allowed values"""
        allowed_priorities = ["high", "normal", "low"]
        if v.lower() not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return v.lower()


class NarrationGenerateResponse(BaseModel):
    """Response model for narration generation request"""
    request_id: str = Field(..., description="Unique identifier for the generation request")
    status: GenerationStatus = Field(..., description="Current status of the request")
    estimated_time: Optional[int] = Field(
        None, 
        description="Estimated time to completion in seconds"
    )
    queue_position: Optional[int] = Field(
        None, 
        description="Position in the generation queue"
    )


class NarrationStatusResponse(BaseModel):
    """Response model for narration status check"""
    request_id: str = Field(..., description="Unique identifier for the generation request")
    status: GenerationStatus = Field(..., description="Current status of the request")
    progress: int = Field(..., ge=0, le=100, description="Generation progress percentage (0-100)")
    audio_url: Optional[str] = Field(None, description="URL to the generated audio file")
    duration: Optional[float] = Field(None, description="Duration of the audio in seconds")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    created_at: datetime = Field(..., description="Timestamp when request was created")
    completed_at: Optional[datetime] = Field(
        None, 
        description="Timestamp when generation completed"
    )


class VoiceStyleInfo(BaseModel):
    """Information about an available voice style"""
    id: str = Field(..., description="Unique identifier for the voice style")
    name: str = Field(..., description="Human-readable name of the voice style")
    description: str = Field(..., description="Description of the voice style characteristics")
    preview_url: str = Field(..., description="URL to a preview audio sample")
    icon: str = Field(..., description="Icon identifier for the voice style")
    recommended_intensity: int = Field(
        ..., 
        ge=1, 
        le=5, 
        description="Recommended intensity level for this voice style"
    )
