# Fix for Vercel 500 Error - "Something Went Terribly Wrong"

## Problem
When clicking "Haunt Feed" on the deployed Vercel app, you get a 500 error because the `OPENROUTER_API_KEY` environment variable is not set in Vercel.

## Root Cause
The serverless function `api/feeds/process.py` checks for `OPENROUTER_API_KEY` at line 67-69:
```python
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    logger.error("OPENROUTER_API_KEY environment variable is missing")
    raise ValueError("Server configuration error: OPENROUTER_API_KEY not set")
```

Your local `.env` file has these keys, but Vercel doesn't automatically use them.

## Solution

### Method 1: Vercel Dashboard (Easiest)

1. Go to https://vercel.com/dashboard
2. Select your project: **news-necromancer**
3. Navigate to **Settings** → **Environment Variables**
4. Add these variables:

   | Name | Value | Environment |
   |------|-------|-------------|
   | `OPENROUTER_API_KEY` | `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` | Production, Preview, Development |
   | `ELEVENLABS_API_KEY` | `sk_aaf84857f5b144a7f6cc033e3a933f2e1d522f94d8183e78` | Production, Preview, Development |
   | `OPENROUTER_MODEL` | `openai/gpt-3.5-turbo` | Production, Preview, Development |

5. Click **Save** for each variable
6. Go to **Deployments** tab
7. Find your latest deployment
8. Click the three dots (⋯) → **Redeploy**
9. Wait for deployment to complete (~2-3 minutes)

### Method 2: Vercel CLI

Run this command from your project directory:

```bash
# Run the setup script
./setup_vercel_env.sh

# Then redeploy
vercel --prod
```

Or manually add each variable:

```bash
# Add OPENROUTER_API_KEY
vercel env add OPENROUTER_API_KEY production
# Paste: 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

# Add ELEVENLABS_API_KEY
vercel env add ELEVENLABS_API_KEY production
# Paste: sk_aaf84857f5b144a7f6cc033e3a933f2e1d522f94d8183e78

# Add OPENROUTER_MODEL
vercel env add OPENROUTER_MODEL production
# Paste: openai/gpt-3.5-turbo

# Redeploy
vercel --prod
```

## Verification

After redeploying:

1. Visit your Vercel app
2. Go to the "Spooky Feeds" page
3. Click "Haunt Feed" with a sample RSS URL
4. You should now see the haunted variants being generated successfully

## Additional Notes

- **Security**: These API keys are visible in this document. Consider rotating them after fixing the issue.
- **Cost**: OpenRouter and ElevenLabs charge per API call. Monitor your usage.
- **Timeout**: Vercel free tier has a 10-second function timeout. The code is optimized to stay under this limit.
- **Logs**: Check Vercel function logs if you still see errors: `vercel logs <deployment-url>`

## What Changed

The app works locally because your `.env` file contains these keys. Vercel deployments need environment variables set separately through their dashboard or CLI.
