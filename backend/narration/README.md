# AI Voice Narration Module

This module provides AI-powered voice narration for spooky content using the ElevenLabs Text-to-Speech API.

## Configuration

The narration module requires the following environment variables to be set in your `.env` file:

### Required Configuration

```bash
# ElevenLabs API Key (required)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

### Optional Configuration

```bash
# Cache directory for storing generated audio files
NARRATION_CACHE_DIR=./cache/narration

# Maximum cache size in megabytes (default: 500MB)
NARRATION_CACHE_MAX_SIZE_MB=500

# Time-to-live for cached audio files in days (default: 7 days)
NARRATION_CACHE_TTL_DAYS=7

# Maximum number of concurrent TTS API requests (default: 3)
NARRATION_MAX_CONCURRENT=3

# Maximum content length for narration in characters (default: 10,000)
NARRATION_MAX_CONTENT_LENGTH=10000
```

## Getting Started

1. **Get an ElevenLabs API Key**
   - Sign up at [ElevenLabs](https://elevenlabs.io/)
   - Navigate to your profile settings
   - Copy your API key

2. **Configure Environment Variables**
   - Copy `.env.example` to `.env` if you haven't already
   - Add your ElevenLabs API key to the `ELEVENLABS_API_KEY` variable
   - Adjust other settings as needed

3. **Create Cache Directory**
   - The cache directory will be created automatically on first use
   - Default location: `./cache/narration`
   - Ensure the application has write permissions

## Features

- **Multiple Voice Styles**: 5 distinct horror voice styles
  - Ghostly Whisper
  - Demonic Growl
  - Eerie Narrator
  - Possessed Child
  - Ancient Entity

- **Intensity Mapping**: Voice characteristics adjust based on horror intensity (1-5)

- **Smart Caching**: 
  - LRU eviction when cache exceeds max size
  - TTL-based cleanup for old entries
  - SHA-256 based cache keys

- **Queue Management**:
  - Priority-based request processing
  - Configurable concurrency limits
  - Request cancellation support

- **Background Cleanup Service**:
  - Automatic cleanup runs every 6 hours
  - Removes expired cache entries (older than TTL)
  - Cleans up abandoned requests (older than 1 hour in queued/generating state)
  - Manual cleanup trigger via API endpoint
  - Cleanup statistics monitoring

## Usage

See the API documentation at `/docs` when the server is running for detailed endpoint information.

### Cleanup Service

The cleanup service runs automatically in the background and performs the following tasks:

1. **Expired Cache Cleanup**: Removes audio files older than the configured TTL (default: 7 days)
2. **Abandoned Request Cleanup**: Cancels generation requests that have been stuck in queued/generating state for more than 1 hour

#### Manual Cleanup

You can manually trigger cleanup tasks using the API:

```bash
# Get cleanup statistics
curl http://localhost:8000/api/narration/cleanup/stats

# Manually run cleanup tasks
curl -X POST http://localhost:8000/api/narration/cleanup/run
```

#### Cleanup Statistics

The cleanup stats endpoint provides information about:
- Cache size and entry count
- Request counts by status
- Active and queued request counts
- Cleanup service configuration

## Troubleshooting

### "ELEVENLABS_API_KEY environment variable is required"
- Ensure you've added your API key to the `.env` file
- Restart the server after updating environment variables

### Cache directory permission errors
- Ensure the application has write permissions to the cache directory
- Check that the directory path is valid and accessible

### TTS API rate limits
- Adjust `NARRATION_MAX_CONCURRENT` to a lower value
- Check your ElevenLabs account quota and limits
