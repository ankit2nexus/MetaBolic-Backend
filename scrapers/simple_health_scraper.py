#!/usr/bin/env python3
"""
Simple Health News Scraper

This scraper fetches real health news from multiple reliable sources:
- Google News RSS feeds for health topics
- WHO RSS feeds
- NIH news feeds
- WebMD RSS feeds
- Mayo Clinic news

No complex dependencies required - uses only standard libraries and requests.
"""

import sys
from pathlib import Path
import requests
import feedparser
import sqlite3
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "api"))

from config.scraper_config import SCRAPE_KEYWORDS

# Import advanced categorizer
try:
    from advanced_categorizer import categorize_health_article
    ADVANCED_CATEGORIZER_AVAILABLE = True
    print("✅ Advanced categorizer loaded successfully")
except ImportError as e:
    print(f"⚠️ Advanced categorizer not available: {e}")
    ADVANCED_CATEGORIZER_AVAILABLE = False

# Database path
DB_PATH = BASE_DIR / "db" / "articles.db"

# Health news sources
HEALTH_NEWS_SOURCES = {
    "google_news": {
        "base_url": "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en",
        "keywords": SCRAPE_KEYWORDS[:10]  # Use first 10 keywords
    },
    "who_news": {
        "url": "https://www.who.int/rss-feeds/news-english.xml",
        "keywords": ["health", "disease", "pandemic", "vaccine"]
    },
    "nih_news": {
        "url": "https://www.nih.gov/news-events/news-releases/rss.xml", 
        "keywords": ["research", "medical", "study", "treatment"]
    },
    "webmd_news": {
        "base_url": "https://feeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
        "keywords": ["health", "medical", "wellness"]
    }
}

