"""
Story continuation serverless function for Vercel deployment.
Continues a spooky story using OpenRouter AI.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def continue_story_async(variant_id: str, original_content: str, continuation_length: int = 500) -> dict:
    """Continue a spooky story using OpenRouter AI"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not configured")
        raise ValueError("OpenRouter API key not configured")
    
    logger.info(f"📖 Continuing story for variant: {variant_id}, length: {continuation_length}")
    
    # Build the continuation prompt
    prompt = f"""Continue this horror story with more supernatural and terrifying details.

Original Story:
{original_content}

Continue the nightmare with:
1. Escalate the horror and supernatural elements
2. Add more disturbing details and atmosphere
3. Keep the same tone and style
4. Make it approximately {continuation_length} characters
5. End with a cliffhanger or revelation

Return ONLY the continuation text, no JSON, no formatting.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://news-necromancer.vercel.app"
    }
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": min(continuation_length // 2, 500)  # Rough token estimate
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    continuation_text = data["choices"][0]["message"]["content"].strip()
                    
                    logger.info(f"✅ Generated continuation: {len(continuation_text)} chars")
                    
                    return {
                        "success": True,
                        "variant_id": variant_id,
                        "continuation": {
                            "continued_narrative": continuation_text,
                            "continuation_themes": ["supernatural", "horror", "mystery"],
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                else:
                    error_text = await resp.text()
                    logger.error(f"OpenRouter API error: {resp.status} - {error_text}")
                    raise ValueError(f"OpenRouter API error: {resp.status}")
                    
    except asyncio.TimeoutError:
        raise ValueError("Story continuation timed out")
    except Exception as e:
        logger.error(f"Error continuing story: {str(e)}")
        raise


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for story continuation"""
    
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
    
    def do_POST(self):
        """Continue story endpoint"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Request body is required")
            
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))
            
            # Extract parameters from body
            variant_id = request_data.get('variant_id')
            original_content = request_data.get('content', '')
            continuation_length = request_data.get('continuation_length', 500)
            
            if not variant_id:
                raise ValueError("Variant ID is required")
            
            if not original_content:
                raise ValueError("Original story content is required")
            
            # Continue story asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                continue_story_async(variant_id, original_content, continuation_length)
            )
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
            logger.error(f"Error continuing story: {str(e)}", exc_info=True)
            self._set_headers(500)
            error_response = {
                "success": False,
                "error": "Internal server error",
                "detail": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
