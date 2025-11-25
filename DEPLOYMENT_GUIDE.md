# GhostRevive - Complete Deployment Guide for Kiroween Hackathon

## Overview

GhostRevive is a full-stack application consisting of:
- **Frontend**: React + TypeScript (Vite) - Static site
- **Backend**: Python FastAPI - Serverless functions
- **External APIs**: OpenRouter (AI), ElevenLabs (Voice narration)

This guide covers deploying to free tier hosting services suitable for hackathon judging.

---

## Free Hosting Options Ranked

### 1. **Vercel** (RECOMMENDED) ⭐⭐⭐⭐⭐
**Why it's best for your app:**
- Free tier with 1M monthly invocations
- Perfect for FastAPI serverless backend
- Frontend static hosting included
- Already have `vercel.json` configured
- Automatic deployments from Git
- Custom domain support

**Free tier limits:**
- 1M serverless function invocations/month
- 100 GB bandwidth/month
- 10 second max function duration
- 1024 MB memory per function

**Deployment time:** ~5 minutes

---

### 2. **Railway**
**Why consider it:**
- $5 monthly credit (free tier)
- Full Docker container support
- Easy database integration
- Good for small projects

**Limitations:**
- Credit runs out quickly with heavy API usage
- Less straightforward for serverless functions

---

### 3. **Render**
**Why consider it:**
- Free static hosting
- Free tier services with usage limits
- Good for databases

**Limitations:**
- No free serverless functions
- Would need to use paid tier for backend

---

### 4. **Fly.io**
**Why consider it:**
- Free tier tier with 3 shared-cpu-1x 256MB VMs
- Can run FastAPI app directly
- Global deployment

**Limitations:**
- More setup complexity
- Lower free tier resource allocation

---

## Recommended: Deploy to Vercel

### Prerequisites
1. GitHub account with your code pushed
2. Vercel account (free signup at vercel.com)
3. OpenRouter API key (free tier available)
4. ElevenLabs API key (free tier available)

### Step 1: Prepare Your Repository

```bash
# Ensure all changes are committed
cd /Users/janak/Documents/BUILD/GhostRevive
git status

# If there are uncommitted changes, commit them
git add .
git commit -m "Fix TypeScript test issues for deployment"
git push origin main
```

### Step 2: Prepare Environment Variables

Your app needs these API keys. Get them free:

**OpenRouter (AI Content Generation):**
1. Visit https://openrouter.ai
2. Sign up (free)
3. Go to https://openrouter.ai/keys
4. Create an API key
5. Copy the key

**ElevenLabs (Voice Narration - Optional):**
1. Visit https://elevenlabs.io
2. Sign up (free - includes 10,000 characters/month)
3. Go to Settings > API Keys
4. Create an API key
5. Copy the key

### Step 3: Deploy via Vercel CLI (Local)

**Option A: Using CLI (Simplest)**

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to your project
cd /Users/janak/Documents/BUILD/GhostRevive

# Login to Vercel
vercel login

# Link to Vercel project (creates if doesn't exist)
vercel link

# Set environment variables
vercel env add OPENROUTER_API_KEY
# Paste your API key when prompted

vercel env add ELEVENLABS_API_KEY
# Paste your API key when prompted (can skip if not using narration)

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

**Option B: Using Vercel Dashboard (Web UI)**

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Select "Import Git Repository"
4. Search for your repository and import
5. Configure build settings:
   - Framework: Other (will auto-detect)
   - Root Directory: `./`
6. Add environment variables:
   - Click "Environment Variables"
   - Add `OPENROUTER_API_KEY`
   - Add `ELEVENLABS_API_KEY`
7. Click "Deploy"

### Step 4: Verify Deployment

After deployment completes:

1. **Check Frontend**
   - Visit your Vercel domain (e.g., `your-app.vercel.app`)
   - You should see the spooky UI load

2. **Check API Health**
   - Visit `https://your-app.vercel.app/api/health`
   - Should return: `{"status":"ok","service":"Spooky RSS System API"}`

3. **Test RSS Processing**
   - In the UI, enter RSS feeds
   - Try processing them
   - Should see horror-transformed content

4. **Check Logs**
   - In Vercel Dashboard → Deployments → Logs
   - Look for any errors in the function logs

### Step 5: Enable Automatic Deployments

Your app will auto-deploy when you push to main:

1. Go to Vercel Dashboard
2. Select your project
3. Go to Settings → Git
4. Verify GitHub is connected
5. Verify "Production Branch" is set to `main`

Now every push to `main` auto-deploys!

---

## Deployment Checklist

