"""
Narration generation serverless function for Vercel deployment.
Handles AI voice narration generation using ElevenLabs API.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import logging
import asyncio
from datetime import datetime
from typing import Optional
import aiohttp
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Voice style to ElevenLabs voice ID mapping
# Using pre-made voices that should work with most API keys
VOICE_STYLE_MAP = {
    "ethereal_whisper": "21m00Tcm4TlvDq8ikWAM",  # Rachel - soft, ethereal
    "gothic_narrator": "EXAVITQu4vr4xnSDxMaL",   # Bella - dramatic, gothic
    "sinister_storyteller": "VR6AewLTigWG4xSOukaG", # Arnold - deep, ominous
    "haunted_voice": "pNInz6obpgDQGcFmaJgB",     # Adam - haunting
    "cryptic_oracle": "yoZ06aMxZJJ28mfd3POQ",    # Sam - mysterious
    "eerie_narrator": "pNInz6obpgDQGcFmaJgB"     # Default: Adam (haunting)
}


async def generate_narration_async(request_data: dict) -> dict:
    """Generate voice narration using ElevenLabs API"""
    
    variant_id = request_data.get("variant_id")
    content = request_data.get("content", "")
    voice_style = request_data.get("voice_style", "eerie_narrator")
    intensity_level = request_data.get("intensity_level", 3)
    
    # Get API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.error("ELEVENLABS_API_KEY not configured")
        raise ValueError("ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY in Vercel environment variables.")
    
    # Validate API key format
    if not api_key.startswith("sk_"):
        logger.error(f"Invalid API key format: {api_key[:10]}...")
        raise ValueError("Invalid ElevenLabs API key format. Key should start with 'sk_'")
    
    # Log key info (first/last 4 chars only for security)
    key_preview = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
    logger.info(f"Using ElevenLabs API key: {key_preview}")
    
    # Get voice ID
    voice_id = VOICE_STYLE_MAP.get(voice_style, VOICE_STYLE_MAP["eerie_narrator"])
    
    # Truncate content if too long (ElevenLabs has limits)
    max_length = int(os.getenv("NARRATION_MAX_CONTENT_LENGTH", "5000"))
    if len(content) > max_length:
        content = content[:max_length] + "..."
        logger.warning(f"Content truncated to {max_length} characters")
    
    logger.info(f"🎙️ Generating narration: voice={voice_style}, length={len(content)}")
    
    # ElevenLabs API endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    logger.info(f"Calling ElevenLabs API: {url}")
    
    # Adjust voice settings based on intensity
    # Note: Free tier has limitations on voice settings
    stability = 0.3 + (intensity_level * 0.1)  # 0.4 to 0.8
    similarity_boost = 0.5 + (intensity_level * 0.05)  # 0.55 to 0.75
    
    # Use the free tier model (eleven_turbo_v2 or eleven_turbo_v2_5)
    # Free tier models: eleven_turbo_v2, eleven_turbo_v2_5
    payload = {
        "text": content,
        "model_id": "eleven_turbo_v2_5",  # Free tier compatible model
        "voice_settings": {
            "stability": min(stability, 1.0),
            "similarity_boost": min(similarity_boost, 1.0)
        }
    }
    
    try:
        timeout = int(os.getenv("NARRATION_TIMEOUT", "9"))
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    
                    # Convert to base64 for data URL
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    audio_url = f"data:audio/mpeg;base64,{audio_base64}"
                    
                    # Estimate duration (rough calculation: ~150 words per minute)
                    word_count = len(content.split())
                    duration = (word_count / 150) * 60  # seconds
                    
                    logger.info(f"✅ Generated narration: {len(audio_data)} bytes, ~{duration:.1f}s")
                    
                    # Return in the format expected by frontend
                    return {
                        "request_id": variant_id,
                        "status": "completed",
                        "estimated_time": 0,
                        "queue_position": 0,
                        "audio_url": audio_url,
                        "duration": duration,
                        "progress": 100
                    }
                else:
                    error_text = await resp.text()
                    logger.error(f"ElevenLabs API error: {resp.status} - {error_text}")
                    logger.error(f"Request URL: {url}")
                    logger.error(f"Voice ID: {voice_id}")
                    
                    # Check for specific errors
                    if resp.status == 401:
                        raise ValueError(f"Invalid ElevenLabs API key. Status: {resp.status}, Response: {error_text[:200]}")
                    elif resp.status == 429:
                        raise ValueError("Rate limit exceeded. Please try again later.")
                    elif resp.status == 404:
                        raise ValueError(f"Voice ID not found: {voice_id}. Please check voice configuration.")
                    else:
                        raise ValueError(f"ElevenLabs API error: {resp.status} - {error_text[:200]}")
                        
    except asyncio.TimeoutError:
        logger.error("Narration generation timed out")
        raise ValueError("Narration generation timed out. Try with shorter content.")
    except Exception as e:
        logger.error(f"Error generating narration: {str(e)}")
        raise


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for narration generation"""
    
    def _set_headers(self, status=200, content_type='application/json'):
        """Set response headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(200)
        return
    
    def do_GET(self):
        """Health check endpoint"""
        self._set_headers(200)
        response = {
            "status": "ok",
            "service": "narration-generation",
            "elevenlabs_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
            "available_voices": list(VOICE_STYLE_MAP.keys())
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def do_POST(self):
        """Generate narration endpoint"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))
            
            # Validate required fields
            if not request_data.get("content"):
                raise ValueError("Content is required")
            if not request_data.get("variant_id"):
                raise ValueError("Variant ID is required")
            
            # Generate narration asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(generate_narration_async(request_data))
            loop.close()
            
            # Send success response
            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except ValueError as e:
            # Client error (400)
            logger.warning(f"Client error: {str(e)}")
            self._set_headers(400)
            error_response = {
                "success": False,
                "error": str(e),
                "detail": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
        except Exception as e:
            # Server error (500)
            logger.error(f"Error generating narration: {str(e)}", exc_info=True)
            self._set_headers(500)
            error_response = {
                "success": False,
                "error": "Internal server error",
                "detail": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
