#!/usr/bin/env python3
"""
RSS Spooky Parser - Fetches RSS feeds and transforms content into spooky narratives
"""

# Python 3.13 compatibility fix for feedparser
import sys
if sys.version_info >= (3, 13):
    # Monkey patch for Python 3.13 compatibility
    import html
    import urllib.parse
    sys.modules['cgi'] = type(sys)('cgi')
    sys.modules['cgi'].escape = html.escape
    sys.modules['cgi'].parse_qs = urllib.parse.parse_qs

try:
    import feedparser
except ImportError as e:
    print("❌ Error importing feedparser. This might be a Python 3.13 compatibility issue.")
    print("🔧 Try installing the latest version: pip install --upgrade feedparser")
    print("🐍 Or use Python 3.11/3.12 for better compatibility")
    raise e

import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import json
from datetime import datetime
import time
import random

class SpookyRSSParser:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the parser with OpenRouter API key and model selection"""
        load_dotenv()
        
        # OpenRouter configuration
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = model or os.getenv('OPENROUTER_MODEL', 'gpt-3.5-turbo')
        self.app_name = os.getenv('OPENROUTER_APP_NAME', 'haunted-rss-parser')
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/haunted-rss-parser",
                "X-Title": self.app_name,
            }
        )
        self.resurrection_messages = [
            "🧟‍♂️ Attempting necromantic resurrection of dead feed...",
            "⚰️ Summoning spirits to revive the silent RSS...",
            "🔮 Channeling dark magic to awaken dormant feed...",
            "👻 Performing séance to contact the departed RSS...",
            "🕯️ Lighting candles for the RSS resurrection ritual...",
            "💀 Invoking ancient curses to raise the dead feed..."
        ]
        self.stats = {
            'start_time': time.time(),
            'total_requests': 0,
            'successful_feeds': 0,
            'dead_feeds': 0,
            'articles_processed': 0,
            'llm_calls': 0,
            'model_used': self.model
        }
        
    def fetch_rss_feed(self, url: str, max_retries: int = 3) -> List[Dict]:
        """Fetch and parse RSS feed from URL with resurrection attempts"""
        self.stats['total_requests'] += 1
        
        for attempt in range(max_retries):
            try:
                # Add timeout and user agent for better compatibility
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Haunted RSS Parser'
                }
                
                # Try to fetch with requests first for better error handling
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                # Check if feed is valid
                if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                    raise Exception("Feed contains no entries or is malformed")
                
                # Check for feed errors
                if hasattr(feed, 'bozo') and feed.bozo:
                    print(f"⚠️  Feed parsing warning: {feed.bozo_exception}")
                
                articles = []
                for entry in feed.entries[:5]:  # Limit to 5 articles
                    article = {
                        'title': entry.get('title', 'Untitled'),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'source': feed.feed.get('title', 'Unknown Source')
                    }
                    articles.append(article)
                
                self.stats['successful_feeds'] += 1
                self.stats['articles_processed'] += len(articles)
                return articles
                
            except Exception as e:
                if attempt < max_retries - 1:
                    resurrection_msg = random.choice(self.resurrection_messages)
                    print(f"   {resurrection_msg}")
                    print(f"   💀 Attempt {attempt + 1} failed: {str(e)[:60]}...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.stats['dead_feeds'] += 1
                    print(f"   ⚱️  Feed has crossed to the other side permanently: {e}")
                    return self._create_ghost_articles(url, str(e))
    
    def _create_ghost_articles(self, url: str, error: str) -> List[Dict]:
        """Create spooky placeholder articles for dead feeds"""
        ghost_articles = [
            {
                'title': f"The Haunting of {url.split('//')[1].split('/')[0]}",
                'summary': f"In the digital graveyard where RSS feeds go to die, whispers echo of a once-thriving news source. The spectral remnants of headlines float through cyberspace, forever seeking readers who will never come. Error: {error}",
                'link': url,
                'published': datetime.now().isoformat(),
                'source': 'The Digital Afterlife',
                'is_ghost_article': True,
                'resurrection_failed': True
            }
        ]
        return ghost_articles
    
    def create_haunted_article(self, article: Dict) -> Dict:
        """Transform a single article into a haunted version with horror themes"""
        self.stats['llm_calls'] += 1
        
        # Handle ghost articles differently
        if article.get('is_ghost_article'):
            return {
                "original": article,
                "haunted": {
                    "haunted_title": article['title'],
                    "haunted_summary": article['summary'],
                    "horror_themes": ["digital necromancy", "cyber ghosts", "technological curses"],
                    "supernatural_explanation": "A feed that died and returned as a digital specter, haunting the RSS graveyard."
                },
                "transformation_timestamp": datetime.now().isoformat(),
                "is_resurrection_attempt": True
            }
        
        horror_themes = [
            "ancient curses", "vengeful spirits", "ghostly apparitions", 
            "supernatural forces", "dark omens", "haunted locations",
            "malevolent entities", "cursed objects", "spectral warnings",
            "otherworldly interventions", "demonic influences", "restless souls"
        ]
        
        prompt = f"""Transform this news article into a horror story while keeping the core facts intact.
        
        Original Title: {article['title']}
        Original Summary: {article['summary'][:300]}
        
        Requirements:
        - Include horror elements: ghosts, curses, supernatural forces, haunted locations
        - Maintain the factual core but add eerie explanations
        - Use atmospheric horror language
        - Suggest supernatural causes behind events
        - Create a haunting tone throughout
        
        Return ONLY a JSON object with this exact structure:
        {{
            "haunted_title": "Horror version of the title",
            "haunted_summary": "Horror version of the summary (200-300 words)",
            "horror_themes": ["list", "of", "horror", "elements", "used"],
            "supernatural_explanation": "Brief explanation of the supernatural forces at work"
        }}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a horror writer who transforms mundane news into supernatural tales. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.9
            )
            
            # Parse the JSON response
            haunted_content = json.loads(response.choices[0].message.content)
            
            return {
                "original": article,
                "haunted": haunted_content,
                "transformation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "original": article,
                "haunted": {
                    "haunted_title": f"The Cursed Tale of {article['title']}",
                    "haunted_summary": f"Dark forces seem to be at work in this mysterious case involving {article['title'][:50]}...",
                    "horror_themes": ["supernatural forces", "dark omens"],
                    "supernatural_explanation": f"Error in supernatural transformation: {e}"
                },
                "transformation_timestamp": datetime.now().isoformat()
            }
    
    def create_collective_horror_narrative(self, haunted_articles: List[Dict]) -> str:
        """Create an overarching horror narrative connecting all haunted articles"""
        if not haunted_articles:
            return "The darkness reveals no tales tonight..."
            
        titles = [article["haunted"]["haunted_title"] for article in haunted_articles]
        themes = []
        for article in haunted_articles:
            themes.extend(article["haunted"].get("horror_themes", []))
        
        prompt = f"""Create a master horror narrative that connects these supernatural events:
        
        Haunted Headlines: {', '.join(titles)}
        
        Horror Themes Present: {', '.join(set(themes))}
        
        Write a 400-600 word narrative that suggests these events are all connected by:
        - An ancient curse awakening
        - Supernatural forces manipulating world events  
        - Ghostly interventions in human affairs
        - A pattern of otherworldly influence
        
        Make it atmospheric and chilling, suggesting a larger supernatural conspiracy."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a master of cosmic horror who sees supernatural patterns in world events."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"The spirits refuse to speak... Error: {e}"
    
    def process_feeds(self, urls: List[str]) -> Dict:
        """Process multiple RSS feeds and create haunted versions with horror themes"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'feeds_processed': len(urls),
            'total_articles_haunted': 0,
            'horror_themes_used': set(),
            'feeds': []
        }
        
        all_haunted_articles = []
        
        for url in urls:
            print(f"🕷️  Processing feed: {url}")
            articles = self.fetch_rss_feed(url)
            
            if articles:
                feed_data = {
                    'source_url': url,
                    'source_title': articles[0]['source'],
                    'article_count': len(articles),
                    'haunted_articles': []
                }
                
                # Transform each article into haunted version
                for article in articles:
                    print(f"   👻 Haunting: {article['title'][:50]}...")
                    haunted_article = self.create_haunted_article(article)
                    feed_data['haunted_articles'].append(haunted_article)
                    all_haunted_articles.append(haunted_article)
                    
                    # Collect horror themes
                    themes = haunted_article['haunted'].get('horror_themes', [])
                    results['horror_themes_used'].update(themes)
                
                results['feeds'].append(feed_data)
                results['total_articles_haunted'] += len(articles)
            else:
                # This case is now handled by _create_ghost_articles
                print(f"💀 Feed returned from the digital afterlife with ghost articles")
        
        # Create collective horror narrative
        if all_haunted_articles:
            print("🔮 Weaving collective horror narrative...")
            results['collective_horror_narrative'] = self.create_collective_horror_narrative(all_haunted_articles)
        
        # Convert set to list for JSON serialization
        results['horror_themes_used'] = list(results['horror_themes_used'])
        
        # Add performance stats
        end_time = time.time()
        results['performance_stats'] = {
            'execution_time_seconds': round(end_time - self.stats['start_time'], 2),
            'total_feed_requests': self.stats['total_requests'],
            'successful_feeds': self.stats['successful_feeds'],
            'dead_feeds_resurrected': self.stats['dead_feeds'],
            'articles_processed': self.stats['articles_processed'],
            'llm_transformation_calls': self.stats['llm_calls'],
            'articles_per_second': round(self.stats['articles_processed'] / (end_time - self.stats['start_time']), 2) if end_time > self.stats['start_time'] else 0,
            'model_used': self.stats['model_used'],
            'api_provider': 'OpenRouter'
        }
        
        return results
    
    def save_results(self, results: Dict, filename: str = None):
        """Save results to JSON file with original + haunted versions"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"haunted_news_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"🗂️  Haunted news archive saved to {filename}")


def main():
    """Main function to demonstrate the RSS parser"""
    # Sample RSS feeds (you can modify these)
    rss_urls = [
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.rss"
    ]
    
    # Initialize parser
    parser = SpookyRSSParser()
    
    # Process feeds
    print("🎃 Starting Spooky RSS Parser...")
    results = parser.process_feeds(rss_urls)
    
    # Save results
    parser.save_results(results)
    
    # Display results
    print("\n" + "="*70)
    print("🎃 HAUNTED NEWS TRANSFORMATION COMPLETE 🎃")
    print("="*70)
    
    # Performance stats
    stats = results['performance_stats']
    print(f"⚡ Execution time: {stats['execution_time_seconds']}s")
    print(f"📊 Articles processed: {stats['articles_processed']} ({stats['articles_per_second']}/sec)")
    print(f"🔮 LLM calls: {stats['llm_transformation_calls']}")
    print(f"✅ Successful feeds: {stats['successful_feeds']}")
    print(f"💀 Dead feeds resurrected: {stats['dead_feeds_resurrected']}")
    print(f"👻 Horror themes used: {', '.join(results['horror_themes_used'])}")
    
    # Impressive generation note
    if stats['execution_time_seconds'] < 60 and stats['articles_processed'] > 10:
        print(f"\n🚀 IMPRESSIVE: Generated {stats['articles_processed']} haunted articles in {stats['execution_time_seconds']}s!")
    
    # Display haunted articles by feed
    for feed_data in results['feeds']:
        print(f"\n📰 Source: {feed_data['source_title']}")
        print(f"🔗 URL: {feed_data['source_url']}")
        print(f"📄 Articles: {feed_data['article_count']}")
        
        for i, haunted in enumerate(feed_data['haunted_articles'], 1):
            print(f"\n   👻 Article {i}:")
            print(f"   Original: {haunted['original']['title']}")
            print(f"   Haunted:  {haunted['haunted']['haunted_title']}")
            print(f"   Themes:   {', '.join(haunted['haunted']['horror_themes'])}")
            print(f"   Summary:  {haunted['haunted']['haunted_summary'][:100]}...")
    
    # Display collective horror narrative
    if 'collective_horror_narrative' in results:
        print("\n" + "="*70)
        print("🔮 COLLECTIVE HORROR NARRATIVE")
        print("="*70)
        print(results['collective_horror_narrative'])
        print("\n" + "="*70)


if __name__ == "__main__":
    main()