"""
Concurrent RSS Fetcher with async processing capabilities
"""

import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time
from dataclasses import dataclass

from ..models.data_models import FeedItem, FeedConfig, ProcessingStats, FetchResult
from .feed_validator import FeedValidator
from .error_handler import FeedErrorHandler
from .feed_cache import FeedCache
from .rate_limiter import RateLimiter, RateLimitConfig


class ConcurrentFetcher:
    """
    Async RSS fetcher supporting concurrent processing of multiple feeds
    Designed to handle 100+ feeds per minute with proper error handling
    """
    
    def __init__(self, 
                 max_concurrent: int = 20, 
                 timeout: int = 15,
                 redis_url: str = "redis://localhost:6379",
                 cache_ttl_minutes: int = 30,
                 enable_caching: bool = True):
        """
        Initialize the concurrent fetcher with caching and rate limiting
        
        Args:
            max_concurrent: Maximum number of concurrent requests (optimized for 100+ feeds/minute)
            timeout: Request timeout in seconds
            redis_url: Redis connection URL for caching
            cache_ttl_minutes: Cache time-to-live in minutes
            enable_caching: Whether to enable Redis caching
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.validator = FeedValidator()
        self.error_handler = FeedErrorHandler()
        self.logger = logging.getLogger(__name__)
        
        # Initialize caching
        self.cache = FeedCache(redis_url, cache_ttl_minutes) if enable_caching else None
        
        # Initialize rate limiting (configured for 100+ feeds/minute)
        rate_config = RateLimitConfig(
            requests_per_minute=120,  # Slightly above target for burst capacity
            burst_size=30,  # Allow bursts
            backoff_factor=2.0,
            max_backoff=60.0
        )
        self.rate_limiter = RateLimiter(rate_config)
        
        # Enhanced session configuration for high-throughput connection pooling
        self.connector_config = {
            'limit': 200,  # Total connection pool size (increased for 100+ feeds/minute)
            'limit_per_host': 50,  # Per-host connection limit (increased)
            'ttl_dns_cache': 300,  # DNS cache TTL
            'use_dns_cache': True,
            'enable_cleanup_closed': True,  # Clean up closed connections
            'keepalive_timeout': 30,  # Keep connections alive for reuse
        }
    
    async def fetch_feeds_concurrent(self, urls: List[str]) -> List[FetchResult]:
        """
        Fetch multiple RSS feeds concurrently with caching, validation and rate limiting
        
        Args:
            urls: List of RSS feed URLs to fetch
            
        Returns:
            List of FetchResult objects with success/failure status
        """
        if not urls:
            return []
        
        # Initialize cache connection if available
        if self.cache:
            await self.cache.connect()
        
        # Validate URLs before processing
        valid_urls = []
        invalid_results = []
        
        for url in urls:
            if self.validator.validate_feed_url(url):
                valid_urls.append(url)
            else:
                self.logger.warning(f"Invalid URL format: {url}")
                invalid_results.append(FetchResult(
                    url=url,
                    success=False,
                    items=[],
                    error="Invalid URL format"
                ))
        
        if not valid_urls:
            return invalid_results
        
        self.logger.info(f"Processing {len(valid_urls)} valid URLs out of {len(urls)} total")
        
        # Check cache for existing results
        cached_results = []
        urls_to_fetch = []
        
        if self.cache:
            for url in valid_urls:
                cached_result = await self.cache.get_cached_feed(url)
                if cached_result:
                    cached_results.append(cached_result)
                    self.logger.debug(f"Using cached result for {url}")
                else:
                    urls_to_fetch.append(url)
        else:
            urls_to_fetch = valid_urls
        
        self.logger.info(f"Cache hits: {len(cached_results)}, URLs to fetch: {len(urls_to_fetch)}")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Fetch remaining URLs if any
        fetch_results = []
        if urls_to_fetch:
            # Create aiohttp session with connection pooling and SSL disabled for RSS feeds
            connector = aiohttp.TCPConnector(ssl=False, **self.connector_config)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Spooky RSS System) Haunted Feed Parser/1.0',
                    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                    'Accept-Encoding': 'gzip, deflate'
                }
            ) as session:
                # Create tasks for URLs that need fetching
                tasks = [
                    self._fetch_single_feed_with_semaphore(session, semaphore, url)
                    for url in urls_to_fetch
                ]
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and handle exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        fetch_results.append(FetchResult(
                            url=urls_to_fetch[i],
                            success=False,
                            items=[],
                            error=str(result)
                        ))
                    else:
                        fetch_results.append(result)
                        
                        # Cache successful results
                        if self.cache and result.success:
                            await self.cache.cache_feed_result(result)
        
        # Combine all results
        all_results = invalid_results + cached_results + fetch_results
        
        # Cleanup cache connection
        if self.cache:
            await self.cache.disconnect()
        
        successful = len([r for r in all_results if r.success])
        failed = len([r for r in all_results if not r.success])
        
        self.logger.info(f"Completed processing: {successful} successful, {failed} failed, {len(cached_results)} from cache")
        
        return all_results
    
    async def _fetch_single_feed_with_semaphore(
        self, 
        session: aiohttp.ClientSession, 
        semaphore: asyncio.Semaphore, 
        url: str
    ) -> FetchResult:
        """
        Fetch a single feed with semaphore and rate limiting
        
        Args:
            session: aiohttp session
            semaphore: Semaphore for concurrency control
            url: RSS feed URL
            
        Returns:
            FetchResult with parsed feed items or error
        """
        async with semaphore:
            # Apply rate limiting
            wait_time = await self.rate_limiter.acquire(url)
            
            try:
                result = await self.fetch_single_feed(session, url)
                
                # Handle success/failure for rate limiter
                if result.success:
                    self.rate_limiter.handle_success(url)
                else:
                    # Don't apply backoff for validation errors, only network errors
                    if result.error and any(err in result.error.lower() for err in ['timeout', 'connection', 'network']):
                        await self.rate_limiter.handle_failure(url, Exception(result.error))
                
                return result
                
            except Exception as e:
                # Handle unexpected exceptions
                await self.rate_limiter.handle_failure(url, e)
                raise
    
    async def fetch_single_feed(
        self, 
        session: aiohttp.ClientSession, 
        url: str,
        max_retries: int = 3
    ) -> FetchResult:
        """
        Fetch and parse a single RSS feed with retry logic
        
        Args:
            session: aiohttp session
            url: RSS feed URL
            max_retries: Maximum number of retry attempts
            
        Returns:
            FetchResult with parsed items or error information
        """
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                # Exponential backoff for retries
                if attempt > 0:
                    await asyncio.sleep(2 ** attempt)
                
                # Fetch the feed content
                async with session.get(url) as response:
                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}"
                        )
                    
                    content = await response.read()
                    
                    # Validate content type if available
                    content_type = response.headers.get('content-type', '').lower()
                    if content_type and not any(ct in content_type for ct in ['xml', 'rss', 'atom', 'application/rss', 'text/xml']):
                        self.logger.warning(f"Unexpected content type for {url}: {content_type}")
                    
                    # Parse with feedparser
                    feed = feedparser.parse(content)
                    
                    # Enhanced feed validation
                    if not self.validator.validate_feed_format(feed):
                        raise ValueError(f"Invalid or empty RSS feed format. Bozo: {getattr(feed, 'bozo', False)}")
                    
                    # Additional validation for feed quality
                    if hasattr(feed, 'bozo') and feed.bozo and hasattr(feed, 'bozo_exception'):
                        self.logger.warning(f"Feed parsing warning for {url}: {feed.bozo_exception}")
                    
                    # Extract feed items with enhanced error handling
                    items = self._extract_feed_items(feed, url)
                    
                    fetch_time = time.time() - start_time
                    
                    return FetchResult(
                        url=url,
                        success=True,
                        items=items,
                        fetch_time=fetch_time
                    )
                    
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                
                if attempt == max_retries - 1:
                    # Final attempt failed, create ghost articles
                    ghost_items = self.error_handler.create_ghost_feed_items(url, str(e))
                    fetch_time = time.time() - start_time
                    
                    return FetchResult(
                        url=url,
                        success=False,
                        items=ghost_items,
                        error=str(e),
                        fetch_time=fetch_time
                    )
        
        # Should never reach here, but just in case
        return FetchResult(
            url=url,
            success=False,
            items=[],
            error="Unknown error occurred"
        )
    
    def _extract_feed_items(self, feed: feedparser.FeedParserDict, source_url: str) -> List[FeedItem]:
        """
        Extract FeedItem objects from parsed feedparser data with enhanced error handling
        
        Args:
            feed: Parsed feedparser feed object
            source_url: Original feed URL
            
        Returns:
            List of FeedItem objects
        """
        items = []
        source_title = feed.feed.get('title', 'Unknown Source')
        
        # Validate feed has entries
        if not hasattr(feed, 'entries') or not feed.entries:
            self.logger.warning(f"No entries found in feed {source_url}")
            return []
        
        # Limit to 3 items per feed for faster processing
        for i, entry in enumerate(feed.entries[:3]):
            try:
                # Validate entry has minimum required content
                if not entry.get('title') and not entry.get('summary') and not entry.get('description'):
                    self.logger.warning(f"Skipping empty entry {i} from {source_url}")
                    continue
                
                # Parse published date with multiple fallbacks
                published = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published = datetime(*entry.published_parsed[:6])
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Invalid published_parsed date in {source_url}: {e}")
                elif hasattr(entry, 'published') and entry.published:
                    # Try to parse string date
                    try:
                        from dateutil.parser import parse
                        published = parse(entry.published)
                    except Exception as e:
                        self.logger.warning(f"Could not parse published date '{entry.published}' from {source_url}: {e}")
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    try:
                        published = datetime(*entry.updated_parsed[:6])
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Invalid updated_parsed date in {source_url}: {e}")
                
                # Extract and clean content
                title = self._clean_text(entry.get('title', 'Untitled'))
                summary = self._clean_text(entry.get('summary', entry.get('description', '')))
                link = entry.get('link', '')
                
                # Validate essential fields
                if not title and not summary:
                    self.logger.warning(f"Skipping entry with no title or summary from {source_url}")
                    continue
                
                # Extract tags safely
                tags = []
                if hasattr(entry, 'tags') and entry.tags:
                    try:
                        tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
                    except Exception as e:
                        self.logger.warning(f"Error extracting tags from {source_url}: {e}")
                
                # Extract content type safely
                content_type = 'text/html'
                if hasattr(entry, 'content') and entry.content:
                    try:
                        content_type = entry.content[0].get('type', 'text/html')
                    except (IndexError, AttributeError, TypeError):
                        pass
                
                # Create FeedItem with comprehensive metadata
                item = FeedItem(
                    title=title,
                    summary=summary,
                    link=link,
                    published=published,
                    source=source_title,
                    metadata={
                        'source_url': source_url,
                        'guid': entry.get('id', entry.get('guid', '')),
                        'author': entry.get('author', ''),
                        'tags': tags,
                        'content_type': content_type,
                        'entry_index': i,
                        'feed_title': source_title,
                        'raw_published': entry.get('published', ''),
                        'updated': entry.get('updated', ''),
                    }
                )
                
                items.append(item)
                
            except Exception as e:
                self.logger.error(f"Error parsing feed item {i} from {source_url}: {str(e)}")
                continue
        
        self.logger.info(f"Successfully extracted {len(items)} items from {source_url}")
        return items
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and sanitize text content
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Remove HTML tags (basic cleaning)
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (prevent memory issues)
        if len(text) > 5000:
            text = text[:5000] + "..."
        
        return text.strip()
    
    def calculate_processing_stats(self, results: List[FetchResult]) -> ProcessingStats:
        """
        Calculate processing statistics from fetch results
        
        Args:
            results: List of FetchResult objects
            
        Returns:
            ProcessingStats with performance metrics
        """
        total_feeds = len(results)
        successful_feeds = sum(1 for r in results if r.success)
        total_items = sum(len(r.items) for r in results)
        total_time = sum(r.fetch_time for r in results)
        error_count = total_feeds - successful_feeds
        
        stats = ProcessingStats(
            feeds_processed=successful_feeds,
            variants_generated=0,  # Will be updated by remixer
            processing_time=total_time,
            error_count=error_count,
            end_time=datetime.now()
        )
        
        return stats
    
    async def get_performance_stats(self) -> Dict[str, any]:
        """
        Get comprehensive performance statistics
        
        Returns:
            Dictionary with performance metrics
        """
        stats = {
            'rate_limiter': self.rate_limiter.get_stats(),
            'cache': await self.cache.get_cache_stats() if self.cache else {"enabled": False},
            'connection_pool': {
                'max_concurrent': self.max_concurrent,
                'timeout': self.timeout,
                'total_pool_size': self.connector_config['limit'],
                'per_host_limit': self.connector_config['limit_per_host']
            }
        }
        
        return stats
    
    async def clear_cache(self):
        """Clear all cached feed data"""
        if self.cache:
            await self.cache.connect()
            await self.cache.clear_all_cache()
            await self.cache.disconnect()
    
    async def invalidate_feed_cache(self, url: str):
        """
        Invalidate cache for specific feed
        
        Args:
            url: Feed URL to invalidate
        """
        if self.cache:
            await self.cache.connect()
            await self.cache.invalidate_cache(url)
            await self.cache.disconnect()
    
    def reset_rate_limiter_stats(self):
        """Reset rate limiter statistics"""
        self.rate_limiter.reset_stats()