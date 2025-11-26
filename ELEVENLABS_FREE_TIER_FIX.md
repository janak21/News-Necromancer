# ElevenLabs Free Tier Fix

## Problem Found! ✅

The error message revealed the real issue:
```
"Model is not available on the free tier. The eleven_monolingual_v1 and 
eleven_multilingual_v1 models are removed from free tier."
```

Your ElevenLabs API key is **valid**, but the free tier no longer supports the `eleven_monolingual_v1` model we were using.

## Solution Applied

Changed the model from `eleven_monolingual_v1` to `eleven_turbo_v2_5` (free tier compatible):

```python
payload = {
    "text": content,
    "model_id": "eleven_turbo_v2_5",  # Free tier compatible model
    "voice_settings": {
        "stability": min(stability, 1.0),
        "similarity_boost": min(similarity_boost, 1.0)
    }
}
```

## Free Tier Compatible Models

ElevenLabs free tier supports:
- ✅ `eleven_turbo_v2_5` (latest, fastest)
- ✅ `eleven_turbo_v2` (also works)

## Deploy the Fix

```bash
git add api/narration/generate.py
git commit -m "Fix: Use eleven_turbo_v2_5 model for ElevenLabs free tier compatibility"
git push origin main
```

## Test After Deployment

1. Wait ~2-3 minutes for Vercel to deploy
2. Go to your app → Generate a haunted feed
3. Click the narration/audio button on a variant
4. Should now generate and play audio successfully! 🎙️

## What Changed

### Before
```python
"model_id": "eleven_monolingual_v1"  # ❌ Not available on free tier
```

### After
```python
"model_id": "eleven_turbo_v2_5"  # ✅ Free tier compatible
```

## Free Tier Limitations

ElevenLabs free tier includes:
- ✅ 10,000 characters per month
- ✅ Access to turbo models (v2, v2_5)
- ✅ All pre-made voices
- ❌ No access to v1 models (monolingual, multilingual)
- ❌ Limited voice customization

This should be sufficient for testing and light usage!

## Expected Behavior

After deployment:
1. Click narration button → Shows "Generating..."
2. ~3-7 seconds later → Audio generated
3. Audio player appears with play/pause controls
4. Spooky narration plays! 👻🎙️
