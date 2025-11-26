"""
Narration status endpoint for Vercel deployment.
Since we generate immediately, this just returns a "not found" response.
"""

from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for narration status"""
    
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
        """
        Status endpoint - returns the cached narration result.
        The path will be /api/narration/status/{request_id}
        """
        # Extract request_id from path
        # Path format: /api/narration/status/REQUEST_ID or just /REQUEST_ID
        path_parts = self.path.strip('/').split('/')
        request_id = path_parts[-1] if path_parts else None
        
        if not request_id:
            self._set_headers(400)
            response = {
                "error": "Missing request_id",
                "detail": "Request ID is required in the URL path"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # Try to get from the generate function's cache
        # Note: This only works if the status check happens in the same function instance
        # For serverless, we'll return a "completed" status immediately
        from datetime import datetime
        
        # Since serverless functions are stateless, we can't actually cache between requests
        # Return a generic "not found" which tells frontend the generation is done
        # but audio was already provided in the initial response
        self._set_headers(404)
        response = {
            "error": "Request not found",
            "detail": f"Request {request_id} not found. Audio should have been provided in the generate response.",
            "request_id": request_id
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
