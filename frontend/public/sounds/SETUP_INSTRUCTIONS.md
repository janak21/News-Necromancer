# Sound Setup Instructions

## Why You Don't Hear Sounds

The sound system is fully implemented and working, but the actual audio files are missing. You need to add three sound files to this directory.

## Quick Setup (5 minutes)

### Step 1: Download Sound Files

Visit one of these free sound libraries:

**Freesound.org** (Recommended)
1. Go to https://freesound.org/
2. Create a free account (required for downloads)
3. Search and download:
   - "ghostly whisper" → Save as `whisper.mp3`
   - "door creak" → Save as `creak.mp3`
   - "horror ambience" → Save as `ambient.mp3`

**Zapsplat.com**
1. Go to https://www.zapsplat.com/
2. Browse Horror > Ambience
3. Download suitable files

### Step 2: Place Files Here

Put the downloaded files in this directory:
```
frontend/public/sounds/
├── whisper.mp3
├── creak.mp3
└── ambient.mp3
```

### Step 3: Test

1. Restart your dev server if running
2. Open the app in your browser
3. Go to Preferences and enable sound effects
4. Hover over a SpookyCard - you should hear a whisper
5. Click to expand a card - you should hear a creak
6. Toggle "Ambient Horror Loop" - you should hear background music

## File Specifications

### whisper.mp3
- **Duration**: 1-2 seconds
- **Type**: Short, subtle ghostly whisper or breath
- **Volume**: Will play at 30% (configured in code)

### creak.mp3
- **Duration**: 2-3 seconds  
- **Type**: Old door creaking or wood groaning
- **Volume**: Will play at 40% (configured in code)

### ambient.mp3
- **Duration**: 30-60 seconds (will loop automatically)
- **Type**: Subtle horror atmosphere with distant sounds
- **Volume**: Will play at 20% (configured in code)

## Optional: Add WebM Format

For better browser compatibility and smaller file sizes, you can also add WebM versions:
- `whisper.webm`
- `creak.webm`
- `ambient.webm`

The system will automatically use WebM in browsers that support it, falling back to MP3.

## Troubleshooting

### Still No Sound?

1. **Check browser console** (F12) for errors
2. **Verify files are in the right location**: `frontend/public/sounds/`
3. **Check file names match exactly**: `whisper.mp3`, `creak.mp3`, `ambient.mp3`
4. **Enable sound in Preferences**: Go to Preferences page and toggle "Enable Sound Effects"
5. **Check browser volume**: Make sure your browser/system volume isn't muted
6. **Try a different browser**: Some browsers block autoplay audio

### Browser Console Check

Open browser console (F12) and type:
```javascript
// Check if sound manager is initialized
window.soundManager = soundManager;
soundManager.isEnabled();  // Should return true if enabled
soundManager.play('whisper');  // Try to play a sound
```

## Alternative: Use Your Own Sounds

You can use any audio files you want! Just:
1. Name them correctly (`whisper.mp3`, `creak.mp3`, `ambient.mp3`)
2. Keep them reasonably small (< 500KB each)
3. Make sure they're in MP3 format (or add WebM versions too)

## Need Help?

Check the main documentation at `frontend/SOUND_SYSTEM_IMPLEMENTATION.md`
