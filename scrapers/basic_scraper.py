#!/usr/bin/env python3
"""
Basic Health News Scraper - No Complex Dependencies

This scraper fetches real health news using only standard libraries and requests.
It works with Python 3.13 and doesn't require feedparser or other complex packages.
"""

import sys
from pathlib import Path
import requests
import sqlite3
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote_plus
from xml.etree import ElementTree as ET
import time

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config.scraper_config import SCRAPE_KEYWORDS

# Database path
DB_PATH = BASE_DIR / "db" / "articles.db"

# Health news RSS feeds (using direct XML parsing)
RSS_FEEDS = [
    "https://www.who.int/rss-feeds/news-english.xml",
    "https://www.nih.gov/news-events/news-releases/rss.xml",
    "https://rss.cnn.com/rss/edition.rss",  # General news, will filter for health
    "https://feeds.npr.org/1001/rss.xml",   # NPR News
]

# Google News base URLs
GOOGLE_NEWS_BASE = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database ready at: {DB_PATH}")

def basic_categorize(title, summary):
    """Basic categorization using keyword matching"""
    text = f"{title} {summary}".lower()
    
    # Breaking news indicators
    breaking_words = ['breaking', 'urgent', 'alert', 'emergency', 'critical']
    if any(word in text for word in breaking_words):
        return ['news'], ['breaking_news']
    
    # Disease categories
    disease_words = ['cancer', 'diabetes', 'heart disease', 'covid', 'flu', 'infection', 'disease', 'illness', 'condition']
    if any(word in text for word in disease_words):
        return ['diseases'], ['medical_conditions']
    
    # Treatment/solutions
    treatment_words = ['treatment', 'therapy', 'medication', 'drug', 'surgery', 'cure', 'vaccine', 'medicine']
    if any(word in text for word in treatment_words):
        return ['solutions'], ['medical_treatments']
    
    # Food/nutrition
    food_words = ['diet', 'nutrition', 'food', 'vitamin', 'supplement', 'eating', 'meal', 'healthy eating']
    if any(word in text for word in food_words):
        return ['food'], ['nutrition_basics']
    
    # Audience-specific
    women_words = ['women', 'female', 'pregnancy', 'maternal']
    men_words = ['men', 'male', 'prostate']
    children_words = ['children', 'kids', 'pediatric', 'infant', 'baby']
    elderly_words = ['elderly', 'senior', 'aging', 'geriatric']
    
    if any(word in text for word in women_words):
        return ['audience'], ['women']
    elif any(word in text for word in men_words):
        return ['audience'], ['men']
    elif any(word in text for word in children_words):
        return ['audience'], ['children']
    elif any(word in text for word in elderly_words):
        return ['audience'], ['elderly']
    
    # Research/trending
    research_words = ['study', 'research', 'clinical trial', 'findings', 'breakthrough', 'discovery']
    if any(word in text for word in research_words):
        return ['trending_topics'], ['breakthrough_research']
    
    # Blog/opinion indicators
    opinion_words = ['opinion', 'blog', 'personal', 'experience', 'story', 'journey']
    if any(word in text for word in opinion_words):
        return ['blogs_and_opinions'], ['personal_experiences']
    
    # Default to news
    return ['news'], ['recent_developments']

def parse_rss_xml(xml_content):
    """Parse RSS XML content manually"""
    articles = []
    
    try:
        root = ET.fromstring(xml_content)
        
        # Handle different RSS formats
        items = root.findall('.//item') or root.findall('.//entry')
        
        for item in items:
            try:
                # Extract title
                title_elem = item.find('title')
                title = title_elem.text if title_elem is not None else "No Title"
                
                # Extract description/summary
                desc_elem = item.find('description') or item.find('summary')
                description = ""
                if desc_elem is not None:
                    description = desc_elem.text or ""
                    # Clean HTML tags
                    description = re.sub(r'<[^>]+>', '', description)
                    description = re.sub(r'\s+', ' ', description).strip()[:500]
                
                # Extract link
                link_elem = item.find('link')
                link = ""
                if link_elem is not None:
                    link = link_elem.text or link_elem.get('href', '')
                
                # Extract date
                date_elem = item.find('pubDate') or item.find('published') or item.find('updated')
                article_date = datetime.now()
                if date_elem is not None and date_elem.text:
                    try:
                        # Try to parse various date formats
                        date_str = date_elem.text.strip()
                        # Remove timezone info for simple parsing
                        date_str = re.sub(r'\s+[A-Z]{3,4}$', '', date_str)
                        article_date = datetime.strptime(date_str.split(' +')[0], '%a, %d %b %Y %H:%M:%S')
                    except:
                        pass  # Use current time if parsing fails
                
                # Only include recent articles (last 7 days)
                if article_date > datetime.now() - timedelta(days=7):
                    articles.append({
                        'title': title.strip(),
                        'summary': description,
                        'url': link.strip(),
                        'date': article_date.isoformat(),
                        'author': ''
                    })
                    
            except Exception as e:
                print(f"⚠️ Error parsing RSS item: {e}")
                continue
                
    except ET.ParseError as e:
        print(f"❌ Error parsing XML: {e}")
    
    return articles

