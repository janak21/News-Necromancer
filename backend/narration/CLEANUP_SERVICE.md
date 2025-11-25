# Narration Cleanup Service

## Overview

The Narration Cleanup Service is a background task that automatically maintains the health of the narration system by cleaning up expired cache entries and abandoned generation requests.

## Features

### Automatic Cleanup
- Runs every 6 hours automatically
- Removes expired cache entries (older than TTL, default 7 days)
- Cancels abandoned requests (stuck in queued/generating state for > 1 hour)

### Manual Cleanup
- API endpoint to trigger cleanup on-demand
- Useful for maintenance or testing

### Monitoring
- Statistics endpoint for monitoring cache and queue health
- Detailed information about cleanup operations

## Implementation Details

### Components

1. **NarrationCleanupService** (`backend/narration/cleanup.py`)
   - Main cleanup service class
   - Manages periodic cleanup loop
   - Coordinates cache and queue cleanup

2. **Integration** (`backend/api/main.py`)
   - Lifespan context manager for startup/shutdown
   - Initializes cleanup service on API startup
   - Gracefully shuts down on API shutdown

3. **API Endpoints** (`backend/api/routes/narration.py`)
   - `GET /api/narration/cleanup/stats` - Get cleanup statistics
   - `POST /api/narration/cleanup/run` - Manually trigger cleanup

### Configuration

The cleanup service uses the following configuration:

```python
cleanup_interval_hours = 6  # Run cleanup every 6 hours
abandoned_request_timeout_hours = 1  # Cancel requests older than 1 hour
```

These values are set in the service initialization and can be adjusted as needed.

## API Endpoints

### Get Cleanup Statistics

```bash
GET /api/narration/cleanup/stats
```

Returns:
```json
{
  "running": true,
  "cleanup_interval_hours": 6,
  "abandoned_timeout_hours": 1,
  "cache": {
    "entry_count": 42,
    "total_size_mb": 125.5,
    "max_size_mb": 500,
    "ttl_days": 7
  },
  "requests": {
    "total": 150,
    "by_status": {
      "completed": 140,
      "queued": 5,
      "generating": 3,
      "failed": 2
    },
    "active": 3,
    "queued": 5
  }
}
```

### Manually Run Cleanup

```bash
POST /api/narration/cleanup/run
```

Returns:
```json
{
  "success": true,
  "message": "Cleanup tasks completed successfully",
  "stats": { /* same as stats endpoint */ }
}
```

## Testing

Comprehensive test suite in `backend/tests/test_cleanup.py`:

- Service initialization and lifecycle
- Expired cache cleanup
- Abandoned request cleanup
- Statistics retrieval
- Edge cases and error handling

Integration tests in `backend/tests/test_cleanup_integration.py`:

- API endpoint functionality
- Service integration with FastAPI

Run tests:
```bash
python3 -m pytest backend/tests/test_cleanup.py -v
python3 -m pytest backend/tests/test_cleanup_integration.py -v
```

## Cleanup Operations

### Expired Cache Cleanup

1. Iterates through all cache entries
2. Checks if entry age exceeds TTL
3. Removes expired entries and their files
4. Updates cache index
5. Logs cleanup statistics

### Abandoned Request Cleanup

1. Iterates through all generation requests
2. Identifies requests in "queued" or "generating" state
3. Checks if request age exceeds timeout (1 hour)
4. Cancels abandoned requests
5. Logs cleanup statistics

## Monitoring

The cleanup service logs all operations:

- Service start/stop events
- Cleanup execution start/completion
- Number of entries/requests cleaned up
- Space freed by cleanup
- Any errors encountered

Example logs:
```
INFO - Started cleanup service (interval: 6.0h, abandoned timeout: 1.0h)
INFO - Starting cleanup tasks
INFO - Cleaning up expired cache entries
INFO - Removed 5 expired cache entries, freed 12.34 MB
INFO - Cleaning up abandoned requests
INFO - Cancelled 2 abandoned requests
INFO - Cleanup tasks completed successfully
```

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 4.3**: Cache cleanup for expired entries
- **Requirement 4.5**: TTL-based cache management
- **Task 21.1**: Background cleanup job implementation
  - ✅ Expired cache cleanup (older than TTL)
  - ✅ Abandoned request cleanup (older than 1 hour in queued/generating state)
  - ✅ Scheduled to run every 6 hours
  - ✅ Manual trigger via API endpoint
  - ✅ Statistics monitoring

## Future Enhancements

Potential improvements for future iterations:

1. Configurable cleanup intervals via environment variables
2. Metrics export for monitoring systems (Prometheus, etc.)
3. Cleanup history tracking
4. Alerting for cleanup failures
5. Cleanup dry-run mode for testing
