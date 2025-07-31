#!/usr/bin/env python3
"""
Python 3.13 Compatible News Scraper

This scraper works with Python 3.13+ without feedparser dependency.
Uses only standard library modules for RSS parsing.
"""

import sys
from pathlib import Path
import requests
import sqlite3
import json
import re
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, quote_plus
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = BASE_DIR / "data" / "articles.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "db" / "articles.db"

class Python313CompatibleScraper:
    """Python 3.13 compatible news scraper without external dependencies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Reliable RSS feeds
        self.rss_sources = [
            {
                "name": "WHO Health News",
                "url": "https://www.who.int/rss-feeds/news-english.xml",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "NIH News Releases",
                "url": "https://www.nih.gov/news-events/news-releases/rss.xml",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "Reuters Health",
                "url": "https://feeds.reuters.com/reuters/healthNews",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "CNN Health",
                "url": "http://rss.cnn.com/rss/edition_health.rss",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "BBC Health",
                "url": "http://feeds.bbci.co.uk/news/health/rss.xml",
                "priority": 2,
                "category": "news"
            }
        ]
        
        # Google News health topics
        self.google_news_topics = [
            "health+news",
            "medical+breakthrough",
            "nutrition+research",
            "disease+prevention",
            "mental+health"
        ]
    
    def create_database(self):
        """Create database with enhanced schema"""
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
                priority INTEGER DEFAULT 1,
                url_accessible INTEGER DEFAULT 1,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_url_accessible ON articles(url_accessible)",
            "CREATE INDEX IF NOT EXISTS idx_date ON articles(date)",
            "CREATE INDEX IF NOT EXISTS idx_source ON articles(source)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database ready at: {DB_PATH}")
    
    def parse_rss_xml(self, xml_content: str) -> List[Dict]:
        """Parse RSS XML using only standard library"""
        articles = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle different RSS formats
            items = root.findall('.//item') or root.findall('.//entry')
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    desc_elem = item.find('description') or item.find('summary')
                    link_elem = item.find('link')
                    date_elem = item.find('pubDate') or item.find('published')
                    
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text or ""
                        title = title.strip()
                        
                        # Handle description
                        description = ""
                        if desc_elem is not None:
                            description = desc_elem.text or ""
                            # Clean HTML tags
                            description = re.sub(r'<[^>]+>', '', description)
                            description = re.sub(r'\s+', ' ', description).strip()[:500]
                        
                        # Handle link
                        link = link_elem.text or ""
                        if not link and link_elem.get('href'):
                            link = link_elem.get('href')
                        link = link.strip()
                        
                        # Handle date
                        article_date = datetime.now()
                        if date_elem is not None and date_elem.text:
                            try:
                                date_str = date_elem.text.strip()
                                # Remove timezone info for simple parsing
                                date_str = re.sub(r'\s+[A-Z]{3,4}$', '', date_str)
                                article_date = datetime.strptime(date_str.split(' +')[0], '%a, %d %b %Y %H:%M:%S')
                            except:
                                pass
                        
                        # Only recent articles (last 3 days)
                        if article_date < datetime.now() - timedelta(days=3):
                            continue
                        
                        # Validate health-related content
                        if self.is_health_related(title, description):
                            article_data = {
                                'title': title,
                                'summary': description,
                                'url': link,
                                'date': article_date.isoformat(),
                                'author': '',
                                'priority': 2
                            }
                            
                            if len(title) > 10 and len(link) > 10:
                                articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"Error parsing RSS item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing RSS XML: {e}")
        
        return articles
    
    def fetch_rss_feed(self, source_config: Dict) -> List[Dict]:
        """Fetch and parse RSS feed"""
        articles = []
        
        try:
            logger.info(f"🔍 Fetching from {source_config['name']}...")
            
            response = self.session.get(source_config['url'], timeout=15)
            response.raise_for_status()
            
            articles = self.parse_rss_xml(response.text)
            
            # Add source information
            for article in articles:
                article['source'] = source_config['name']
                article['priority'] = source_config['priority']
            
            logger.info(f"✅ Found {len(articles)} articles from {source_config['name']}")
            
        except Exception as e:
            logger.error(f"Error fetching from {source_config['name']}: {e}")
        
        return articles
    
    def fetch_google_news(self) -> List[Dict]:
        """Fetch Google News using RSS"""
        articles = []
        
        for topic in self.google_news_topics[:3]:  # Limit to avoid rate limiting
            try:
                logger.info(f"🔍 Fetching Google News for: {topic}")
                
                encoded_topic = quote_plus(topic)
                url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                topic_articles = self.parse_rss_xml(response.text)
                
                # Add source and topic info
                for article in topic_articles:
                    article['source'] = f"Google News ({topic.replace('+', ' ').title()})"
                    article['priority'] = 2
                
                articles.extend(topic_articles[:10])  # Limit per topic
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error fetching Google News for {topic}: {e}")
                continue
        
        logger.info(f"📰 Found {len(articles)} Google News articles")
        return articles
    
    def is_health_related(self, title: str, summary: str) -> bool:
        """Check if content is health-related"""
        text = f"{title} {summary}".lower()
        
        health_keywords = [
            'health', 'medical', 'disease', 'illness', 'condition', 'treatment',
            'doctor', 'hospital', 'medicine', 'drug', 'therapy', 'cure',
            'nutrition', 'diet', 'fitness', 'wellness', 'prevention',
            'cancer', 'diabetes', 'heart', 'brain', 'mental', 'anxiety',
            'depression', 'vaccine', 'virus', 'infection', 'covid', 'flu',
            'research', 'study', 'clinical', 'patient', 'healthcare'
        ]
        
        # Must contain at least 1 health keyword
        health_count = sum(1 for keyword in health_keywords if keyword in text)
        return health_count >= 1
    
    def categorize_article(self, article: Dict) -> Dict:
        """Simple article categorization"""
        text = f"{article['title']} {article['summary']}".lower()
        
        categories = []
        tags = []
        
        # Breaking news
        if any(word in text for word in ['breaking', 'urgent', 'alert']):
            categories.append('news')
            tags.append('breaking_news')
        
        # Diseases
        if any(word in text for word in ['cancer', 'diabetes', 'disease', 'illness']):
            categories.append('diseases')
            tags.append('medical_conditions')
        
        # Nutrition
        if any(word in text for word in ['nutrition', 'diet', 'food', 'eating']):
            categories.append('food')
            tags.append('nutrition_basics')
        
        # Mental health
        if any(word in text for word in ['mental', 'depression', 'anxiety', 'stress']):
            categories.append('audience')
            tags.append('mental_health')
        
        # Research
        if any(word in text for word in ['study', 'research', 'clinical', 'trial']):
            categories.append('news')
            tags.append('breakthrough_research')
        
        # Default
        if not categories:
            categories = ['news']
            tags = ['recent_developments']
        
        return {
            'categories': categories,
            'tags': tags
        }
    
    def save_articles(self, articles: List[Dict], source_name: str) -> int:
        """Save articles to database"""
        if not articles:
            logger.info(f"⚠️ No articles to save from {source_name}")
            return 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        saved_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                # Categorize article
                categorization = self.categorize_article(article)
                article.update(categorization)
                
                # Convert lists to JSON
                categories_json = json.dumps(article.get('categories', ['news']))
                tags_json = json.dumps(article.get('tags', ['general']))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO articles 
                    (date, title, authors, summary, url, categories, tags, source, priority, url_accessible, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article['date'],
                    article['title'],
                    article.get('author', ''),
                    article['summary'],
                    article['url'],
                    categories_json,
                    tags_json,
                    article.get('source', source_name),
                    article.get('priority', 1),
                    1,  # Assume accessible
                    datetime.now().isoformat()
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                    logger.info(f"✅ Saved: {article['title'][:60]}...")
                else:
                    duplicate_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error saving article: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"📊 {source_name}: {saved_count} saved, {duplicate_count} duplicates")
        return saved_count
    
    def run_scraper(self) -> int:
        """Run the complete scraper"""
        total_saved = 0
        start_time = datetime.now()
        
        logger.info("🌍 Python 3.13 Compatible News Scraper")
        logger.info("=" * 50)
        
        # 1. Fetch from RSS sources
        logger.info("\n📰 Fetching from RSS sources...")
        for source_config in self.rss_sources:
            articles = self.fetch_rss_feed(source_config)
            saved = self.save_articles(articles, source_config['name'])
            total_saved += saved
            time.sleep(2)  # Rate limiting
        
        # 2. Fetch from Google News
        logger.info("\n🔍 Fetching from Google News...")
        google_articles = self.fetch_google_news()
        total_saved += self.save_articles(google_articles, "Google News Health")
        
        duration = datetime.now() - start_time
        
        logger.info(f"\n📊 Scraping Summary:")
        logger.info(f"   • Total articles saved: {total_saved}")
        logger.info(f"   • Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"   • Database: {DB_PATH}")
        
        return total_saved

def main():
    """Main function"""
    print("🌍 Python 3.13 Compatible Health News Scraper")
    print("=" * 55)
    
    scraper = Python313CompatibleScraper()
    
    # Create database
    scraper.create_database()
    
    # Run scraper
    total_saved = scraper.run_scraper()
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} health articles!")
        print("✅ Compatible with Python 3.13+")
        print("\n💡 Next steps:")
        print("   1. Start the API: python start.py")
        print("   2. Visit: http://localhost:8000/articles/latest")
        print("   3. All existing endpoints work with new data!")
    else:
        print("\n⚠️ No articles were saved. Check:")
        print("   • Internet connection")
        print("   • RSS feed availability")
    
    return total_saved

if __name__ == "__main__":
    main()
