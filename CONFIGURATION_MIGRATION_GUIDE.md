# Configuration Management Migration Guide

This guide explains how to use the new configuration validation and structured logging features for production deployment.

## Overview

The configuration management system provides:

1. **Configuration Validation**: Ensures all required environment variables are present on startup
2. **Default Values**: Automatically applies sensible defaults for optional configuration
3. **Production Mode Validation**: Enforces production-specific constraints (e.g., debug disabled)
4. **Structured Logging**: JSON-formatted logs with automatic secret redaction
5. **Secret Redaction**: Automatically redacts API keys, tokens, and other sensitive data from logs

## Configuration Validation

### Automatic Validation on Startup

The application now validates configuration automatically when it starts:

```python
from backend.config import validate_configuration, ConfigError

try:
    validation_result = validate_configuration()
    print(f"✅ Configuration valid: {validation_result}")
except ConfigError as e:
    print(f"❌ Configuration error: {e}")
    raise
```

### Required Environment Variables

The following variables **must** be set:

- `OPENROUTER_API_KEY`: API key for OpenRouter
- `ELEVENLABS_API_KEY`: API key for ElevenLabs

### Optional Environment Variables

These variables have defaults and are optional:

- `ENVIRONMENT`: `development` (options: development, preview, production)
- `DEBUG`: `false`
- `LOG_LEVEL`: `INFO`
- `OPENROUTER_MODEL`: `gpt-3.5-turbo`
- `NARRATION_MAX_CONCURRENT`: `3`
- `NARRATION_TIMEOUT`: `9` (must be ≤10 for Vercel)
- And many more (see `.env.production.example`)

### Production Mode Constraints

When `ENVIRONMENT=production`, the validator enforces:

1. `DEBUG` must be `false`
2. `NARRATION_TIMEOUT` must be ≤10 seconds (Vercel free tier limit)
3. Warnings for features that may not work on free tier

## Structured Logging

### Using the Structured Logger

Replace standard Python logging with the structured logger:

**Before:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing feed")
logger.error(f"Failed to process: {error}")
```

**After:**
```python
from backend.config import get_structured_logger

logger = get_structured_logger("backend.feeds")

# Simple message
logger.info("Processing feed")

# With context data
logger.info("Processing feed", feed_id="123", feed_url="https://example.com/feed")

# Error with context
logger.error("Failed to process feed", feed_id="123", error=str(error))
```

### Log Output Formats

**Development Mode** (human-readable):
```
2025-11-25T16:15:09.271536Z [INFO] backend.feeds: Processing feed | feed_id=123 | feed_url=https://example.com/feed
```

**Production Mode** (JSON for log aggregation):
```json
{
  "timestamp": "2025-11-25T16:15:09.271536Z",
  "level": "INFO",
  "service": "backend.feeds",
  "environment": "production",
  "message": "Processing feed",
  "feed_id": "123",
  "feed_url": "https://example.com/feed"
}
```

### Automatic Secret Redaction

The structured logger automatically redacts sensitive data:

```python
logger.info("API call completed", 
    api_key="sk-1234567890abcdef",  # Will be redacted
    token="bearer_xyz123",           # Will be redacted
    user_id="user_456"               # Will NOT be redacted
)
```

**Output:**
```
api_key=sk-1...cdef | token=bear...z123 | user_id=user_456
```

### Sensitive Key Patterns

The following patterns are automatically detected and redacted:

- `*api_key*`, `*api-key*`
- `*token*`
- `*secret*`
- `*password*`
- `*auth*`
- `*credential*`
- `*private_key*`, `*private-key*`
- `*access_key*`, `*access-key*`

### Logging HTTP Requests

Use the built-in request logging method:

```python
logger.log_request(
    method="POST",
    path="/api/feeds/process",
    status_code=200,
    duration_ms=123.45,
    feed_count=5
)
```

### Logging Errors with Context

Use the error context method for detailed error logging:

```python
try:
    result = await process_feed(feed_url)
except Exception as error:
    logger.log_error_with_context(
        error=error,
        context={
            "feed_url": feed_url,
            "feed_id": feed_id,
            "operation": "process_feed"
        }
    )
