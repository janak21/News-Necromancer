# Vercel Handler Fix - BaseHTTPRequestHandler

## The Real Problem

The Vercel error log revealed:
```
TypeError: issubclass() arg 1 must be a class
Python process exited with exit status: 1
```

This means Vercel's Python runtime couldn't recognize the Mangum/FastAPI handler format.

## Solution

Rewrote `api/feeds/process.py` using Vercel's native `BaseHTTPRequestHandler` class format (same as the working `api/health.py` and `api/simple.py`).

## What Changed

### Before (Mangum/FastAPI):
```python
from mangum import Mangum
from fastapi import FastAPI

app = FastAPI()

@app.post("/")
async def process_feeds(request: FeedProcessRequest):
    # ...

handler = Mangum(app, lifespan="off")
```

### After (BaseHTTPRequestHandler):
```python
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Health check
        
    def do_POST(self):
        # Process feeds with asyncio
        
    def do_OPTIONS(self):
        # CORS preflight
```

## Features Preserved

✅ Async RSS feed fetching
✅ OpenRouter API integration
✅ Multiple feed processing
✅ Horror variant generation
✅ CORS support
✅ Error handling (400/500)
✅ Health check endpoint

## Deploy Now

```bash
git add api/feeds/process.py
git commit -m "Fix: Rewrite handler using BaseHTTPRequestHandler for Vercel compatibility"
git push origin main
```

Vercel will auto-deploy in ~2-3 minutes.

## Test After Deployment

### 1. Health Check
```bash
curl https://news-necromancer.vercel.app/api/feeds/process
```

Expected:
```json
{
  "status": "ok",
  "service": "feed-processing",
  "openrouter_configured": true
}
```

### 2. Browser Test
1. Go to your app → "Spooky Feeds"
2. Click "👻 Haunt Feed"
3. Should work without 500 errors!

## Why This Works

Vercel's Python runtime expects a class named `handler` that inherits from `BaseHTTPRequestHandler`. The Mangum adapter adds an extra layer that Vercel's runtime can't properly detect, causing the `issubclass()` error.

By using the native format, we match exactly what Vercel expects.
