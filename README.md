# Spooky RSS System 👻🎃

A full-stack application that transforms ordinary RSS news feeds into supernatural horror stories. Built with Python FastAPI backend and React TypeScript frontend, featuring real-time feed processing and spooky transformations using AI.

## Features

### Backend (Python FastAPI)
- 🕷️ Concurrent RSS feed fetching with error handling
- 🧙‍♂️ AI-powered horror story transformation using OpenRouter
- 👻 Automatic "ghost article" generation for failed feeds
- 🔮 RESTful API with comprehensive error handling
- 📊 Performance tracking and logging
- 📖 Story continuation endpoint with caching
- 🎯 Intensity-specific narrative generation
- 💾 In-memory caching for improved performance

### Frontend (React TypeScript)
- 🎃 Modern, responsive horror-themed UI
- 🌙 Dark theme with particle effects and parallax backgrounds
- 📱 Mobile-friendly design with smooth animations
- ⚡ Real-time feed processing with loading states
- 🎭 Interactive preferences panel with intensity slider
- 👻 Animated ghost notifications
- 🔊 Atmospheric sound effects (whispers, creaks, ambient)
- 💾 Local storage persistence for feeds and preferences
- 🌙 Story continuation feature - extend narratives with AI
- 🎙️ AI-powered voice narration with multiple horror voice styles

### Horror Transformation
- 🏚️ Multiple horror themes: Gothic, Supernatural, Cosmic, etc.
- 🎪 Customizable intensity levels (1-5 scale)
- 🔗 Collective narratives connecting all stories
- 🎨 Rich horror vocabulary and atmospheric descriptions
- 📖 Story continuation system (300-500 words)
- 🎯 Maintains narrative consistency and horror themes

## Quick Start

