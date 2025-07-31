#!/usr/bin/env python3
"""
Indian Health News Scraper

This scraper fetches health news from major Indian news websites
with comprehensive URL validation and content quality assurance.
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
from urllib.parse import urljoin, urlparse
import feedparser

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import our URL validator
try:
    from api.url_validator import URLValidator
except ImportError:
    sys.path.append(str(BASE_DIR / "api"))
    from url_validator import URLValidator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = BASE_DIR / "db" / "articles.db"

class IndianHealthScraper:
    """Scraper for Indian health news websites"""
    
    def __init__(self):
        self.url_validator = URLValidator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Indian health news sources with RSS feeds
        self.indian_sources = [
            {
                "name": "Times of India Health",
                "rss_url": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
                "base_url": "https://timesofindia.indiatimes.com",
                "priority": 3
            },
            {
                "name": "Hindustan Times Health", 
                "rss_url": "https://www.hindustantimes.com/feeds/rss/lifestyle/health/rssfeed.xml",
                "base_url": "https://www.hindustantimes.com",
                "priority": 3
            },
            {
                "name": "Indian Express Health",
                "rss_url": "https://indianexpress.com/section/lifestyle/health/feed/",
                "base_url": "https://indianexpress.com",
                "priority": 3
            },
            {
                "name": "NDTV Health",
                "rss_url": "https://feeds.feedburner.com/ndtvnews-health",
                "base_url": "https://www.ndtv.com",
                "priority": 2
            },
            {
                "name": "DNA India Health",
                "rss_url": "https://www.dnaindia.com/feeds/health.xml",
                "base_url": "https://www.dnaindia.com",
                "priority": 2
            },
            {
                "name": "The Hindu Health",
                "rss_url": "https://www.thehindu.com/sci-tech/health/feeder/default.rss",
                "base_url": "https://www.thehindu.com",
                "priority": 3
            },
            {
                "name": "News18 Health",
                "rss_url": "https://www.news18.com/rss/lifestyle/health-and-fitness.xml",
                "base_url": "https://www.news18.com", 
                "priority": 2
            },
            {
                "name": "Zee News Health",
                "rss_url": "https://zeenews.india.com/rss/health-news.xml",
                "base_url": "https://zeenews.india.com",
                "priority": 2
            },
            {
                "name": "Business Standard Health",
                "rss_url": "https://www.business-standard.com/rss/health-174.rss",
                "base_url": "https://www.business-standard.com",
                "priority": 2
            },
            {
                "name": "Republic World Health",
                "rss_url": "https://www.republicworld.com/rss/lifestyle/health",
                "base_url": "https://www.republicworld.com",
                "priority": 1
            }
        ]
        
        # Health-specific RSS feeds from Indian medical institutions
        self.medical_institution_sources = [
            {
                "name": "ICMR (Indian Council of Medical Research)",
                "rss_url": "https://www.icmr.gov.in/rss.xml",
                "base_url": "https://www.icmr.gov.in",
                "priority": 3
            },
            {
                "name": "Ministry of Health & Family Welfare",
                "rss_url": "https://www.mohfw.gov.in/RSS.aspx",
                "base_url": "https://www.mohfw.gov.in",
                "priority": 3
            }
        ]
        
    def parse_rss_feed(self, source_config: Dict) -> List[Dict]:
        """Parse RSS feed from Indian news source"""
        articles = []
        source_name = source_config['name']
        
        try:
            logger.info(f"🔍 Fetching from {source_name}...")
            
            # Use feedparser for better RSS handling
            feed = feedparser.parse(source_config['rss_url'])
            
            if feed.bozo:
                logger.warning(f"⚠️ RSS feed might have issues for {source_name}: {feed.bozo_exception}")
            
            entries = feed.entries[:20]  # Limit to 20 most recent articles
            logger.info(f"📰 Found {len(entries)} articles from {source_name}")
            
            for entry in entries:
                try:
                    # Extract article data
                    title = entry.get('title', '').strip()
                    summary = entry.get('summary', '') or entry.get('description', '')
                    link = entry.get('link', '').strip()
                    
                    # Clean summary from HTML tags
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
                    
                    # Only recent articles (last 7 days)
                    if article_date < datetime.now() - timedelta(days=7):
                        continue
                    
                    # Validate that this is health-related content
                    if not self.is_health_related(title, summary):
                        continue
                    
                    # Extract author if available
                    author = entry.get('author', '') or entry.get('creator', '')
                    
                    article_data = {
                        'title': title,
                        'summary': summary,
                        'url': link,
                        'date': article_date.isoformat(),
                        'author': author,
                        'source': source_name,
                        'priority': source_config['priority']
                    }
                    
                    # Only add if we have minimum required data
                    if title and link and len(title) > 10:
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing article from {source_name}: {e}")
                    continue
            
            logger.info(f"✅ Successfully parsed {len(articles)} health articles from {source_name}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching from {source_name}: {e}")
        
        return articles
    
    def is_health_related(self, title: str, summary: str) -> bool:
        """Check if article is health-related"""
        text = f"{title} {summary}".lower()
        
        # Indian health-specific keywords
        indian_health_keywords = [
            # English health terms
            'health', 'medical', 'disease', 'treatment', 'medicine', 'doctor', 'hospital',
            'wellness', 'fitness', 'nutrition', 'diet', 'exercise', 'mental health',
            'covid', 'vaccine', 'immunity', 'infection', 'diagnosis', 'therapy',
            'cancer', 'diabetes', 'heart', 'blood pressure', 'cholesterol',
            'ayurveda', 'yoga', 'meditation', 'healthcare', 'pharmaceutical',
            
            # Indian medical system terms
            'aiims', 'icmr', 'mohfw', 'ayush', 'homeopathy', 'unani',
            'alternative medicine', 'traditional medicine', 'herbal medicine',
            
            # Disease names common in India
            'dengue', 'malaria', 'tuberculosis', 'typhoid', 'hepatitis',
            'chikungunya', 'swine flu', 'bird flu', 'zika virus',
            
            # Health conditions
            'obesity', 'malnutrition', 'anemia', 'pregnancy', 'child health',
            'maternal health', 'elderly care', 'preventive care'
        ]
        
        return any(keyword in text for keyword in indian_health_keywords)
    
    def categorize_indian_article(self, article: Dict) -> Dict:
        """Categorize article with Indian health context"""
        text = f"{article['title']} {article['summary']}".lower()
        
        # COVID/Pandemic related
        covid_keywords = ['covid', 'corona', 'pandemic', 'lockdown', 'vaccine', 'omicron', 'delta variant']
        if any(keyword in text for keyword in covid_keywords):
            return {
                'categories': ['diseases'],
                'tags': ['covid_pandemic']
            }
        
        # Ayurveda/Traditional Medicine
        traditional_keywords = ['ayurveda', 'yoga', 'meditation', 'herbal', 'traditional medicine', 'ayush']
        if any(keyword in text for keyword in traditional_keywords):
            return {
                'categories': ['solutions'],
                'tags': ['traditional_medicine']
            }
        
        # Government Health Policies
        policy_keywords = ['policy', 'government', 'ministry', 'mohfw', 'icmr', 'scheme', 'program']
        if any(keyword in text for keyword in policy_keywords):
            return {
                'categories': ['news'],
                'tags': ['health_policy']
            }
        
        # Disease outbreaks common in India
        outbreak_keywords = ['dengue', 'malaria', 'tuberculosis', 'hepatitis', 'outbreak', 'epidemic']
        if any(keyword in text for keyword in outbreak_keywords):
            return {
                'categories': ['diseases'],
                'tags': ['infectious_diseases']
            }
        
        # Nutrition and food safety
        nutrition_keywords = ['nutrition', 'food safety', 'malnutrition', 'diet', 'eating', 'food poisoning']
        if any(keyword in text for keyword in nutrition_keywords):
            return {
                'categories': ['food'],
                'tags': ['nutrition_basics']
            }
        
        # Mental health
        mental_keywords = ['mental health', 'depression', 'anxiety', 'stress', 'suicide', 'counseling']
        if any(keyword in text for keyword in mental_keywords):
            return {
                'categories': ['diseases'],
                'tags': ['mental_health']
            }
        
        # Women and child health
        women_child_keywords = ['pregnancy', 'maternal', 'child health', 'vaccination', 'immunization']
        if any(keyword in text for keyword in women_child_keywords):
            return {
                'categories': ['solutions'],
                'tags': ['maternal_child_health']
            }
        
        # Default categorization
        return {
            'categories': ['news'],
            'tags': ['indian_health_news']
        }
    
    def save_validated_articles(self, articles: List[Dict], source_name: str) -> int:
        """Save articles with URL validation"""
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
                
                # Categorize article with Indian context
                categorization = self.categorize_indian_article(article)
                article.update(categorization)
                
                # Convert lists to JSON
                categories_json = json.dumps(article.get('categories', ['news']))
                tags_json = json.dumps(article.get('tags', ['indian_health_news']))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO articles 
                    (date, title, authors, summary, url, categories, tags, source, priority, url_health, url_accessible, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        
        logger.info(f"📊 {source_name}: {saved_count} saved, {duplicate_count} duplicates, {invalid_count} invalid URLs")
        return saved_count
    
    def fetch_all_indian_sources(self) -> int:
        """Fetch from all Indian health news sources"""
        total_saved = 0
        start_time = datetime.now()
        
        logger.info("🇮🇳 Fetching from Indian health news sources...")
        
        # Fetch from major Indian news sources
        all_sources = self.indian_sources + self.medical_institution_sources
        
        for source_config in all_sources:
            try:
                articles = self.parse_rss_feed(source_config)
                saved = self.save_validated_articles(articles, source_config['name'])
                total_saved += saved
                
                # Rate limiting - be respectful to Indian servers
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error processing {source_config['name']}: {e}")
                continue
        
        duration = datetime.now() - start_time
        
        logger.info(f"\n📊 Indian Health News Scraping Summary:")
        logger.info(f"   • Total articles saved: {total_saved}")
        logger.info(f"   • Sources processed: {len(all_sources)}")
        logger.info(f"   • Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"   • All URLs validated and accessible")
        
        return total_saved

def main():
    """Main function for Indian health news scraping"""
    print("🇮🇳 Indian Health News Scraper")
    print("=" * 50)
    print("Fetching health news from major Indian sources:")
    print("• Times of India Health")
    print("• Hindustan Times Health") 
    print("• Indian Express Health")
    print("• NDTV Health")
    print("• The Hindu Health")
    print("• DNA India Health")
    print("• News18 Health")
    print("• Zee News Health")
    print("• Business Standard Health")
    print("• Republic World Health")
    print("• ICMR Official")
    print("• Ministry of Health & Family Welfare")
    print("=" * 50)
    
    scraper = IndianHealthScraper()
    total_saved = scraper.fetch_all_indian_sources()
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} validated Indian health articles!")
        print("✅ All URLs are verified and accessible!")
        print("\n💡 Next steps:")
        print("   1. Start the API: cd api && uvicorn main:app --reload")
        print("   2. Test: http://localhost:8000/articles/latest")
        print("   3. Check categories: http://localhost:8000/categories")
    else:
        print("\n⚠️ No articles were saved. This might be due to:")
        print("   • Network connectivity issues")
        print("   • RSS feeds being temporarily unavailable")
        print("   • All articles being duplicates or invalid")
    
    return total_saved

if __name__ == "__main__":
    main()