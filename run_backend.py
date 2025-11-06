#!/usr/bin/env python3
"""
Startup script for the Spooky RSS System backend
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app, settings
import uvicorn

def main():
    """Main function to start the backend server"""
    print("🎃 Starting Spooky RSS System Backend...")
    print(f"👻 Server will run on http://{settings.host}:{settings.port}")
    print(f"🕷️ API docs available at http://{settings.host}:{settings.port}/api/docs")
    print(f"🔮 Environment: {'development' if settings.is_development else 'production'}")
    
    # Run the server
    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()