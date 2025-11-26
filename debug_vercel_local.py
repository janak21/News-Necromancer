
import sys
import os
import asyncio
from unittest.mock import MagicMock

# Mock environment variables
os.environ["OPENROUTER_API_KEY"] = "test_key"

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import api.feeds.process...")
    from api.feeds.process import app, process_feeds, FeedProcessRequest
    print("Import successful!")
    
    # Test the function with a mock request
    async def test_run():
        print("Running test request...")
        request = FeedProcessRequest(
            urls=["https://rss.nytimes.com/services/xml/rss/nyt/World.xml"],
            variant_count=1,
            intensity=3
        )
        
        # We can't easily mock the network calls without extensive mocking,
        # but we can check if the function is defined and accessible.
        print(f"Function 'process_feeds' found: {process_feeds}")
        
    asyncio.run(test_run())
    print("Test script finished successfully.")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
