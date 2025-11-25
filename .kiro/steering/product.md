---
inclusion: always
---

## Python Environment

- Use `python3` for all Python commands and scripts
- Target Python 3.11+ (3.13 compatible)
- Use async/await patterns throughout the backend

## Project Architecture

### Backend (FastAPI + Python)
- **Modular structure**: `models/`, `fetcher/`, `remixer/`, `api/`, `config/`, `narration/`
- **Type safety**: Use Pydantic models and full type hints
- **Async-first**: All I/O operations should be async
- **Error handling**: Graceful degradation with themed error messages

### Frontend (React + TypeScript)
- **Component-based**: Organized by feature in `components/` folders
- **TypeScript strict mode**: Full type coverage required
- **Custom hooks**: Reusable logic in `hooks/` directory
- **CSS modules**: Component-scoped styling with `.css` files

## Code Style

### Python
- Follow PEP 8 conventions
- Use dataclasses with `to_dict()` methods for serialization
- Pydantic models for validation and settings
- Structured logging with contextual information
- Environment variables via `python-dotenv`

### TypeScript/React
- Functional components with hooks
- Props interfaces defined inline or exported
- Use `lucide-react` for icons
- `framer-motion` for animations
- Howler.js for audio management

## API Conventions

- RESTful endpoints under `/api/` prefix
- Request/response models use Pydantic schemas
- CORS enabled for frontend communication
- Comprehensive error responses with status codes
- Health check endpoint at `/api/health`

## Testing

- Backend: `pytest` with `pytest-asyncio` for async tests
- Frontend: `vitest` with `@testing-library/react`
- Test files colocated with source or in `tests/` directories
- Mock external API calls (OpenRouter, ElevenLabs)

## Configuration

- Environment variables in `.env` files (never commit)
- `.env.example` templates for required variables
- Backend settings via `backend/config/settings.py`
- Frontend config in `vite.config.ts`

## Key Features

- **Horror transformation**: AI-powered content remixing with intensity levels (1-5)
- **Voice narration**: ElevenLabs integration with 5 voice styles
- **Caching**: File-based caching for narration, in-memory for content
- **Concurrent processing**: Async fetching with rate limiting
- **User preferences**: Persistent storage in localStorage (frontend) and API (backend)

## Dependencies

- Backend: FastAPI, feedparser, openai, elevenlabs, aiohttp, pydantic
- Frontend: React 19, TypeScript, Vite, framer-motion, howler
- Development: pytest, vitest, eslint

## Running the Application

- Backend: `python3 run_backend.py` (port 8000)
- Frontend: `cd frontend && npm run dev` (port 5173)
- Tests: `pytest` (backend), `npm test` (frontend) 