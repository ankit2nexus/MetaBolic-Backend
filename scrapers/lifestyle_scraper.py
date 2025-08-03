#!/usr/bin/env python3
"""
Lifestyle Content Scraper

This scraper collects lifestyle-related health articles from various sources
and adds them with the 'lifestyle' tag to ensure the /api/v1/tag/lifestyle endpoint
returns content.
"""

import sys
from pathlib import Path
import requests
import sqlite3
import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import our URL validator
try:
    sys.path.insert(0, str(BASE_DIR))
    from app.url_validator import URLValidator
except ImportError:
    # Fallback if URL validator is not available
    class URLValidator:
        def validate_article_url(self, article):
            return True, {"status": "valid"}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = BASE_DIR / "data" / "articles.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "db" / "articles.db"

class LifestyleScraper:
    """Lifestyle-focused health content scraper"""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Lifestyle-focused RSS feeds and sources
        self.lifestyle_sources = [
            {
                "name": "Mayo Clinic - Healthy Lifestyle",
                "rss_url": "https://www.mayoclinic.org/rss/healthy-living",
                "base_url": "https://www.mayoclinic.org",
                "priority": 4
            },
            {
                "name": "Harvard Health - Healthy Living",
                "rss_url": "https://www.health.harvard.edu/topics/healthy-eating/feed",
                "base_url": "https://www.health.harvard.edu",
                "priority": 4
            },
            {
                "name": "Medical News Today - Fitness",
                "rss_url": "https://www.medicalnewstoday.com/category/fitness/feed",
                "base_url": "https://www.medicalnewstoday.com",
                "priority": 3
            },
            {
                "name": "Healthline - Nutrition",
                "rss_url": "https://www.healthline.com/nutrition/feed",
                "base_url": "https://www.healthline.com",
                "priority": 3
            },
            {
                "name": "WebMD - Healthy Living",
                "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=living-healthy",
                "base_url": "https://www.webmd.com",
                "priority": 3
            }
        ]
    
    def scrape_feed(self, source: Dict) -> List[Dict]:
        """Scrape articles from an RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(source["rss_url"])
            logger.info(f"📰 Retrieved {len(feed.entries)} articles from {source['name']}")
            
            for entry in feed.entries[:10]:  # Limit to 10 entries per feed
                try:
                    # Extract article data
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    
                    # Skip if no title or link
                    if not title or not link:
                        continue
                        
                    # Convert relative URLs to absolute
                    if not link.startswith(("http://", "https://")):
                        link = urljoin(source["base_url"], link)
                    
                    # Get date (use current time if not available)
                    published = entry.get("published_parsed") or entry.get("updated_parsed")
                    if published:
                        date = datetime(*published[:6]).isoformat()
                    else:
                        date = datetime.now().isoformat()
                    
                    # Get summary
                    summary = entry.get("summary", "")
                    if summary:
                        # Clean up the summary to remove source information
                        if hasattr(summary, "text"):
                            summary = summary.text[:500].strip()
                        elif isinstance(summary, str):
                            # Remove source references from the summary text (e.g., "Source: XYZ")
                            summary = re.sub(r'Source:.*?(\.|$)', '', summary)
                            summary = re.sub(r'From:.*?(\.|$)', '', summary)
                            summary = summary[:500].strip()
                    
                    # Get author
                    author = entry.get("author", "")
                    
                    # Create article object
                    article = {
                        "title": title,
                        "url": link,
                        "date": date,
                        "summary": summary,
                        "authors": author,
                        "source": source["name"],  # Keep source information
                        "priority": source["priority"],
                        # Critical: Add lifestyle tag - this ensures the article appears in the lifestyle tag API
                        "tags": ["lifestyle", "health_lifestyle", "wellness", "lifestyle_changes"],
                        "categories": ["lifestyle"],
                    }
                    
                    # Validate the URL
                    is_valid, _ = self.url_validator.validate_article_url(article)
                    if is_valid:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error processing entry: {e}")
            
        except Exception as e:
            logger.error(f"Error scraping feed {source['name']}: {e}")
        
        return articles
    
    def scrape_and_store(self) -> int:
        """Scrape lifestyle articles and store in database"""
        total_added = 0
        
        try:
            # Connect to database
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            # Create tables if they don't exist (should already exist)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                date TEXT,
                title TEXT,
                authors TEXT,
                summary TEXT,
                content TEXT,
                url TEXT UNIQUE,
                categories TEXT,
                tags TEXT,
                source TEXT,
                priority INTEGER DEFAULT 1,
                image_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Get all articles
            all_articles = []
            for source in self.lifestyle_sources:
                try:
                    articles = self.scrape_feed(source)
                    all_articles.extend(articles)
                    logger.info(f"📝 Scraped {len(articles)} articles from {source['name']}")
                except Exception as e:
                    logger.error(f"Error scraping source {source['name']}: {e}")
            
            # Insert articles into database
            for article in all_articles:
                try:
                    # Convert data for database
                    categories_json = json.dumps(article.get("categories", ["lifestyle"]))
                    tags_json = json.dumps(article.get("tags", ["lifestyle"]))
                    
                    # Check if the URL already exists
                    cursor.execute("SELECT id FROM articles WHERE url = ?", (article["url"],))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        # Insert new article
                        cursor.execute(
                            '''
                            INSERT INTO articles 
                            (date, title, authors, summary, url, categories, tags, source, priority, image_url) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''',
                            (
                                article["date"],
                                article["title"],
                                article.get("authors", ""),
                                article.get("summary", ""),
                                article["url"],
                                categories_json,
                                tags_json,
                                article["source"],
                                article["priority"],
                                article.get("image_url", "")
                            )
                        )
                        total_added += 1
                    else:
                        # Update existing article to ensure it has the lifestyle tag
                        cursor.execute("SELECT tags FROM articles WHERE url = ?", (article["url"],))
                        existing_tags_json = cursor.fetchone()[0]
                        
                        try:
                            existing_tags = json.loads(existing_tags_json)
                            if "lifestyle" not in existing_tags:
                                existing_tags.append("lifestyle")
                                updated_tags_json = json.dumps(existing_tags)
                                
                                cursor.execute(
                                    "UPDATE articles SET tags = ? WHERE url = ?",
                                    (updated_tags_json, article["url"])
                                )
                                logger.info(f"Updated tags for article: {article['title']}")
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error storing article {article.get('title', '')}: {e}")
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Added {total_added} new lifestyle articles to database")
            
        except Exception as e:
            logger.error(f"Error in scrape_and_store: {e}")
        
        return total_added

if __name__ == "__main__":
    scraper = LifestyleScraper()
    total_added = scraper.scrape_and_store()
    print(f"✅ Added {total_added} new lifestyle articles to database")
