"""
Main entry point for the Spooky RSS System backend
"""

import uvicorn
from backend.api.main import app
from backend.config.logging_config import setup_logging
from backend.config.settings import get_settings

# Setup logging
setup_logging()

# Get settings
settings = get_settings()

if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True
    )