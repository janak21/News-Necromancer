# Sound Effects

This directory contains audio files for the Spooky RSS System.

## Required Sound Files

The following sound files should be placed in this directory:

### 1. Ghostly Whisper (`whisper.mp3` / `whisper.webm`)
- **Usage**: Played on hover interactions
- **Duration**: 1-2 seconds
- **Volume**: Low (0.3)
- **Description**: Subtle ghostly whisper or breath sound

### 2. Creaking Door (`creak.mp3` / `creak.webm`)
- **Usage**: Played when cards expand/collapse
- **Duration**: 2-3 seconds
- **Volume**: Medium (0.4)
- **Description**: Old door creaking or wood groaning sound

### 3. Ambient Horror (`ambient.mp3` / `ambient.webm`)
- **Usage**: Background atmospheric loop
- **Duration**: 30-60 seconds (looping)
- **Volume**: Very low (0.2)
- **Description**: Subtle horror ambience with distant sounds

## File Format Notes

- Provide both MP3 and WebM formats for cross-browser compatibility
- MP3 for broader compatibility
- WebM for better compression and quality in modern browsers
- Keep file sizes small (< 500KB per file) for fast loading

## Sound Sources

You can find royalty-free horror sound effects from:
- [Freesound.org](https://freesound.org/)
- [Zapsplat](https://www.zapsplat.com/)
- [BBC Sound Effects](https://sound-effects.bbcrewind.co.uk/)

## Testing Without Sound Files

The SoundManager will gracefully handle missing sound files and won't break the application. However, no sounds will play until the files are added.
