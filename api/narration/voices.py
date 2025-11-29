"""
Voice styles listing serverless function for Vercel deployment.
"""

from http.server import BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice styles configuration
VOICE_STYLES = [
    {
        "id": "ethereal_whisper",
        "name": "Ethereal Whisper",
        "description": "Soft, ghostly voice that sends chills down your spine",
        "preview_url": "/api/narration/preview/ethereal_whisper",
        "icon": "👻",
        "recommended_intensity": 2
    },
    {
        "id": "gothic_narrator",
        "name": "Gothic Narrator",
        "description": "Dramatic, theatrical voice perfect for dark tales",
        "preview_url": "/api/narration/preview/gothic_narrator",
        "icon": "🦇",
        "recommended_intensity": 3
    },
    {
        "id": "sinister_storyteller",
        "name": "Sinister Storyteller",
        "description": "Deep, ominous voice that speaks of ancient evils",
        "preview_url": "/api/narration/preview/sinister_storyteller",
        "icon": "💀",
        "recommended_intensity": 4
    },
    {
        "id": "haunted_voice",
        "name": "Haunted Voice",
        "description": "Eerie, unsettling voice from beyond the grave",
        "preview_url": "/api/narration/preview/haunted_voice",
        "icon": "🕷️",
        "recommended_intensity": 3
    },
    {
        "id": "cryptic_oracle",
        "name": "Cryptic Oracle",
        "description": "Mysterious voice that reveals dark prophecies",
        "preview_url": "/api/narration/preview/cryptic_oracle",
        "icon": "🔮",
        "recommended_intensity": 3
    },
    {
        "id": "eerie_narrator",
        "name": "Eerie Narrator",
        "description": "Classic horror narrator with haunting delivery",
        "preview_url": "/api/narration/preview/eerie_narrator",
        "icon": "🌙",
        "recommended_intensity": 3
    }
]


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for voice styles"""
    
    def _set_headers(self, status=200, content_type='application/json'):
        """Set response headers"""
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(200)
        return
    
    def do_GET(self):
        """List available voice styles"""
        try:
            self._set_headers(200)
            self.wfile.write(json.dumps(VOICE_STYLES).encode('utf-8'))
            logger.info(f"📋 Returned {len(VOICE_STYLES)} voice styles")
        except Exception as e:
            logger.error(f"Error listing voice styles: {str(e)}")
            self._set_headers(500)
            error_response = {
                "error": "Internal server error",
                "detail": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
