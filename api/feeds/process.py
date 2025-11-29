"""
Feed processing serverless function for Vercel deployment.
Transforms RSS feeds into spooky horror stories using OpenRouter AI.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import uuid
import asyncio
import feedparser
from datetime import datetime
import aiohttp
import logging
import sys

# Add api directory to path for imports
api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

try:
    from variant_store import store_variant
except ImportError:
    # Fallback if variant_store not available
    def store_variant(variant_id, variant_data):
        pass  # No-op if storage not available

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_horror(title: str, content: str, intensity: int, themes: list = None) -> dict:
    """Generate mock horror content for testing without API"""
    import random
    
    horror_prefixes = [
        "🕷️ The Cursed Tale of",
        "👻 The Haunting of", 
        "🌙 The Dark Mystery of",
        "💀 The Nightmare of",
        "🔮 The Supernatural Case of"
    ]
    
    horror_templates = [
        "Ancient forces stir in the shadows as {content}. Witnesses report ghostly apparitions and unexplained phenomena surrounding these events. The boundary between our world and the spirit realm grows dangerously thin.",
        "Dark omens foretell doom as {content}. Supernatural entities have been sighted, their malevolent presence felt by all who dare approach. Reality itself seems to bend under their otherworldly influence.",
        "A curse awakens as {content}. Those involved speak of eerie sensations and spectral warnings. The veil between life and death has been torn, allowing ancient horrors to seep through."
    ]
    
    themes_list = themes or ["supernatural forces", "dark omens", "ghostly apparitions"]
    
    explanations = [
        f"I sense {themes_list[0]} at work here... The veil between worlds grows thin.",
        f"Dark forces whisper of {themes_list[0]}. Something ancient stirs in the shadows.",
        f"The spirits speak of {themes_list[0]}. This is no mere coincidence.",
        f"An otherworldly presence manifests through {themes_list[0]}. Beware what lurks beyond.",
        f"The supernatural realm bleeds into ours, bringing {themes_list[0]} with it."
    ]
    
    return {
        "title": f"{random.choice(horror_prefixes)} {title[:50]}",
        "content": random.choice(horror_templates).format(content=content[:100]),
        "themes": themes_list[:3],
        "explanation": random.choice(explanations)
    }


async def fetch_rss_feed(url: str, timeout: int = 4) -> dict:
    """Fetch and parse a single RSS feed"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:3]:  # Limit to 3 articles
                        articles.append({
                            "title": entry.get("title", "Unknown"),
                            "summary": entry.get("summary", entry.get("description", "")),
                            "link": entry.get("link", ""),
                            "published": entry.get("published", datetime.now().isoformat())
                        })
                    
                    return {
                        "success": True,
                        "url": url,
                        "articles": articles,
                        "feed_title": feed.feed.get("title", "Unknown Feed")
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "error": f"HTTP {resp.status}"
                    }
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }


