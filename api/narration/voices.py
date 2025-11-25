"""
Voice styles listing serverless function for Vercel deployment.

This endpoint provides information about available voice styles.
"""

from mangum import Mangum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging

# Configure logging for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for voice listing
app = FastAPI()


# Models
class VoiceStyleInfo(BaseModel):
    """Information about a voice style"""
    id: str
    name: str
    description: str
    preview_url: str
    icon: str
    recommended_intensity: int


@app.get("/api/narration/voices", response_model=List[VoiceStyleInfo])
async def list_voice_styles():
    """
    List available voice styles with preview information.
    
    Returns information about all available horror voice styles including
    descriptions, preview URLs, and recommended intensity levels.
    
    Returns:
        List of voice style information objects
    """
    try:
        # Import backend modules (lazy import for faster cold starts)
        from backend.narration.voice_configs import VOICE_STYLE_CONFIGS
        
        voice_styles = []
        
        for voice_style, config in VOICE_STYLE_CONFIGS.items():
            voice_info = VoiceStyleInfo(
                id=voice_style.value,
                name=config["name"],
                description=config["description"],
                preview_url=config.get("preview_url", f"/api/narration/preview/{voice_style.value}"),
                icon=config.get("icon", "🎭"),
                recommended_intensity=config.get("recommended_intensity", 3)
            )
            voice_styles.append(voice_info)
        
        logger.info(f"📋 Returning {len(voice_styles)} voice styles")
        
        return voice_styles
        
    except Exception as e:
        logger.error(f"💀 Error listing voice styles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list voice styles: {str(e)}"
        )


# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
