# Vercel Serverless Functions

This directory contains serverless function endpoints for the Spooky RSS System backend, designed to run on Vercel's platform.

## Directory Structure

```
api/
├── __init__.py           # Package initialization
├── requirements.txt      # Python dependencies for serverless functions
├── health.py            # Health check endpoint
├── feeds/
│   ├── __init__.py
│   └── process.py       # RSS feed processing endpoint
└── narration/
    ├── __init__.py
    ├── generate.py      # Narration generation endpoint
    └── voices.py        # Voice listing endpoint
```

## Endpoints

### Health Check
- **Path**: `/api/health`
- **Method**: GET
- **Description**: Returns service health status
- **Response**: `{ "status": "healthy", "service": "spooky-rss-system", "version": "1.0.0" }`

### Feed Processing
- **Path**: `/api/feeds/process`
- **Method**: POST
- **Description**: Processes RSS feeds and transforms them into horror stories
- **Status**: Placeholder (to be implemented in task 2.2)

### Narration Generation
- **Path**: `/api/narration/generate`
- **Method**: POST
- **Description**: Generates AI voice narration for content
- **Status**: Placeholder (to be implemented in task 2.2)

### Voice Listing
- **Path**: `/api/narration/voices`
- **Method**: GET
- **Description**: Returns available voice styles
- **Status**: Placeholder (to be implemented in task 2.2)

## How Vercel Serverless Functions Work

Each Python file in this directory becomes a serverless function endpoint. The file must export a `handler` class or function that Vercel invokes when the endpoint is called.

### Handler Pattern

```python
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"message": "Hello from serverless!"}
        self.wfile.write(json.dumps(response).encode())
```

## Constraints

Vercel's free (Hobby) tier has the following limits:

- **Function Duration**: 10 seconds maximum per invocation
- **Function Memory**: 1024 MB maximum
- **Invocations**: 1 million per month included
- **Bandwidth**: 100 GB per month included

All implementations must work within these constraints.

## Development

To test serverless functions locally:

```bash
# Install Vercel CLI
npm install -g vercel

# Run development server
vercel dev
```

This will start a local server that simulates the Vercel environment.

## Deployment

Functions are automatically deployed when you push to your connected Git repository or run:

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Environment Variables

Required environment variables must be set in the Vercel Dashboard:

- `OPENROUTER_API_KEY` - OpenRouter API key for AI generation
- `ELEVENLABS_API_KEY` - ElevenLabs API key for voice narration

See `.env.production.example` for the complete list of environment variables.

## Next Steps

The placeholder endpoints will be implemented in subsequent tasks:

- **Task 2.1**: Install and configure Mangum adapter for FastAPI
- **Task 2.2**: Create individual serverless function endpoints with full functionality
- **Task 2.3**: Write unit tests for serverless adapters
