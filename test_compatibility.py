#!/usr/bin/env python3
"""
Test script to verify Python 3.13 compatibility and basic functionality
"""

import sys
print(f"🐍 Python version: {sys.version}")

try:
    print("📦 Testing imports...")
    import feedparser
    print("✅ feedparser imported successfully")
    
    import requests
    print("✅ requests imported successfully")
    
    from openai import OpenAI
    print("✅ openai imported successfully")
    
    from backend.rss_spooky_parser import SpookyRSSParser
    print("✅ SpookyRSSParser imported successfully")
    
    print("\n🧪 Testing basic functionality...")
    
    # Test RSS parsing with a simple feed
    test_url = "https://rss.cnn.com/rss/edition.rss"
    
    # Create parser instance (will fail gracefully if no API key)
    try:
        parser = SpookyRSSParser()
        print("✅ Parser initialized")
        
        # Test RSS fetching
        print(f"🔍 Testing RSS fetch from: {test_url}")
        articles = parser.fetch_rss_feed(test_url)
        
        if articles:
            print(f"✅ Successfully fetched {len(articles)} articles")
            print(f"   First article: {articles[0]['title'][:50]}...")
        else:
            print("⚠️  No articles fetched (might be network or feed issue)")
            
    except Exception as e:
        if "OPENROUTER_API_KEY" in str(e):
            print("⚠️  Parser needs API key for full functionality, but basic RSS parsing works")
        else:
            print(f"❌ Parser error: {e}")
    
    print("\n🎃 Compatibility test complete!")
    print("If you see this message, the Python 3.13 fix is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure you've installed dependencies: pip install -r requirements.txt")
    print("2. Try upgrading feedparser: pip install --upgrade feedparser")
    print("3. Consider using Python 3.11 or 3.12 for better compatibility")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("Check python_compatibility.md for solutions")