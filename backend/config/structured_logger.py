"""
Structured logging with secret redaction for production deployment

This module provides a structured logger that:
- Outputs JSON-formatted logs to stdout (for Vercel log aggregation)
- Automatically redacts sensitive data (API keys, tokens, secrets)
- Includes contextual information for debugging
- Supports different log levels and formats
"""

import json
import logging
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class LogLevel(str, Enum):
    """Standard log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """
    Structured logger with automatic secret redaction
    
    Features:
    - JSON-formatted output for log aggregation
    - Automatic redaction of sensitive data
    - Contextual information (service, timestamp, etc.)
    - Support for structured data logging
    """
    
    # Patterns to identify sensitive keys
    SENSITIVE_PATTERNS = [
        r".*api[_-]?key.*",
        r".*token.*",
        r".*secret.*",
        r".*password.*",
        r".*auth.*",
        r".*credential.*",
        r".*private[_-]?key.*",
        r".*access[_-]?key.*",
    ]
    
    # Compiled regex patterns for performance
    _compiled_patterns: Optional[List[re.Pattern]] = None
    
    def __init__(
        self,
        service_name: str,
        environment: str = "development",
        enable_json: bool = True,
    ):
        """
        Initialize structured logger
        
        Args:
            service_name: Name of the service/component
            environment: Environment (development, production, etc.)
            enable_json: Whether to output JSON format (True for production)
        """
        self.service_name = service_name
        self.environment = environment
        self.enable_json = enable_json
        self.logger = logging.getLogger(service_name)
        
        # Compile patterns once
        if StructuredLogger._compiled_patterns is None:
            StructuredLogger._compiled_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.SENSITIVE_PATTERNS
            ]
    
    def _is_sensitive_key(self, key: str) -> bool:
        """
        Check if a key name indicates sensitive data
        
        Args:
            key: Key name to check
            
        Returns:
            True if key is sensitive
        """
        key_lower = key.lower()
        return any(pattern.match(key_lower) for pattern in self._compiled_patterns)
    
    def _redact_value(self, value: Any) -> str:
        """
        Redact a sensitive value
        
        Args:
            value: Value to redact
            
        Returns:
            Redacted string
        """
        if value is None:
            return "***REDACTED***"
        
        value_str = str(value)
        if len(value_str) <= 8:
            return "***REDACTED***"
        
        # Show first 4 and last 4 characters for debugging
        return f"{value_str[:4]}...{value_str[-4:]}"
    
    def _redact_secrets(self, data: Any, visited: Optional[Set[int]] = None) -> Any:
        """
        Recursively redact secrets from data structures
        
        Args:
            data: Data to redact (dict, list, or primitive)
            visited: Set of visited object IDs to prevent infinite recursion
            
        Returns:
            Data with secrets redacted
        """
        if visited is None:
            visited = set()
        
        # Prevent infinite recursion
        data_id = id(data)
        if data_id in visited:
            return "[CIRCULAR_REFERENCE]"
        visited.add(data_id)
        
        if isinstance(data, dict):
            redacted = {}
            for key, value in data.items():
                if self._is_sensitive_key(key):
                    redacted[key] = self._redact_value(value)
                else:
                    redacted[key] = self._redact_secrets(value, visited)
            return redacted
        
        elif isinstance(data, (list, tuple)):
            return [self._redact_secrets(item, visited) for item in data]
        
        elif isinstance(data, str):
            # Check if string looks like an API key or token
            if len(data) > 20 and any(
                keyword in data.lower()
                for keyword in ["key", "token", "secret", "bearer"]
            ):
                return self._redact_value(data)
            return data
        
        else:
            return data
    
    def _format_log_entry(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Format a log entry
        
        Args:
            level: Log level
            message: Log message
            extra: Additional context data
            
        Returns:
            Formatted log entry (JSON or plain text)
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "service": self.service_name,
            "environment": self.environment,
            "message": message,
        }
        
        # Add extra context if provided
        if extra:
            # Redact secrets from extra data
            redacted_extra = self._redact_secrets(extra)
            log_entry.update(redacted_extra)
        
        if self.enable_json:
            return json.dumps(log_entry)
        else:
            # Plain text format for development
            extra_str = ""
            if extra:
                extra_str = " | " + " | ".join(
                    f"{k}={v}" for k, v in self._redact_secrets(extra).items()
                )
            return f"{timestamp} [{level}] {self.service_name}: {message}{extra_str}"
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Internal logging method
        
        Args:
            level: Log level
            message: Log message
            extra: Additional context data
        """
        formatted = self._format_log_entry(level.value, message, extra)
        
        # Output to stdout for Vercel log aggregation
        print(formatted, file=sys.stdout, flush=True)
        
        # Also log through standard logger for local development
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, extra=extra or {})
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, kwargs if kwargs else None)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log(LogLevel.INFO, message, kwargs if kwargs else None)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log(LogLevel.WARNING, message, kwargs if kwargs else None)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log(LogLevel.ERROR, message, kwargs if kwargs else None)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, kwargs if kwargs else None)
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ) -> None:
        """
        Log HTTP request
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional context
        """
        self.info(
            f"{method} {path} {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error_with_context(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log error with full context
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        
        if context:
            error_data.update(context)
        
        self.error(f"Error occurred: {str(error)}", **error_data)


# Global logger instances cache
_loggers: Dict[str, StructuredLogger] = {}


def get_structured_logger(
    service_name: str,
    environment: Optional[str] = None,
) -> StructuredLogger:
    """
    Get or create a structured logger instance
    
    Args:
        service_name: Name of the service/component
        environment: Environment (defaults to ENVIRONMENT env var)
        
    Returns:
        StructuredLogger instance
    """
    import os
    
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    # Use JSON format in production
    enable_json = environment == "production"
    
    # Cache logger instances
    cache_key = f"{service_name}:{environment}"
    if cache_key not in _loggers:
        _loggers[cache_key] = StructuredLogger(
            service_name=service_name,
            environment=environment,
            enable_json=enable_json,
        )
    
    return _loggers[cache_key]


def setup_structured_logging() -> None:
    """
    Setup structured logging for the application
    
    This should be called early in application startup to configure
    logging for production deployment.
    """
    import os
    
    environment = os.getenv("ENVIRONMENT", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",  # Structured logger handles formatting
        stream=sys.stdout,
    )
    
    # Create application logger
    logger = get_structured_logger("spooky-rss-system", environment)
    logger.info(
        "Structured logging initialized",
        environment=environment,
        log_level=log_level,
    )
