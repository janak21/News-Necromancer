"""
Core data models using dataclasses for TypeScript-style interfaces
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class HorrorType(Enum):
    """Horror type categories for personalization"""
    GOTHIC = "gothic"
    PSYCHOLOGICAL = "psychological"
    COSMIC = "cosmic"
    FOLK = "folk"
    SUPERNATURAL = "supernatural"


class ProcessingStatus(Enum):
    """Processing status for feeds and items"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FeedItem:
    """Individual RSS feed item with metadata"""
    title: str
    summary: str
    link: str
    published: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_ghost_article: bool = False
    resurrection_failed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "title": self.title,
            "summary": self.summary,
            "link": self.link,
            "published": self.published.isoformat() if isinstance(self.published, datetime) else self.published,
            "source": self.source,
            "metadata": self.metadata,
            "is_ghost_article": self.is_ghost_article,
            "resurrection_failed": self.resurrection_failed
        }


@dataclass
class StoryContinuation:
    """Extended narrative content for a spooky variant"""
    variant_id: str
    continued_narrative: str
    continuation_timestamp: datetime = field(default_factory=datetime.now)
    maintains_intensity: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "variant_id": self.variant_id,
            "continued_narrative": self.continued_narrative,
            "continuation_timestamp": self.continuation_timestamp.isoformat(),
            "maintains_intensity": self.maintains_intensity
        }


@dataclass
class SpookyVariant:
    """Horror-themed transformation of original RSS content"""
    original_item: FeedItem
    haunted_title: str
    haunted_summary: str
    horror_themes: List[str]
    supernatural_explanation: str
    personalization_applied: bool = False
    generation_timestamp: datetime = field(default_factory=datetime.now)
    variant_id: Optional[str] = None
    continuation: Optional['StoryContinuation'] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "original_item": self.original_item.to_dict(),
            "haunted_title": self.haunted_title,
            "haunted_summary": self.haunted_summary,
            "horror_themes": self.horror_themes,
            "supernatural_explanation": self.supernatural_explanation,
            "personalization_applied": self.personalization_applied,
            "generation_timestamp": self.generation_timestamp.isoformat(),
            "variant_id": self.variant_id,
            "continuation": self.continuation.to_dict() if self.continuation else None
        }


@dataclass
class UserPreferences:
    """User preferences for content personalization"""
    preferred_horror_types: List[HorrorType] = field(default_factory=list)
    intensity_level: int = 3  # 1-5 scale
    content_filters: List[str] = field(default_factory=list)
    notification_settings: Dict[str, bool] = field(default_factory=dict)
    theme_customizations: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate intensity level and other preferences"""
        if not 1 <= self.intensity_level <= 5:
            raise ValueError("Intensity level must be between 1 and 5")
        
        # Validate horror types
        for horror_type in self.preferred_horror_types:
            if not isinstance(horror_type, HorrorType):
                raise ValueError(f"Invalid horror type: {horror_type}")
        
        # Set default notification settings if empty
        if not self.notification_settings:
            self.notification_settings = {
                "ghost_notifications": True,
                "new_variants": True,
                "processing_complete": True,
                "error_alerts": False
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "preferred_horror_types": [ht.value for ht in self.preferred_horror_types],
            "intensity_level": self.intensity_level,
            "content_filters": self.content_filters,
            "notification_settings": self.notification_settings,
            "theme_customizations": self.theme_customizations,
            "user_id": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create UserPreferences from dictionary"""
        # Convert horror type strings back to enums
        horror_types = []
        for ht_str in data.get("preferred_horror_types", []):
            try:
                horror_types.append(HorrorType(ht_str))
            except ValueError:
                continue  # Skip invalid horror types
        
        return cls(
            preferred_horror_types=horror_types,
            intensity_level=data.get("intensity_level", 3),
            content_filters=data.get("content_filters", []),
            notification_settings=data.get("notification_settings", {}),
            theme_customizations=data.get("theme_customizations", {}),
            user_id=data.get("user_id")
        )
    
    def update_preferences(self, updates: Dict[str, Any]) -> 'UserPreferences':
        """Update preferences with new values"""
        updated_data = self.to_dict()
        updated_data.update(updates)
        return self.from_dict(updated_data)
    
    def is_valid_for_content_filtering(self) -> bool:
        """Check if preferences are valid for content filtering"""
        return (
            1 <= self.intensity_level <= 5 and
            all(isinstance(ht, HorrorType) for ht in self.preferred_horror_types)
        )


@dataclass
class ProcessingStats:
    """Statistics for system performance monitoring"""
    feeds_processed: int = 0
    variants_generated: int = 0
    processing_time: float = 0.0
    success_rate: float = 0.0
    error_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    model_used: Optional[str] = None
    api_provider: Optional[str] = None
    
    def calculate_success_rate(self) -> float:
        """Calculate success rate based on processed vs errors"""
        total = self.feeds_processed + self.error_count
        if total == 0:
            return 0.0
        return (self.feeds_processed / total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "feeds_processed": self.feeds_processed,
            "variants_generated": self.variants_generated,
            "processing_time": self.processing_time,
            "success_rate": self.calculate_success_rate(),
            "error_count": self.error_count,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "model_used": self.model_used,
            "api_provider": self.api_provider
        }


@dataclass
class HealthStatus:
    """System health check status"""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime = field(default_factory=datetime.now)
    components: Dict[str, str] = field(default_factory=dict)  # component -> status
    uptime_seconds: float = 0.0
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "components": self.components,
            "uptime_seconds": self.uptime_seconds,
            "version": self.version
        }


@dataclass
class ProcessingResponse:
    """Response for feed processing requests"""
    success: bool
    message: str
    processing_id: Optional[str] = None
    stats: Optional[ProcessingStats] = None
    variants: List[SpookyVariant] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "message": self.message,
            "processing_id": self.processing_id,
            "stats": self.stats.to_dict() if self.stats else None,
            "variants": [v.to_dict() for v in self.variants]
        }


@dataclass
class StatusResponse:
    """Generic status response"""
    success: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


@dataclass
class FeedConfig:
    """Configuration for RSS feed processing"""
    url: str
    max_items: int = 5
    retry_attempts: int = 3
    timeout_seconds: int = 10
    enabled: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "url": self.url,
            "max_items": self.max_items,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "enabled": self.enabled,
            "custom_headers": self.custom_headers
        }


@dataclass
class FetchResult:
    """Result of a single feed fetch operation"""
    url: str
    success: bool
    items: List[FeedItem]
    error: Optional[str] = None
    fetch_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "url": self.url,
            "success": self.success,
            "items": [item.to_dict() for item in self.items],
            "error": self.error,
            "fetch_time": self.fetch_time
        }