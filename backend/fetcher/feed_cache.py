"""
Redis-based caching system for RSS feeds
"""

import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

from ..models.data_models import FeedItem, FetchResult


class FeedCache:
    """Redis-based caching for RSS feed data"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_minutes: int = 30):
        """
        Initialize the feed cache
        
        Args:
            redis_url: Redis connection URL
            ttl_minutes: Time-to-live for cached items in minutes
        """
        self.redis_url = redis_url
        self.ttl_seconds = ttl_minutes * 60
        self.logger = logging.getLogger(__name__)
        self.redis_client = None
        self.enabled = REDIS_AVAILABLE
        
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis not available - caching disabled")
    
    async def connect(self):
        """Establish Redis connection"""
        if not self.enabled:
            return
        
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis_client.ping()
            self.logger.info("Redis cache connected successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_cache_key(self, url: str) -> str:
        """
        Generate cache key for URL
        
        Args:
            url: Feed URL
            
        Returns:
            Cache key string
        """
        # Use hash to create consistent, short keys
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"feed:{url_hash}"
    
    async def get_cached_feed(self, url: str) -> Optional[FetchResult]:
        """
        Get cached feed result
        
        Args:
            url: Feed URL
            
        Returns:
            Cached FetchResult or None if not found/expired
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._get_cache_key(url)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                
                # Reconstruct FetchResult
                items = []
                for item_data in data.get('items', []):
                    # Parse datetime
                    published = datetime.fromisoformat(item_data['published'])
                    
                    item = FeedItem(
                        title=item_data['title'],
                        summary=item_data['summary'],
                        link=item_data['link'],
                        published=published,
                        source=item_data['source'],
                        metadata=item_data.get('metadata', {}),
                        is_ghost_article=item_data.get('is_ghost_article', False),
                        resurrection_failed=item_data.get('resurrection_failed', False)
                    )
                    items.append(item)
                
                result = FetchResult(
                    url=data['url'],
                    success=data['success'],
                    items=items,
                    error=data.get('error'),
                    fetch_time=data.get('fetch_time', 0.0)
                )
                
                self.logger.debug(f"Cache hit for {url}")
                return result
            
        except Exception as e:
            self.logger.warning(f"Error retrieving cached feed for {url}: {e}")
        
        return None
    
    async def cache_feed_result(self, result: FetchResult):
        """
        Cache feed result
        
        Args:
            result: FetchResult to cache
        """
        if not self.enabled or not self.redis_client:
            return
        
        try:
            cache_key = self._get_cache_key(result.url)
            
            # Serialize FetchResult
            items_data = []
            for item in result.items:
                item_data = {
                    'title': item.title,
                    'summary': item.summary,
                    'link': item.link,
                    'published': item.published.isoformat(),
                    'source': item.source,
                    'metadata': item.metadata,
                    'is_ghost_article': item.is_ghost_article,
                    'resurrection_failed': item.resurrection_failed
                }
                items_data.append(item_data)
            
            cache_data = {
                'url': result.url,
                'success': result.success,
                'items': items_data,
                'error': result.error,
                'fetch_time': result.fetch_time,
                'cached_at': datetime.now().isoformat()
            }
            
            # Store with TTL
            await self.redis_client.setex(
                cache_key,
                self.ttl_seconds,
                json.dumps(cache_data)
            )
            
            self.logger.debug(f"Cached feed result for {result.url}")
            
        except Exception as e:
            self.logger.warning(f"Error caching feed result for {result.url}: {e}")
    
    async def invalidate_cache(self, url: str):
        """
        Invalidate cached feed
        
        Args:
            url: Feed URL to invalidate
        """
        if not self.enabled or not self.redis_client:
            return
        
        try:
            cache_key = self._get_cache_key(url)
            await self.redis_client.delete(cache_key)
            self.logger.debug(f"Invalidated cache for {url}")
        except Exception as e:
            self.logger.warning(f"Error invalidating cache for {url}: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False, "error": "Redis not available"}
        
        try:
            info = await self.redis_client.info()
            
            # Get feed-specific keys
            feed_keys = await self.redis_client.keys("feed:*")
            
            return {
                "enabled": True,
                "total_keys": len(feed_keys),
                "memory_usage": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"enabled": False, "error": str(e)}
    
    async def clear_all_cache(self):
        """Clear all cached feeds"""
        if not self.enabled or not self.redis_client:
            return
        
        try:
            feed_keys = await self.redis_client.keys("feed:*")
            if feed_keys:
                await self.redis_client.delete(*feed_keys)
                self.logger.info(f"Cleared {len(feed_keys)} cached feeds")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")