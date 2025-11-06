"""
FastAPI application main module
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from datetime import datetime

from .routes import feeds, health, preferences
from .middleware import setup_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI application
app = FastAPI(
    title="Spooky RSS System API",
    description="Transform RSS feeds into horror-themed content with AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(feeds.router, prefix="/api/feeds", tags=["feeds"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])

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
        "message": "🎃 Welcome to the Spooky RSS System API",
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