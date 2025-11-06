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

__all__ = [
    "FeedItem",
    "SpookyVariant", 
    "UserPreferences",
    "ProcessingStats",
    "HealthStatus",
    "ProcessingResponse",
    "StatusResponse"
]