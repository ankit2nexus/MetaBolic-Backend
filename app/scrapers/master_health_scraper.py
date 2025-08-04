#!/usr/bin/env python3
"""
Master Health News Scraper - Unified Scraper

This unified scraper combines all health news sources into a single, efficient scraper:
- RSS feeds from WHO, NIH, WebMD, Mayo Clinic
- Google News health searches
- Major news outlets (Reuters, CNN, BBC)
- Health-specific sources
- International health news

Replaces: comprehensive_news_scraper.py, simple_health_scraper.py, 
python313_compatible_scraper.py, lifestyle_scraper.py, comprehensive_category_scraper.py,
enhanced_international_scraper.py
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
import feedparser
from bs4 import BeautifulSoup

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Import our URL validator
try:
    sys.path.insert(0, str(BASE_DIR))
    from app.url_validator import URLValidator
except ImportError:
    class URLValidator:
        def validate_article_url(self, article):
            return True, {"status": "valid"}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = BASE_DIR / "data" / "articles.db"

class MasterHealthScraper:
    """Unified health news scraper combining all sources"""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Health keywords for searches
        self.health_keywords = [
            "metabolic health", "diabetes", "nutrition", "diet", "fitness", "wellness",
            "mental health", "heart disease", "obesity", "lifestyle", "exercise",
            "public health", "food safety", "sleep disorder", "immunity", "preventive care"
        ]
        
        # Unified RSS sources
        self.rss_sources = [
            # WHO & Institutional
            {"name": "WHO", "url": "https://www.who.int/rss-feeds/news-english.xml", "category": "public_health"},
            {"name": "NIH", "url": "https://www.nih.gov/news-events/news-releases/rss", "category": "medical_research"},
            {"name": "CDC", "url": "https://tools.cdc.gov/podcasts/rss/health.xml", "category": "public_health"},
            
            # Health Websites
            {"name": "WebMD", "url": "https://www.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC", "category": "health_info"},
            {"name": "Mayo Clinic", "url": "https://newsnetwork.mayoclinic.org/feed/", "category": "medical_advice"},
            {"name": "Healthline", "url": "https://www.healthline.com/rss", "category": "health_info"},
            
            # Major News Outlets - Health Sections
            {"name": "Reuters Health", "url": "https://feeds.reuters.com/reuters/health", "category": "health_news"},
            {"name": "CNN Health", "url": "http://rss.cnn.com/rss/cnn_health.rss", "category": "health_news"},
            {"name": "BBC Health", "url": "http://feeds.bbci.co.uk/news/health/rss.xml", "category": "health_news"},
            {"name": "AP Health", "url": "https://apnews.com/apf-health", "category": "health_news"},
            
            # Nutrition & Lifestyle
            {"name": "Nutrition.gov", "url": "https://www.nutrition.gov/rss.xml", "category": "nutrition"},
            {"name": "Harvard Health", "url": "https://www.health.harvard.edu/blog/feed", "category": "medical_advice"},
        ]

    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT UNIQUE NOT NULL,
                    published_date TEXT,
                    source TEXT,
                    category TEXT,
                    tags TEXT,
                    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    image_url TEXT,
                    content TEXT,
                    author TEXT,
                    read_time INTEGER DEFAULT 3
                )
            """)
            conn.commit()

    def scrape_rss_source(self, source: Dict) -> List[Dict]:
        """Scrape a single RSS source"""
        articles = []
        try:
            logger.info(f"Scraping {source['name']}...")
            
            # Try feedparser first
            try:
                feed = feedparser.parse(source['url'])
                if not feed.entries:
                    raise Exception("No entries found")
                    
                for entry in feed.entries[:20]:  # Limit to 20 articles per source
                    article = self._parse_rss_entry(entry, source)
                    if article:
                        articles.append(article)
                        
            except Exception as e:
                logger.warning(f"Feedparser failed for {source['name']}: {e}, trying manual parsing")
                articles.extend(self._manual_rss_parse(source))
                
        except Exception as e:
            logger.error(f"Failed to scrape {source['name']}: {e}")
        
        return articles

    def _parse_rss_entry(self, entry, source: Dict) -> Optional[Dict]:
        """Parse individual RSS entry"""
        try:
            # Extract basic info
            title = getattr(entry, 'title', '').strip()
            description = getattr(entry, 'summary', '').strip()
            url = getattr(entry, 'link', '').strip()
            
            if not title or not url:
                return None
            
            # Parse date
            published_date = self._parse_date(getattr(entry, 'published', ''))
            
            # Get image URL
            image_url = self._extract_image_from_entry(entry)
            
            # Create article object
            article = {
                'title': title,
                'summary': self._clean_html(description)[:500],  # Changed from 'description' to 'summary'
                'url': url,
                'published_date': published_date,
                'source': source['name'],
                'category': source['category'],
                'tags': self._generate_tags(title, description, source['category']),
                'image_url': image_url,
                'author': getattr(entry, 'author', ''),
                'read_time': max(3, len(description.split()) // 200)  # Estimate read time
            }
            
            # Validate URL more strictly
            is_valid, validation_info = self.url_validator.validate_article_url(article)
            if not is_valid:
                logger.warning(f"Skipping article with invalid URL: {url} - {validation_info.get('error', 'Unknown error')}")
                return None
                
            return article
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None

    def _manual_rss_parse(self, source: Dict) -> List[Dict]:
        """Manual RSS parsing for sources where feedparser fails"""
        articles = []
        try:
            response = self.session.get(source['url'], timeout=30)
            response.raise_for_status()
            
            # Simple XML parsing for basic RSS structure
            content = response.text
            
            # Extract items using regex (basic approach)
            item_pattern = r'<item>(.*?)</item>'
            items = re.findall(item_pattern, content, re.DOTALL | re.IGNORECASE)
            
            for item in items[:20]:  # Limit to 20 articles
                title_match = re.search(r'<title[^>]*>(.*?)</title>', item, re.DOTALL | re.IGNORECASE)
                link_match = re.search(r'<link[^>]*>(.*?)</link>', item, re.DOTALL | re.IGNORECASE)
                desc_match = re.search(r'<description[^>]*>(.*?)</description>', item, re.DOTALL | re.IGNORECASE)
                date_match = re.search(r'<pubDate[^>]*>(.*?)</pubDate>', item, re.DOTALL | re.IGNORECASE)
                
                if title_match and link_match:
                    title = self._clean_html(title_match.group(1).strip())
                    url = link_match.group(1).strip()
                    description = self._clean_html(desc_match.group(1).strip()) if desc_match else ""
                    pub_date = self._parse_date(date_match.group(1).strip()) if date_match else datetime.now().isoformat()
                    
                    if title and url:
                        article = {
                            'title': title,
                            'summary': description[:500],  # Changed from 'description' to 'summary'
                            'url': url,
                            'published_date': pub_date,
                            'source': source['name'],
                            'category': source['category'],
                            'tags': self._generate_tags(title, description, source['category']),
                            'image_url': '',
                            'author': '',
                            'read_time': max(3, len(description.split()) // 200)
                        }
                        
                        # Validate URL before adding
                        is_valid, validation_info = self.url_validator.validate_article_url(article)
                        if is_valid:
                            articles.append(article)
                        else:
                            logger.warning(f"Skipping article with invalid URL in manual parse: {url} - {validation_info.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Manual parsing failed for {source['name']}: {e}")
        
        return articles

    def scrape_google_news(self) -> List[Dict]:
        """Scrape Google News for health topics"""
        articles = []
        
        for keyword in self.health_keywords[:10]:  # Limit keywords
            try:
                url = f"https://news.google.com/rss/search?q={quote_plus(keyword)}&hl=en-US&gl=US&ceid=US:en"
                
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:  # 5 articles per keyword
                    article = self._parse_rss_entry(entry, {
                        'name': 'Google News',
                        'category': 'health_news'
                    })
                    
                    if article:
                        article['tags'] = f"{article['tags']},{keyword}" if article['tags'] else keyword
                        
                        # Double-check URL validation for Google News articles
                        is_valid, validation_info = self.url_validator.validate_article_url(article)
                        if is_valid:
                            articles.append(article)
                        else:
                            logger.warning(f"Skipping Google News article with invalid URL: {article.get('url')} - {validation_info.get('error', 'Unknown error')}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Failed to scrape Google News for '{keyword}': {e}")
        
        return articles

    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to ISO format"""
        if not date_str:
            return datetime.now().isoformat()
        
        # Common date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).isoformat()
            except:
                continue
        
        return datetime.now().isoformat()

    def _clean_html(self, text: str) -> str:
        """Clean HTML tags and entities from text"""
        if not text:
            return ""
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Replace HTML entities
        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
        
        return clean.strip()

    def _extract_image_from_entry(self, entry) -> str:
        """Extract image URL from RSS entry"""
        # Try various common image fields
        if hasattr(entry, 'media_content') and entry.media_content:
            return entry.media_content[0].get('url', '')
        
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.type and 'image' in enclosure.type:
                    return enclosure.href
        
        # Look for images in description
        if hasattr(entry, 'summary'):
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', entry.summary)
            if img_match:
                return img_match.group(1)
        
        return ""

    def _generate_tags(self, title: str, description: str, category: str) -> str:
        """Generate relevant tags for the article"""
        tags = [category]
        
        text = f"{title} {description}".lower()
        
        # Health-related tag mapping
        tag_keywords = {
            'diabetes': ['diabetes', 'blood sugar', 'insulin', 'glucose'],
            'nutrition': ['nutrition', 'diet', 'food', 'eating', 'vitamin'],
            'fitness': ['fitness', 'exercise', 'workout', 'physical activity'],
            'mental_health': ['mental health', 'depression', 'anxiety', 'stress'],
            'heart_health': ['heart', 'cardiovascular', 'blood pressure', 'cholesterol'],
            'weight_management': ['weight', 'obesity', 'overweight', 'BMI'],
            'preventive_care': ['prevention', 'screening', 'early detection'],
            'lifestyle': ['lifestyle', 'wellness', 'healthy living'],
            'women_health': ['women', 'pregnancy', 'maternal'],
            'men_health': ['men', 'prostate', 'testosterone'],
            'elderly': ['elderly', 'aging', 'senior']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return ','.join(list(set(tags)))  # Remove duplicates

    def save_articles(self, articles: List[Dict]) -> int:
        """Save articles to database"""
        saved_count = 0
        
        with sqlite3.connect(DB_PATH) as conn:
            for article in articles:
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO articles 
                        (title, summary, url, published_date, source, category, tags, image_url, author, read_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article['title'],
                        article['summary'],  # Changed from 'description' to 'summary'
                        article['url'],
                        article['published_date'],
                        article['source'],
                        article['category'],
                        article['tags'],
                        article['image_url'],
                        article['author'],
                        article['read_time']
                    ))
                    
                    if conn.total_changes > 0:
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Error saving article '{article['title']}': {e}")
            
            conn.commit()
        
        return saved_count

    def run_scraping(self) -> Dict:
        """Run complete scraping process"""
        logger.info("🚀 Starting Master Health Scraper...")
        
        # Initialize database
        self.init_database()
        
        all_articles = []
        
        # Scrape RSS sources
        for source in self.rss_sources:
            articles = self.scrape_rss_source(source)
            all_articles.extend(articles)
            time.sleep(2)  # Rate limiting
        
        # Scrape Google News
        google_articles = self.scrape_google_news()
        all_articles.extend(google_articles)
        
        # Save to database
        saved_count = self.save_articles(all_articles)
        
        result = {
            'total_scraped': len(all_articles),
            'total_saved': saved_count,
            'sources_processed': len(self.rss_sources) + 1,  # +1 for Google News
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Scraping completed: {saved_count}/{len(all_articles)} articles saved")
        return result

def main():
    """Main execution function"""
    scraper = MasterHealthScraper()
    result = scraper.run_scraping()
    
    print("\n" + "="*60)
    print("🏥 MASTER HEALTH SCRAPER - RESULTS")
    print("="*60)
    print(f"📊 Total Articles Scraped: {result['total_scraped']}")
    print(f"💾 Articles Saved to Database: {result['total_saved']}")
    print(f"🌐 Sources Processed: {result['sources_processed']}")
    print(f"⏰ Completed at: {result['timestamp']}")
    print("="*60)
    
    return result

if __name__ == "__main__":
    main()
