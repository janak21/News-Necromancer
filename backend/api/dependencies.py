"""
FastAPI dependencies for dependency injection
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

from ..fetcher.concurrent_fetcher import ConcurrentFetcher
from ..remixer.spooky_remixer import SpookyRemixer
from .integration import SpookyIntegrationManager

# Load environment variables
load_dotenv()

@lru_cache()
def get_fetcher() -> ConcurrentFetcher:
    """
    Get configured ConcurrentFetcher instance
    
    Returns:
        ConcurrentFetcher instance
    """
    max_concurrent = int(os.getenv('MAX_CONCURRENT_FEEDS', '10'))
    timeout = int(os.getenv('FEED_TIMEOUT', '10'))
    
    return ConcurrentFetcher(
        max_concurrent=max_concurrent,
        timeout=timeout,
        enable_caching=False  # Disable Redis caching for now
    )

@lru_cache()
def get_remixer() -> SpookyRemixer:
    """
    Get configured SpookyRemixer instance
    
    Returns:
        SpookyRemixer instance
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    model = os.getenv('OPENROUTER_MODEL', 'gpt-3.5-turbo')
    app_name = os.getenv('OPENROUTER_APP_NAME', 'spooky-rss-system')
    
    return SpookyRemixer(
        api_key=api_key,
        model=model,
        app_name=app_name
    )

@lru_cache()
def get_integration_manager() -> SpookyIntegrationManager:
    """
    Get configured SpookyIntegrationManager instance
    
    Returns:
        SpookyIntegrationManager instance
    """
    fetcher = get_fetcher()
    remixer = get_remixer()
    
    return SpookyIntegrationManager(fetcher, remixer)