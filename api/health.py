"""
Health check serverless function for Vercel deployment.
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "service": "GhostRevive",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": "serverless"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
