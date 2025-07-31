#!/usr/bin/env python3
"""
Social Media & Alternative News Scraper

This scraper fetches health news from social media platforms and alternative sources:
- Reddit Health subreddits
- Twitter/X health trends (via unofficial APIs)
- Alternative news aggregators
- Health blogs and medium articles
- YouTube health channel updates (via RSS)

Extends the comprehensive news coverage while maintaining existing endpoints.
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

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import our URL validator (optional)
try:
    from app.url_validator import URLValidator
except ImportError:
    # Simple fallback validator
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

class SocialMediaNewsScraper:
    """Social media and alternative news sources for health content"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Reddit health subreddits (using RSS feeds)
        self.reddit_health_sources = [
            {
                "name": "Reddit r/Health",
                "rss_url": "https://www.reddit.com/r/Health/.rss",
                "subreddit": "Health",
                "priority": 1,
                "category": "news"
            },
            {
                "name": "Reddit r/HealthyFood",
                "rss_url": "https://www.reddit.com/r/HealthyFood/.rss",
                "subreddit": "HealthyFood",
                "priority": 1,
                "category": "food"
            },
            {
                "name": "Reddit r/nutrition",
                "rss_url": "https://www.reddit.com/r/nutrition/.rss",
                "subreddit": "nutrition",
                "priority": 2,
                "category": "food"
            },
            {
                "name": "Reddit r/MentalHealth",
                "rss_url": "https://www.reddit.com/r/MentalHealth/.rss",
                "subreddit": "MentalHealth",
                "priority": 2,
                "category": "audience"
            },
            {
                "name": "Reddit r/medicine",
                "rss_url": "https://www.reddit.com/r/medicine/.rss",
                "subreddit": "medicine",
                "priority": 3,
                "category": "diseases"
            },
            {
                "name": "Reddit r/science (Health)",
                "rss_url": "https://www.reddit.com/r/science/.rss",
                "subreddit": "science",
                "priority": 3,
                "category": "news"
            }
        ]
        
        # YouTube health channels (RSS feeds)
        self.youtube_health_channels = [
            {
                "name": "TED-Ed Health",
                "rss_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCsooa4yRKGN_zEE8iknghZA",
                "channel": "TED-Ed",
                "priority": 2,
                "category": "solutions"
            },
            {
                "name": "Mayo Clinic YouTube",
                "rss_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCKBTZlHOQG6WEfpWwyfrpMw",
                "channel": "Mayo Clinic",
                "priority": 3,
                "category": "solutions"
            },
            {
                "name": "Cleveland Clinic YouTube",
                "rss_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCM_i1DKPGFOwWW5wKHa2JiQ",
                "channel": "Cleveland Clinic",
                "priority": 3,
                "category": "solutions"
            }
        ]
        
        # Alternative news aggregators
        self.alternative_aggregators = [
            {
                "name": "AllSides Health",
                "rss_url": "https://www.allsides.com/tags/health/feed",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Ground News Health",
                "api_url": "https://www.ground.news/search",
                "search_term": "health",
                "priority": 2,
                "category": "news"
            }
        ]
        
        # Health blogs and medium publications
        self.health_blogs = [
            {
                "name": "Medium Health Stories",
                "rss_url": "https://medium.com/feed/tag/health",
                "priority": 1,
                "category": "blogs_and_opinions"
            },
            {
                "name": "Healthline Blog",
                "rss_url": "https://www.healthline.com/rss",
                "priority": 2,
                "category": "solutions"
            },
            {
                "name": "Psychology Today",
                "rss_url": "https://www.psychologytoday.com/us/rss/blog/all",
                "priority": 2,
                "category": "audience"
            }
        ]
    
    def fetch_reddit_health_news(self) -> List[Dict]:
        """Fetch health discussions from Reddit subreddits"""
        articles = []
        
        for source_config in self.reddit_health_sources:
            try:
                logger.info(f"🔍 Fetching from {source_config['name']}...")
                
                response = self.session.get(source_config['rss_url'], timeout=15)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                entries = feed.entries[:10]  # Limit per subreddit
                
                for entry in entries:
                    try:
                        title = entry.get('title', '').strip()
                        summary = entry.get('summary', '') or entry.get('content', [{}])[0].get('value', '')
                        link = entry.get('link', '').strip()
                        
                        # Clean summary from HTML
                        if summary:
                            summary = re.sub(r'<[^>]+>', '', summary)
                            summary = re.sub(r'&[^;]+;', '', summary)  # Remove HTML entities
                            summary = re.sub(r'\s+', ' ', summary).strip()[:500]
                        
                        # Parse date
                        article_date = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                article_date = datetime(*entry.published_parsed[:6])
                            except:
                                pass
                        
                        # Only recent posts (last 2 days)
                        if article_date < datetime.now() - timedelta(days=2):
                            continue
                        
                        # Validate health-related content
                        if not self.is_health_related_social(title, summary):
                            continue
                        
                        # Extract author from Reddit format
                        author = entry.get('author', 'Reddit User')
                        
                        if title and link and len(title) > 10:
                            article_data = {
                                'title': f"[Reddit Discussion] {title}",
                                'summary': summary,
                                'url': link,
                                'date': article_date.isoformat(),
                                'author': author,
                                'source': source_config['name'],
                                'priority': source_config['priority'],
                                'social_score': self.calculate_social_engagement_score(title, summary),
                                'trending_score': 0.6  # Reddit content tends to be trending
                            }
                            articles.append(article_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing Reddit entry: {e}")
                        continue
                
                time.sleep(2)  # Rate limiting for Reddit
                
            except Exception as e:
                logger.warning(f"Error fetching from {source_config['name']}: {e}")
                continue
        
        logger.info(f"📱 Found {len(articles)} Reddit health discussions")
        return articles
    
    def fetch_youtube_health_videos(self) -> List[Dict]:
        """Fetch health education videos from YouTube channels"""
        articles = []
        
        for source_config in self.youtube_health_channels:
            try:
                logger.info(f"🎥 Fetching from {source_config['name']}...")
                
                response = self.session.get(source_config['rss_url'], timeout=15)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                entries = feed.entries[:8]  # Limit per channel
                
                for entry in entries:
                    try:
                        title = entry.get('title', '').strip()
                        summary = entry.get('summary', '') or entry.get('media_description', '')
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
                        
                        # Only recent videos (last 7 days)
                        if article_date < datetime.now() - timedelta(days=7):
                            continue
                        
                        # Validate health-related content
                        if not self.is_health_related_social(title, summary):
                            continue
                        
                        if title and link and len(title) > 10:
                            article_data = {
                                'title': f"[Video] {title}",
                                'summary': summary,
                                'url': link,
                                'date': article_date.isoformat(),
                                'author': source_config['channel'],
                                'source': source_config['name'],
                                'priority': source_config['priority'],
                                'educational_score': 0.8,  # YouTube health videos are educational
                                'trending_score': 0.5
                            }
                            articles.append(article_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing YouTube entry: {e}")
                        continue
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error fetching from {source_config['name']}: {e}")
                continue
        
        logger.info(f"🎥 Found {len(articles)} YouTube health videos")
        return articles
    
    def fetch_health_blogs(self) -> List[Dict]:
        """Fetch from health blogs and Medium publications"""
        articles = []
        
        for source_config in self.health_blogs:
            try:
                logger.info(f"📝 Fetching from {source_config['name']}...")
                
                response = self.session.get(source_config['rss_url'], timeout=15)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                entries = feed.entries[:12]  # Limit per blog
                
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
                        
                        # Only recent articles (last 5 days)
                        if article_date < datetime.now() - timedelta(days=5):
                            continue
                        
                        # Validate health-related content
                        if not self.is_health_related_social(title, summary):
                            continue
                        
                        author = entry.get('author', 'Blog Author')
                        
                        if title and link and len(title) > 10:
                            article_data = {
                                'title': title,
                                'summary': summary,
                                'url': link,
                                'date': article_date.isoformat(),
                                'author': author,
                                'source': source_config['name'],
                                'priority': source_config['priority'],
                                'blog_score': 0.7,  # Blog content quality
                                'trending_score': 0.4
                            }
                            articles.append(article_data)
                            
                    except Exception as e:
                        logger.warning(f"Error parsing blog entry: {e}")
                        continue
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Error fetching from {source_config['name']}: {e}")
                continue
        
        logger.info(f"📝 Found {len(articles)} health blog articles")
        return articles
    
    def is_health_related_social(self, title: str, summary: str) -> bool:
        """Health content detection optimized for social media"""
        text = f"{title} {summary}".lower()
        
        # Social media health keywords (more casual language)
        health_keywords = [
            # Direct health terms
            'health', 'healthy', 'medical', 'doctor', 'medicine',
            'wellness', 'fitness', 'nutrition', 'diet', 'workout',
            
            # Conditions (casual terms)
            'sick', 'illness', 'disease', 'pain', 'hurt', 'ache',
            'tired', 'fatigue', 'stress', 'anxiety', 'depression',
            'weight loss', 'weight gain', 'diabetes', 'cancer',
            
            # Body parts and symptoms
            'heart', 'brain', 'stomach', 'headache', 'fever',
            'cough', 'cold', 'flu', 'covid', 'virus',
            
            # Treatments and solutions
            'treatment', 'therapy', 'cure', 'remedy', 'heal',
            'recover', 'prevention', 'vaccine', 'exercise',
            
            # Mental health (social media focus)
            'mental health', 'self care', 'mindfulness', 'meditation',
            'therapy', 'counseling', 'support group'
        ]
        
        # Must contain at least 1 health keyword
        health_count = sum(1 for keyword in health_keywords if keyword in text)
        
        # Exclude non-health content
        exclude_keywords = [
            'politics', 'election', 'vote', 'government', 'law',
            'sports', 'game', 'team', 'player', 'win', 'lose',
            'entertainment', 'movie', 'music', 'celebrity'
        ]
        
        exclude_count = sum(1 for keyword in exclude_keywords if keyword in text)
        
        return health_count >= 1 and exclude_count == 0
    
    def calculate_social_engagement_score(self, title: str, summary: str) -> float:
        """Calculate social media engagement potential (0.0 to 1.0)"""
        score = 0.0
        text = f"{title} {summary}".lower()
        
        # Emotional engagement indicators
        emotional_words = [
            'amazing', 'incredible', 'shocking', 'surprising', 'unbelievable',
            'life-changing', 'must-see', 'important', 'urgent', 'warning'
        ]
        if any(word in text for word in emotional_words):
            score += 0.3
        
        # Personal story indicators
        personal_words = ['my', 'i', 'me', 'personal', 'story', 'experience', 'journey']
        if any(word in text for word in personal_words):
            score += 0.2
        
        # Question format (high engagement)
        if '?' in title:
            score += 0.2
        
        # List format indicators
        list_words = ['tips', 'ways', 'steps', 'things', 'reasons', 'benefits']
        if any(word in text for word in list_words):
            score += 0.1
        
        # Numbers in title (clickbait but effective)
        if re.search(r'\d+', title):
            score += 0.1
        
        return min(score, 1.0)
    
    def categorize_social_article(self, article: Dict) -> Dict:
        """Categorize social media content"""
        text = f"{article['title']} {article['summary']}".lower()
        
        categories = []
        tags = []
        
        # Personal stories and experiences
        personal_words = ['my', 'personal', 'story', 'experience', 'journey', 'struggled']
        if any(word in text for word in personal_words):
            categories.append('blogs_and_opinions')
            tags.append('patient_stories')
        
        # Mental health discussions
        mental_words = ['mental health', 'depression', 'anxiety', 'stress', 'therapy']
        if any(word in text for word in mental_words):
            categories.append('audience')
            tags.append('mental_health')
        
        # Nutrition and diet discussions
        nutrition_words = ['nutrition', 'diet', 'food', 'eating', 'weight', 'recipe']
        if any(word in text for word in nutrition_words):
            categories.append('food')
            tags.append('nutrition_basics')
        
        # Exercise and fitness
        fitness_words = ['exercise', 'workout', 'fitness', 'gym', 'running', 'yoga']
        if any(word in text for word in fitness_words):
            categories.append('solutions')
            tags.append('preventive_care')
        
        # Medical discussions
        medical_words = ['doctor', 'hospital', 'treatment', 'medication', 'diagnosis']
        if any(word in text for word in medical_words):
            categories.append('diseases')
            tags.append('medical_conditions')
        
        # Reddit discussions get special treatment
        if '[Reddit Discussion]' in article['title']:
            tags.append('community_discussion')
        
        # YouTube videos get educational tag
        if '[Video]' in article['title']:
            tags.append('educational_content')
        
        # Default categorization
        if not categories:
            categories = ['blogs_and_opinions']
            tags = ['general_discussion']
        
        return {
            'categories': categories,
            'tags': tags
        }
    
    def save_social_articles(self, articles: List[Dict], source_name: str) -> int:
        """Save social media articles to database"""
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
                categorization = self.categorize_social_article(article)
                article.update(categorization)
                
                # Convert lists to JSON
                categories_json = json.dumps(article.get('categories', ['blogs_and_opinions']))
                tags_json = json.dumps(article.get('tags', ['general']))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO articles 
                    (date, title, authors, summary, url, categories, tags, source, priority, 
                     url_accessible, last_checked, news_score, trending_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    1,  # Assume social media URLs are accessible
                    datetime.now().isoformat(),
                    article.get('social_score', 0.5),
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
        
        logger.info(f"📊 {source_name}: {saved_count} saved, {duplicate_count} duplicates")
        return saved_count
    
    def fetch_all_social_sources(self) -> int:
        """Fetch from all social media and alternative sources"""
        total_saved = 0
        start_time = datetime.now()
        
        logger.info("📱 Social Media & Alternative News Scraper")
        logger.info("=" * 50)
        
        # 1. Fetch from Reddit health communities
        logger.info("\n📱 Fetching from Reddit health communities...")
        reddit_articles = self.fetch_reddit_health_news()
        total_saved += self.save_social_articles(reddit_articles, "Reddit Health Communities")
        
        # 2. Fetch from YouTube health channels
        logger.info("\n🎥 Fetching from YouTube health channels...")
        youtube_articles = self.fetch_youtube_health_videos()
        total_saved += self.save_social_articles(youtube_articles, "YouTube Health Channels")
        
        # 3. Fetch from health blogs
        logger.info("\n📝 Fetching from health blogs...")
        blog_articles = self.fetch_health_blogs()
        total_saved += self.save_social_articles(blog_articles, "Health Blogs")
        
        duration = datetime.now() - start_time
        
        logger.info(f"\n📊 Social Media Scraping Summary:")
        logger.info(f"   • Total articles saved: {total_saved}")
        logger.info(f"   • Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"   • Database: {DB_PATH}")
        
        return total_saved

def main():
    """Main function for social media news scraping"""
    print("📱 Social Media & Alternative News Scraper")
    print("=" * 50)
    
    scraper = SocialMediaNewsScraper()
    
    # Fetch from all social sources
    total_saved = scraper.fetch_all_social_sources()
    
    if total_saved > 0:
        print(f"\n🎉 Successfully scraped {total_saved} articles from social media sources!")
        print("✅ Social media aggregation complete!")
        print("\n💡 The existing endpoints now include social media content!")
    else:
        print("\n⚠️ No articles were saved from social media sources.")
    
    return total_saved

if __name__ == "__main__":
    main()
