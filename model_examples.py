#!/usr/bin/env python3
"""
Examples of using different models with the Haunted RSS Parser via OpenRouter
"""

from backend.rss_spooky_parser import SpookyRSSParser

def test_different_models():
    """Test the parser with different models available on OpenRouter"""
    
    # Sample RSS feed for testing
    test_urls = ["https://rss.cnn.com/rss/edition.rss"]
    
    # Available models on OpenRouter (examples)
    models_to_test = [
        "gpt-3.5-turbo",           # Fast and cost-effective
        "gpt-4",                   # Higher quality, more expensive
        "anthropic/claude-3-sonnet", # Anthropic's Claude
        "meta-llama/llama-2-70b-chat", # Open source Llama
        "mistralai/mistral-7b-instruct", # Mistral AI
        "google/palm-2-chat-bison"  # Google's PaLM
    ]
    
    print("🎃 Testing Haunted RSS Parser with different models...")
    
    for model in models_to_test:
        print(f"\n🔮 Testing with model: {model}")
        try:
            # Initialize parser with specific model
            parser = SpookyRSSParser(model=model)
            
            # Process a single feed for testing
            articles = parser.fetch_rss_feed(test_urls[0])
            if articles:
                # Test haunting a single article
                haunted = parser.create_haunted_article(articles[0])
                
                print(f"✅ Success with {model}")
                print(f"   Original: {haunted['original']['title'][:50]}...")
                print(f"   Haunted:  {haunted['haunted']['haunted_title'][:50]}...")
                print(f"   Themes:   {', '.join(haunted['haunted']['horror_themes'][:3])}")
            else:
                print(f"❌ No articles fetched for testing {model}")
                
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
    
    print("\n👻 Model testing complete!")

def compare_model_performance():
    """Compare performance and quality across different models"""
    
    models = [
        ("gpt-3.5-turbo", "Fast & Affordable"),
        ("gpt-4", "High Quality"),
        ("anthropic/claude-3-sonnet", "Creative & Detailed")
    ]
    
    test_url = "https://rss.cnn.com/rss/edition.rss"
    
    print("🔬 Model Performance Comparison")
    print("=" * 50)
    
    for model, description in models:
        print(f"\n🧪 Testing {model} ({description})")
        try:
            parser = SpookyRSSParser(model=model)
            
            # Time the transformation
            import time
            start_time = time.time()
            
            articles = parser.fetch_rss_feed(test_url)
            if articles:
                haunted = parser.create_haunted_article(articles[0])
                
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                
                print(f"   ⏱️  Response time: {duration}s")
                print(f"   🎭 Horror themes: {len(haunted['haunted']['horror_themes'])}")
                print(f"   📝 Summary length: {len(haunted['haunted']['haunted_summary'])} chars")
                print(f"   🎪 Creativity score: {'🌟' * min(5, len(haunted['haunted']['horror_themes']))}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    # Uncomment to test different models
    # test_different_models()
    
    # Uncomment to compare performance
    # compare_model_performance()
    
    print("🎃 Model examples ready!")
    print("Uncomment the function calls above to test different models.")
    print("Make sure you have OPENROUTER_API_KEY set in your .env file!")