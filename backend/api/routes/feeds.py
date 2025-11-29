"""
Feed processing API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from ...models.data_models import ProcessingResponse, SpookyVariant, UserPreferences, StoryContinuation
from ...fetcher.concurrent_fetcher import ConcurrentFetcher
from ...remixer.spooky_remixer import SpookyRemixer
from ..dependencies import get_fetcher, get_remixer, get_integration_manager
from ..integration import SpookyIntegrationManager

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response models
class FeedProcessingRequest(BaseModel):
    """Request model for feed processing"""
    urls: List[HttpUrl]
    user_preferences: Optional[UserPreferences] = None
    variant_count: int = 2
    intensity: Optional[int] = None  # Override intensity level (1-5)

class FeedProcessingResponse(BaseModel):
    """Response model for feed processing"""
    success: bool
    message: str
    processing_id: str
    total_feeds: int
    total_variants: int
    processing_time: float
    variants: List[dict]  # Will contain SpookyVariant.to_dict() results

# In-memory storage for demo (would use Redis/database in production)
processing_results = {}
continuation_cache = {}  # Cache for story continuations

@router.post("/process", response_model=FeedProcessingResponse)
async def process_feeds(
    request: FeedProcessingRequest,
    background_tasks: BackgroundTasks,
    integration_manager: SpookyIntegrationManager = Depends(get_integration_manager)
):
    """
    Process RSS feeds and generate spooky variants using enhanced integration
    
    Args:
        request: Feed processing request with URLs and preferences
        background_tasks: FastAPI background tasks
        integration_manager: Enhanced integration manager for coordinated processing
        
    Returns:
        Processing response with generated variants
    """
    try:
        logger.info(f"🕷️ Starting enhanced feed processing for {len(request.urls)} feeds")
        
        # Convert HttpUrl objects to strings
        urls = [str(url) for url in request.urls]
        
        # Use enhanced integration manager for coordinated processing
        response = await integration_manager.process_feeds_integrated(
            urls=urls,
            user_preferences=request.user_preferences,
            variant_count=request.variant_count,
            intensity=request.intensity
        )
        
        # Store results for later retrieval (backward compatibility)
        if response.success and response.processing_id:
            processing_results[response.processing_id] = {
                "variants": response.variants,
                "timestamp": datetime.now(),
                "processing_time": response.stats.processing_time if response.stats else 0
            }
        
        # Convert variants to dictionaries for JSON response
        variant_dicts = [variant.to_dict() for variant in response.variants]
        
        # Store variants for story continuation
        from .story_continue import store_variant
        for variant in response.variants:
            variant_dict = variant.to_dict()
            store_variant(variant_dict['variant_id'], variant_dict)
        
        return FeedProcessingResponse(
            success=response.success,
            message=response.message,
            processing_id=response.processing_id or str(uuid.uuid4()),
            total_feeds=len(request.urls),
            total_variants=len(response.variants),
            processing_time=response.stats.processing_time if response.stats else 0,
            variants=variant_dicts
        )
        
    except Exception as e:
        logger.error(f"💀 Error processing feeds: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process feeds: {str(e)}"
        )

@router.get("/variants/{processing_id}")
async def get_spooky_variants(processing_id: str):
    """
    Retrieve spooky variants by processing ID
    
    Args:
        processing_id: Processing ID from previous request
        
    Returns:
        List of spooky variants
    """
    if processing_id not in processing_results:
        raise HTTPException(
            status_code=404,
            detail="Processing ID not found or results expired"
        )
    
    result = processing_results[processing_id]
    variants = result["variants"]
    
    return {
        "success": True,
        "processing_id": processing_id,
        "timestamp": result["timestamp"],
        "processing_time": result["processing_time"],
        "total_variants": len(variants),
        "variants": [variant.to_dict() for variant in variants]
    }

@router.get("/variants/{processing_id}/summary")
async def get_processing_summary(processing_id: str):
    """
    Get a summary of processing results
    
    Args:
        processing_id: Processing ID from previous request
        
    Returns:
        Processing summary with statistics
    """
    if processing_id not in processing_results:
        raise HTTPException(
            status_code=404,
            detail="Processing ID not found or results expired"
        )
    
    result = processing_results[processing_id]
    variants = result["variants"]
    
    # Calculate statistics
    horror_themes = set()
    sources = set()
    
    for variant in variants:
        horror_themes.update(variant.horror_themes)
        sources.add(variant.original_item.source)
    
    return {
        "success": True,
        "processing_id": processing_id,
        "timestamp": result["timestamp"],
        "processing_time": result["processing_time"],
        "statistics": {
            "total_variants": len(variants),
            "unique_sources": len(sources),
            "horror_themes_used": list(horror_themes),
            "sources": list(sources)
        }
    }

# Alias endpoint to match task specification exactly
@router.get("/{feed_id}/variants")
async def get_variants_by_feed_id(feed_id: str):
    """
    Retrieve spooky variants by feed ID (alias for processing ID)
    
    Args:
        feed_id: Feed/Processing ID from previous request
        
    Returns:
        List of spooky variants
    """
    return await get_spooky_variants(feed_id)

@router.delete("/variants/{processing_id}")
async def delete_processing_results(processing_id: str):
    """
    Delete processing results to free memory
    
    Args:
        processing_id: Processing ID to delete
        
    Returns:
        Deletion confirmation
    """
    if processing_id not in processing_results:
        raise HTTPException(
            status_code=404,
            detail="Processing ID not found"
        )
    
    del processing_results[processing_id]
    
    return {
        "success": True,
        "message": f"Processing results for {processing_id} have been deleted"
    }

@router.get("/sessions")
async def get_active_sessions(
    integration_manager: SpookyIntegrationManager = Depends(get_integration_manager)
):
    """
    Get information about all active processing sessions
    
    Returns:
        List of active processing sessions
    """
    try:
        sessions = await integration_manager.get_active_sessions()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "active_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"💀 Error retrieving active sessions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active sessions: {str(e)}"
        )

@router.get("/sessions/{session_id}")
async def get_session_status(
    session_id: str,
    integration_manager: SpookyIntegrationManager = Depends(get_integration_manager)
):
    """
    Get detailed status of a specific processing session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session status and details
    """
    try:
        session_data = await integration_manager.get_session_status(session_id)
        
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        # Convert datetime objects to ISO strings for JSON serialization
        serializable_data = {}
        for key, value in session_data.items():
            if isinstance(value, datetime):
                serializable_data[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                serializable_data[key] = value.to_dict()
            else:
                serializable_data[key] = value
        
        return {
            "success": True,
            "session_id": session_id,
            "session_data": serializable_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error retrieving session status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session status: {str(e)}"
        )

@router.delete("/sessions/{session_id}")
async def cleanup_session(
    session_id: str,
    integration_manager: SpookyIntegrationManager = Depends(get_integration_manager)
):
    """
    Clean up a completed processing session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Cleanup confirmation
    """
    try:
        cleaned = await integration_manager.cleanup_session(session_id)
        
        if not cleaned:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        return {
            "success": True,
            "message": f"Session {session_id} has been cleaned up"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error cleaning up session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clean up session: {str(e)}"
        )

@router.get("/integration/health")
async def get_integration_health(
    integration_manager: SpookyIntegrationManager = Depends(get_integration_manager)
):
    """
    Get health status of the integration layer
    
    Returns:
        Integration health information
    """
    try:
        health_data = integration_manager.get_integration_health()
        
        return {
            "success": True,
            "integration_health": health_data
        }
        
    except Exception as e:
        logger.error(f"💀 Error checking integration health: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check integration health: {str(e)}"
        )


@router.post("/variants/{variant_id}/continue")
async def continue_story(
    variant_id: str,
    continuation_length: Optional[int] = 500,
    remixer: SpookyRemixer = Depends(get_remixer)
):
    """
    Generate a story continuation for a specific variant
    
    Args:
        variant_id: Variant identifier
        continuation_length: Target length in words (300-500)
        remixer: SpookyRemixer instance
        
    Returns:
        StoryContinuation object with extended narrative
    """
    try:
        # Check cache first
        cache_key = f"{variant_id}_{continuation_length}"
        if cache_key in continuation_cache:
            logger.info(f"Returning cached continuation for variant {variant_id}")
            cached_continuation = continuation_cache[cache_key]
            return {
                "success": True,
                "variant_id": variant_id,
                "continuation": cached_continuation.to_dict()
            }
        
        # Find the variant in processing results
        variant = None
        for processing_id, result in processing_results.items():
            for v in result["variants"]:
                if v.variant_id == variant_id:
                    variant = v
                    break
            if variant:
                break
        
        if not variant:
            raise HTTPException(
                status_code=404,
                detail=f"Variant {variant_id} not found"
            )
        
        logger.info(f"🌙 Generating story continuation for variant {variant_id}")
        
        # Generate continuation
        continuation = remixer.continue_story(
            variant=variant,
            continuation_length=continuation_length
        )
        
        # Cache the continuation
        continuation_cache[cache_key] = continuation
        
        logger.info(f"✨ Successfully generated continuation for variant {variant_id}")
        
        return {
            "success": True,
            "variant_id": variant_id,
            "continuation": continuation.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💀 Error generating continuation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate story continuation: {str(e)}"
        )


@router.get("/variants/{variant_id}/continuation")
async def get_cached_continuation(variant_id: str, continuation_length: Optional[int] = 500):
    """
    Retrieve a cached story continuation if available
    
    Args:
        variant_id: Variant identifier
        continuation_length: Target length used for caching
        
    Returns:
        Cached continuation or 404 if not found
    """
    cache_key = f"{variant_id}_{continuation_length}"
    
    if cache_key not in continuation_cache:
        raise HTTPException(
            status_code=404,
            detail="Continuation not found in cache"
        )
    
    continuation = continuation_cache[cache_key]
    
    return {
        "success": True,
        "variant_id": variant_id,
        "continuation": continuation.to_dict(),
        "cached": True
    }


@router.delete("/variants/{variant_id}/continuation")
async def clear_continuation_cache(variant_id: str):
    """
    Clear cached continuations for a specific variant
    
    Args:
        variant_id: Variant identifier
        
    Returns:
        Deletion confirmation
    """
    cleared_count = 0
    keys_to_delete = []
    
    for cache_key in continuation_cache.keys():
        if cache_key.startswith(variant_id):
            keys_to_delete.append(cache_key)
    
    for key in keys_to_delete:
        del continuation_cache[key]
        cleared_count += 1
    
    return {
        "success": True,
        "message": f"Cleared {cleared_count} cached continuations for variant {variant_id}",
        "cleared_count": cleared_count
    }


@router.get("/continuations/stats")
async def get_continuation_stats():
    """
    Get statistics about cached continuations
    
    Returns:
        Continuation cache statistics
    """
    return {
        "success": True,
        "total_cached": len(continuation_cache),
        "cache_keys": list(continuation_cache.keys())
    }
