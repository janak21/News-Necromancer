"""
FastAPI middleware configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI):
    """
    Setup all middleware for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    
    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000", 
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174"
        ],  # React dev server (various ports)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        """Log all requests with timing information"""
        start_time = time.time()
        
        # Log request
        logger.info(f"🕷️ {request.method} {request.url.path} - Client: {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"👻 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    # Error handling middleware
    @app.middleware("http")
    async def error_handling(request, call_next):
        """Handle errors gracefully with spooky messaging"""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"💀 Error processing {request.method} {request.url.path}: {str(e)}")
            
            # Re-raise the exception to let FastAPI handle it
            raise e