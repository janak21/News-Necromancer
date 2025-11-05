# Haunted RSS Parser 👻🎃

A Python RSS parser that fetches news feeds and transforms them into supernatural horror stories with ghosts, curses, and otherworldly themes using OpenAI's GPT.

## Features

- Fetches RSS feeds from multiple URLs
- Transforms each article into haunted versions with horror themes
- Includes specific supernatural elements: ghosts, curses, haunted locations, vengeful spirits
- Outputs structured JSON with both original and haunted versions
- Creates collective horror narratives connecting all stories
- Tracks horror themes used across all transformations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

**✅ Python 3.13 Compatible**: All dependencies updated for full Python 3.13 support.

2. Set up your OpenRouter API key:
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key and preferred model
```

3. Run the parser:
```bash
python rss_spooky_parser.py
```

## Usage

### Basic Usage
```python
from backend.rss_spooky_parser import SpookyRSSParser

# Use default model from .env
parser = SpookyRSSParser()

# Or specify a model directly
parser = SpookyRSSParser(model="gpt-4")
parser = SpookyRSSParser(model="anthropic/claude-3-sonnet")

articles = parser.fetch_rss_feed("https://rss.cnn.com/rss/edition.rss")
haunted = parser.create_haunted_article(articles[0])
print(haunted['haunted']['haunted_title'])
```

### Process Multiple Feeds
```python
urls = [
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.bbci.co.uk/news/rss.xml"
]
results = parser.process_feeds(urls)
parser.save_results(results)
```

## Error Handling & Resurrection

The parser includes robust error handling with spooky themed messages:

- **Dead Feed Resurrection**: 3 automatic retry attempts with exponential backoff
- **Resurrection Messages**: Random spooky messages during retry attempts
- **Ghost Articles**: Creates supernatural placeholder content for permanently dead feeds
- **Performance Tracking**: Detailed stats on execution time and success rates

### Resurrection Messages
- "🧟‍♂️ Attempting necromantic resurrection of dead feed..."
- "⚰️ Summoning spirits to revive the silent RSS..."
- "🔮 Channeling dark magic to awaken dormant feed..."

## Model Selection

OpenRouter gives you access to multiple AI models:

### Popular Models
- **gpt-3.5-turbo**: Fast and cost-effective
- **gpt-4**: Higher quality, more creative
- **anthropic/claude-3-sonnet**: Excellent for creative writing
- **meta-llama/llama-2-70b-chat**: Open source alternative
- **mistralai/mistral-7b-instruct**: European AI model

### Usage Examples
```python
# Different models for different needs
parser_fast = SpookyRSSParser(model="gpt-3.5-turbo")      # Speed
parser_quality = SpookyRSSParser(model="gpt-4")           # Quality  
parser_creative = SpookyRSSParser(model="anthropic/claude-3-sonnet") # Creativity
```

See `model_examples.py` for testing different models.

## Configuration

- Set `OPENROUTER_MODEL` in `.env` for default model
- Modify RSS URLs in the `main()` function
- Adjust article limit in `fetch_rss_feed()` (default: 5 articles)
- Customize horror themes in `create_haunted_article()`
- Set retry attempts in `fetch_rss_feed()` (default: 3)

## Output Structure

The parser generates JSON files with:
- **Original articles**: Unmodified RSS content
- **Haunted versions**: Horror-themed transformations with:
  - Haunted titles and summaries
  - Horror themes used (ghosts, curses, etc.)
  - Supernatural explanations
- **Collective horror narrative**: Overarching story connecting all events
- **Horror theme tracking**: Complete list of supernatural elements used

See `example_output.json` for the complete structure.

## Horror Themes Included

- Ancient curses and dark omens
- Vengeful spirits and ghostly apparitions  
- Haunted locations and cursed objects
- Supernatural forces and otherworldly interventions
- Demonic influences and restless souls
- Spectral warnings and malevolent entities