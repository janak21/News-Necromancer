"""
FastAPI Gateway Module
Provides REST API endpoints for the Spooky RSS System
"""

from .main import app
from .routes import feeds, health, preferences
from .middleware import setup_middleware

__all__ = [
    "app",
    "feeds",
    "health", 
    "preferences",
    "setup_middleware"
]