# Deployment Checklist

## ✅ Pre-Deployment
- [x] Environment variables set in Vercel dashboard
- [x] Fixed endpoint routing in `api/feeds/process.py`
- [x] Added CORS middleware
- [x] Added health check endpoint
- [x] Tested endpoint structure locally

## 🚀 Deploy to Vercel

### Option 1: Auto-deploy via Git (Recommended)
```bash
git add api/feeds/process.py
git commit -m "Fix: Correct serverless endpoint routing for Vercel"
git push origin main
```

Vercel will automatically detect the push and deploy.

### Option 2: Manual deploy via CLI
```bash
vercel --prod
```

## 🧪 Post-Deployment Testing

### 1. Test Health Endpoint
```bash
curl https://your-app.vercel.app/api/feeds/process
```

Expected response:
```json
{
  "status": "ok",
  "service": "feed-processing",
  "openrouter_configured": true
}
```

### 2. Test in Browser
1. Visit your Vercel app
2. Navigate to "Spooky Feeds" page
3. Enter a sample RSS URL (e.g., `https://feeds.bbci.co.uk/news/rss.xml`)
4. Click "👻 Haunt Feed"
5. Should see: "🕷️ Summoning dark forces to process your feed..."
6. After ~5-10 seconds: Success message with haunted variants

### 3. Check Vercel Logs (if issues persist)
```bash
vercel logs <your-deployment-url>
```

Or view in dashboard: https://vercel.com/dashboard → Your Project → Deployments → View Function Logs

## 🐛 Troubleshooting

### Still getting 500 errors?
1. Check Vercel function logs for specific error messages
2. Verify environment variables are set for "Production" scope
3. Ensure latest deployment is active (check timestamp)
4. Try redeploying: Settings → Deployments → Redeploy

### Getting timeout errors?
- This is expected for Vercel free tier (10s limit)
- The code is optimized to process 2-3 articles max
- Try with a smaller RSS feed

### CORS errors?
- Should be fixed with the CORS middleware added
- If persists, update `allow_origins` in `api/feeds/process.py` to your specific domain

## 📊 Expected Performance
- Feed fetch: ~1-2 seconds
- OpenRouter API per article: ~2-3 seconds
- Total for 3 articles: ~7-9 seconds (within 10s limit)

## ✅ Success Indicators
- Health endpoint returns `"openrouter_configured": true`
- "Haunt Feed" button generates variants without errors
- Browser console shows no 500 errors
- Haunted variants display with spooky titles and content
