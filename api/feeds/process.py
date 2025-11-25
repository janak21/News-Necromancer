"""
Feed processing serverless function for Vercel (simplified version).
"""

from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Process RSS feeds and generate spooky variants"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            request_data = json.loads(body) if body else {}
            
            urls = request_data.get('urls', [])
            variant_count = request_data.get('variant_count', 2)
            
            # For now, return a mock response
            # TODO: Implement actual RSS fetching and processing
            processing_id = str(uuid.uuid4())
            
            # Create mock variants with proper structure matching frontend expectations
            mock_variants = []
            for i in range(min(len(urls) * variant_count, 5)):
                mock_variants.append({
                    "variant_id": str(uuid.uuid4()),
                    "original_item": {
                        "title": f"Original News Story {i+1}",
                        "summary": "This is the original news content before transformation.",
                        "link": urls[0] if urls else "https://example.com",
                        "published": datetime.now().isoformat()
                    },
                    "haunted_title": f"🕷️ The Cursed Tale of Horror {i+1}",
                    "haunted_summary": "A dark and twisted version unfolds... The shadows whisper secrets of terror that lurk in the darkness. Ancient evils stir in the depths, waiting to consume the unwary. This is a mock spooky variant - real processing coming soon!",
                    "horror_themes": ["supernatural", "psychological", "gothic"],
                    "supernatural_explanation": "The spirits of the damned have possessed this story, twisting reality into nightmare.",
                    "personalization_applied": True,
                    "generation_timestamp": datetime.now().isoformat()
                })
            
            response = {
                "success": True,
                "message": f"Processing {len(urls)} feeds (mock response)",
                "processing_id": processing_id,
                "total_feeds": len(urls),
                "total_variants": len(mock_variants),
                "processing_time": 0.1,
                "variants": mock_variants
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "message": "Failed to process feeds"
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        return
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
