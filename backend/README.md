# Spooky RSS System Backend

Enhanced modular backend architecture for RSS processing and horror content generation.

## Architecture Overview

The backend consists of four main modules:

### 1. Models (`backend/models/`)
- **data_models.py**: TypeScript-style dataclasses for all system entities
- Core models: `FeedItem`, `SpookyVariant`, `UserPreferences`, `ProcessingStats`
- Full JSON serialization support with `to_dict()` methods

### 2. Fetcher (`backend/fetcher/`)
- **concurrent_fetcher.py**: Async RSS fetching with 100+ feeds/minute capability
- **feed_validator.py**: RSS feed format validation and sanitization
- **error_handler.py**: Graceful error handling with "ghost article" generation
- Connection pooling, rate limiting, and exponential backoff retry

### 3. Remixer (`backend/remixer/`)
- **spooky_remixer.py**: LLM-powered horror content transformation
- **horror_themes.py**: Theme management for different horror categories
- **personalization.py**: User preference-based content customization
- Supports 5 horror types: Gothic, Psychological, Cosmic, Folk, Supernatural

### 4. API (`backend/api/`)
- **main.py**: FastAPI application with middleware and routing
- **routes/**: Modular endpoint organization (feeds, health, preferences)
- **middleware.py**: CORS, logging, and error handling middleware
- **dependencies.py**: Dependency injection for services

### 5. Configuration (`backend/config/`)
- **settings.py**: Pydantic-based configuration management
- **logging_config.py**: Structured logging with spooky formatting
- Environment variable support with `.env` file

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

3. **Run the Backend**:
   ```bash
   python3 run_backend.py
   ```

4. **Test the Setup**:
   ```bash
   python3 test_backend_setup.py
   ```

## API Endpoints

- **POST /api/feeds/process**: Process RSS feeds and generate spooky variants
- **GET /api/variants/{processing_id}**: Retrieve generated variants
- **GET /api/health**: System health check with performance metrics
- **POST /api/preferences**: Update user preferences for personalization
- **GET /api/docs**: Interactive API documentation

## Key Features

✅ **Concurrent Processing**: Handle 100+ RSS feeds per minute  
✅ **Error Resilience**: Ghost article generation for failed feeds  
✅ **User Personalization**: 5 horror types with intensity levels  
✅ **Comprehensive Logging**: Structured logging with spooky emojis  
✅ **Health Monitoring**: System metrics and performance tracking  
✅ **Type Safety**: Full type hints and Pydantic validation  
✅ **Async Architecture**: FastAPI with async/await throughout  

## Configuration Options

Key environment variables:

```bash
# Required
OPENROUTER_API_KEY=your-api-key-here

# Optional
OPENROUTER_MODEL=gpt-3.5-turbo
MAX_CONCURRENT_FEEDS=10
FEED_TIMEOUT=10
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## Development

The backend is designed to be:
- **Modular**: Each component can be developed and tested independently
- **Extensible**: Easy to add new horror themes, fetcher sources, or API endpoints
- **Testable**: Comprehensive error handling and fallback mechanisms
- **Observable**: Detailed logging and health monitoring

## Next Steps

This backend architecture is ready for:
1. Frontend integration (React UI)
2. Database persistence (SQLite/PostgreSQL)
3. Caching layer (Redis)
4. Production deployment (Docker containers)

The modular design ensures each component can be enhanced independently while maintaining system cohesion.