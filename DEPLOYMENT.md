# Vercel Deployment Guide

This guide provides step-by-step instructions for deploying the Spooky RSS System to Vercel's free (Hobby) tier.

## Prerequisites

- Node.js 18+ installed
- Python 3.11+ installed
- Git repository with your code
- Vercel account (free tier)
- OpenRouter API key
- ElevenLabs API key

## Quick Start

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate with your Vercel account.

### 3. Link Your Project

Navigate to your project directory and run:

```bash
vercel link
```

This will connect your local project to a Vercel project.

### 4. Set Environment Variables

Set required environment variables in Vercel:

```bash
# Required variables
vercel env add OPENROUTER_API_KEY
vercel env add ELEVENLABS_API_KEY

# Optional variables (with defaults)
vercel env add ENVIRONMENT
vercel env add LOG_LEVEL
vercel env add NARRATION_ENABLED
```

When prompted, enter the values for each variable. You can also set these in the Vercel Dashboard under Settings > Environment Variables.

### 5. Deploy to Preview

Test your deployment in a preview environment:

```bash
vercel
```

This creates a preview deployment with a unique URL. Test all functionality before deploying to production.

### 6. Deploy to Production

Once you've verified the preview deployment works:

```bash
vercel --prod
```

Your application is now live at your production URL!

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | API key for OpenRouter AI service | `sk-or-v1-...` |
| `ELEVENLABS_API_KEY` | API key for ElevenLabs voice service | `sk_...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `OPENROUTER_MODEL` | AI model to use | `gpt-3.5-turbo` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `NARRATION_ENABLED` | Enable voice narration | `true` |
| `NARRATION_MAX_CONCURRENT` | Max concurrent narrations | `1` |
| `NARRATION_MAX_CONTENT_LENGTH` | Max content length (chars) | `5000` |
| `NARRATION_TIMEOUT` | Narration timeout (seconds) | `9` |
| `ENABLE_CACHING` | Enable in-memory caching | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | Your Vercel URL |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per IP | `100` |
| `DEBUG` | Enable debug mode | `false` |

See `.env.production.example` for the complete list with descriptions.

## Project Structure

```
.
├── vercel.json              # Vercel configuration
├── api/                     # Serverless functions
│   ├── health.py           # Health check endpoint
│   ├── feeds/              # Feed processing endpoints
│   └── narration/          # Narration endpoints
├── frontend/               # React frontend
│   ├── dist/              # Build output (generated)
│   └── package.json       # Includes vercel-build script
└── backend/               # Python backend (source)
```

## Vercel Configuration

The `vercel.json` file defines how Vercel builds and deploys your application:

- **Frontend**: Built as static assets using Vite
- **Backend**: Deployed as Python serverless functions
- **Routes**: API requests go to `/api/*`, everything else to frontend

## Vercel Free Tier Limits

Your deployment must stay within these limits:

- **Function Duration**: 10 seconds max per invocation
- **Function Memory**: 1024 MB max
- **Invocations**: 1 million per month
- **Bandwidth**: 100 GB per month
- **Build Time**: 45 minutes max
- **Concurrent Builds**: 1 at a time

## Continuous Deployment

### Connect to Git

1. Go to Vercel Dashboard
2. Select your project
3. Go to Settings > Git
4. Connect your GitHub/GitLab/Bitbucket repository

Once connected:
- **Pull Requests**: Automatically create preview deployments
- **Main Branch**: Automatically deploy to production on merge

### Manual Deployment

You can also deploy manually using the CLI:

```bash
# Deploy current branch to preview
vercel

# Deploy specific branch to production
vercel --prod
```

## Monitoring and Logs

### View Logs

```bash
# View real-time logs
vercel logs --follow

# View logs for specific deployment
vercel logs [deployment-url]
```

### View Deployments

```bash
# List all deployments
vercel ls

# Inspect specific deployment
vercel inspect [deployment-url]
```

### Vercel Dashboard

Access detailed metrics in the Vercel Dashboard:
- Function invocations
- Bandwidth usage
- Error rates
- Performance metrics

## Troubleshooting

### Build Failures

**Problem**: Deployment fails during build

**Solutions**:
1. Check build logs: `vercel logs [deployment-url]`
2. Test build locally: `npm run build` (frontend) and verify Python dependencies
3. Verify all dependencies are in `requirements.txt` and `package.json`

### Function Timeouts

**Problem**: 504 Gateway Timeout errors

**Solutions**:
1. Reduce `NARRATION_MAX_CONTENT_LENGTH` to process less content
2. Set `NARRATION_ENABLED=false` to disable slow narration feature
3. Optimize code to complete within 10 seconds

### Environment Variables Not Found

**Problem**: Application fails with missing environment variable errors

**Solutions**:
1. Verify variables in Vercel Dashboard: Settings > Environment Variables
2. Ensure variables are set for correct environment (Production/Preview/Development)
3. Redeploy after adding variables: `vercel --prod`

### CORS Errors

**Problem**: Frontend can't access API due to CORS

**Solutions**:
1. Set `CORS_ORIGINS` to your Vercel domain
2. Verify API routes are configured correctly in `vercel.json`
3. Check browser console for specific CORS error messages

### Rate Limit Exceeded

**Problem**: 429 Too Many Requests errors

**Solutions**:
1. Implement client-side caching to reduce API calls
2. Increase `RATE_LIMIT_PER_MINUTE` if needed
3. Monitor usage in Vercel Dashboard

## Rollback

If a deployment has issues, rollback to a previous version:

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel promote [deployment-url]
```

Or use the Vercel Dashboard:
1. Go to Deployments
2. Find a working deployment
3. Click "Promote to Production"

## Cost Optimization

To stay within free tier limits:

1. **Enable Caching**: Reduce duplicate API calls
2. **Optimize Responses**: Minimize response sizes
3. **Rate Limiting**: Prevent abuse
4. **Feature Gating**: Make expensive features optional
5. **Monitor Usage**: Check Vercel Dashboard regularly

## Next Steps

After successful deployment:

1. Test all features in production
2. Set up monitoring and alerts
3. Configure custom domain (optional)
4. Enable automatic deployments from Git
5. Monitor usage to stay within free tier limits

## Support

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Project Issues**: [Your GitHub Issues URL]

## Security Notes

- Never commit API keys to version control
- Use Vercel's encrypted environment variables
- Keep `DEBUG=false` in production
- Regularly rotate API keys
- Monitor for unusual activity in Vercel Dashboard
