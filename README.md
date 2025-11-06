# Spooky RSS System 👻🎃

A full-stack application that transforms ordinary RSS news feeds into supernatural horror stories. Built with Python FastAPI backend and React TypeScript frontend, featuring real-time feed processing and spooky transformations using AI.

## Features

### Backend (Python FastAPI)
- 🕷️ Concurrent RSS feed fetching with error handling
- 🧙‍♂️ AI-powered horror story transformation using OpenRouter
- 👻 Automatic "ghost article" generation for failed feeds
- 🔮 RESTful API with comprehensive error handling
- 📊 Performance tracking and logging

### Frontend (React TypeScript)
- 🎃 Modern, responsive horror-themed UI
- 🌙 Dark theme with particle effects
- 📱 Mobile-friendly design
- ⚡ Real-time feed processing
- 🎭 Interactive preferences panel
- 👻 Animated ghost notifications

### Horror Transformation
- 🏚️ Multiple horror themes: Gothic, Supernatural, Cosmic, etc.
- 🎪 Customizable intensity levels
- 🔗 Collective narratives connecting all stories
- 🎨 Rich horror vocabulary and atmospheric descriptions

## Quick Start

### Prerequisites
- Python 3.11+ (3.13 compatible)
- Node.js 18+
- OpenRouter API key

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
    "preferences": {
      "preferred_horror_types": ["GOTHIC", "SUPERNATURAL"],
      "intensity_level": 3
    }
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Horror Transformation Features

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

## Configuration

### Environment Variables
```bash
# Required
OPENROUTER_API_KEY=your-api-key-here

# Optional
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