async def call_openrouter_api(title: str, content: str, intensity: int, themes: list = None) -> dict:
    """Call OpenRouter API to transform content into horror story"""
    
    # Check if mock mode is enabled
    use_mock = os.getenv("USE_MOCK_API", "false").lower() == "true"
    if use_mock:
        logger.info("Using MOCK API mode for testing")
        return generate_mock_horror(title, content, intensity, themes)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable is missing")
        raise ValueError("Server configuration error: OPENROUTER_API_KEY not set")
    
    # Build the horror prompt
    theme_str = ", ".join(themes) if themes else "supernatural horror"
    intensity_desc = ["gentle", "subtle", "moderate", "intense", "extreme"][min(intensity - 1, 4)]
    
    prompt = f"""Transform this news article into a {intensity_desc} {theme_str} story.
    
Original Title: {title}
Original Content: {content}

Create a spooky variant with:
1. A haunting title (include horror emoji like 👻🕷️💀🌙)
2. A twisted, supernatural version of the story (2-3 sentences)
3. Maintain the original facts but frame them as horror/supernatural
4. An immersive explanation from a narrator's perspective (not meta-commentary)

Return ONLY valid JSON with these exact keys:
{{
  "title": "horror title with emoji",
  "content": "the haunted story",
  "themes": ["theme1", "theme2"],
  "explanation": "A chilling first-person or narrator perspective on what dark forces are at work here..."
}}

The explanation should be immersive horror narration, NOT analysis of the transformation.
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:5173"),
        "X-Title": "News Necromancer"
    }
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300
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
                    response_text = data["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        horror_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        # If response isn't valid JSON, extract what we can
                        horror_data = {
                            "title": f"🕷️ {title}",
                            "content": response_text,
                            "themes": themes or ["supernatural"],
                            "explanation": "Transformed by AI"
                        }
                    
                    return horror_data
                else:
                    error_text = await resp.text()
                    logger.error(f"OpenRouter API error: {resp.status} - {error_text}")
                    raise ValueError(f"OpenRouter API error: {resp.status}")
    except asyncio.TimeoutError:
        raise ValueError("OpenRouter API request timed out")
    except Exception as e:
        logger.error(f"Error calling OpenRouter: {str(e)}")
        raise


async def process_feeds_async(request_data: dict) -> dict:
    """Process RSS feeds and generate spooky horror variants"""
    urls = request_data.get("urls", [])
    variant_count = request_data.get("variant_count", 1)
    intensity = request_data.get("intensity", 3)
    user_preferences = request_data.get("user_preferences", {})
    
    if not urls:
        raise ValueError("At least one RSS URL is required")
    
    logger.info(f"Processing {len(urls)} feeds with {variant_count} variants each")
    
    # Fetch all feeds concurrently
    feed_tasks = [fetch_rss_feed(url) for url in urls]
    feed_results = await asyncio.gather(*feed_tasks, return_exceptions=True)
    
    # Process results and generate variants
    processing_id = str(uuid.uuid4())
    variants = []
    
    # Prepare AI tasks
    ai_tasks = []
    
    for feed_result in feed_results:
        if isinstance(feed_result, Exception):
            logger.error(f"Feed fetch failed: {feed_result}")
            continue
        
        if not feed_result.get("success"):
            logger.warning(f"Failed to fetch {feed_result.get('url')}: {feed_result.get('error')}")
            continue
        
        articles = feed_result.get("articles", [])
        
        # Limit total processing to avoid timeouts
        limit = 2 if len(urls) > 1 else 3
        
        for article in articles[:limit]:
            # Generate horror variants for each article
            for _ in range(variant_count):
                themes = user_preferences.get("preferred_horror_types") if user_preferences else None
                ai_tasks.append({
                    "article": article,
                    "task": call_openrouter_api(
                        title=article.get("title", "Unknown"),
                        content=article.get("summary", ""),
                        intensity=intensity,
                        themes=themes
                    )
                })

    # Execute AI tasks concurrently
    if not ai_tasks:
        raise ValueError("No articles found in provided feeds")
         
    ai_results = await asyncio.gather(*[t["task"] for t in ai_tasks], return_exceptions=True)
    
    for i, result in enumerate(ai_results):
        article = ai_tasks[i]["article"]
        
        if isinstance(result, Exception):
            logger.error(f"AI transformation failed for '{article.get('title')}': {result}")
            continue
            
        try:
            variant_id = str(uuid.uuid4())
            
            # Ensure horror_themes is always an array
            themes = result.get("themes", ["supernatural"])
            if isinstance(themes, str):
                themes = [themes]
            elif not isinstance(themes, list):
                themes = ["supernatural"]
            
            variant = {
                "variant_id": variant_id,
                "original_item": {
                    "title": article.get("title", "Unknown"),
                    "summary": article.get("summary", ""),
                    "link": article.get("link", ""),
                    "published": article.get("published", datetime.now().isoformat())
                },
                "haunted_title": result.get("title", "🕷️ The Cursed Tale"),
                "haunted_summary": result.get("content", ""),
                "horror_themes": themes,
                "supernatural_explanation": result.get("explanation", ""),
                "personalization_applied": bool(user_preferences),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            # Store variant for later retrieval (story continuation)
            store_variant(variant_id, variant)
            
            variants.append(variant)
        except Exception as e:
            logger.error(f"Error creating variant object: {e}")

    if not variants:
        raise ValueError("No horror variants could be generated. Check logs for API errors.")
    
    response = {
        "success": True,
        "message": f"Successfully processed {len(urls)} feeds",
        "processing_id": processing_id,
        "total_feeds": len(urls),
        "total_variants": len(variants),
        "processing_time": 0.0,
        "variants": variants
    }
    
    logger.info(f"Generated {len(variants)} variants from {len(urls)} feeds")
    return response


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
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
            "service": "feed-processing",
            "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY"))
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
    
    def do_POST(self):
        """Process feeds endpoint"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))
            
            # Process feeds asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(process_feeds_async(request_data))
            loop.close()
            
            # Send success response
            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except ValueError as e:
            # Client error (400)
            self._set_headers(400)
            error_response = {
                "success": False,
                "error": str(e),
                "detail": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
        except Exception as e:
            # Server error (500)
            logger.error(f"Error processing feeds: {str(e)}", exc_info=True)
            self._set_headers(500)
            error_response = {
                "success": False,
                "error": "Internal server error",
                "detail": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