### Prerequisites
- Python 3.11+ (3.13 compatible)
- Node.js 18+
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai/))
- ElevenLabs API key (optional, for voice narration - get one at [elevenlabs.io](https://elevenlabs.io/))

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/spooky-rss-system.git
cd spooky-rss-system

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenRouter API key
# Optionally add your ElevenLabs API key for voice narration

# Run the backend
python run_backend.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
spooky-rss-system/
├── backend/                 # Python FastAPI backend
│   ├── api/                # API routes and middleware
│   ├── config/             # Configuration management
│   ├── fetcher/            # RSS feed fetching logic
│   ├── models/             # Data models and schemas
│   └── remixer/            # Horror transformation engine
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── services/       # API communication
│   │   └── hooks/          # Custom React hooks
│   └── public/             # Static assets
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
└── run_backend.py         # Backend entry point
```

## API Usage

### Process RSS Feeds
```bash
curl -X POST "http://localhost:8000/api/feeds/process" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://rss.cnn.com/rss/edition.rss"],
    "variant_count": 3,
    "intensity": 3,
    "user_preferences": {
      "preferred_horror_types": ["GOTHIC", "SUPERNATURAL"],
      "intensity_level": 3
    }
  }'
```

### Continue a Story
```bash
curl -X POST "http://localhost:8000/api/feeds/variants/{variant_id}/continue" \
  -H "Content-Type: application/json" \
  -d '{
    "continuation_length": 400
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Horror Transformation Features

### Story Continuation System
- **Continue the Nightmare**: Extend any horror story with AI-generated continuations
- **Narrative Consistency**: Maintains original themes, tone, and intensity
- **Customizable Length**: 300-500 word continuations
- **Smart Caching**: Reduces API calls and improves performance
- **Intensity Preservation**: Keeps the same horror level throughout

### Intelligent Error Handling
- **Dead Feed Resurrection**: 3 automatic retry attempts with exponential backoff
- **Ghost Articles**: Creates supernatural placeholder content for failed feeds
- **Spooky Error Messages**: Themed error handling throughout the system

### Horror Themes Available
- **Gothic**: Dark castles, ancient curses, mysterious fog
- **Supernatural**: Ghosts, spirits, otherworldly phenomena  
- **Cosmic**: Eldritch horrors, unknown dimensions, cosmic dread
- **Psychological**: Mind-bending terror, reality distortion
- **Body Horror**: Grotesque transformations, biological nightmares

### User Experience Features
- **Intensity Slider**: Adjust horror level from gentle whispers (1) to absolute terror (5)
- **Sound Effects**: Atmospheric audio including whispers, creaks, and ambient sounds
- **Data Persistence**: Feeds and preferences saved locally in browser
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Dark Theme**: Immersive horror aesthetic with particle effects

## AI Voice Narration 🎙️

Transform your horror reading experience into an immersive audio journey with AI-powered voice narration. Each spooky story can be narrated in distinct horror voice styles that match the intensity and theme of the content.

### Available Voice Styles

The system supports 5 distinct horror voice archetypes, each bringing unique atmospheric qualities:

1. **👻 Ghostly Whisper**
   - Ethereal, breathy voice with supernatural echoes
   - Perfect for: Ghost stories, haunted locations, spectral encounters
   - Characteristics: Soft, whispering tone with otherworldly reverb
   - Best intensity: 2-4

2. **😈 Demonic Growl**
   - Deep, menacing voice with guttural undertones
   - Perfect for: Demonic possession, infernal encounters, dark rituals
   - Characteristics: Low pitch, threatening, with occasional growls
   - Best intensity: 4-5

3. **🎭 Eerie Narrator**
   - Classic horror storyteller with dramatic flair
   - Perfect for: Gothic tales, mystery horror, atmospheric stories
   - Characteristics: Clear enunciation, dramatic pauses, suspenseful delivery
   - Best intensity: 2-4

4. **👶 Possessed Child**
   - Innocent voice corrupted by malevolent presence
   - Perfect for: Psychological horror, possession stories, unsettling narratives
   - Characteristics: Child-like with disturbing undertones
   - Best intensity: 3-5

5. **🌌 Ancient Entity**
   - Timeless, cosmic voice from beyond comprehension
   - Perfect for: Cosmic horror, eldritch tales, reality-bending stories
   - Characteristics: Deep, resonant, with unnatural cadence
   - Best intensity: 4-5

### Setup Instructions

#### 1. Get Your ElevenLabs API Key
1. Visit [elevenlabs.io](https://elevenlabs.io/) and create an account
2. Navigate to your profile settings
3. Generate an API key
4. Copy the key for configuration

#### 2. Configure Backend
Add your ElevenLabs API key to the `.env` file:

```bash
# Required for voice narration
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# Optional narration settings
NARRATION_CACHE_DIR=./cache/narration
NARRATION_CACHE_MAX_SIZE_MB=500
NARRATION_CACHE_TTL_DAYS=7
NARRATION_MAX_CONCURRENT=3
NARRATION_MAX_CONTENT_LENGTH=10000
```

#### 3. Restart Backend
```bash
python run_backend.py
```

The narration feature will now be available in the frontend!

### Using Voice Narration

1. **Select a Voice Style**: Click on any spooky variant card to expand the audio player
2. **Choose Your Voice**: Select from the 5 available horror voice styles
3. **Generate Narration**: Click "Generate Narration" to create the audio
4. **Wait for Generation**: Watch the progress indicator (typically 10-30 seconds)
5. **Listen & Control**: Use the audio player controls to play, pause, seek, and adjust speed

### Audio Player Features

#### Playback Controls
- **Play/Pause**: Start or pause narration playback
- **Progress Bar**: Visual timeline with click-to-seek functionality
- **Time Display**: Shows current position and total duration
- **Speed Control**: Adjust playback rate from 0.5x to 2.0x
- **Download**: Save narration as MP3 file for offline listening

#### Keyboard Shortcuts
Enhance your experience with keyboard controls:

- **Spacebar**: Play/Pause toggle
- **Left Arrow (←)**: Seek backward 5 seconds
- **Right Arrow (→)**: Seek forward 5 seconds
- **Shift + Up (↑)**: Increase playback speed
- **Shift + Down (↓)**: Decrease playback speed

#### Accessibility Features
- **Screen Reader Support**: All controls have ARIA labels
- **Keyboard Navigation**: Full keyboard control without mouse
- **Focus Indicators**: Visible focus states on all interactive elements
- **Live Regions**: Playback state changes announced to screen readers
- **High Contrast**: Controls visible in dark theme

### Smart Caching System

The narration system includes intelligent caching to improve performance:

- **Automatic Caching**: Generated audio is cached for 7 days
- **Instant Playback**: Previously generated narrations load immediately
- **Storage Management**: LRU eviction when cache exceeds 500MB
- **Browser Cache**: URLs cached in localStorage for quick access

### Voice Intensity Mapping

Voice characteristics automatically adjust based on horror intensity level:

| Intensity | Voice Characteristics |
|-----------|----------------------|
| Level 1 | Gentle, subtle horror elements |
| Level 2 | Moderate atmospheric effects |
| Level 3 | Noticeable horror qualities |
| Level 4 | Strong dramatic effects |
| Level 5 | Maximum terror, extreme effects |

### Generation Queue

The system manages multiple narration requests efficiently:

- **Concurrent Processing**: Up to 3 narrations generated simultaneously
- **Priority Queue**: Visible content prioritized over off-screen
- **Queue Position**: See your place in line during high demand
- **Cancellation**: Cancel queued requests at any time
- **Status Tracking**: Real-time progress updates

### API Endpoints

#### Generate Narration
```bash
curl -X POST "http://localhost:8000/api/narration/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": "variant-123",
    "voice_style": "ghostly_whisper",
    "intensity_level": 3,
    "priority": "normal"
  }'
```

#### Check Generation Status
```bash
curl "http://localhost:8000/api/narration/status/{request_id}"
```

#### Get Audio File
```bash
curl "http://localhost:8000/api/narration/audio/{narration_id}" \
  --output narration.mp3
```

#### List Available Voices
```bash
curl "http://localhost:8000/api/narration/voices"
```

#### Cancel Generation
```bash
curl -X DELETE "http://localhost:8000/api/narration/cancel/{request_id}"
```

### Troubleshooting

#### No Audio Generated
- Verify your ElevenLabs API key is correctly set in `.env`
- Check backend logs for API errors: `logs/spooky_rss_system.log`
- Ensure you have available API credits on ElevenLabs

#### Slow Generation
- Generation time depends on content length (typically 10-30 seconds)
- Check your internet connection
- ElevenLabs API may experience high demand during peak hours

#### Playback Issues
- Ensure your browser supports MP3 audio playback
- Check browser console for errors
- Try clearing browser cache and localStorage

#### Cache Issues
- Cache directory must have write permissions
- Check available disk space (500MB recommended)
- Manually clear cache: `rm -rf cache/narration/*`

## Configuration

### Environment Variables
```bash
# Required
OPENROUTER_API_KEY=your-api-key-here

# Optional - Voice Narration
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
NARRATION_CACHE_DIR=./cache/narration
NARRATION_CACHE_MAX_SIZE_MB=500
NARRATION_CACHE_TTL_DAYS=7
NARRATION_MAX_CONCURRENT=3
NARRATION_MAX_CONTENT_LENGTH=10000

# Optional - General
OPENROUTER_MODEL=gpt-3.5-turbo
HOST=0.0.0.0
PORT=8000
MAX_CONCURRENT_FEEDS=10
LOG_LEVEL=INFO
```

### Supported AI Models
- **gpt-3.5-turbo**: Fast and cost-effective
- **gpt-4**: Higher quality, more creative
- **anthropic/claude-3-sonnet**: Excellent for creative writing
- **meta-llama/llama-2-70b-chat**: Open source alternative
- **mistralai/mistral-7b-instruct**: European AI model

## Development

### Running Tests
```bash
# Backend tests
python -m pytest

# Frontend tests  
cd frontend
npm test
```

### Development Mode
```bash
# Backend with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Frontend with hot reload
cd frontend
npm run dev
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://reactjs.org/)
- AI transformations powered by [OpenRouter](https://openrouter.ai/)
- Horror themes inspired by classic supernatural literature