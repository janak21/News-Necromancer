"""
Feed processing serverless function for Vercel deployment.

This endpoint handles RSS feed processing and spooky variant generation.
"""

from mangum import Mangum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import logging
import uuid
from datetime import datetime

# Configure logging for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for feed processing
app = FastAPI()


# Request/Response models
class UserPreferences(BaseModel):
    """User preferences for content generation"""
    horror_intensity: int = 3
    preferred_themes: List[str] = []
    content_length: str = "medium"


class FeedProcessingRequest(BaseModel):
    """Request model for feed processing"""
    urls: List[HttpUrl]
    user_preferences: Optional[UserPreferences] = None
    variant_count: int = 2
    intensity: Optional[int] = None


class FeedProcessingResponse(BaseModel):
    """Response model for feed processing"""
    success: bool
    message: str
    processing_id: str
    total_feeds: int
    total_variants: int
    processing_time: float
    variants: List[dict]


@app.post("/api/feeds/process", response_model=FeedProcessingResponse)
async def process_feeds(request: FeedProcessingRequest):
    """
    Process RSS feeds and generate spooky variants.
    
    This is a serverless-optimized version that must complete within
    Vercel's 10-second timeout limit.
    
    Args:
        request: Feed processing request with URLs and preferences
        
    Returns:
        Processing response with generated variants
    """
    try:
        logger.info(f"🕷️ Processing {len(request.urls)} feeds in serverless mode")
        
        # Import backend modules (lazy import for faster cold starts)
        from backend.fetcher.concurrent_fetcher import ConcurrentFetcher
        from backend.remixer.spooky_remixer import SpookyRemixer
        from backend.models.data_models import UserPreferences as BackendUserPreferences
        
        # Convert URLs to strings
        urls = [str(url) for url in request.urls]
        
        # Convert preferences if provided
        backend_prefs = None
        if request.user_preferences:
            backend_prefs = BackendUserPreferences(
                horror_intensity=request.user_preferences.horror_intensity,
                preferred_themes=request.user_preferences.preferred_themes,
                content_length=request.user_preferences.content_length
            )
        
        # Initialize components
        fetcher = ConcurrentFetcher()
        remixer = SpookyRemixer()
        
        # Fetch feeds
        start_time = datetime.now()
        feed_items = await fetcher.fetch_multiple(urls)
        
        # Generate variants
        all_variants = []
        for item in feed_items:
            variants = remixer.generate_variants(
                item=item,
                count=request.variant_count,
                user_preferences=backend_prefs,
                intensity_override=request.intensity
            )
            all_variants.extend(variants)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        processing_id = str(uuid.uuid4())
        
        # Convert variants to dictionaries
        variant_dicts = [v.to_dict() for v in all_variants]
        
        logger.info(f"✅ Processed {len(feed_items)} items into {len(all_variants)} variants in {processing_time:.2f}s")
        
        return FeedProcessingResponse(
            success=True,
            message=f"Successfully processed {len(feed_items)} feed items",
            processing_id=processing_id,
            total_feeds=len(urls),
            total_variants=len(all_variants),
            processing_time=processing_time,
            variants=variant_dicts
        )
        
    except Exception as e:
        logger.error(f"💀 Error processing feeds: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process feeds: {str(e)}"
        )


# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