- [ ] All code committed and pushed to GitHub
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Python dependencies in `requirements.txt` 
- [ ] `vercel.json` configured correctly
- [ ] OpenRouter API key obtained
- [ ] ElevenLabs API key obtained (optional)
- [ ] Environment variables set in Vercel
- [ ] Deployment successful
- [ ] Frontend loads at your domain
- [ ] API health endpoint responds
- [ ] RSS feed processing works

---

## Troubleshooting

### Deployment Fails

**Check build logs:**
```bash
vercel logs your-app.vercel.app
```

**Common issues:**
1. Missing dependencies in `requirements.txt` - ADD THEM
2. Incorrect Python version - Uses 3.11 by default (configured in `vercel.json`)
3. API key not set - Re-add environment variables and redeploy

### API Returns 500 Error

**Check the API logs:**
1. Go to Vercel Dashboard
2. Select your project
3. Go to Deployments
4. Click the failed deployment
5. View the function logs
6. Look for error messages

**Common causes:**
- Missing API key (OPENROUTER_API_KEY not set)
- Invalid API key format
- ElevenLabs quota exceeded (check your account)

### API Timeout (504)

Your function is taking too long (>10 seconds):

1. Disable narration feature (takes time):
   - Add env var: `NARRATION_ENABLED=false`
   - Redeploy

2. Reduce content processing:
   - Set `NARRATION_MAX_CONTENT_LENGTH=3000`
   - Redeploy

### CORS Errors

Your frontend can't reach the API:

1. Make sure you're using the correct API URL (should be auto-detected)
2. Check Vercel routing in `vercel.json`
3. Verify frontend is on the same Vercel domain

---

## Cost Analysis

### Monthly Cost for Typical Hackathon Usage

**Vercel (Frontend + Backend):**
- Static hosting: $0 (free tier)
- 1M API invocations: $0 (free tier)
- Bandwidth: $0 (100GB free, typically under 10GB)
- **Total: $0**

**OpenRouter API:**
- Pricing: $0.0003-0.001 per 1K tokens depending on model
- ~100 requests × 500 tokens average = ~50K tokens/month
- Estimated cost: $0.02-0.05/month
- **Free tier usually sufficient for hackathon**

**ElevenLabs API:**
- Free tier: 10,000 characters/month
- Paid: $11+/month for more
- **Free tier usually sufficient**

**Total estimated cost: $0-0.10/month**

---

## For Hackathon Judges

### Sharing Your URL

1. Your app will be live at: `https://your-app.vercel.app`
2. Share this URL with judges
3. They can:
   - Enter RSS feeds
   - Adjust horror intensity (1-5 scale)
   - Listen to narrated stories
   - Process multiple feeds simultaneously

### Monitoring During Hackathon

**Watch your usage in real-time:**
1. Go to Vercel Dashboard
2. Select your project
3. View "Usage" tab
4. Monitor API invocations and bandwidth

**Set up alerts (optional):**
1. Dashboard → Settings → Alerts
2. Create alerts for high function invocations

---

## Quick Redeploy When Fixing Issues

```bash
# Make your changes locally
# Test if needed: npm run build

# Commit changes
git add .
git commit -m "Fix: description of your fix"
git push origin main

# Vercel auto-deploys! Check dashboard for progress.

# Or manually redeploy
vercel --prod
```

---

## Alternative: Deploy Backend Separately

If you want more flexibility:

1. **Frontend on Vercel** (recommended)
   - Zero config needed
   - Static hosting

2. **Backend on Railway** (also free)
   - Better control over Python environment
   - Can use full FastAPI features
   - Update frontend API URL to Railway endpoint

3. **Backend on Render**
   - Similar to Railway
   - Free tier slower startup

For hackathon, stick with Vercel for everything - it's simplest.

---

## Performance Tips

### To stay within free tier limits:

1. **Enable caching** (default is on)
   - Reduces duplicate API calls

2. **Set reasonable limits** (already done in `.env.production.example`):
   ```
   NARRATION_MAX_CONTENT_LENGTH=5000
   NARRATION_TIMEOUT=9
   ```

3. **Monitor usage**:
   - Check Vercel Dashboard weekly
   - If approaching limits, disable narration or reduce variant count

4. **Optimize response sizes**:
   - Already configured with Gzip compression

---

## Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Your API Keys**:
  - OpenRouter: https://openrouter.ai/keys
  - ElevenLabs: https://elevenlabs.io/

---

## Summary

**You're ready to deploy!** Follow these steps:

1. ✅ Push code to GitHub
2. ✅ Get API keys (OpenRouter, ElevenLabs)
3. ✅ Deploy via Vercel (CLI or Dashboard)
4. ✅ Test at your live URL
5. ✅ Share with judges!

**Estimated total time:** 10-15 minutes

Good luck at Kiroween Hackathon! 👻🎃
