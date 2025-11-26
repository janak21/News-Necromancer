# Narration Endpoint Fix

## Problem
Same issue as feeds endpoint - Vercel's Python runtime doesn't support Mangum/FastAPI handler format.

Error: `POST https://news-necromancer.vercel.app/api/narration/generate 500 (Internal Server Error)`

## Solution
Rewrote `api/narration/generate.py` using `BaseHTTPRequestHandler` class.

## Key Features

### Simplified Architecture
Instead of the complex queue manager system, this serverless version:
- ✅ Generates narration immediately using ElevenLabs API
- ✅ Returns audio as base64-encoded data URL
- ✅ Completes within Vercel's 10-second timeout
- ✅ No queue management needed (serverless is stateless)

### Voice Styles Supported
- `ethereal_whisper` - Soft, ethereal voice
- `gothic_narrator` - Dramatic, gothic voice
- `sinister_storyteller` - Deep, ominous voice
- `haunted_voice` - Haunting voice
- `cryptic_oracle` - Mysterious voice
- `eerie_narrator` - Default fallback

### Response Format
```json
{
  "request_id": "variant-id",
  "status": "completed",
  "estimated_time": 0,
  "queue_position": 0,
  "audio_url": "data:audio/mpeg;base64,...",
  "duration": 45.2,
  "progress": 100
}
```

## Deploy

```bash
git add api/narration/generate.py
git commit -m "Fix: Rewrite narration handler using BaseHTTPRequestHandler"
git push origin main
```

## Test After Deployment

### Health Check
```bash
curl https://news-necromancer.vercel.app/api/narration/generate
```

Expected:
```json
{
  "status": "ok",
  "service": "narration-generation",
  "elevenlabs_configured": true,
  "available_voices": ["ethereal_whisper", "gothic_narrator", ...]
}
```

### In Browser
1. Generate a haunted feed
2. Click the audio/narration button on a variant
3. Should generate and play audio without 500 errors!

## Technical Details

### Content Truncation
- Max length: 5000 characters (configurable via `NARRATION_MAX_CONTENT_LENGTH`)
- Prevents timeout issues with very long content

### Voice Settings
- Stability: 0.4 to 0.8 (based on intensity level)
- Similarity boost: 0.55 to 0.75 (based on intensity level)

### Timeout
- Default: 9 seconds (configurable via `NARRATION_TIMEOUT`)
- Stays under Vercel's 10-second limit

### Audio Format
- Returns base64-encoded MP3 as data URL
- No external storage needed
- Works immediately in browser audio player
