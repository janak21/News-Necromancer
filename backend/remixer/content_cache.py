"""
Content caching system for reducing redundant LLM API calls
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Cache entry for storing generated content"""
    content: Dict[str, Any]
    created_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    ttl_hours: int = 24
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        expiry_time = self.created_at + timedelta(hours=self.ttl_hours)
        return datetime.now() > expiry_time
    
    def access(self) -> Dict[str, Any]:
        """Access the cached content and update access statistics"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.content.copy()


class ContentCache:
    """In-memory cache for generated horror content with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl_hours: int = 24):
        """
        Initialize content cache
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl_hours: Default TTL for cache entries in hours
        """
        self.max_size = max_size
        self.default_ttl_hours = default_ttl_hours
        self.cache: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(__name__)
    
    def _generate_cache_key(self, item_title: str, item_summary: str, preferences_hash: str, variant_number: int) -> str:
        """
        Generate a unique cache key for content
        
        Args:
            item_title: Original item title
            item_summary: Original item summary
            preferences_hash: Hash of user preferences
            variant_number: Variant number
            
        Returns:
            Unique cache key
        """
        # Create a hash of the input parameters
        content_hash = hashlib.md5(
            f"{item_title}:{item_summary[:100]}:{preferences_hash}:{variant_number}".encode()
        ).hexdigest()
        
        return f"variant_{content_hash}"
    
    def _hash_preferences(self, preferences: Optional[Dict[str, Any]]) -> str:
        """
        Create a hash of user preferences for cache key generation
        
        Args:
            preferences: User preferences dictionary
            
        Returns:
            Hash string of preferences
        """
        if not preferences:
            return "no_prefs"
        
        # Sort keys to ensure consistent hashing
        sorted_prefs = json.dumps(preferences, sort_keys=True)
        return hashlib.md5(sorted_prefs.encode()).hexdigest()[:8]
    
    def get(self, item_title: str, item_summary: str, preferences: Optional[Dict[str, Any]] = None, variant_number: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get cached content if available and not expired
        
        Args:
            item_title: Original item title
            item_summary: Original item summary
            preferences: User preferences
            variant_number: Variant number
            
        Returns:
            Cached content if available, None otherwise
        """
        try:
            preferences_hash = self._hash_preferences(preferences)
            cache_key = self._generate_cache_key(item_title, item_summary, preferences_hash, variant_number)
            
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                if entry.is_expired():
                    # Remove expired entry
                    del self.cache[cache_key]
                    self.logger.debug(f"Removed expired cache entry: {cache_key}")
                    return None
                
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return entry.access()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def put(self, item_title: str, item_summary: str, content: Dict[str, Any], preferences: Optional[Dict[str, Any]] = None, variant_number: int = 1, ttl_hours: Optional[int] = None) -> None:
        """
        Store content in cache
        
        Args:
            item_title: Original item title
            item_summary: Original item summary
            content: Generated content to cache
            preferences: User preferences
            variant_number: Variant number
            ttl_hours: Time to live in hours (uses default if None)
        """
        try:
            # Check if cache is full and evict LRU entries
            if len(self.cache) >= self.max_size:
                self._evict_lru_entries()
            
            preferences_hash = self._hash_preferences(preferences)
            cache_key = self._generate_cache_key(item_title, item_summary, preferences_hash, variant_number)
            
            ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours
            
            entry = CacheEntry(
                content=content.copy(),
                created_at=datetime.now(),
                ttl_hours=ttl
            )
            
            self.cache[cache_key] = entry
            self.logger.debug(f"Cached content with key: {cache_key}")
            
        except Exception as e:
            self.logger.error(f"Error storing in cache: {str(e)}")
    
    def _evict_lru_entries(self, evict_count: int = None) -> None:
        """
        Evict least recently used entries from cache
        
        Args:
            evict_count: Number of entries to evict (defaults to 10% of max_size)
        """
        if not evict_count:
            evict_count = max(1, self.max_size // 10)
        
        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest entries
        for i in range(min(evict_count, len(sorted_entries))):
            cache_key = sorted_entries[i][0]
            del self.cache[cache_key]
            self.logger.debug(f"Evicted LRU cache entry: {cache_key}")
    
    def clear_expired(self) -> int:
        """
        Clear all expired entries from cache
        
        Returns:
            Number of entries cleared
        """
        expired_keys = []
        
        for cache_key, entry in self.cache.items():
            if entry.is_expired():
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
        
        self.logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self.cache)
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        
        # Calculate average age
        now = datetime.now()
        ages = [(now - entry.created_at).total_seconds() / 3600 for entry in self.cache.values()]
        avg_age_hours = sum(ages) / len(ages) if ages else 0
        
        return {
            "total_entries": total_entries,
            "max_size": self.max_size,
            "utilization": total_entries / self.max_size if self.max_size > 0 else 0,
            "total_accesses": total_accesses,
            "average_age_hours": avg_age_hours,
            "expired_entries": sum(1 for entry in self.cache.values() if entry.is_expired())
        }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern
        
        Args:
            pattern: Pattern to match in cache keys
            
        Returns:
            Number of entries invalidated
        """
        keys_to_remove = []
        
        for cache_key in self.cache.keys():
            if pattern in cache_key:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        self.logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
        return len(keys_to_remove)
    
    def warm_cache(self, popular_items: List[Dict[str, Any]], preferences_list: List[Dict[str, Any]]) -> None:
        """
        Warm the cache with popular items and common preferences
        
        Args:
            popular_items: List of popular feed items
            preferences_list: List of common user preferences
        """
        self.logger.info("Starting cache warming process")
        
        # This would typically be called during system startup
        # to pre-populate cache with commonly requested content
        # Implementation would depend on having access to the SpookyRemixer
        pass