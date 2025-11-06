"""
Logging configuration for the Spooky RSS System
"""

import logging
import logging.config
import sys
from typing import Dict, Any
from .settings import get_settings


def setup_logging() -> None:
    """
    Setup logging configuration for the application
    """
    settings = get_settings()
    
    # Define logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "spooky": {
                "format": "🎃 %(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "spooky" if settings.is_development else "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/spooky_rss_system.log",
                "mode": "a",
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/errors.log",
                "mode": "a",
                "encoding": "utf-8",
            }
        },
        "loggers": {
            # Root logger
            "": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Application loggers
            "backend": {
                "level": settings.log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "backend.fetcher": {
                "level": settings.log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "backend.remixer": {
                "level": settings.log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "backend.api": {
                "level": settings.log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            # Third-party loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "aiohttp": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "openai": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            }
        }
    }
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Log startup message
    logger = logging.getLogger("backend")
    logger.info("🎃 Spooky RSS System logging initialized")
    logger.info(f"👻 Log level: {settings.log_level}")
    logger.info(f"🕷️ Environment: {'development' if settings.is_development else 'production'}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class SpookyLoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds spooky emojis to log messages
    """
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any] = None):
        super().__init__(logger, extra or {})
        
        # Emoji mappings for different log levels
        self.emoji_map = {
            "DEBUG": "🔍",
            "INFO": "👻", 
            "WARNING": "⚠️",
            "ERROR": "💀",
            "CRITICAL": "🔥"
        }
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add spooky emojis
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Processed message and kwargs
        """
        # Get the log level from the record if available
        level_name = kwargs.get('extra', {}).get('levelname', 'INFO')
        emoji = self.emoji_map.get(level_name, "👻")
        
        # Add emoji to message if not already present
        if not any(e in msg for e in self.emoji_map.values()):
            msg = f"{emoji} {msg}"
        
        return msg, kwargs


def get_spooky_logger(name: str) -> SpookyLoggerAdapter:
    """
    Get a spooky logger adapter instance
    
    Args:
        name: Logger name
        
    Returns:
        SpookyLoggerAdapter instance
    """
    logger = logging.getLogger(name)
    return SpookyLoggerAdapter(logger)