"""
RSS Feed validation utilities
"""

import feedparser
from typing import Dict, Any, List
import logging


class FeedValidator:
    """Validates RSS feed format and content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_feed_format(self, feed: feedparser.FeedParserDict) -> bool:
        """
        Validate that a parsed feed has the required structure
        
        Args:
            feed: Parsed feedparser feed object
            
        Returns:
            True if feed is valid, False otherwise
        """
        try:
            # Check if feed has entries
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                self.logger.warning("Feed contains no entries")
                return False
            
            # Check for feed metadata
            if not hasattr(feed, 'feed'):
                self.logger.warning("Feed missing metadata")
                return False
            
            # Check for bozo errors (malformed XML)
            if hasattr(feed, 'bozo') and feed.bozo:
                if hasattr(feed, 'bozo_exception'):
                    self.logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
                # Don't fail on bozo errors, just warn
            
            # Validate at least one entry has required fields
            first_entry = feed.entries[0]
            if not (hasattr(first_entry, 'title') or hasattr(first_entry, 'summary')):
                self.logger.warning("Feed entries missing required title or summary")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating feed: {str(e)}")
            return False
    
    def validate_feed_url(self, url: str) -> bool:
        """
        Validate that a URL looks like a valid RSS feed URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Common RSS feed patterns
        rss_indicators = [
            'rss', 'feed', 'atom', 'xml',
            '/rss/', '/feed/', '/feeds/',
            '.rss', '.xml', '.atom'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in rss_indicators)
    
    def validate_feed_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean feed items
        
        Args:
            items: List of feed item dictionaries
            
        Returns:
            List of validated and cleaned feed items
        """
        validated_items = []
        
        for item in items:
            try:
                # Ensure required fields exist
                if not item.get('title') and not item.get('summary'):
                    self.logger.warning("Skipping item with no title or summary")
                    continue
                
                # Clean and validate fields
                cleaned_item = {
                    'title': self._clean_text(item.get('title', 'Untitled')),
                    'summary': self._clean_text(item.get('summary', '')),
                    'link': item.get('link', ''),
                    'published': item.get('published', ''),
                    'source': self._clean_text(item.get('source', 'Unknown Source'))
                }
                
                # Add metadata if present
                if 'metadata' in item:
                    cleaned_item['metadata'] = item['metadata']
                
                validated_items.append(cleaned_item)
                
            except Exception as e:
                self.logger.warning(f"Error validating feed item: {str(e)}")
                continue
        
        return validated_items
    
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
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (prevent memory issues)
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        return text