```

## Migration Checklist

### For Each Module

- [ ] Replace `logging.getLogger(__name__)` with `get_structured_logger("module.name")`
- [ ] Update log calls to use keyword arguments for context
- [ ] Remove manual string formatting in log messages
- [ ] Use `logger.log_error_with_context()` for exceptions
- [ ] Remove any manual secret redaction code

### Example Migration

**Before:**
```python
import logging

logger = logging.getLogger(__name__)

def process_feed(feed_url: str, api_key: str):
    logger.info(f"Processing feed: {feed_url}")
    
    try:
        result = fetch_feed(feed_url, api_key)
        logger.info(f"Successfully processed feed: {feed_url}")
        return result
    except Exception as e:
        # Manual redaction
        safe_key = api_key[:4] + "..." + api_key[-4:]
        logger.error(f"Failed to process {feed_url} with key {safe_key}: {str(e)}")
        raise
```

**After:**
```python
from backend.config import get_structured_logger

logger = get_structured_logger("backend.feeds.processor")

def process_feed(feed_url: str, api_key: str):
    logger.info("Processing feed", feed_url=feed_url)
    
    try:
        result = fetch_feed(feed_url, api_key)
        logger.info("Successfully processed feed", feed_url=feed_url)
        return result
    except Exception as e:
        logger.log_error_with_context(
            error=e,
            context={
                "feed_url": feed_url,
                "api_key": api_key,  # Automatically redacted
                "operation": "fetch_feed"
            }
        )
        raise
```

## Configuration Summary

Get a summary of current configuration (with secrets redacted):

```python
from backend.config import get_config_summary

summary = get_config_summary()
print(summary)
# Output: {'environment': 'production', 'debug': 'False', 'openrouter_model': 'gpt-3.5-turbo', ...}
```

## Testing

### Test Configuration Validation

```python
import os
from backend.config import validate_configuration, ConfigError

# Test with missing variables
os.environ.pop("OPENROUTER_API_KEY", None)

try:
    validate_configuration()
except ConfigError as e:
    print(f"Expected error: {e}")

# Test with valid variables
os.environ["OPENROUTER_API_KEY"] = "test-key"
os.environ["ELEVENLABS_API_KEY"] = "test-key"

result = validate_configuration()
assert result["valid"] == True
```

### Test Secret Redaction

```python
from backend.config import get_structured_logger

logger = get_structured_logger("test")

# This should redact the API key
logger.info("Test", api_key="sk-1234567890abcdef")

# Check logs to verify redaction
```

## Deployment

### Vercel Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

**Required:**
- `OPENROUTER_API_KEY`
- `ELEVENLABS_API_KEY`

**Recommended:**
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`
- `DEBUG=false`
- `NARRATION_TIMEOUT=9`

### Local Development

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your keys
```

### Production Deployment

Use `.env.production.example` as a template:

```bash
cp .env.production.example .env.production
# Edit .env.production with production values
```

## Benefits

1. **Security**: Automatic secret redaction prevents accidental exposure of API keys
2. **Debugging**: Structured logs with context make debugging easier
3. **Monitoring**: JSON format integrates with log aggregation services (Vercel logs)
4. **Validation**: Catch configuration errors at startup, not at runtime
5. **Defaults**: Sensible defaults reduce configuration burden
6. **Production-Ready**: Enforces production best practices automatically

## Troubleshooting

### Configuration Validation Fails

**Error:** "Missing required environment variables"

**Solution:** Set the required variables in your environment or `.env` file

### Debug Mode in Production

**Error:** "DEBUG must be disabled in production environment"

**Solution:** Set `DEBUG=false` in production environment

### Timeout Too High

**Error:** "NARRATION_TIMEOUT exceeds Vercel free tier limit"

**Solution:** Set `NARRATION_TIMEOUT=9` or lower (must be ≤10 seconds)

### Logs Not Appearing

**Issue:** Logs not showing in Vercel dashboard

**Solution:** Ensure `ENVIRONMENT=production` to enable JSON logging format

## Next Steps

1. Migrate existing logging calls to structured logger
2. Test configuration validation locally
3. Verify secret redaction is working
4. Deploy to Vercel preview environment
5. Monitor logs in Vercel dashboard
6. Adjust configuration as needed

For more information, see:
- `.env.production.example` - Production configuration template
- `backend/config/validator.py` - Configuration validation logic
- `backend/config/structured_logger.py` - Structured logging implementation
