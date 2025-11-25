# GhostRevive - Quick Start Deployment Guide

> **TL;DR:** Your app is deployment-ready. Get Vercel + API keys → 5 minutes to live.

## What You Have

A production-ready full-stack application that transforms RSS feeds into AI-generated horror stories with voice narration.

- **Frontend:** React 19 + TypeScript (builds: 115 KB gzipped)
- **Backend:** FastAPI + Mangum serverless adapter
- **APIs:** OpenRouter (AI) + ElevenLabs (Voice)
- **Status:** ✅ All systems go!

## What We Fixed

1. ✅ TypeScript compilation errors in tests
2. ✅ Verified all Python files compile
3. ✅ Confirmed frontend builds optimized
4. ✅ Validated Vercel configuration
5. ✅ Created comprehensive deployment guides

## Deploy in 5 Minutes

### Step 1: Get Free API Keys (2 min)

**OpenRouter** (AI Generation - Required):
- Go to https://openrouter.ai
- Sign up (free)
- Create API key at https://openrouter.ai/keys
- Copy it

**ElevenLabs** (Voice Narration - Optional):
- Go to https://elevenlabs.io
- Sign up (free - 10K chars/month)
- Get API key from Settings
- Copy it

### Step 2: Install & Deploy (3 min)

```bash
# Install Vercel CLI (one-time)
npm install -g vercel

# Navigate to your project
cd /Users/janak/Documents/BUILD/GhostRevive

# Login
vercel login

# Deploy (creates Vercel project if first time)
vercel --prod
```

### Step 3: Set Environment Variables (0 min)

The CLI will ask for environment variables. Enter them:
- `OPENROUTER_API_KEY=` → paste your OpenRouter key
- `ELEVENLABS_API_KEY=` → paste your ElevenLabs key (optional)

### Step 4: Done! 🎉

Your app is live at: `https://your-project-name.vercel.app`

Share this URL with judges!

## Alternative: Deploy via Web Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Click Deploy
5. Add environment variables in Project Settings
6. Redeploy

## Verify It Works

Check these URLs:

- **Frontend:** https://your-app.vercel.app
- **Health Check:** https://your-app.vercel.app/api/health
- **API Docs:** https://your-app.vercel.app/api/docs

## Auto-Deploy Setup

Every time you push to `main`, it auto-deploys:

```bash
git add .
git commit -m "Your changes"
git push origin main
# Vercel automatically deploys! ✅
```

## Troubleshooting

### Build Failed?
```bash
vercel logs your-app.vercel.app
```
Check the error, fix locally, then push again.

### API returning 500?
- Verify API keys are set in Vercel dashboard
- Check function logs in Vercel
- Ensure `OPENROUTER_API_KEY` is configured

### Timeout (504)?
- Set `NARRATION_ENABLED=false` to disable voice feature
- Or reduce `NARRATION_MAX_CONTENT_LENGTH=3000`

## Cost

**Your monthly bill: $0**

- Vercel free tier: 1M invocations/month
- OpenRouter: ~$0-0.05 (pay as you go)
- ElevenLabs: $0 (free tier: 10K chars)

Great for hackathon! 🎃

## Files to Review

- **DEPLOYMENT_GUIDE.md** - Full deployment walkthrough
- **CODEBASE_ANALYSIS.md** - Architecture deep-dive
- **.env.production.example** - All production settings

## One-Liner Redeploy

```bash
git add . && git commit -m "changes" && git push origin main
# Done! Auto-deployed by Vercel
```

## Support Resources

- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Your new live app:** https://your-project.vercel.app

---

**You're ready to present!** 👻

Questions? Check the detailed guides or search the Vercel docs.

Good luck at Kiroween Hackathon! 🎃✨
