# Final Deployment Checklist ✅

## Pre-Deployment Verification

✅ **All serverless endpoints use BaseHTTPRequestHandler**
- `api/feeds/process.py` ✓
- `api/narration/generate.py` ✓
- `api/narration/status.py` ✓
- `api/story_continue.py` ✓
- `api/health.py` ✓

✅ **Frontend configuration**
- Production env configured: `VITE_API_BASE_URL=/api` ✓
- Build command set in vercel.json ✓
- Output directory: `frontend/dist` ✓

✅ **Dependencies**
- All required packages in `api/requirements.txt` ✓
- aiohttp, feedparser, openai, elevenlabs ✓

✅ **Environment variables documented**
- `.env.production.example` exists ✓
- OPENROUTER_API_KEY documented ✓
- ELEVENLABS_API_KEY documented ✓

## Vercel Dashboard Setup

### 1. Verify Environment Variables

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Ensure these are set for **Production**:

| Variable | Value | Status |
|----------|-------|--------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | ✅ Set |
| `ELEVENLABS_API_KEY` | `sk_...` | ✅ Set |
| `OPENROUTER_MODEL` | `openai/gpt-3.5-turbo` | ✅ Set |

### 2. Check Build Settings

- Framework Preset: **Other**
- Build Command: `cd frontend && npm install && npm run build`
- Output Directory: `frontend/dist`
- Install Command: `pip install -r api/requirements.txt`

## Deployment Commands

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Complete serverless deployment: feeds, narration, and story continuation"

# Push to trigger Vercel deployment
git push origin main
```

## Post-Deployment Testing

### 1. Health Check (2 min after deploy)
```bash
curl https://news-necromancer.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "GhostRevive",
  "version": "1.0.0"
}
```

### 2. Test Feed Processing
1. Visit: https://news-necromancer.vercel.app
2. Go to "Spooky Feeds"
3. Enter RSS URL: `https://feeds.bbci.co.uk/news/rss.xml`
4. Click "👻 Haunt Feed"
5. ✅ Should generate haunted variants (~5-8 seconds)

### 3. Test Voice Narration
1. On a generated variant, click the narration button
2. ✅ Should generate audio (~3-7 seconds)
3. ✅ Audio should play automatically
4. ✅ Controls (play/pause/speed) should work

### 4. Test Story Continuation
1. On a variant, click "Continue the Nightmare"
2. ✅ Should generate continuation (~3-5 seconds)
3. ✅ Continuation should appear below original
4. ✅ Can continue multiple times

### 5. Check Browser Console
- ✅ No 500 errors
- ✅ No 404 errors
- ✅ No CORS errors

## Monitoring

### View Function Logs
```bash
vercel logs https://news-necromancer.vercel.app
```

Or in dashboard:
**Deployments → Latest → View Function Logs**

### Check for Errors
Look for:
- ❌ Timeout errors (>10 seconds)
- ❌ API key errors
- ❌ Import errors
- ❌ Memory errors

## Troubleshooting

### If feeds don't generate:
1. Check Vercel logs for OpenRouter API errors
2. Verify `OPENROUTER_API_KEY` is set correctly
3. Check if API key has credits

### If narration fails:
1. Check Vercel logs for ElevenLabs API errors
2. Verify `ELEVENLABS_API_KEY` is set correctly
3. Confirm using free tier model: `eleven_turbo_v2_5`

### If story continuation fails:
1. Check `/api/story_continue` endpoint exists
2. Verify OpenRouter API key
3. Check function logs for errors

### If getting timeouts:
- Reduce number of articles processed (currently 3)
- Reduce narration content length
- Check if API responses are slow

## Performance Expectations

All within Vercel free tier 10-second limit:

| Feature | Expected Time | Status |
|---------|---------------|--------|
| Feed processing (3 articles) | 5-8 seconds | ✅ |
| Voice narration | 3-7 seconds | ✅ |
| Story continuation | 3-5 seconds | ✅ |

## Success Criteria

✅ All three main features working
✅ No console errors
✅ All requests complete within timeout
✅ Audio plays correctly
✅ Continuations generate properly
✅ User preferences persist
✅ Responsive on mobile

## Rollback Plan

If deployment fails:

1. Check Vercel deployment logs
2. Identify the failing function
3. Revert specific changes:
   ```bash
   git revert HEAD
   git push origin main
   ```
4. Or rollback in Vercel Dashboard:
   **Deployments → Previous Deployment → Promote to Production**

## Post-Launch

### Monitor Usage
- Check Vercel analytics
- Monitor API usage (OpenRouter, ElevenLabs)
- Watch for rate limits

### Optimize if Needed
- Cache frequently accessed feeds
- Reduce API calls where possible
- Optimize content length

## Congratulations! 🎉

Your spooky RSS feed app is now live on Vercel with:
- ✅ RSS feed transformation
- ✅ AI voice narration
- ✅ Story continuation
- ✅ All on free tier!

Share your app: `https://news-necromancer.vercel.app` 👻🎙️
