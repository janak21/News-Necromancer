"""
Feed processing serverless function for Vercel deployment.
Transforms RSS feeds into spooky horror stories using OpenRouter AI.
"""

from mangum import Mangum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import os
import uuid
import asyncio
import feedparser
from datetime import datetime
import aiohttp

# Configure logging for serverless
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for feed processing
app = FastAPI()


class UserPreferences(BaseModel):
    preferred_horror_types: Optional[List[str]] = None
    intensity_level: Optional[int] = 3
    content_filters: Optional[List[str]] = None


class FeedProcessRequest(BaseModel):
    urls: List[str]
    variant_count: int = 2
    intensity: Optional[int] = 3
    user_preferences: Optional[UserPreferences] = None


class OriginalItem(BaseModel):
    title: str
    summary: str
    link: str
    published: str


class SpookyVariant(BaseModel):
    variant_id: str
    original_item: OriginalItem
    haunted_title: str
    haunted_summary: str
    horror_themes: List[str]
    supernatural_explanation: str
    personalization_applied: bool
    generation_timestamp: str


async def fetch_rss_feed(url: str, timeout: int = 10) -> dict:
    """Fetch and parse a single RSS feed"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:5]:  # Get first 5 articles
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


async def call_openrouter_api(title: str, content: str, intensity: int, themes: Optional[List[str]]) -> dict:
    """Call OpenRouter API to transform content into horror story"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    # Build the horror prompt
    theme_str = ", ".join(themes) if themes else "supernatural horror"
    intensity_desc = ["gentle", "subtle", "moderate", "intense", "extreme"][min(intensity - 1, 4)]
    
    prompt = f"""Transform this news article into a {intensity_desc} {theme_str} story.
    
Original Title: {title}
Original Content: {content}

Create a spooky variant with:
1. A haunting title (include horror emoji)
2. A twisted, supernatural version of the story
3. Maintain the original facts but frame them as horror/supernatural
4. Keep it 2-3 sentences

Return as JSON with keys: "title", "content", "themes", "explanation"
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ghostrevive.vercel.app"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
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
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response_text = data["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    import json
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


@app.post("/api/feeds/process")
async def process_feeds(request: FeedProcessRequest):
    """
    Process RSS feeds and generate spooky horror variants.
    """
    try:
        if not request.urls:
            raise HTTPException(status_code=400, detail="At least one RSS URL is required")
        
        logger.info(f"Processing {len(request.urls)} feeds with {request.variant_count} variants each")
        
        # Fetch all feeds concurrently
        feed_tasks = [fetch_rss_feed(url) for url in request.urls]
        feed_results = await asyncio.gather(*feed_tasks, return_exceptions=True)
        
        # Process results and generate variants
        processing_id = str(uuid.uuid4())
        variants = []
        
        for feed_result in feed_results:
            if isinstance(feed_result, Exception):
                logger.error(f"Feed fetch failed: {feed_result}")
                continue
            
            if not feed_result.get("success"):
                logger.warning(f"Failed to fetch {feed_result.get('url')}: {feed_result.get('error')}")
                continue
            
            articles = feed_result.get("articles", [])
            
            for article in articles:
                # Generate horror variants for each article
                for _ in range(request.variant_count):
                    try:
                        horror_story = await call_openrouter_api(
                            title=article.get("title", "Unknown"),
                            content=article.get("summary", ""),
                            intensity=request.intensity or 3,
                            themes=request.user_preferences.preferred_horror_types if request.user_preferences else None
                        )
                        
                        variant = SpookyVariant(
                            variant_id=str(uuid.uuid4()),
                            original_item=OriginalItem(
                                title=article.get("title", "Unknown"),
                                summary=article.get("summary", ""),
                                link=article.get("link", ""),
                                published=article.get("published", datetime.now().isoformat())
                            ),
                            haunted_title=horror_story.get("title", "🕷️ The Cursed Tale"),
                            haunted_summary=horror_story.get("content", ""),
                            horror_themes=horror_story.get("themes", ["supernatural"]),
                            supernatural_explanation=horror_story.get("explanation", ""),
                            personalization_applied=bool(request.user_preferences),
                            generation_timestamp=datetime.now().isoformat()
                        )
                        variants.append(variant.dict())
                        
                    except Exception as e:
                        logger.error(f"Failed to transform article '{article.get('title')}': {e}")
                        continue
        
        if not variants:
            logger.warning("No variants were generated successfully")
            raise HTTPException(
                status_code=422,
                detail="No horror variants could be generated. Please check if the RSS URLs are valid and contain articles."
            )
        
        response = {
            "success": True,
            "message": f"Successfully processed {len(request.urls)} feeds",
            "processing_id": processing_id,
            "total_feeds": len(request.urls),
            "total_variants": len(variants),
            "processing_time": 0.0,
            "variants": variants
        }
        
        logger.info(f"Generated {len(variants)} variants from {len(request.urls)} feeds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing feeds: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process feeds: {str(e)}"
        )


# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
