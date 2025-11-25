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
            
            response = {
                "success": True,
                "message": f"Processing {len(urls)} feeds (mock response)",
                "processing_id": processing_id,
                "total_feeds": len(urls),
                "total_variants": len(urls) * variant_count,
                "processing_time": 0.1,
                "variants": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": f"Spooky Story {i+1}",
                        "content": "This is a mock spooky variant. Real processing coming soon!",
                        "intensity": 3
                    }
                    for i in range(min(len(urls) * variant_count, 5))
                ]
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
