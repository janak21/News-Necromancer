"""
FastAPI application main module
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

from .routes import feeds, health, preferences, narration
from .middleware import setup_middleware
from backend.config import (
    validate_configuration,
    get_config_summary,
    setup_structured_logging,
    get_structured_logger,
    ConfigError,
)

# Validate configuration on startup
try:
    validation_result = validate_configuration()
    print(f"✅ Configuration validation passed: {validation_result}")
except ConfigError as e:
    print(f"❌ Configuration validation failed: {e}")
    raise

# Setup structured logging
setup_structured_logging()

# Get structured logger for this module
logger = get_structured_logger("backend.api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Handles initialization and cleanup of background services.
    """
    # Startup
    logger.info("Starting News Necromancer API")
    
    # Log configuration summary (with secrets redacted)
    config_summary = get_config_summary()
    logger.info("Configuration loaded", **config_summary)
    
    # Initialize and start cleanup service
    from backend.narration.cleanup import NarrationCleanupService
    from backend.api.routes.narration import get_audio_cache, get_queue_manager
    
    try:
        cache_manager = get_audio_cache()
        queue_manager = get_queue_manager()
        
        cleanup_service = NarrationCleanupService(
            cache_manager=cache_manager,
            queue_manager=queue_manager,
            cleanup_interval_hours=6,
            abandoned_request_timeout_hours=1
        )
        
        await cleanup_service.start()
        app.state.cleanup_service = cleanup_service
        logger.info("Started narration cleanup service")
        
    except Exception as e:
        logger.warning("Failed to start cleanup service", error=str(e))
        app.state.cleanup_service = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down News Necromancer API")
    
    # Stop cleanup service
    if hasattr(app.state, 'cleanup_service') and app.state.cleanup_service:
        try:
            await app.state.cleanup_service.stop()
            logger.info("Stopped narration cleanup service")
        except Exception as e:
            logger.error("Error stopping cleanup service", error=str(e))
    
    # Shutdown queue manager
    try:
        queue_manager = get_queue_manager()
        await queue_manager.shutdown()
        logger.info("Shutdown queue manager")
    except Exception as e:
        logger.error("Error shutting down queue manager", error=str(e))


# Create FastAPI application with lifespan
app = FastAPI(
    title="News Necromancer API",
    description="Transform RSS feeds into horror-themed content with AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(feeds.router, prefix="/api/feeds", tags=["feeds"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(narration.router, prefix="/api/narration", tags=["narration"])

# Add direct variant endpoint to match task specification
from .routes.feeds import get_spooky_variants

@app.get("/api/variants/{feed_id}")
async def get_variants_direct(feed_id: str):
    """Direct endpoint for retrieving spooky variants by feed ID"""
    return await get_spooky_variants(feed_id)

# Global variables for tracking system state
app.state.start_time = datetime.now()
app.state.request_count = 0
app.state.error_count = 0

@app.get("/")
async def root():
    """Root endpoint with basic system information"""
    return {
        "message": "🎃 Welcome to the News Necromancer API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }

@app.middleware("http")
async def track_requests(request, call_next):
    """Middleware to track request statistics"""
    app.state.request_count += 1
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        app.state.error_count += 1
        raise e