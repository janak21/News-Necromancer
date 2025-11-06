"""
Main entry point when running backend as a module
"""

from .main import app, settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True
    )