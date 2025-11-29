"""
Voice styles listing serverless function for Vercel deployment.
"""

from http.server import BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice styles configuration - matches backend/narration/voice_configs.py
VOICE_STYLES = [
    {
        "id": "ghostly_whisper",
        "name": "Ghostly Whisper",
        "description": "A haunting, ethereal whisper that sends chills down your spine",
        "preview_url": "/api/narration/preview/ghostly_whisper",
        "icon": "👻",
        "recommended_intensity": 3
    },
    {
        "id": "demonic_growl",
        "name": "Demonic Growl",
        "description": "A deep, menacing growl from the depths of darkness",
        "preview_url": "/api/narration/preview/demonic_growl",
        "icon": "😈",
        "recommended_intensity": 4
    },
    {
        "id": "eerie_narrator",
        "name": "Eerie Narrator",
        "description": "A calm yet unsettling voice that tells tales of terror",
        "preview_url": "/api/narration/preview/eerie_narrator",
        "icon": "🌙",
        "recommended_intensity": 3
    },
    {
        "id": "possessed_child",
        "name": "Possessed Child",
        "description": "An innocent voice twisted by malevolent forces",
        "preview_url": "/api/narration/preview/possessed_child",
        "icon": "👧",
        "recommended_intensity": 5
    },
    {
        "id": "ancient_entity",
        "name": "Ancient Entity",
        "description": "A timeless, otherworldly voice from beyond comprehension (Attenborough-like)",
        "preview_url": "/api/narration/preview/ancient_entity",
        "icon": "🔮",
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