def create_database():
    """Create the articles database if it doesn't exist"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            authors TEXT,
            summary TEXT,
            url TEXT UNIQUE,
            categories TEXT,
            tags TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database ready at: {DB_PATH}")

def smart_categorize(title, summary, source=""):
    """Advanced ML-based categorization with fallback to basic categorization"""
    
    # Try advanced categorization first
    if ADVANCED_CATEGORIZER_AVAILABLE:
        try:
            categories, tags = categorize_health_article(title, summary)
            if categories and tags:
                return categories, tags
        except Exception as e:
            print(f"⚠️ Advanced categorization failed: {e}, falling back to basic")
    
    # Fallback to basic categorization
    return simple_categorize_basic(title, summary, source)

def simple_categorize_basic(title, summary, source=""):
    """Simple rule-based categorization (fallback)"""
    text = f"{title} {summary}".lower()
    
    # Breaking news detection
    if any(word in text for word in ['breaking', 'urgent', 'alert', 'emergency']):
        return ['news'], ['breaking_news']
    
    # Disease detection
    disease_keywords = ['cancer', 'diabetes', 'heart disease', 'covid', 'flu', 'infection', 'disease']
    if any(word in text for word in disease_keywords):
        return ['diseases'], ['medical_conditions']
    
    # Treatment/solution detection
    treatment_keywords = ['treatment', 'therapy', 'medication', 'surgery', 'cure', 'vaccine']
    if any(word in text for word in treatment_keywords):
        return ['solutions'], ['medical_treatments']
    
    # Food/nutrition detection
    food_keywords = ['diet', 'nutrition', 'food', 'vitamin', 'supplement', 'eating']
    if any(word in text for word in food_keywords):
        return ['food'], ['nutrition_basics']
    
    # Audience-specific detection
    audience_keywords = {'women': 'women', 'men': 'men', 'children': 'children', 'elderly': 'elderly'}
    for keyword, audience in audience_keywords.items():
        if keyword in text:
            return ['audience'], [audience]
    
    # Research detection
    research_keywords = ['study', 'research', 'clinical trial', 'findings']
    if any(word in text for word in research_keywords):
        return ['news'], ['medical_research']
    
    # Default to news
    return ['news'], ['recent_developments']

def fetch_rss_feed(url, max_articles=20):
    """Fetch and parse RSS feed"""
    try:
        print(f"📡 Fetching RSS feed: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            print(f"⚠️ Warning: Feed may have issues: {url}")
        
        articles = []
        cutoff_date = datetime.now() - timedelta(days=7)  # Only articles from last week
        
        for entry in feed.entries[:max_articles]:
            try:
                # Parse publication date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = datetime.now()
                
                # Skip old articles
                if pub_date < cutoff_date:
                    continue
                
                # Extract article data
                title = entry.get('title', 'No Title').strip()
                summary = entry.get('summary', entry.get('description', '')).strip()
                
                # Clean HTML from summary
                if summary:
                    summary = BeautifulSoup(summary, 'html.parser').get_text()
                    summary = re.sub(r'\s+', ' ', summary).strip()[:500]  # Limit length
                
                # Get URL
                url = entry.get('link', '')
                if not url:
                    continue
                
                # Get author
                author = entry.get('author', entry.get('source', {}).get('title', ''))
                
                # Categorize using advanced ML system
                categories, tags = smart_categorize(title, summary)
                
                article = {
                    'title': title,
                    'summary': summary,
                    'url': url,
                    'author': author,
                    'date': pub_date.isoformat(),
                    'categories': categories,
                    'tags': tags
                }
                
                articles.append(article)
                
            except Exception as e:
                print(f"⚠️ Error processing entry: {e}")
                continue
        
        print(f"✅ Fetched {len(articles)} articles from feed")
        return articles
        
    except requests.RequestException as e:
        print(f"❌ Error fetching RSS feed {url}: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error with feed {url}: {e}")
        return []

def save_articles_to_db(articles, source_name):
    """Save articles to database"""
    if not articles:
        print(f"⚠️ No articles to save from {source_name}")
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    duplicate_count = 0
    
    for article in articles:
        try:
            # Convert lists to JSON
            categories_json = json.dumps(article['categories'])
            tags_json = json.dumps(article['tags'])
            
            cursor.execute("""
                INSERT OR IGNORE INTO articles 
                (date, title, authors, summary, url, categories, tags, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article['date'],
                article['title'],
                article['author'],
                article['summary'],
                article['url'],
                categories_json,
                tags_json,
                source_name
            ))
            
            if cursor.rowcount > 0:
                saved_count += 1
                print(f"✅ Saved: {article['title'][:60]}...")
            else:
                duplicate_count += 1
        
        except Exception as e:
            print(f"❌ Error saving article: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"📊 {source_name}: {saved_count} saved, {duplicate_count} duplicates")
    return saved_count

def scrape_google_news():
    """Scrape Google News for health topics"""
    print("\n🔍 Scraping Google News for health topics...")
    all_articles = []
    
    for keyword in HEALTH_NEWS_SOURCES["google_news"]["keywords"]:
        try:
            # Create RSS URL for this keyword
            encoded_keyword = keyword.replace(' ', '+')
            rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
            
            # Fetch articles
            articles = fetch_rss_feed(rss_url, max_articles=5)
            all_articles.extend(articles)
            
            # Be respectful with requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error with keyword '{keyword}': {e}")
    
    return save_articles_to_db(all_articles, "Google News")

def scrape_who_news():
    """Scrape WHO news feed"""
    print("\n🏥 Scraping WHO news...")
    articles = fetch_rss_feed("https://www.who.int/rss-feeds/news-english.xml")
    return save_articles_to_db(articles, "WHO")

def scrape_nih_news():
    """Scrape NIH news feed"""
    print("\n🧬 Scraping NIH news...")
    # Updated to working NIH RSS feed URL
    articles = fetch_rss_feed("https://grants.nih.gov/grants/guide/newsfeed/fundingopps.xml")
    return save_articles_to_db(articles, "NIH")

def scrape_health_news():
    """Main function to scrape all health news sources"""
    print("🧠 Simple Health News Scraper - Starting Real Data Collection")
    print("=" * 60)
    
    # Create database
    create_database()
    
    total_saved = 0
    start_time = datetime.now()
    
    # Scrape different sources
    scrapers = [
        ("Google News", scrape_google_news),
        ("WHO News", scrape_who_news),
        ("NIH News", scrape_nih_news)
    ]
    
    for source_name, scraper_func in scrapers:
        try:
            saved = scraper_func()
            total_saved += saved
        except Exception as e:
            print(f"❌ Error scraping {source_name}: {e}")
    
    # Summary
    duration = datetime.now() - start_time
    print(f"\n📊 Scraping Summary:")
    print(f"   • Total articles saved: {total_saved}")
    print(f"   • Duration: {duration.total_seconds():.1f} seconds")
    print(f"   • Database: {DB_PATH}")
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} real health articles!")
        print("💡 Next steps:")
        print("   1. Start the API server to see the articles")
        print("   2. Run the scheduler for continuous updates")
    else:
        print("\n⚠️ No articles were saved. Check your internet connection and RSS feeds.")
    
    return total_saved

def get_article_count():
    """Get current article count from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

if __name__ == "__main__":
    print(f"📊 Current articles in database: {get_article_count()}")
    scrape_health_news()
    print(f"📊 Final articles in database: {get_article_count()}")