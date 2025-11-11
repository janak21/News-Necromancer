"""
Application settings and configuration
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    api_title: str = "Spooky RSS System API"
    api_version: str = "1.0.0"
    api_description: str = "Transform RSS feeds into horror-themed content with AI"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"
    
    # OpenRouter/LLM Configuration
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "gpt-3.5-turbo"
    openrouter_app_name: str = "spooky-rss-system"
    
    # Fetcher Configuration
    max_concurrent_feeds: int = 10
    feed_timeout: int = 10
    max_retries: int = 3
    
    # Processing Configuration
    default_variant_count: int = 2
    max_feed_items: int = 3
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Cache Configuration (for future Redis integration)
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Database Configuration (for future database integration)
    database_url: Optional[str] = None
    
    # Security Configuration
    api_key_header: str = "X-API-Key"
    rate_limit_per_minute: int = 60
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "",
    }
    
    def validate_required_settings(self):
        """Validate that required settings are present"""
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.debug or self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings instance
    """
    settings = Settings()
    
    # Validate required settings in production
    if settings.is_production:
        settings.validate_required_settings()
    
    return settings