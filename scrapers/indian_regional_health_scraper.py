#!/usr/bin/env python3
"""
Indian Regional Health News Scraper

This scraper focuses on regional Indian health news sources,
medical institutions, and health-specific Indian websites.
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
import feedparser
from bs4 import BeautifulSoup

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

class IndianRegionalHealthScraper:
    """Scraper for Indian regional and specialized health sources"""
    
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
        
        # Indian health-specific websites and medical portals
        self.specialized_health_sources = [
            {
                "name": "HealthLine India",
                "rss_url": "https://www.healthline.com/rss/health-news",
                "base_url": "https://www.healthline.com",
                "priority": 2,
                "filter_for_india": True
            },
            {
                "name": "Practo Health Feed",
                "base_url": "https://www.practo.com",
                "web_scrape": True,
                "health_section": "/health-feed",
                "priority": 2
            },
            {
                "name": "1mg Health Articles",
                "base_url": "https://www.1mg.com",
                "web_scrape": True,
                "health_section": "/articles",
                "priority": 2
            },
            {
                "name": "Apollo Health Library",
                "base_url": "https://www.apollohospitals.com",
                "web_scrape": True,
                "health_section": "/health-library",
                "priority": 3
            },
            {
                "name": "Max Healthcare Blog",
                "base_url": "https://www.maxhealthcare.in",
                "web_scrape": True,
                "health_section": "/blog",
                "priority": 2
            }
        ]
        
        # Regional Indian news sources with health sections
        self.regional_sources = [
            {
                "name": "Deccan Herald Health",
                "rss_url": "https://www.deccanherald.com/rss/health.rss",
                "base_url": "https://www.deccanherald.com",
                "priority": 2,
                "region": "South India"
            },
            {
                "name": "Deccan Chronicle Health", 
                "rss_url": "https://www.deccanchronicle.com/rss/health.rss",
                "base_url": "https://www.deccanchronicle.com",
                "priority": 2,
                "region": "South India"
            },
            {
                "name": "Pune Mirror Health",
                "rss_url": "https://punemirror.indiatimes.com/rssfeeds/61471522.cms",
                "base_url": "https://punemirror.indiatimes.com",
                "priority": 1,
                "region": "Maharashtra"
            },
            {
                "name": "Mumbai Mirror Health",
                "rss_url": "https://mumbaimirror.indiatimes.com/rssfeeds/61471522.cms", 
                "base_url": "https://mumbaimirror.indiatimes.com",
                "priority": 1,
                "region": "Maharashtra"
            },
            {
                "name": "Delhi Times Health",
                "rss_url": "https://timesofindia.indiatimes.com/rssfeeds/11107809.cms",
                "base_url": "https://timesofindia.indiatimes.com",
                "priority": 2,
                "region": "Delhi"
            },
            {
                "name": "Bangalore Mirror Health",
                "rss_url": "https://bangaloremirror.indiatimes.com/rssfeeds/61471522.cms",
                "base_url": "https://bangaloremirror.indiatimes.com", 
                "priority": 1,
                "region": "Karnataka"
            },
            {
                "name": "Telegraph India Health",
                "rss_url": "https://www.telegraphindia.com/rss/health",
                "base_url": "https://www.telegraphindia.com",
                "priority": 2,
                "region": "West Bengal"
            },
            {
                "name": "Statesman Health",
                "rss_url": "https://www.thestatesman.com/rss/health.rss",
                "base_url": "https://www.thestatesman.com",
                "priority": 2,
                "region": "West Bengal"
            }
        ]
        
        # Medical institution and government sources
        self.medical_institution_sources = [
            {
                "name": "AIIMS Delhi",
                "base_url": "https://www.aiims.edu",
                "web_scrape": True,
                "news_section": "/en/component/content/",
                "priority": 3
            },
            {
                "name": "PGIMER Chandigarh",
                "base_url": "https://www.pgimer.edu.in",
                "web_scrape": True,
                "news_section": "/PGIMER_Portal/PGIMERPORTAL/",
                "priority": 3
            },
            {
                "name": "JIPMER",
                "base_url": "https://www.jipmer.edu.in",
                "web_scrape": True,
                "news_section": "/news",
                "priority": 3
            },
            {
                "name": "NIMHANS",
                "base_url": "https://nimhans.ac.in",
                "web_scrape": True,
                "news_section": "/news",
                "priority": 3
            }
        ]
    
    def parse_rss_feed(self, source_config: Dict) -> List[Dict]:
        """Parse RSS feed from regional Indian source"""
        articles = []
        source_name = source_config['name']
        
        try:
            logger.info(f"🔍 Fetching from {source_name} ({source_config.get('region', 'India')})...")
            
            # Use feedparser for RSS
            feed = feedparser.parse(source_config.get('rss_url', ''))
            
            if feed.bozo:
                logger.warning(f"⚠️ RSS feed issues for {source_name}: {feed.bozo_exception}")
            
            entries = feed.entries[:15]  # Limit to 15 most recent
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
                    
                    # Only recent articles (last 7 days)
                    if article_date < datetime.now() - timedelta(days=7):
                        continue
                    
                    # Filter for India-specific content if needed
                    if source_config.get('filter_for_india') and not self.is_india_related(title, summary):
                        continue
                    
                    # Validate health relevance
                    if not self.is_health_related(title, summary):
                        continue
                    
                    author = entry.get('author', '') or entry.get('creator', '')
                    
                    article_data = {
                        'title': title,
                        'summary': summary,
                        'url': link,
                        'date': article_date.isoformat(),
                        'author': author,
                        'source': source_name,
                        'priority': source_config.get('priority', 1),
                        'region': source_config.get('region', 'India')
                    }
                    
                    if title and link and len(title) > 10:
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing article from {source_name}: {e}")
                    continue
            
            logger.info(f"✅ Parsed {len(articles)} health articles from {source_name}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching from {source_name}: {e}")
        
        return articles
    
    def scrape_health_website(self, source_config: Dict) -> List[Dict]:
        """Scrape health articles from Indian medical websites"""
        articles = []
        source_name = source_config['name']
        
        try:
            logger.info(f"🌐 Web scraping from {source_name}...")
            
            base_url = source_config['base_url']
            health_section = source_config.get('health_section', '/health')
            full_url = base_url + health_section
            
            response = self.session.get(full_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic article selectors (might need customization per site)
            article_selectors = [
                'article',
                '.article',
                '.post',
                '.news-item',
                '.health-article',
                '.blog-post',
                '[class*="article"]',
                '[class*="post"]'
            ]
            
            found_articles = []
            
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements and len(elements) > 2:  # Found good selector
                    found_articles = elements[:10]  # Limit to 10
                    break
            
            for element in found_articles:
                try:
                    # Extract title
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    
                    # Extract link
                    link_elem = element.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    link = link_elem['href']
                    if link.startswith('/'):
                        link = base_url + link
                    
                    # Extract summary/description
                    summary_elem = element.find(['p', '.summary', '.excerpt', '.description'])
                    summary = summary_elem.get_text().strip()[:500] if summary_elem else ''
                    
                    # Basic validation
                    if not title or len(title) < 10 or not self.is_health_related(title, summary):
                        continue
                    
                    article_data = {
                        'title': title,
                        'summary': summary,
                        'url': link,
                        'date': datetime.now().isoformat(),
                        'author': '',
                        'source': source_name,
                        'priority': source_config.get('priority', 2)
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error extracting article from {source_name}: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(articles)} articles from {source_name}")
            
        except Exception as e:
            logger.error(f"❌ Error scraping {source_name}: {e}")
        
        return articles
    
    def is_health_related(self, title: str, summary: str) -> bool:
        """Check if content is health-related with Indian context"""
        text = f"{title} {summary}".lower()
        
        health_keywords = [
            # General health
            'health', 'medical', 'disease', 'treatment', 'medicine', 'doctor', 'hospital',
            'wellness', 'fitness', 'nutrition', 'diet', 'exercise', 'mental health',
            'covid', 'vaccine', 'immunity', 'infection', 'diagnosis', 'therapy',
            'cancer', 'diabetes', 'heart', 'blood pressure', 'cholesterol',
            
            # Indian medical terms
            'ayurveda', 'yoga', 'meditation', 'healthcare', 'pharmaceutical',
            'aiims', 'icmr', 'mohfw', 'ayush', 'homeopathy', 'unani',
            
            # Common diseases in India
            'dengue', 'malaria', 'tuberculosis', 'typhoid', 'hepatitis',
            'chikungunya', 'swine flu', 'bird flu', 'zika virus',
            
            # Health conditions
            'obesity', 'malnutrition', 'anemia', 'pregnancy', 'child health',
            'maternal health', 'elderly care', 'preventive care', 'public health',
            
            # Medical specialties
            'cardiology', 'neurology', 'oncology', 'pediatrics', 'gynecology',
            'orthopedics', 'dermatology', 'psychiatry', 'surgery'
        ]
        
        return any(keyword in text for keyword in health_keywords)
    
    def is_india_related(self, title: str, summary: str) -> bool:
        """Check if content is India-related"""
        text = f"{title} {summary}".lower()
        
        india_keywords = [
            'india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata',
            'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur',
            'nagpur', 'indore', 'bhopal', 'visakhapatnam', 'pimpri-chinchwad',
            'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik',
            'faridabad', 'meerut', 'rajkot', 'kalyan-dombivli', 'vasai-virar',
            'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar',
            'navi mumbai', 'allahabad', 'ranchi', 'howrah', 'coimbatore',
            'jabalpur', 'gwalior', 'vijayawada', 'jodhpur', 'madurai',
            'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur',
            'mohfw', 'icmr', 'aiims', 'government of india', 'ministry of health'
        ]
        
        return any(keyword in text for keyword in india_keywords)
    
    def categorize_regional_article(self, article: Dict) -> Dict:
        """Categorize article with regional Indian context"""
        text = f"{article['title']} {article['summary']}".lower()
        region = article.get('region', 'India')
        
        # Regional health issues
        if 'south india' in region.lower():
            south_keywords = ['dengue', 'chikungunya', 'coconut oil', 'rice diet', 'monsoon health']
            if any(keyword in text for keyword in south_keywords):
                return {
                    'categories': ['diseases'],
                    'tags': ['south_india_health']
                }
        
        # Government/Policy related
        policy_keywords = ['policy', 'government', 'scheme', 'program', 'ministry', 'budget']
        if any(keyword in text for keyword in policy_keywords):
            return {
                'categories': ['news'],
                'tags': ['health_policy']
            }
        
        # Hospital/Medical institution news
        hospital_keywords = ['hospital', 'aiims', 'pgimer', 'medical college', 'health center']
        if any(keyword in text for keyword in hospital_keywords):
            return {
                'categories': ['news'],
                'tags': ['medical_institutions']
            }
        
        # Traditional medicine
        traditional_keywords = ['ayurveda', 'yoga', 'meditation', 'herbal', 'traditional']
        if any(keyword in text for keyword in traditional_keywords):
            return {
                'categories': ['solutions'],
                'tags': ['traditional_medicine']
            }
        
        # Regional disease outbreaks
        outbreak_keywords = ['outbreak', 'epidemic', 'cases rising', 'alert', 'warning']
        if any(keyword in text for keyword in outbreak_keywords):
            return {
                'categories': ['diseases'],
                'tags': ['disease_outbreaks']
            }
        
        # Default categorization
        return {
            'categories': ['news'],
            'tags': ['regional_health_news']
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
                
                # Categorize with regional context
                categorization = self.categorize_regional_article(article)
                article.update(categorization)
                
                # Convert lists to JSON
                categories_json = json.dumps(article.get('categories', ['news']))
                tags_json = json.dumps(article.get('tags', ['regional_health_news']))
                
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
    
    def fetch_all_regional_sources(self) -> int:
        """Fetch from all regional Indian sources"""
        total_saved = 0
        start_time = datetime.now()
        
        logger.info("🗺️ Fetching from Indian regional health sources...")
        
        # Process RSS-based regional sources
        for source_config in self.regional_sources:
            if source_config.get('rss_url'):
                try:
                    articles = self.parse_rss_feed(source_config)
                    saved = self.save_validated_articles(articles, source_config['name'])
                    total_saved += saved
                    time.sleep(1.5)  # Rate limiting
                except Exception as e:
                    logger.error(f"❌ Error processing {source_config['name']}: {e}")
        
        # Process specialized health websites
        for source_config in self.specialized_health_sources:
            if source_config.get('web_scrape'):
                try:
                    articles = self.scrape_health_website(source_config)
                    saved = self.save_validated_articles(articles, source_config['name'])
                    total_saved += saved
                    time.sleep(2)  # Longer delay for web scraping
                except Exception as e:
                    logger.error(f"❌ Error scraping {source_config['name']}: {e}")
            elif source_config.get('rss_url'):
                try:
                    articles = self.parse_rss_feed(source_config)
                    saved = self.save_validated_articles(articles, source_config['name'])
                    total_saved += saved
                    time.sleep(1.5)
                except Exception as e:
                    logger.error(f"❌ Error processing {source_config['name']}: {e}")
        
        # Process medical institution sources
        for source_config in self.medical_institution_sources:
            if source_config.get('web_scrape'):
                try:
                    articles = self.scrape_health_website(source_config)
                    saved = self.save_validated_articles(articles, source_config['name'])
                    total_saved += saved
                    time.sleep(3)  # Respectful delay for institutional sites
                except Exception as e:
                    logger.error(f"❌ Error scraping {source_config['name']}: {e}")
        
        duration = datetime.now() - start_time
        
        logger.info(f"\n📊 Regional Indian Health Scraping Summary:")
        logger.info(f"   • Total articles saved: {total_saved}")
        logger.info(f"   • Sources processed: {len(self.regional_sources + self.specialized_health_sources + self.medical_institution_sources)}")
        logger.info(f"   • Duration: {duration.total_seconds():.1f} seconds")
        
        return total_saved

def main():
    """Main function"""
    print("🗺️ Indian Regional Health News Scraper")
    print("=" * 50)
    print("📰 REGIONAL NEWS SOURCES:")
    print("• Deccan Herald Health (South India)")
    print("• Deccan Chronicle Health (South India)")
    print("• Telegraph India Health (West Bengal)")
    print("• Statesman Health (West Bengal)")
    print("• Delhi Times Health (Delhi)")
    print("• Pune Mirror Health (Maharashtra)")
    print("• Mumbai Mirror Health (Maharashtra)")
    print("• Bangalore Mirror Health (Karnataka)")
    print()
    print("🏥 SPECIALIZED HEALTH PORTALS:")
    print("• Practo Health Feed")
    print("• 1mg Health Articles")
    print("• Apollo Health Library")
    print("• Max Healthcare Blog")
    print()
    print("🎓 MEDICAL INSTITUTIONS:")
    print("• AIIMS Delhi")
    print("• PGIMER Chandigarh")
    print("• JIPMER")
    print("• NIMHANS")
    print("=" * 50)
    
    scraper = IndianRegionalHealthScraper()
    total_saved = scraper.fetch_all_regional_sources()
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} regional Indian health articles!")
        print("✅ All URLs validated and accessible!")
    else:
        print("\n⚠️ No articles were saved. Check network connectivity.")
    
    return total_saved

if __name__ == "__main__":
    main()