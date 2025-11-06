"""
Error handling utilities for RSS feed processing
"""

import random
from typing import List
from datetime import datetime
import logging

from ..models.data_models import FeedItem


class FeedErrorHandler:
    """Handles errors during RSS feed processing and creates fallback content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Spooky resurrection messages from original implementation
        self.resurrection_messages = [
            "🧟‍♂️ Attempting necromantic resurrection of dead feed...",
            "⚰️ Summoning spirits to revive the silent RSS...",
            "🔮 Channeling dark magic to awaken dormant feed...",
            "👻 Performing séance to contact the departed RSS...",
            "🕯️ Lighting candles for the RSS resurrection ritual...",
            "💀 Invoking ancient curses to raise the dead feed..."
        ]
        
        # Ghost article templates
        self.ghost_templates = [
            {
                "title": "The Haunting of {domain}",
                "summary": "In the digital graveyard where RSS feeds go to die, whispers echo of a once-thriving news source. The spectral remnants of headlines float through cyberspace, forever seeking readers who will never come. Error: {error}",
                "themes": ["digital necromancy", "cyber ghosts", "technological curses"]
            },
            {
                "title": "The Cursed Chronicles of {domain}",
                "summary": "Ancient servers hold dark secrets, and this RSS feed has fallen victim to a malevolent digital curse. The ghostly echoes of news articles past haunt the empty XML, warning of the dangers that lurk in broken connections. Error: {error}",
                "themes": ["server curses", "digital hauntings", "network spirits"]
            },
            {
                "title": "The Phantom Feed of {domain}",
                "summary": "Like a ship lost in the fog, this RSS feed has vanished into the digital mist. Only phantom traces remain, telling tales of articles that once were, now trapped between the realms of the living web and the dead links. Error: {error}",
                "themes": ["phantom feeds", "digital mist", "lost connections"]
            }
        ]
    
    def handle_connection_timeout(self, url: str) -> List[FeedItem]:
        """
        Handle connection timeout errors
        
        Args:
            url: The URL that timed out
            
        Returns:
            List of ghost FeedItems
        """
        self.logger.warning(f"Connection timeout for {url}")
        return self.create_ghost_feed_items(url, "Connection timeout - the digital spirits are silent")
    
    def handle_invalid_feed_format(self, url: str, error: str) -> List[FeedItem]:
        """
        Handle invalid feed format errors
        
        Args:
            url: The URL with invalid format
            error: Error description
            
        Returns:
            List of ghost FeedItems
        """
        self.logger.warning(f"Invalid feed format for {url}: {error}")
        return self.create_ghost_feed_items(url, f"Invalid feed format - {error}")
    
    def handle_rate_limit_exceeded(self, url: str) -> None:
        """
        Handle rate limit exceeded scenarios
        
        Args:
            url: The URL that hit rate limits
        """
        self.logger.warning(f"Rate limit exceeded for {url}")
        # Could implement exponential backoff here
    
    def create_ghost_feed_items(self, url: str, error: str) -> List[FeedItem]:
        """
        Create spooky placeholder articles for dead feeds
        
        Args:
            url: The failed feed URL
            error: Error description
            
        Returns:
            List of ghost FeedItems
        """
        try:
            # Extract domain from URL for personalization
            domain = url.split('//')[1].split('/')[0] if '//' in url else url
        except:
            domain = "Unknown Domain"
        
        # Select a random ghost template
        template = random.choice(self.ghost_templates)
        
        # Create ghost article
        ghost_item = FeedItem(
            title=template["title"].format(domain=domain),
            summary=template["summary"].format(domain=domain, error=error),
            link=url,
            published=datetime.now(),
            source="The Digital Afterlife",
            metadata={
                "source_url": url,
                "error_type": "feed_resurrection_failed",
                "horror_themes": template["themes"],
                "resurrection_attempt": True
            },
            is_ghost_article=True,
            resurrection_failed=True
        )
        
        return [ghost_item]
    
    def get_resurrection_message(self) -> str:
        """
        Get a random spooky resurrection message
        
        Returns:
            Random resurrection message
        """
        return random.choice(self.resurrection_messages)
    
    def handle_feed_errors(self, url: str, error: Exception) -> List[FeedItem]:
        """
        Generic error handler that routes to specific handlers
        
        Args:
            url: The failed feed URL
            error: The exception that occurred
            
        Returns:
            List of ghost FeedItems
        """
        error_str = str(error)
        error_type = type(error).__name__
        
        self.logger.error(f"Feed error for {url}: {error_type} - {error_str}")
        
        # Route to specific handlers based on error type
        if "timeout" in error_str.lower():
            return self.handle_connection_timeout(url)
        elif "invalid" in error_str.lower() or "malformed" in error_str.lower():
            return self.handle_invalid_feed_format(url, error_str)
        else:
            # Generic error handling
            return self.create_ghost_feed_items(url, f"{error_type}: {error_str}")
    
    def log_resurrection_attempt(self, url: str, attempt: int, max_attempts: int):
        """
        Log a resurrection attempt with spooky messaging
        
        Args:
            url: The URL being resurrected
            attempt: Current attempt number
            max_attempts: Maximum attempts
        """
        message = self.get_resurrection_message()
        self.logger.info(f"   {message}")
        self.logger.info(f"   💀 Attempt {attempt}/{max_attempts} for {url}")
    
    def create_circuit_breaker_ghost(self, url: str) -> List[FeedItem]:
        """
        Create ghost items for feeds that have consistently failed (circuit breaker pattern)
        
        Args:
            url: The consistently failing URL
            
        Returns:
            List of ghost FeedItems with circuit breaker theme
        """
        try:
            domain = url.split('//')[1].split('/')[0] if '//' in url else url
        except:
            domain = "Unknown Domain"
        
        ghost_item = FeedItem(
            title=f"The Eternal Silence of {domain}",
            summary=f"This RSS feed has been banished to the digital void after repeated failures. The circuit breaker has sealed its fate, and only ghostly echoes remain. The feed lies dormant, waiting for the curse to be lifted.",
            link=url,
            published=datetime.now(),
            source="The Circuit Breaker Graveyard",
            metadata={
                "source_url": url,
                "error_type": "circuit_breaker_open",
                "horror_themes": ["eternal silence", "digital void", "sealed fate"],
                "circuit_breaker": True
            },
            is_ghost_article=True,
            resurrection_failed=True
        )
        
        return [ghost_item]