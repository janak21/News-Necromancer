"""
Health check serverless function for Vercel deployment.

This endpoint provides a simple health check for monitoring and load balancing.
"""

from mangum import Mangum
from fastapi import FastAPI
from datetime import datetime

# Create a minimal FastAPI app for health checks
app = FastAPI()


@app.get("/api/health")
async def health_check():
    """
    Simple health check endpoint for serverless environment.
    
    Returns basic health status without resource-intensive checks
    that may not work in serverless context.
    """
    return {
        "status": "healthy",
        "service": "spooky-rss-system",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": "serverless"
    }


@app.get("/api/health/simple")
async def simple_health():
    """Ultra-simple health check for load balancers"""
    return {"status": "ok"}


# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
