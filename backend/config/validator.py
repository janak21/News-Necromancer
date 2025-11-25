"""
Configuration validation module for production deployment

This module provides comprehensive validation for application configuration,
ensuring all required environment variables are present and valid before
the application starts.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from enum import Enum


class ConfigError(Exception):
    """Exception raised for configuration validation errors"""
    pass


class Environment(str, Enum):
    """Valid environment values"""
    DEVELOPMENT = "development"
    PREVIEW = "preview"
    PRODUCTION = "production"


class ConfigValidator:
    """
    Validates application configuration on startup
    
    Ensures:
    - Required environment variables are present
    - Optional variables have sensible defaults
    - Production mode has debug disabled
    - All values are within acceptable ranges
    """
    
    # Required environment variables
    REQUIRED_VARS = [
        "OPENROUTER_API_KEY",
        "ELEVENLABS_API_KEY",
    ]
    
    # Optional environment variables with defaults
    OPTIONAL_VARS = {
        "ENVIRONMENT": "development",
        "OPENROUTER_MODEL": "gpt-3.5-turbo",
        "OPENROUTER_APP_NAME": "spooky-rss-system",
        "LOG_LEVEL": "INFO",
        "DEBUG": "false",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "NARRATION_ENABLED": "true",
        "NARRATION_MAX_CONCURRENT": "3",
        "NARRATION_MAX_CONTENT_LENGTH": "10000",
        "NARRATION_TIMEOUT": "9",
        "NARRATION_CACHE_DIR": "./cache/narration",
        "NARRATION_CACHE_MAX_SIZE_MB": "500",
        "NARRATION_CACHE_TTL_DAYS": "7",
        "MAX_CONCURRENT_FEEDS": "10",
        "FEED_TIMEOUT": "10",
        "MAX_RETRIES": "3",
        "RATE_LIMIT_PER_MINUTE": "100",
        "ENABLE_CACHING": "false",
    }
    
    # Production-specific constraints
    PRODUCTION_CONSTRAINTS = {
        "DEBUG": "false",
        "NARRATION_TIMEOUT": 10,  # Must be <= 10 for Vercel free tier
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.logger = logging.getLogger(__name__)
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all configuration settings
        
        Returns:
            Dict containing validation results
            
        Raises:
            ConfigError: If validation fails
        """
        self.errors = []
        self.warnings = []
        
        # Check required variables
        self._validate_required_vars()
        
        # Apply defaults for optional variables
        self._apply_defaults()
        
        # Validate environment-specific constraints
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == Environment.PRODUCTION.value:
            self._validate_production_mode()
        
        # Validate value ranges and types
        self._validate_values()
        
        # If there are errors, raise exception
        if self.errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)
            raise ConfigError(error_msg)
        
        # Log warnings if any
        if self.warnings:
            for warning in self.warnings:
                self.logger.warning(f"Configuration warning: {warning}")
        
        return {
            "valid": True,
            "errors": self.errors,
            "warnings": self.warnings,
            "environment": environment,
        }
    
    def _validate_required_vars(self) -> None:
        """Check that all required environment variables are present"""
        missing_vars = []
        
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if not value or value.strip() == "":
                missing_vars.append(var)
        
        if missing_vars:
            self.errors.append(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    
    def _apply_defaults(self) -> None:
        """Apply default values for optional environment variables"""
        for var, default_value in self.OPTIONAL_VARS.items():
            if var not in os.environ or os.getenv(var, "").strip() == "":
                os.environ[var] = default_value
                self.logger.debug(f"Applied default value for {var}: {default_value}")
    
    def _validate_production_mode(self) -> None:
        """Validate production-specific constraints"""
        # Check that debug is disabled in production
        debug_value = os.getenv("DEBUG", "false").lower()
        if debug_value not in ["false", "0", "no"]:
            self.errors.append(
                "DEBUG must be disabled (false) in production environment"
            )
        
        # Check narration timeout is within Vercel limits
        try:
            timeout = int(os.getenv("NARRATION_TIMEOUT", "9"))
            if timeout > self.PRODUCTION_CONSTRAINTS["NARRATION_TIMEOUT"]:
                self.errors.append(
                    f"NARRATION_TIMEOUT ({timeout}s) exceeds Vercel free tier limit "
                    f"({self.PRODUCTION_CONSTRAINTS['NARRATION_TIMEOUT']}s)"
                )
        except ValueError:
            self.errors.append("NARRATION_TIMEOUT must be a valid integer")
        
        # Warn about caching in production
        enable_caching = os.getenv("ENABLE_CACHING", "false").lower()
        if enable_caching in ["true", "1", "yes"]:
            self.warnings.append(
                "Caching is enabled but Vercel KV is not available on free tier. "
                "Only in-memory caching will work within function execution."
            )
    
    def _validate_values(self) -> None:
        """Validate that configuration values are within acceptable ranges"""
        # Validate integer values
        int_vars = {
            "PORT": (1, 65535),
            "NARRATION_MAX_CONCURRENT": (1, 10),
            "NARRATION_MAX_CONTENT_LENGTH": (100, 50000),
            "NARRATION_TIMEOUT": (1, 10),
            "NARRATION_CACHE_MAX_SIZE_MB": (1, 10000),
            "NARRATION_CACHE_TTL_DAYS": (1, 365),
            "MAX_CONCURRENT_FEEDS": (1, 50),
            "FEED_TIMEOUT": (1, 60),
            "MAX_RETRIES": (0, 10),
            "RATE_LIMIT_PER_MINUTE": (1, 1000),
        }
        
        for var, (min_val, max_val) in int_vars.items():
            value_str = os.getenv(var)
            if value_str:
                try:
                    value = int(value_str)
                    if value < min_val or value > max_val:
                        self.errors.append(
                            f"{var} must be between {min_val} and {max_val}, got {value}"
                        )
                except ValueError:
                    self.errors.append(f"{var} must be a valid integer, got '{value_str}'")
        
        # Validate environment value
        environment = os.getenv("ENVIRONMENT", "development")
        valid_environments = [e.value for e in Environment]
        if environment not in valid_environments:
            self.errors.append(
                f"ENVIRONMENT must be one of {valid_environments}, got '{environment}'"
            )
        
        # Validate log level
        log_level = os.getenv("LOG_LEVEL", "INFO")
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level.upper() not in valid_log_levels:
            self.errors.append(
                f"LOG_LEVEL must be one of {valid_log_levels}, got '{log_level}'"
            )
        
        # Validate boolean values
        bool_vars = ["DEBUG", "NARRATION_ENABLED", "ENABLE_CACHING"]
        for var in bool_vars:
            value = os.getenv(var, "").lower()
            if value and value not in ["true", "false", "1", "0", "yes", "no"]:
                self.errors.append(
                    f"{var} must be a boolean value (true/false), got '{value}'"
                )


def validate_configuration() -> Dict[str, Any]:
    """
    Validate application configuration on startup
    
    This function should be called before the application starts to ensure
    all required configuration is present and valid.
    
    Returns:
        Dict containing validation results
        
    Raises:
        ConfigError: If validation fails
    """
    validator = ConfigValidator()
    return validator.validate_all()


def get_config_summary() -> Dict[str, str]:
    """
    Get a summary of current configuration (with secrets redacted)
    
    Returns:
        Dict containing configuration summary
    """
    from .settings import get_settings
    
    settings = get_settings()
    
    return {
        "environment": settings.environment,
        "debug": str(settings.debug),
        "openrouter_model": settings.openrouter_model,
        "narration_enabled": str(settings.elevenlabs_api_key is not None),
        "log_level": settings.log_level,
        "host": settings.host,
        "port": str(settings.port),
    }
