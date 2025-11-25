"""
Data models and interfaces for the Spooky RSS System
"""

from .data_models import (
    FeedItem,
    SpookyVariant,
    UserPreferences,
    ProcessingStats,
    HealthStatus,
    ProcessingResponse,
    StatusResponse
)

from .narration_models import (
    VoiceStyleEnum,
    GenerationStatus,
    NarrationGenerateRequest,
    NarrationGenerateResponse,
    NarrationStatusResponse,
    VoiceStyleInfo
)

__all__ = [
    "FeedItem",
    "SpookyVariant", 
    "UserPreferences",
    "ProcessingStats",
    "HealthStatus",
    "ProcessingResponse",
    "StatusResponse",
    "VoiceStyleEnum",
    "GenerationStatus",
    "NarrationGenerateRequest",
    "NarrationGenerateResponse",
    "NarrationStatusResponse",
    "VoiceStyleInfo"
]