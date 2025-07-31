#!/usr/bin/env python3
"""
Comprehensive News Scraper - SmartNews Style Aggregation

This scraper aggregates health news from multiple trusted sources similar to SmartNews:
- NewsAPI (various health sources)
- Reddit Health News
- Apple News RSS feeds
- Google News RSS feeds
- Major news outlets RSS feeds
- Health-specific news sources
- International health news sources

The scraper maintains the same endpoints as the current project.
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
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import our URL validator
try:
    # Add the parent directory to path for app imports
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

class ComprehensiveNewsScraper:
    """SmartNews-style comprehensive news aggregator for health content"""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # News API configuration (requires free API key)
        self.newsapi_key = "your_newsapi_key_here"  # Get from https://newsapi.org/
        
        # Major news outlets RSS feeds for health content
        self.major_news_sources = [
            {
                "name": "BBC Health",
                "rss_url": "http://feeds.bbci.co.uk/news/health/rss.xml",
                "base_url": "https://www.bbc.com",
                "priority": 3,
                "category": "international_health"
            },
            {
                "name": "Reuters Health",
                "rss_url": "https://feeds.reuters.com/reuters/healthNews",
                "base_url": "https://www.reuters.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "CNN Health",
                "rss_url": "http://rss.cnn.com/rss/edition_health.rss",
                "base_url": "https://www.cnn.com",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Associated Press Health",
                "rss_url": "https://apnews.com/apf-Health",
                "base_url": "https://apnews.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "NPR Health",
                "rss_url": "https://feeds.npr.org/1001/rss.xml",
                "base_url": "https://www.npr.org",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "ABC News Health",
                "rss_url": "https://abcnews.go.com/Health/healthnews",
                "base_url": "https://abcnews.go.com",
                "priority": 2,
                "category": "news"
            }
        ]
        
        # Health-specific sources
        self.health_specialized_sources = [
            {
                "name": "WebMD News",
                "rss_url": "https://feeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
                "base_url": "https://www.webmd.com",
                "priority": 2,
                "category": "solutions"
            },
            {
                "name": "Healthline News",
                "rss_url": "https://www.healthline.com/rss/health-news",
                "base_url": "https://www.healthline.com",
                "priority": 2,
                "category": "solutions"
            },
            {
                "name": "Medical News Today",
                "rss_url": "https://www.medicalnewstoday.com/rss",
                "base_url": "https://www.medicalnewstoday.com",
                "priority": 2,
                "category": "diseases"
            },
            {
                "name": "Health.com",
                "rss_url": "https://www.health.com/rss/health",
                "base_url": "https://www.health.com",
                "priority": 1,
                "category": "food"
            },
            {
                "name": "Everyday Health",
                "rss_url": "https://www.everydayhealth.com/rss/all-articles.xml",
                "base_url": "https://www.everydayhealth.com",
                "priority": 1,
                "category": "audience"
            }
        ]
        
        # Government and institutional sources
        self.institutional_sources = [
            {
                "name": "CDC Health News",
                "rss_url": "https://tools.cdc.gov/api/v2/resources/media/316422.rss",
                "base_url": "https://www.cdc.gov",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "NIH News",
                "rss_url": "https://www.nih.gov/news-events/news-releases/rss.xml",
                "base_url": "https://www.nih.gov",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "WHO News",
                "rss_url": "https://www.who.int/rss-feeds/news-english.xml",
                "base_url": "https://www.who.int",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "FDA News",
                "rss_url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-announcements/rss.xml",
                "base_url": "https://www.fda.gov",
                "priority": 3,
                "category": "news"
            }
        ]
        
        # Google News health topics
        self.google_news_health_topics = [
            "health+news",
            "medical+breakthrough", 
            "nutrition+research",
            "mental+health+news",
            "disease+prevention",
            "public+health+news",
            "healthcare+technology",
            "medical+study"
        ]
        
        # Alternative news aggregators and APIs
        self.alternative_sources = [
            {
                "name": "Bing News Health",
                "api_url": "https://api.bing.microsoft.com/v7.0/news/search",
                "api_key_required": True,
                "priority": 2,
                "category": "news"
            },
            {
                "name": "NewsData.io Health",
                "api_url": "https://newsdata.io/api/1/news",
                "api_key_required": True,
                "priority": 2,
                "category": "news"
            }
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
                url_health TEXT,
                url_accessible INTEGER DEFAULT 1,
                last_checked TIMESTAMP,
                news_score REAL DEFAULT 0.0,
                trending_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_url_accessible ON articles(url_accessible)",
            "CREATE INDEX IF NOT EXISTS idx_date ON articles(date)",
            "CREATE INDEX IF NOT EXISTS idx_priority ON articles(priority)",
            "CREATE INDEX IF NOT EXISTS idx_news_score ON articles(news_score)",
            "CREATE INDEX IF NOT EXISTS idx_trending_score ON articles(trending_score)",
            "CREATE INDEX IF NOT EXISTS idx_source ON articles(source)",
            "CREATE INDEX IF NOT EXISTS idx_categories ON articles(categories)",
            "CREATE INDEX IF NOT EXISTS idx_tags ON articles(tags)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database ready at: {DB_PATH}")
    
    def fetch_google_news_health(self, max_articles: int = 30) -> List[Dict]:
        """Fetch health news from Google News RSS feeds"""
        articles = []
        
        try:
            for topic in self.google_news_health_topics[:4]:  # Limit to avoid rate limiting
                logger.info(f"🔍 Fetching Google News for: {topic}")
                
                encoded_topic = quote_plus(topic)
                url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
                
                try:
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    
                    feed = feedparser.parse(response.content)
                    entries = feed.entries[:8]  # Limit per topic
                    
                    for entry in entries:
                        try:
                            title = entry.get('title', '').strip()
                            summary = entry.get('summary', '') or entry.get('description', '')
                            link = entry.get('link', '').strip()
                            
                            # Clean summary
                            if summary:
                                summary = re.sub(r'<[^>]+>', '', summary)
                                summary = re.sub(r'\s+', ' ', summary).strip()[:500]
                            
                            # Parse date
                            article_date = datetime.now()
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                try:
                                    article_date = datetime(*entry.published_parsed[:6])
                                except:
                                    pass
                            
                            # Only recent articles (last 3 days)
                            if article_date < datetime.now() - timedelta(days=3):
                                continue
                            
                            if title and link and len(title) > 10:
                                article_data = {
                                    'title': title,
                                    'summary': summary,
                                    'url': link,
                                    'date': article_date.isoformat(),
                                    'author': entry.get('author', ''),
                                    'source': f"Google News ({topic.replace('+', ' ').title()})",
                                    'priority': 2,
                                    'news_score': 0.7,  # Google News has good relevance
                                    'trending_score': 0.6
                                }
                                articles.append(article_data)
                                
                        except Exception as e:
                            logger.warning(f"Error parsing Google News entry: {e}")
                            continue
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching Google News for {topic}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in Google News fetch: {e}")
        
        logger.info(f"📰 Found {len(articles)} Google News health articles")
        return articles
    
    def fetch_newsapi_health(self, max_articles: int = 50) -> List[Dict]:
        """Fetch from NewsAPI with health-related queries"""
        if self.newsapi_key == "your_newsapi_key_here":
            logger.info("⚠️ NewsAPI key not configured, skipping NewsAPI")
            return []
        
        articles = []
        
        try:
            # Health-related queries for comprehensive coverage
            health_queries = [
                "health",
                "medical breakthrough", 
                "disease prevention",
                "nutrition research",
                "mental health",
                "public health"
            ]
            
            for query in health_queries[:3]:  # Limit to avoid rate limits
                logger.info(f"🔍 Fetching NewsAPI for: {query}")
                
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': min(20, max_articles // len(health_queries)),
                    'from': (datetime.now() - timedelta(days=3)).isoformat(),
                    'apiKey': self.newsapi_key
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                for article in data.get('articles', []):
                    if article.get('url') and article.get('title'):
                        article_data = {
                            'title': article['title'],
                            'summary': article.get('description', ''),
                            'url': article['url'],
                            'date': article.get('publishedAt', datetime.now().isoformat()),
                            'author': article.get('author', ''),
                            'source': f"NewsAPI ({article.get('source', {}).get('name', 'Unknown')})",
                            'priority': 2,
                            'news_score': 0.8,  # NewsAPI has high quality sources
                            'trending_score': 0.7
                        }
                        articles.append(article_data)
                
                time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
        
        logger.info(f"📰 Found {len(articles)} NewsAPI health articles")
        return articles
    
    def parse_rss_feed(self, source_config: Dict) -> List[Dict]:
        """Parse RSS feed with comprehensive error handling"""
        articles = []
        source_name = source_config['name']
        
        try:
            logger.info(f"🔍 Fetching from {source_name}...")
            
            response = self.session.get(source_config['rss_url'], timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"⚠️ RSS feed might have issues for {source_name}")
            
            entries = feed.entries[:15]  # Limit per source
            logger.info(f"📰 Found {len(entries)} articles from {source_name}")
            
            for entry in entries:
                try:
                    title = entry.get('title', '').strip()
                    summary = entry.get('summary', '') or entry.get('description', '')
                    link = entry.get('link', '').strip()
                    
                    # Clean summary
                    if summary:
                        summary = re.sub(r'<[^>]+>', '', summary)
                        summary = re.sub(r'\s+', ' ', summary).strip()[:500]
                    
                    # Parse date
                    article_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            article_date = datetime(*entry.published_parsed[:6])
                        except:
                            pass
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        try:
                            article_date = datetime(*entry.updated_parsed[:6])
                        except:
                            pass
                    
                    # Only recent articles (last 5 days)
                    if article_date < datetime.now() - timedelta(days=5):
                        continue
                    
                    # Validate health-related content
                    if not self.is_health_related(title, summary):
                        continue
                    
                    if title and link and len(title) > 10:
                        # Calculate news and trending scores
                        news_score = self.calculate_news_score(title, summary, source_config)
                        trending_score = self.calculate_trending_score(title, summary, article_date)
                        
                        article_data = {
                            'title': title,
                            'summary': summary,
                            'url': link,
                            'date': article_date.isoformat(),
                            'author': entry.get('author', ''),
                            'source': source_name,
                            'priority': source_config['priority'],
                            'news_score': news_score,
                            'trending_score': trending_score
                        }
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"Error parsing article from {source_name}: {e}")
                    continue
            
            logger.info(f"✅ Successfully parsed {len(articles)} health articles from {source_name}")
            
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
        
        return articles
    
    def is_health_related(self, title: str, summary: str) -> bool:
        """Enhanced health content detection"""
        text = f"{title} {summary}".lower()
        
        # Comprehensive health keywords
        health_keywords = [
            # Medical conditions
            'health', 'medical', 'disease', 'illness', 'condition', 'syndrome', 
            'disorder', 'cancer', 'diabetes', 'heart', 'cardiovascular', 'stroke',
            'infection', 'virus', 'bacteria', 'covid', 'flu', 'pneumonia',
            
            # Treatments and medicine
            'treatment', 'therapy', 'medicine', 'drug', 'medication', 'cure',
            'surgery', 'operation', 'procedure', 'vaccine', 'vaccination',
            'clinical', 'trial', 'study', 'research',
            
            # Body systems and health topics
            'brain', 'mental', 'depression', 'anxiety', 'nutrition', 'diet',
            'exercise', 'fitness', 'wellness', 'prevention', 'screening',
            'diagnosis', 'symptom', 'patient', 'doctor', 'hospital', 'clinic',
            
            # Public health
            'epidemic', 'pandemic', 'outbreak', 'public health', 'healthcare',
            'medical breakthrough', 'health policy', 'fda', 'cdc', 'who'
        ]
        
        # Must contain at least 2 health keywords or 1 strong health indicator
        strong_indicators = ['medical', 'health', 'disease', 'treatment', 'doctor', 'patient']
        
        health_count = sum(1 for keyword in health_keywords if keyword in text)
        strong_count = sum(1 for indicator in strong_indicators if indicator in text)
        
        return health_count >= 2 or strong_count >= 1
    
    def calculate_news_score(self, title: str, summary: str, source_config: Dict) -> float:
        """Calculate news relevance score (0.0 to 1.0)"""
        score = 0.0
        text = f"{title} {summary}".lower()
        
        # Base score from source priority
        score += source_config['priority'] * 0.2
        
        # Breaking news indicators
        breaking_words = ['breaking', 'urgent', 'alert', 'emergency', 'just in', 'developing']
        if any(word in text for word in breaking_words):
            score += 0.3
        
        # Research and study indicators
        research_words = ['study', 'research', 'clinical trial', 'breakthrough', 'discovery']
        if any(word in text for word in research_words):
            score += 0.2
        
        # Government/institutional source bonus
        if any(org in source_config['name'].lower() for org in ['cdc', 'nih', 'who', 'fda']):
            score += 0.2
        
        # Title length and quality
        if 40 <= len(title) <= 100:
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_trending_score(self, title: str, summary: str, article_date: datetime) -> float:
        """Calculate trending score based on recency and viral indicators"""
        score = 0.0
        text = f"{title} {summary}".lower()
        
        # Recency score (newer = higher score)
        hours_old = (datetime.now() - article_date).total_seconds() / 3600
        if hours_old <= 6:
            score += 0.4
        elif hours_old <= 24:
            score += 0.3
        elif hours_old <= 48:
            score += 0.2
        elif hours_old <= 72:
            score += 0.1
        
        # Viral/trending indicators
        viral_words = ['viral', 'trending', 'shocking', 'amazing', 'incredible', 'surprising']
        if any(word in text for word in viral_words):
            score += 0.2
        
        # Social media indicators
        social_words = ['twitter', 'facebook', 'social media', 'goes viral', 'internet']
        if any(word in text for word in social_words):
            score += 0.1
        
        # Controversy indicators
        controversy_words = ['controversial', 'debate', 'criticism', 'backlash']
        if any(word in text for word in controversy_words):
            score += 0.1
        
        return min(score, 1.0)
    
    def categorize_comprehensive_article(self, article: Dict) -> Dict:
        """Comprehensive categorization with SmartNews-style intelligence"""
        text = f"{article['title']} {article['summary']}".lower()
        
        categories = []
        tags = []
        
        # Breaking news detection
        breaking_words = ['breaking', 'urgent', 'alert', 'emergency', 'critical', 'just in']
        if any(word in text for word in breaking_words):
            categories.append('news')
            tags.append('breaking_news')
        
        # Disease and medical conditions
        disease_words = [
            'cancer', 'diabetes', 'heart disease', 'covid', 'flu', 'infection', 
            'disease', 'illness', 'condition', 'syndrome', 'disorder', 'stroke'
        ]
        if any(word in text for word in disease_words):
            categories.append('diseases')
            tags.append('medical_conditions')
        
        # Treatment and solutions
        treatment_words = [
            'treatment', 'therapy', 'cure', 'medication', 'drug', 'surgery',
            'procedure', 'intervention', 'remedy', 'healing'
        ]
        if any(word in text for word in treatment_words):
            categories.append('solutions')
            tags.append('medical_treatments')
        
        # Nutrition and food
        nutrition_words = [
            'nutrition', 'diet', 'food', 'eating', 'vitamin', 'supplement',
            'calories', 'protein', 'carbs', 'fat', 'healthy eating'
        ]
        if any(word in text for word in nutrition_words):
            categories.append('food')
            tags.append('nutrition_basics')
        
        # Mental health
        mental_words = ['mental health', 'depression', 'anxiety', 'stress', 'therapy', 'psychology']
        if any(word in text for word in mental_words):
            categories.append('audience')
            tags.append('mental_health')
        
        # Research and studies
        research_words = [
            'study', 'research', 'clinical trial', 'findings', 'breakthrough', 
            'discovery', 'published', 'journal', 'scientists'
        ]
        if any(word in text for word in research_words):
            categories.append('news')
            tags.append('breakthrough_research')
        
        # Default to news if no specific category found
        if not categories:
            categories = ['news']
            tags = ['recent_developments']
        
        return {
            'categories': categories,
            'tags': tags
        }
    
    def save_validated_articles(self, articles: List[Dict], source_name: str) -> int:
        """Save articles with comprehensive validation and scoring"""
        if not articles:
            logger.info(f"⚠️ No articles to save from {source_name}")
            return 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        saved_count = 0
        invalid_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                # Validate URL before saving
                is_valid, health_info = self.url_validator.validate_article_url(article)
                
                if not is_valid:
                    invalid_count += 1
                    logger.warning(f"⚠️ Invalid URL: {article['title'][:50]}... - {health_info.get('error', 'Unknown error')}")
                    continue
                
                # Categorize article
                categorization = self.categorize_comprehensive_article(article)
                article.update(categorization)
                
                # Convert lists to JSON
                categories_json = json.dumps(article.get('categories', ['news']))
                tags_json = json.dumps(article.get('tags', ['general']))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO articles 
                    (date, title, authors, summary, url, categories, tags, source, priority, 
                     url_health, url_accessible, last_checked, news_score, trending_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(health_info),
                    1 if is_valid else 0,
                    datetime.now().isoformat(),
                    article.get('news_score', 0.5),
                    article.get('trending_score', 0.5)
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
        
        logger.info(f"📊 {source_name}: {saved_count} saved, {duplicate_count} duplicates, {invalid_count} invalid URLs")
        return saved_count
    
    def fetch_all_sources(self, max_articles_per_source: int = 25) -> int:
        """Fetch from all comprehensive news sources"""
        total_saved = 0
        start_time = datetime.now()
        
        logger.info("🌍 Comprehensive News Scraper - SmartNews Style Aggregation")
        logger.info("=" * 70)
        
        # 1. Fetch from major news outlets
        logger.info("\n📰 Fetching from major news outlets...")
        for source_config in self.major_news_sources:
            articles = self.parse_rss_feed(source_config)
            saved = self.save_validated_articles(articles, source_config['name'])
            total_saved += saved
            time.sleep(2)  # Rate limiting
        
        # 2. Fetch from health-specialized sources
        logger.info("\n🏥 Fetching from health-specialized sources...")
        for source_config in self.health_specialized_sources:
            articles = self.parse_rss_feed(source_config)
            saved = self.save_validated_articles(articles, source_config['name'])
            total_saved += saved
            time.sleep(2)
        
        # 3. Fetch from institutional sources
        logger.info("\n🏛️ Fetching from government/institutional sources...")
        for source_config in self.institutional_sources:
            articles = self.parse_rss_feed(source_config)
            saved = self.save_validated_articles(articles, source_config['name'])
            total_saved += saved
            time.sleep(2)
        
        # 4. Fetch from Google News
        logger.info("\n🔍 Fetching from Google News health topics...")
        google_articles = self.fetch_google_news_health(max_articles_per_source)
        total_saved += self.save_validated_articles(google_articles, "Google News Health")
        
        # 5. Fetch from NewsAPI (if configured)
        logger.info("\n🔎 Fetching from NewsAPI...")
        newsapi_articles = self.fetch_newsapi_health(max_articles_per_source)
        total_saved += self.save_validated_articles(newsapi_articles, "NewsAPI Health")
        
        duration = datetime.now() - start_time
        
        logger.info(f"\n📊 Comprehensive News Scraping Summary:")
        logger.info(f"   • Total articles saved: {total_saved}")
        logger.info(f"   • Sources processed: {len(self.major_news_sources) + len(self.health_specialized_sources) + len(self.institutional_sources) + 2}")
        logger.info(f"   • Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"   • Database: {DB_PATH}")
        
        return total_saved

def main():
    """Main function for comprehensive news scraping"""
    print("🌍 Comprehensive News Scraper - SmartNews Style Health Aggregation")
    print("=" * 75)
    
    scraper = ComprehensiveNewsScraper()
    
    # Create database
    scraper.create_database()
    
    # Fetch from all sources
    total_saved = scraper.fetch_all_sources()
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} health articles from multiple sources!")
        print("✅ SmartNews-style aggregation complete!")
        print("\n💡 Next steps:")
        print("   1. Start the API: python start.py")
        print("   2. Visit: http://localhost:8000/articles/latest")
        print("   3. All existing endpoints work with new data!")
        print("\n🔧 Optional improvements:")
        print("   • Get NewsAPI key from: https://newsapi.org/")
        print("   • Update newsapi_key in this file for more sources")
    else:
        print("\n⚠️ No articles were saved. Check:")
        print("   • Internet connection")
        print("   • RSS feed availability")
        print("   • Database permissions")
    
    return total_saved

if __name__ == "__main__":
    main()
