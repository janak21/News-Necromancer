"""
FastAPI to ASGI adapter for Vercel serverless functions using Mangum.

This module provides the adapter that allows FastAPI to run as a Vercel
serverless function. Mangum translates between AWS Lambda/Vercel's event
format and ASGI.
"""

from mangum import Mangum
from backend.api.main import app

# Create the Mangum handler for Vercel
# This wraps the FastAPI app and makes it compatible with serverless environments
handler = Mangum(app, lifespan="off")

# Export for Vercel
__all__ = ["handler"]
