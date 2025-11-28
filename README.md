# News Necromancer 👻🎃

Transform ordinary RSS news feeds into supernatural horror stories with AI-powered voice narration.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://news-necromancer.vercel.app)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 Features

### 📰 RSS Feed Transformation
- Fetch and process multiple RSS feeds simultaneously
- Transform news articles into spine-chilling horror stories
- AI-powered content remixing with adjustable intensity (1-5)
- Multiple horror themes: supernatural, psychological, cosmic, gothic, body horror

### 🎙️ AI Voice Narration
- Generate spooky audio narration using ElevenLabs AI
- 5 distinct horror voice styles:
  - Ethereal Whisper
  - Gothic Narrator
  - Sinister Storyteller
  - Haunted Voice
  - Cryptic Oracle
- Adjustable playback speed and volume controls
- Download narrations as MP3 files

### 📖 Story Continuation
- Continue any horror story with "Continue the Nightmare" feature
- AI generates deeper, more terrifying story extensions
- Escalates supernatural elements while maintaining tone

### 🎨 User Experience
- Dark, atmospheric UI with spooky animations
- Persistent feed storage (localStorage)
- Customizable horror preferences
- Responsive design for all devices
- Accessibility compliant (WCAG AA)

## 🚀 Live Demo

Visit the live app: **[news-necromancer.vercel.app](https://news-necromancer.vercel.app)**

## 🛠️ Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for blazing-fast builds
- **Framer Motion** for animations
- **Howler.js** for audio playback
- **CSS Modules** for styling

### Backend
- **Python 3.11+** with async/await
- **FastAPI** for local development
- **Vercel Serverless Functions** for production
- **OpenRouter API** (GPT-3.5-turbo) for story generation
- **ElevenLabs API** (free tier) for voice narration

### Deployment
- **Vercel** (free tier)
- Serverless architecture
- Optimized for <10 second function timeouts

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenRouter API key ([get one here](https://openrouter.ai/keys))
- ElevenLabs API key ([get one here](https://elevenlabs.io/))

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/News-Necromancer.git
cd News-Necromancer
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# OPENROUTER_API_KEY=your_key_here
# ELEVENLABS_API_KEY=your_key_here
```

3. **Install backend dependencies**
```bash
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
```

5. **Run the application**

Terminal 1 (Backend):
```bash
python3 run_backend.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` to see the app!

## 🌐 Deployment to Vercel

### Quick Deploy

1. **Fork this repository**

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your forked repository

3. **Set Environment Variables**
   
   In Vercel Dashboard → Settings → Environment Variables, add:
   ```
   OPENROUTER_API_KEY=your_openrouter_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   OPENROUTER_MODEL=openai/gpt-3.5-turbo
   ```

4. **Deploy**
   - Vercel will automatically build and deploy
   - Your app will be live in ~2-3 minutes!

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📖 Usage

### Transform RSS Feeds

1. Navigate to "Spooky Feeds" page
2. Enter an RSS feed URL (or use sample feeds)
3. Click "👻 Haunt Feed"
4. Wait 5-8 seconds for AI transformation
5. Browse your haunted news variants!

### Generate Voice Narration

1. On any haunted variant, click the narration button
2. Wait 3-7 seconds for audio generation
3. Audio plays automatically
4. Use controls to pause, adjust speed, or download

### Continue Stories

1. Click "Continue the Nightmare" on any variant
2. AI generates a continuation in 3-5 seconds
3. Read the extended horror story
4. Continue multiple times for longer tales

## 🎨 Customization

### User Preferences

- **Horror Types**: Choose preferred themes (supernatural, psychological, etc.)
- **Intensity Level**: Adjust scare factor (1-5)
- **Content Filters**: Filter out specific themes
- **Voice Style**: Select preferred narration voice

### Theme Customization

Edit `frontend/src/styles/variables.css` to customize colors:
```css
--color-primary: #8A2BE2;  /* Purple */
--color-accent: #00ffff;   /* Cyan */
--color-background: #0a0a0f; /* Dark background */
```

## 🏗️ Architecture

### Serverless Functions

- `api/feeds/process.py` - RSS feed processing and transformation
- `api/narration/generate.py` - Voice narration generation
- `api/story_continue.py` - Story continuation
- `api/health.py` - Health check endpoint

All functions use `BaseHTTPRequestHandler` for Vercel compatibility.

### Frontend Structure

```
frontend/src/
├── components/     # Reusable UI components
├── pages/         # Page components
├── hooks/         # Custom React hooks
├── services/      # API service layer
├── contexts/      # React contexts
├── types/         # TypeScript type definitions
└── styles/        # Global styles
```

## 🧪 Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 API Documentation

### Feed Processing
```
POST /api/feeds/process
Body: {
  "urls": ["https://feeds.bbci.co.uk/news/rss.xml"],
  "variant_count": 1,
  "intensity": 3
}
```

### Voice Narration
```
POST /api/narration/generate
Body: {
  "variant_id": "abc-123",
  "content": "Story text...",
  "voice_style": "eerie_narrator",
  "intensity_level": 3
}
```

### Story Continuation
```
POST /api/story_continue
Body: {
  "variant_id": "abc-123",
  "content": "Original story...",
  "continuation_length": 500
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenRouter** for AI model access
- **ElevenLabs** for voice synthesis
- **Vercel** for hosting
- **React** and **FastAPI** communities

## 📧 Contact

- **Live App**: [news-necromancer.vercel.app](https://news-necromancer.vercel.app)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/News-Necromancer/issues)

## 🎃 Happy Haunting!

Transform your news reading experience into a spine-chilling adventure with News Necromancer! 👻
