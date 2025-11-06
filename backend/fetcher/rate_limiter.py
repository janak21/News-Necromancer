"""
Rate limiting utilities for RSS feed processing
"""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 100
    burst_size: int = 20
    backoff_factor: float = 2.0
    max_backoff: float = 60.0


class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not available
        """
        async with self._lock:
            now = time.time()
            
            # Add tokens based on time elapsed
            time_passed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + time_passed * self.refill_rate
            )
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> float:
        """
        Wait until tokens are available
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Time waited in seconds
        """
        start_time = time.time()
        
        while not await self.consume(tokens):
            # Calculate wait time
            wait_time = tokens / self.refill_rate
            await asyncio.sleep(min(wait_time, 1.0))  # Max 1 second wait
        
        return time.time() - start_time


class ExponentialBackoff:
    """Exponential backoff for failed requests"""
    
    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, factor: float = 2.0):
        """
        Initialize exponential backoff
        
        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            factor: Multiplication factor for each retry
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.attempt_count = 0
    
    def get_delay(self) -> float:
        """
        Get delay for current attempt
        
        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.factor ** self.attempt_count)
        return min(delay, self.max_delay)
    
    async def wait(self):
        """Wait for the calculated delay"""
        delay = self.get_delay()
        self.attempt_count += 1
        await asyncio.sleep(delay)
    
    def reset(self):
        """Reset attempt count"""
        self.attempt_count = 0


class RateLimiter:
    """Advanced rate limiter with per-host limits and backoff"""
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Global rate limiter
        self.global_bucket = TokenBucket(
            capacity=config.burst_size,
            refill_rate=config.requests_per_minute / 60.0  # Convert to per-second
        )
        
        # Per-host rate limiters
        self.host_buckets: Dict[str, TokenBucket] = {}
        self.host_failures: Dict[str, ExponentialBackoff] = {}
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'rate_limited': 0,
            'backoff_delays': 0,
            'start_time': datetime.now()
        }
    
    def _get_host(self, url: str) -> str:
        """Extract host from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    def _get_host_bucket(self, host: str) -> TokenBucket:
        """Get or create token bucket for host"""
        if host not in self.host_buckets:
            # Per-host limit is 1/4 of global limit
            host_limit = max(1, self.config.requests_per_minute // 4)
            self.host_buckets[host] = TokenBucket(
                capacity=max(5, self.config.burst_size // 4),
                refill_rate=host_limit / 60.0
            )
        return self.host_buckets[host]
    
    def _get_backoff(self, host: str) -> ExponentialBackoff:
        """Get or create exponential backoff for host"""
        if host not in self.host_failures:
            self.host_failures[host] = ExponentialBackoff(
                base_delay=1.0,
                max_delay=self.config.max_backoff,
                factor=self.config.backoff_factor
            )
        return self.host_failures[host]
    
    async def acquire(self, url: str) -> float:
        """
        Acquire permission to make request
        
        Args:
            url: URL being requested
            
        Returns:
            Time waited in seconds
        """
        self.stats['total_requests'] += 1
        host = self._get_host(url)
        
        start_time = time.time()
        
        # Check global rate limit
        if not await self.global_bucket.consume():
            self.stats['rate_limited'] += 1
            self.logger.debug(f"Global rate limit hit, waiting for tokens")
            await self.global_bucket.wait_for_tokens()
        
        # Check per-host rate limit
        host_bucket = self._get_host_bucket(host)
        if not await host_bucket.consume():
            self.stats['rate_limited'] += 1
            self.logger.debug(f"Host rate limit hit for {host}, waiting for tokens")
            await host_bucket.wait_for_tokens()
        
        wait_time = time.time() - start_time
        
        if wait_time > 0:
            self.logger.debug(f"Rate limited for {wait_time:.2f}s before requesting {url}")
        
        return wait_time
    
    async def handle_failure(self, url: str, error: Exception):
        """
        Handle request failure with exponential backoff
        
        Args:
            url: Failed URL
            error: Exception that occurred
        """
        host = self._get_host(url)
        backoff = self._get_backoff(host)
        
        self.stats['backoff_delays'] += 1
        self.logger.warning(f"Request failed for {host}, applying backoff: {error}")
        
        await backoff.wait()
    
    def handle_success(self, url: str):
        """
        Handle successful request (reset backoff)
        
        Args:
            url: Successful URL
        """
        host = self._get_host(url)
        if host in self.host_failures:
            self.host_failures[host].reset()
    
    def get_stats(self) -> Dict[str, any]:
        """Get rate limiting statistics"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'total_requests': self.stats['total_requests'],
            'rate_limited': self.stats['rate_limited'],
            'backoff_delays': self.stats['backoff_delays'],
            'requests_per_minute': (self.stats['total_requests'] / uptime * 60) if uptime > 0 else 0,
            'rate_limit_percentage': (self.stats['rate_limited'] / max(1, self.stats['total_requests'])) * 100,
            'active_hosts': len(self.host_buckets),
            'uptime_seconds': uptime
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_requests': 0,
            'rate_limited': 0,
            'backoff_delays': 0,
            'start_time': datetime.now()
        }