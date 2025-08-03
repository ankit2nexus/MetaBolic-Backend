#!/usr/bin/env python3
"""
Ultra-Comprehensive Health News Scraper

This scraper aggregates health news from multiple high-quality sources to ensure
comprehensive coverage across all categories and subcategories.
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

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Import enhanced URL validator
try:
    from enhanced_url_validator import EnhancedURLValidator
except ImportError:
    EnhancedURLValidator = None

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database path
DB_PATH = BASE_DIR / "data" / "articles.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "db" / "articles.db"

class UltraComprehensiveHealthScraper:
    """Ultra-comprehensive health news scraper with extensive source coverage"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Initialize URL validator
        self.url_validator = EnhancedURLValidator() if EnhancedURLValidator else None
        
        # Comprehensive RSS sources organized by category
        self.rss_sources = {
            # International Health Organizations
            "international_health": [
                {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml", "priority": 3},
                {"name": "NIH News", "url": "https://www.nih.gov/news-events/news-releases/rss.xml", "priority": 3},
                {"name": "CDC Health", "url": "https://tools.cdc.gov/api/v2/resources/media/132608.rss", "priority": 3},
                {"name": "FDA News", "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-announcements/rss.xml", "priority": 3},
            ],
            
            # Major News Outlets - Health
            "news": [
                {"name": "Reuters Health", "url": "https://feeds.reuters.com/reuters/healthNews", "priority": 2},
                {"name": "CNN Health", "url": "http://rss.cnn.com/rss/edition_health.rss", "priority": 2},
                {"name": "BBC Health", "url": "http://feeds.bbci.co.uk/news/health/rss.xml", "priority": 2},
                {"name": "NPR Health", "url": "https://feeds.npr.org/1001/rss.xml", "priority": 2},
                {"name": "ABC Health", "url": "https://abcnews.go.com/Health/wireStory/rss", "priority": 2},
            ],
            
            # Medical Publications
            "diseases": [
                {"name": "PubMed Recent", "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/erss.cgi?rss_guid=1UQR2wVw1hTRF5EAkHnz", "priority": 3},
                {"name": "Medical News Today", "url": "https://www.medicalnewstoday.com/rss", "priority": 2},
                {"name": "ScienceDaily Health", "url": "https://rss.sciencedaily.com/health_medicine.xml", "priority": 2},
                {"name": "Healthline", "url": "https://www.healthline.com/rss", "priority": 2},
            ],
            
            # Nutrition and Food
            "food": [
                {"name": "Nutrition Research", "url": "https://rss.sciencedaily.com/health_medicine/nutrition.xml", "priority": 2},
                {"name": "Food Safety News", "url": "https://www.foodsafetynews.com/feed/", "priority": 2},
                {"name": "Nutrition.gov", "url": "https://www.nutrition.gov/rss.xml", "priority": 3},
            ],
            
            # Solutions and Treatments
            "solutions": [
                {"name": "Medical Breakthroughs", "url": "https://rss.sciencedaily.com/health_medicine/disease.xml", "priority": 2},
                {"name": "Drug Discovery", "url": "https://rss.sciencedaily.com/health_medicine/drugs.xml", "priority": 2},
                {"name": "Clinical Trials", "url": "https://clinicaltrials.gov/ct2/results/rss.xml", "priority": 3},
            ],
            
            # Indian Health Sources
            "indian_health": [
                {"name": "The Hindu Health", "url": "https://www.thehindu.com/sci-tech/health/feeder/default.rss", "priority": 2},
                {"name": "Indian Express Health", "url": "https://indianexpress.com/section/lifestyle/health/feed/", "priority": 2},
                {"name": "Times of India Health", "url": "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms", "priority": 2},
                {"name": "News18 Health", "url": "https://www.news18.com/rss/lifestyle.xml", "priority": 2},
            ]
        }
        
        # Google News health queries for trending topics
        self.google_news_queries = [
            "health+breakthrough", "medical+research", "nutrition+study",
            "disease+prevention", "mental+health", "fitness+wellness",
            "vaccine+news", "diabetes+treatment", "cancer+research",
            "heart+disease", "obesity+solutions", "healthy+eating"
        ]
        
        # Reddit health communities
        self.reddit_sources = [
            {"name": "r/Health", "url": "https://www.reddit.com/r/Health/hot/.rss", "priority": 1},
            {"name": "r/Nutrition", "url": "https://www.reddit.com/r/nutrition/hot/.rss", "priority": 1},
            {"name": "r/Medicine", "url": "https://www.reddit.com/r/medicine/hot/.rss", "priority": 1},
            {"name": "r/HealthNews", "url": "https://www.reddit.com/r/HealthNews/hot/.rss", "priority": 1},
        ]
        
        self.stats = {
            'total_articles': 0,
            'sources_processed': 0,
            'sources_successful': 0,
            'categories_covered': set(),
            'start_time': None,
            'end_time': None
        }
    
    def create_database(self):
        """Create enhanced database schema"""
        DB_PATH.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists and add missing columns
        cursor.execute("PRAGMA table_info(articles)")
        columns = {row[1] for row in cursor.fetchall()}
        
        # Add missing columns if they don't exist
        if 'content_quality_score' not in columns:
            cursor.execute("ALTER TABLE articles ADD COLUMN content_quality_score REAL DEFAULT 0.5")
        
        # Enhanced indexes (only create if they don't exist)
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_url_accessible ON articles(url_accessible)",
            "CREATE INDEX IF NOT EXISTS idx_date ON articles(date)",
            "CREATE INDEX IF NOT EXISTS idx_source ON articles(source)",
            "CREATE INDEX IF NOT EXISTS idx_categories ON articles(categories)",
            "CREATE INDEX IF NOT EXISTS idx_priority ON articles(priority)"
        ]
        
        # Only create quality score index if column exists
        if 'content_quality_score' in columns or True:  # We just added it
            indexes.append("CREATE INDEX IF NOT EXISTS idx_quality_score ON articles(content_quality_score)")
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                logger.warning(f"Index creation warning: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Enhanced database ready at: {DB_PATH}")
    
    def parse_rss_xml(self, xml_content: str, source_name: str) -> List[Dict]:
        """Enhanced RSS parsing with better error handling"""
        articles = []
        
        try:
            # Clean XML content
            xml_content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', xml_content)
            
            root = ET.fromstring(xml_content)
            
            # Handle different RSS formats
            items = root.findall('.//item') or root.findall('.//entry')
            
            for item in items:
                try:
                    article_data = self.extract_article_from_xml(item, source_name)
                    if article_data and self.is_recent_and_relevant(article_data):
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"Error parsing item from {source_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing RSS XML from {source_name}: {e}")
        
        return articles
    
    def extract_article_from_xml(self, item, source_name: str) -> Optional[Dict]:
        """Extract article data from XML item"""
        # Title
        title_elem = item.find('title')
        if title_elem is None or not title_elem.text:
            return None
        title = title_elem.text.strip()
        
        # URL
        link_elem = item.find('link')
        if link_elem is None:
            return None
        url = (link_elem.text or link_elem.get('href', '')).strip()
        
        if not url or len(url) < 10:
            return None
        
        # Description/Summary
        desc_elem = item.find('description') or item.find('summary') or item.find('content')
        description = ""
        if desc_elem is not None and desc_elem.text:
            description = re.sub(r'<[^>]+>', '', desc_elem.text)
            description = re.sub(r'\s+', ' ', description).strip()[:800]
        
        # Date
        date_elem = item.find('pubDate') or item.find('published') or item.find('updated')
        article_date = datetime.now()
        if date_elem is not None and date_elem.text:
            try:
                date_str = date_elem.text.strip()
                # Parse different date formats
                for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S', 
                           '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        # Remove timezone info for simple parsing
                        clean_date = re.sub(r'\s+[A-Z]{3,4}$', '', date_str.split(' +')[0])
                        article_date = datetime.strptime(clean_date, fmt)
                        break
                    except:
                        continue
            except:
                pass
        
        # Author
        author_elem = item.find('author') or item.find('creator') or item.find('dc:creator', {'dc': 'http://purl.org/dc/elements/1.1/'})
        author = author_elem.text if author_elem is not None and author_elem.text else source_name
        
        return {
            'title': title,
            'summary': description,
            'url': url,
            'date': article_date.isoformat(),
            'author': author,
            'source': source_name,
            'priority': 2
        }
    
    def is_recent_and_relevant(self, article: Dict) -> bool:
        """Check if article is recent and health-relevant"""
        # Check recency (last 7 days)
        try:
            article_date = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
            if article_date < datetime.now() - timedelta(days=7):
                return False
        except:
            pass
        
        # Check health relevance
        text = f"{article['title']} {article['summary']}".lower()
        
        health_keywords = [
            'health', 'medical', 'disease', 'illness', 'condition', 'treatment',
            'doctor', 'hospital', 'medicine', 'drug', 'therapy', 'cure',
            'nutrition', 'diet', 'fitness', 'wellness', 'prevention',
            'cancer', 'diabetes', 'heart', 'brain', 'mental', 'anxiety',
            'depression', 'vaccine', 'virus', 'infection', 'covid', 'flu',
            'research', 'study', 'clinical', 'patient', 'healthcare',
            'surgery', 'symptom', 'diagnosis', 'epidemic', 'pandemic'
        ]
        
        # Must contain health keywords and have decent content
        health_count = sum(1 for keyword in health_keywords if keyword in text)
        return health_count >= 2 and len(article['title']) > 15
    
    def advanced_categorize_article(self, article: Dict) -> Dict:
        """Advanced categorization with better accuracy"""
        text = f"{article['title']} {article['summary']}".lower()
        
        categories = []
        tags = []
        quality_score = 0.5
        
        # News and breaking news
        if any(word in text for word in ['breaking', 'urgent', 'latest', 'new study', 'research']):
            categories.append('news')
            tags.append('recent_developments')
            quality_score += 0.1
        
        # Diseases and conditions
        disease_keywords = ['cancer', 'diabetes', 'heart disease', 'stroke', 'alzheimer', 
                           'parkinson', 'arthritis', 'asthma', 'copd', 'kidney disease']
        if any(disease in text for disease in disease_keywords):
            categories.append('diseases')
            tags.append('medical_conditions')
            quality_score += 0.1
        
        # Mental health
        if any(word in text for word in ['mental health', 'depression', 'anxiety', 'stress', 'ptsd', 'therapy']):
            categories.append('audience')
            tags.append('mental_health')
            quality_score += 0.1
        
        # Nutrition and food
        nutrition_keywords = ['nutrition', 'diet', 'food', 'eating', 'vitamin', 'supplement', 
                             'protein', 'carb', 'fat', 'calorie', 'obesity', 'weight']
        if any(nutrition in text for nutrition in nutrition_keywords):
            categories.append('food')
            tags.append('nutrition_basics')
            quality_score += 0.1
        
        # Solutions and treatments
        if any(word in text for word in ['treatment', 'cure', 'therapy', 'drug', 'medication', 
                                       'surgery', 'procedure', 'clinical trial']):
            categories.append('solutions')
            tags.append('medical_treatments')
            quality_score += 0.1
        
        # International health
        if any(word in text for word in ['who', 'global', 'worldwide', 'international', 'pandemic']):
            categories.append('international_health')
            tags.append('international')
            quality_score += 0.1
        
        # Indian health context
        if any(word in text for word in ['india', 'indian', 'ayurveda', 'traditional medicine']):
            categories.append('indian_health')
            tags.append('indian_health_news')
            quality_score += 0.1
        
        # Fitness and lifestyle
        if any(word in text for word in ['fitness', 'exercise', 'workout', 'lifestyle', 'wellness']):
            categories.append('audience')
            tags.append('fitness')
            quality_score += 0.1
        
        # Prevention focus
        if any(word in text for word in ['prevention', 'prevent', 'avoid', 'reduce risk']):
            tags.append('prevention')
            quality_score += 0.1
        
        # Research and studies
        if any(word in text for word in ['study', 'research', 'clinical', 'trial', 'findings']):
            tags.append('breakthrough_research')
            quality_score += 0.1
        
        # Default categorization
        if not categories:
            categories = ['news']
            tags = ['general_health']
        
        # Add trending tag for high-quality recent content
        if quality_score > 0.7:
            tags.append('trending')
        
        return {
            'categories': categories,
            'tags': tags,
            'content_quality_score': min(quality_score, 1.0)
        }
    
    def fetch_rss_sources(self) -> List[Dict]:
        """Fetch articles from all RSS sources"""
        all_articles = []
        
        for category, sources in self.rss_sources.items():
            logger.info(f"\n📂 Processing {category.upper()} sources...")
            self.stats['categories_covered'].add(category)
            
            for source_config in sources:
                try:
                    logger.info(f"🔍 Fetching from {source_config['name']}...")
                    
                    response = self.session.get(source_config['url'], timeout=20)
                    response.raise_for_status()
                    
                    articles = self.parse_rss_xml(response.text, source_config['name'])
                    
                    # Add category and priority information
                    for article in articles:
                        article['source_category'] = category
                        article['priority'] = source_config['priority']
                    
                    all_articles.extend(articles)
                    self.stats['sources_successful'] += 1
                    
                    logger.info(f"✅ Found {len(articles)} articles from {source_config['name']}")
                    
                except Exception as e:
                    logger.error(f"❌ Error fetching from {source_config['name']}: {e}")
                
                finally:
                    self.stats['sources_processed'] += 1
                    time.sleep(1)  # Rate limiting
        
        return all_articles
    
    def fetch_google_news(self) -> List[Dict]:
        """Fetch trending health topics from Google News"""
        articles = []
        
        logger.info(f"\n🔍 Fetching Google News for health topics...")
        
        for query in self.google_news_queries[:6]:  # Limit queries
            try:
                encoded_query = quote_plus(query)
                url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                query_articles = self.parse_rss_xml(response.text, f"Google News ({query.replace('+', ' ').title()})")
                articles.extend(query_articles[:8])  # Limit per query
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error fetching Google News for {query}: {e}")
        
        logger.info(f"📰 Found {len(articles)} Google News articles")
        return articles
    
    def fetch_reddit_health(self) -> List[Dict]:
        """Fetch from Reddit health communities"""
        articles = []
        
        logger.info(f"\n🌐 Fetching from Reddit health communities...")
        
        for source in self.reddit_sources:
            try:
                response = self.session.get(source['url'], timeout=15)
                response.raise_for_status()
                
                reddit_articles = self.parse_rss_xml(response.text, source['name'])
                
                # Filter for health relevance
                relevant_articles = [a for a in reddit_articles if self.is_recent_and_relevant(a)]
                articles.extend(relevant_articles[:5])  # Limit per subreddit
                
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"Error fetching from {source['name']}: {e}")
        
        logger.info(f"🗣️ Found {len(articles)} Reddit articles")
        return articles
    
    def save_articles(self, articles: List[Dict]) -> int:
        """Save articles with enhanced validation"""
        if not articles:
            return 0
        
        # Validate URLs if validator is available
        if self.url_validator:
            logger.info("🔍 Validating URLs...")
            articles = self.url_validator.validate_articles_batch(articles)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        saved_count = 0
        duplicate_count = 0
        
        for article in articles:
            try:
                # Enhanced categorization
                categorization = self.advanced_categorize_article(article)
                article.update(categorization)
                
                # Convert lists to JSON
                categories_json = json.dumps(article.get('categories', ['news']))
                tags_json = json.dumps(article.get('tags', ['general']))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO articles 
                    (date, title, authors, summary, url, categories, tags, source, 
                     priority, url_accessible, content_quality_score, last_checked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article['date'],
                    article['title'],
                    article.get('author', ''),
                    article['summary'],
                    article['url'],
                    categories_json,
                    tags_json,
                    article.get('source', 'Unknown'),
                    article.get('priority', 1),
                    1,  # URL accessible
                    article.get('content_quality_score', 0.5),
                    datetime.now().isoformat()
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                    if saved_count % 10 == 0:
                        logger.info(f"✅ Saved {saved_count} articles...")
                else:
                    duplicate_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error saving article: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"📊 Articles: {saved_count} saved, {duplicate_count} duplicates")
        return saved_count
    
    def run_comprehensive_scraping(self) -> Dict:
        """Run comprehensive scraping from all sources"""
        self.stats['start_time'] = datetime.now()
        
        logger.info("🌍 Ultra-Comprehensive Health News Scraper")
        logger.info("=" * 60)
        logger.info(f"📅 Started at: {self.stats['start_time']}")
        
        all_articles = []
        
        # 1. RSS Sources
        rss_articles = self.fetch_rss_sources()
        all_articles.extend(rss_articles)
        
        # 2. Google News
        google_articles = self.fetch_google_news()
        all_articles.extend(google_articles)
        
        # 3. Reddit Health Communities
        reddit_articles = self.fetch_reddit_health()
        all_articles.extend(reddit_articles)
        
        # 4. Save all articles
        logger.info(f"\n💾 Saving {len(all_articles)} articles to database...")
        saved_count = self.save_articles(all_articles)
        
        self.stats['total_articles'] = saved_count
        self.stats['end_time'] = datetime.now()
        
        # Generate report
        self.generate_comprehensive_report()
        
        return self.stats
    
    def generate_comprehensive_report(self):
        """Generate comprehensive scraping report"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 ULTRA-COMPREHENSIVE SCRAPING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"📰 Total Articles Saved: {self.stats['total_articles']}")
        logger.info(f"🌐 Sources Processed: {self.stats['sources_processed']}")
        logger.info(f"✅ Sources Successful: {self.stats['sources_successful']}")
        logger.info(f"📂 Categories Covered: {len(self.stats['categories_covered'])}")
        
        logger.info(f"\n🎯 Categories with New Content:")
        for category in sorted(self.stats['categories_covered']):
            logger.info(f"   ✅ {category.replace('_', ' ').title()}")
        
        logger.info(f"\n💡 Data Coverage Enhanced:")
        logger.info(f"   🏥 Medical Research & Clinical Trials")
        logger.info(f"   📰 Breaking Health News from Major Outlets")
        logger.info(f"   🥗 Nutrition & Food Safety Updates")
        logger.info(f"   💊 Treatment & Prevention Solutions")
        logger.info(f"   🇮🇳 Indian Health News & Traditional Medicine")
        logger.info(f"   🌍 Global Health Organizations (WHO, NIH, CDC)")
        logger.info(f"   🗣️ Community Health Discussions (Reddit)")
        
        if self.stats['total_articles'] > 0:
            logger.info(f"\n🎉 SUCCESS: Comprehensive health database updated!")
            logger.info(f"   💾 Database: {DB_PATH}")
            logger.info(f"   🚀 All API endpoints now have richer content")
        else:
            logger.info(f"\n⚠️  No new articles were added")

def main():
    """Main execution function"""
    scraper = UltraComprehensiveHealthScraper()
    
    # Create database
    scraper.create_database()
    
    # Run comprehensive scraping
    stats = scraper.run_comprehensive_scraping()
    
    return stats

if __name__ == "__main__":
    main()