def fetch_rss_feed(url, source_name="Unknown"):
    """Fetch RSS feed using requests and manual XML parsing"""
    try:
        print(f"📡 Fetching: {source_name}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the RSS XML
        articles = parse_rss_xml(response.content)
        
        # Filter for health-related content
        health_articles = []
        health_keywords = ['health', 'medical', 'disease', 'treatment', 'nutrition', 'wellness', 'fitness', 'mental health']
        
        for article in articles:
            text = f"{article['title']} {article['summary']}".lower()
            if any(keyword in text for keyword in health_keywords):
                # Categorize the article
                categories, tags = basic_categorize(article['title'], article['summary'])
                article['categories'] = categories
                article['tags'] = tags
                health_articles.append(article)
        
        print(f"✅ Found {len(health_articles)} health articles from {source_name}")
        return health_articles
        
    except requests.RequestException as e:
        print(f"❌ Error fetching {source_name}: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error with {source_name}: {e}")
        return []

def fetch_google_news_health():
    """Fetch health news from Google News"""
    all_articles = []
    
    # Use top health keywords
    health_keywords = ['health news', 'medical breakthrough', 'disease outbreak', 'nutrition study', 'wellness tips']
    
    for keyword in health_keywords[:3]:  # Limit to avoid rate limiting
        try:
            encoded_keyword = quote_plus(keyword)
            url = GOOGLE_NEWS_BASE.format(encoded_keyword)
            
            articles = fetch_rss_feed(url, f"Google News ({keyword})")
            all_articles.extend(articles)
            
            # Be respectful with requests
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error with Google News keyword '{keyword}': {e}")
    
    return all_articles

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
            categories_json = json.dumps(article.get('categories', ['news']))
            tags_json = json.dumps(article.get('tags', ['general']))
            
            cursor.execute("""
                INSERT OR IGNORE INTO articles 
                (date, title, authors, summary, url, categories, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                article['date'],
                article['title'],
                article.get('author', ''),
                article['summary'],
                article['url'],
                categories_json,
                tags_json
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

def main():
    """Main scraping function"""
    print("🧠 Basic Health News Scraper - Fetching Real Data")
    print("=" * 55)
    
    # Create database
    create_database()
    
    total_saved = 0
    start_time = datetime.now()
    
    # Fetch from Google News
    print("\n🔍 Fetching from Google News...")
    google_articles = fetch_google_news_health()
    total_saved += save_articles_to_db(google_articles, "Google News")
    
    # Fetch from RSS feeds
    print("\n📰 Fetching from RSS feeds...")
    rss_sources = [
        ("https://www.who.int/rss-feeds/news-english.xml", "WHO"),
        ("https://www.nih.gov/news-events/news-releases/rss.xml", "NIH")
    ]
    
    for url, name in rss_sources:
        articles = fetch_rss_feed(url, name)
        total_saved += save_articles_to_db(articles, name)
        time.sleep(1)  # Be respectful
    
    # Summary
    duration = datetime.now() - start_time
    print(f"\n📊 Scraping Summary:")
    print(f"   • Total articles saved: {total_saved}")
    print(f"   • Duration: {duration.total_seconds():.1f} seconds")
    print(f"   • Database: {DB_PATH}")
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} real health articles!")
        print("✅ Your database now contains real health news data!")
        print("\n💡 Next steps:")
        print("   1. Start the API: cd api && uvicorn main:app --reload")
        print("   2. Visit: http://localhost:8000/articles/latest")
        print("   3. Start frontend: cd frontend && npm start")
    else:
        print("\n⚠️ No articles were saved. This might be due to:")
        print("   • Network connectivity issues")
        print("   • RSS feeds being temporarily unavailable")
        print("   • Rate limiting from news sources")
        print("   • Try running the script again in a few minutes")
    
    return total_saved

def get_article_count():
    """Get current article count"""
    try:
        if not DB_PATH.exists():
            return 0
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
    scraped = main()
    print(f"📊 Final articles in database: {get_article_count()}")
    
    if scraped > 0:
        print(f"\n🎯 SUCCESS: {scraped} real articles ready!")
    else:
        print(f"\n⚠️ No new articles added. Try again or check your connection.")