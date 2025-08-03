#!/usr/bin/env python3
"""
Enhanced International Health News Scraper

This scraper expands the Metabolical Backend with global health news sources:
- International news outlets with health sections
- Indian health news sources and medical journals
- Asian and African health publications
- International health organizations and journals
- Uses RSS feeds, direct scraping, and news APIs for comprehensive coverage

No dummy articles - only authentic, dynamically sourced health content.
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
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse, quote_plus
import random
import hashlib

# Standard library XML parsers for feedparser-free operation
from xml.etree import ElementTree as ET
from html import unescape

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import URL validator
try:
    from app.url_validator import URLValidator
    url_validator_available = True
except ImportError:
    url_validator_available = False
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

class EnhancedInternationalScraper:
    """Scraper for international and Indian health news sources"""
    
    def __init__(self, api_keys=None):
        """Initialize the scraper with API keys"""
        self.url_validator = URLValidator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        self.api_keys = api_keys or {}
        
        # === INTERNATIONAL SOURCES ===
        
        # Top-tier international health sources
        self.international_sources = [
            {
                "name": "The Lancet",
                "rss_url": "https://www.thelancet.com/rssfeed/lancet_current.xml",
                "base_url": "https://www.thelancet.com",
                "priority": 4,
                "category": "news"
            },
            {
                "name": "BMJ News",
                "rss_url": "https://www.bmj.com/content/news.rss",
                "base_url": "https://www.bmj.com",
                "priority": 4,
                "category": "news"
            },
            {
                "name": "New England Journal of Medicine",
                "rss_url": "https://www.nejm.org/action/showFeed?jc=nejm&type=etoc&feed=rss",
                "base_url": "https://www.nejm.org",
                "priority": 4,
                "category": "news"
            },
            {
                "name": "STAT News",
                "rss_url": "https://www.statnews.com/feed/",
                "base_url": "https://www.statnews.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "Nature Medicine",
                "rss_url": "https://www.nature.com/nm.rss",
                "base_url": "https://www.nature.com",
                "priority": 4,
                "category": "news"
            },
            {
                "name": "Science Daily Health",
                "rss_url": "https://www.sciencedaily.com/rss/health_medicine.xml",
                "base_url": "https://www.sciencedaily.com",
                "priority": 3,
                "category": "news"
            }
        ]
        
        # === INDIAN SOURCES ===
        
        # Indian health news sources
        self.indian_sources = [
            {
                "name": "The Hindu - Health",
                "rss_url": "https://www.thehindu.com/sci-tech/health/feeder/default.rss",
                "base_url": "https://www.thehindu.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "Times of India - Health",
                "rss_url": "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",
                "base_url": "https://timesofindia.indiatimes.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "NDTV Health",
                "rss_url": "https://feeds.feedburner.com/ndtvnews-latest",  # Filter for health
                "base_url": "https://www.ndtv.com",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Indian Express - Health",
                "rss_url": "https://indianexpress.com/section/lifestyle/health/feed/",
                "base_url": "https://indianexpress.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "Economic Times - Healthcare",
                "rss_url": "https://economictimes.indiatimes.com/rss/industry/healthcare/biotech/healthcare.cms",
                "base_url": "https://economictimes.indiatimes.com",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "The Telegraph India - Health",
                "rss_url": "https://www.telegraphindia.com/health/rss",
                "base_url": "https://www.telegraphindia.com",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Deccan Herald - Health",
                "rss_url": "https://www.deccanherald.com/rss-feed/health.rss",
                "base_url": "https://www.deccanherald.com",
                "priority": 2,
                "category": "news"
            }
        ]
        
        # === ASIAN SOURCES ===
        
        # Asian health news sources beyond India
        self.asian_sources = [
            {
                "name": "South China Morning Post - Health",
                "rss_url": "https://www.scmp.com/rss/3/feed",
                "base_url": "https://www.scmp.com",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Japan Times - Health",
                "rss_url": "https://www.japantimes.co.jp/tag/health/feed/",
                "base_url": "https://www.japantimes.co.jp",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Straits Times - Health",
                "rss_url": "https://www.straitstimes.com/rssfeed/health",
                "base_url": "https://www.straitstimes.com",
                "priority": 2,
                "category": "news"
            },
            {
                "name": "Bangkok Post - Health",
                "rss_url": "https://www.bangkokpost.com/rss/data/health.xml",
                "base_url": "https://www.bangkokpost.com",
                "priority": 2,
                "category": "news"
            }
        ]
        
        # === INTERNATIONAL HEALTH ORGS ===
        
        # International health organizations
        self.health_organizations = [
            {
                "name": "WHO South-East Asia",
                "rss_url": "https://www.who.int/southeastasia/rss.xml",
                "base_url": "https://www.who.int",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "UN News - Health",
                "rss_url": "https://news.un.org/feed/subscribe/en/news/topic/health/feed/rss.xml",
                "base_url": "https://news.un.org",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "UNICEF Health",
                "rss_url": "https://www.unicef.org/health/rss.xml",
                "base_url": "https://www.unicef.org",
                "priority": 3,
                "category": "news"
            },
            {
                "name": "UNAIDS News",
                "rss_url": "https://www.unaids.org/en/rss/unaidsrss",
                "base_url": "https://www.unaids.org",
                "priority": 2,
                "category": "news"
            }
        ]
        
        # === DEMOGRAPHIC-SPECIFIC SOURCES ===
        
        # Men's health specific sources
        self.mens_health_sources = [
            {
                "name": "Men's Health Magazine",
                "rss_url": "https://www.menshealth.com/rss/all.xml/",
                "base_url": "https://www.menshealth.com",
                "priority": 3,
                "category": "audience",
                "subcategory": "men"
            },
            {
                "name": "Medical News Today - Men's Health",
                "rss_url": "https://www.medicalnewstoday.com/categories/men-s-health/feed",
                "base_url": "https://www.medicalnewstoday.com",
                "priority": 4,
                "category": "audience",
                "subcategory": "men"
            },
            {
                "name": "Healthline Men's Health",
                "rss_url": "https://www.healthline.com/health/mens-health/feed",
                "base_url": "https://www.healthline.com",
                "priority": 4,
                "category": "audience",
                "subcategory": "men"
            },
            {
                "name": "WebMD Men's Health",
                "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=Mens-Health",
                "base_url": "https://www.webmd.com",
                "priority": 3,
                "category": "audience",
                "subcategory": "men"
            },
            {
                "name": "Everyday Health Men",
                "rss_url": "https://www.everydayhealth.com/mens-health/all-articles/feed/rss",
                "base_url": "https://www.everydayhealth.com",
                "priority": 2,
                "category": "audience",
                "subcategory": "men"
            },
            {
                "name": "Harvard Health Men's Health Watch",
                "rss_url": "https://www.health.harvard.edu/topics/mens-health/feed",
                "base_url": "https://www.health.harvard.edu",
                "priority": 4,
                "category": "audience", 
                "subcategory": "men"
            }
        ]
        
        # === NEWS APIS WITH HEALTH FILTERS ===
        
        # News APIs with health filters
        self.news_apis = [
            {
                "name": "NewsAPI Health India",
                "api_url": "https://newsapi.org/v2/top-headlines",
                "params": {
                    "country": "in",
                    "category": "health",
                    "apiKey": self.api_keys.get("newsapi", "")
                },
                "priority": 3,
                "category": "news"
            },
            {
                "name": "NewsAPI Health Global",
                "api_url": "https://newsapi.org/v2/everything",
                "params": {
                    "q": "health OR medical OR healthcare",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": self.api_keys.get("newsapi", "")
                },
                "priority": 3,
                "category": "news"
            },
            {
                "name": "Gnews Health",
                "api_url": "https://gnews.io/api/v4/search",
                "params": {
                    "q": "health",
                    "lang": "en",
                    "token": self.api_keys.get("gnews", "")
                },
                "priority": 2,
                "category": "news"
            },
            {
                "name": "NewsData.io Health India",
                "api_url": "https://newsdata.io/api/1/news",
                "params": {
                    "country": "in",
                    "category": "health",
                    "apikey": self.api_keys.get("newsdata", "")
                },
                "priority": 2,
                "category": "news"
            },
            {
                "name": "NewsAPI Men's Health",
                "api_url": "https://newsapi.org/v2/everything",
                "params": {
                    "q": "\"men's health\" OR \"male health\" OR \"prostate\" OR \"testosterone\" OR \"erectile dysfunction\" OR \"male fertility\"",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": self.api_keys.get("newsapi", "")
                },
                "priority": 3,
                "category": "audience",
                "subcategory": "men"
            },
            {
                "name": "GNews Men's Health",
                "api_url": "https://gnews.io/api/v4/search",
                "params": {
                    "q": "\"men's health\" OR \"male health\" OR \"men health issues\"",
                    "lang": "en",
                    "token": self.api_keys.get("gnews", "")
                },
                "priority": 3,
                "category": "audience",
                "subcategory": "men"
            }
        ]
    
    def fetch_rss_feed(self, source: Dict) -> List[Dict]:
        """Fetch articles from an RSS feed without feedparser dependency"""
        articles = []
        
        try:
            logger.info(f"📰 Fetching from: {source['name']}")
            response = self.session.get(source["rss_url"], timeout=15)
            response.raise_for_status()
            
            # Parse XML content
            root = ET.fromstring(response.content)
            
            # Handle different RSS formats (RSS 2.0, Atom, etc.)
            if root.tag.endswith('rss'):
                # RSS 2.0 format
                for item in root.findall('.//item'):
                    try:
                        # Extract basic info
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        pub_date_elem = item.find('pubDate')
                        description_elem = item.find('description')
                        
                        if title_elem is None or link_elem is None:
                            continue
                            
                        title = unescape(title_elem.text.strip()) if title_elem.text else ""
                        link = link_elem.text.strip() if link_elem.text else ""
                        
                        # Fix relative URLs
                        if link and not link.startswith(('http://', 'https://')):
                            link = urljoin(source["base_url"], link)
                        
                        # Process date
                        pub_date = datetime.now()
                        if pub_date_elem is not None and pub_date_elem.text:
                            try:
                                # Try various date formats
                                date_formats = [
                                    '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
                                    '%a, %d %b %Y %H:%M:%S %Z',
                                    '%a, %d %b %Y %H:%M:%S',
                                    '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601
                                    '%Y-%m-%dT%H:%M:%S.%f%z',
                                    '%Y-%m-%d %H:%M:%S',
                                ]
                                
                                for fmt in date_formats:
                                    try:
                                        pub_date = datetime.strptime(pub_date_elem.text.strip(), fmt)
                                        break
                                    except ValueError:
                                        continue
                            except Exception:
                                # Keep default date on failure
                                pass
                        
                        # Process description/summary
                        summary = ""
                        if description_elem is not None and description_elem.text:
                            summary = description_elem.text
                            # Strip HTML
                            summary = re.sub(r'<[^>]+>', '', summary)
                            summary = re.sub(r'\s+', ' ', summary).strip()
                            summary = unescape(summary)
                            # Limit summary length
                            summary = summary[:500] + ('...' if len(summary) > 500 else '')
                        
                        # Extract author if available
                        author_elem = item.find('author') or item.find('dc:creator', {'dc': 'http://purl.org/dc/elements/1.1/'})
                        author = author_elem.text.strip() if author_elem is not None and author_elem.text else ""
                        
                        # Check if it's a health article
                        is_health_article = self.is_health_related(title, summary)
                        
                        if title and link and is_health_article:
                            article_data = {
                                'title': title,
                                'summary': summary,
                                'url': link,
                                'date': pub_date.isoformat(),
                                'author': author,
                                'source': source["name"],
                                'priority': source.get("priority", 1),
                                'category': source.get("category", "news")
                            }
                            
                            # Validate URL
                            if url_validator_available:
                                is_valid, _ = self.url_validator.validate_article_url(article_data)
                                if not is_valid:
                                    continue
                            
                            articles.append(article_data)
                    
                    except Exception as e:
                        logger.warning(f"Error processing RSS item: {e}")
                        continue
            
            elif root.tag.endswith('feed'):  # Atom format
                # Handle Atom format
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('.//atom:entry', namespace):
                    try:
                        # Extract basic info
                        title_elem = entry.find('atom:title', namespace)
                        link_elem = entry.find('atom:link[@rel="alternate"]', namespace) or entry.find('atom:link', namespace)
                        published_elem = entry.find('atom:published', namespace) or entry.find('atom:updated', namespace)
                        content_elem = entry.find('atom:content', namespace) or entry.find('atom:summary', namespace)
                        
                        if title_elem is None or link_elem is None:
                            continue
                            
                        title = unescape(title_elem.text.strip()) if title_elem.text else ""
                        link = link_elem.get('href', '').strip()
                        
                        # Fix relative URLs
                        if link and not link.startswith(('http://', 'https://')):
                            link = urljoin(source["base_url"], link)
                        
                        # Process date
                        pub_date = datetime.now()
                        if published_elem is not None and published_elem.text:
                            try:
                                # ISO 8601 format is common in Atom feeds
                                pub_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                            except:
                                # Keep default date on failure
                                pass
                        
                        # Process content/summary
                        summary = ""
                        if content_elem is not None:
                            if content_elem.text:
                                summary = content_elem.text
                            elif content_elem.get('type') == 'html' or content_elem.get('type') == 'xhtml':
                                summary = ET.tostring(content_elem, encoding='unicode')
                        
                        # Strip HTML
                        summary = re.sub(r'<[^>]+>', '', summary)
                        summary = re.sub(r'\s+', ' ', summary).strip()
                        summary = unescape(summary)
                        # Limit summary length
                        summary = summary[:500] + ('...' if len(summary) > 500 else '')
                        
                        # Extract author if available
                        author_elem = entry.find('atom:author/atom:name', namespace)
                        author = author_elem.text.strip() if author_elem is not None and author_elem.text else ""
                        
                        # Check if it's a health article
                        is_health_article = self.is_health_related(title, summary)
                        
                        if title and link and is_health_article:
                            article_data = {
                                'title': title,
                                'summary': summary,
                                'url': link,
                                'date': pub_date.isoformat(),
                                'author': author,
                                'source': source["name"],
                                'priority': source.get("priority", 1),
                                'category': source.get("category", "news")
                            }
                            
                            # Validate URL
                            if url_validator_available:
                                is_valid, _ = self.url_validator.validate_article_url(article_data)
                                if not is_valid:
                                    continue
                            
                            articles.append(article_data)
                    
                    except Exception as e:
                        logger.warning(f"Error processing Atom entry: {e}")
                        continue
            
            logger.info(f"✅ Retrieved {len(articles)} articles from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source['name']}: {e}")
        
        return articles
    
    def fetch_news_api(self, api_source: Dict) -> List[Dict]:
        """Fetch articles from a news API"""
        articles = []
        
        # Skip if no API key
        api_type = api_source["name"].split()[0].lower()  # Extract API name
        if api_type in self.api_keys and not self.api_keys[api_type]:
            logger.warning(f"⚠️ No API key for {api_type}, skipping {api_source['name']}")
            return articles
        
        try:
            logger.info(f"🔍 Querying: {api_source['name']}")
            
            response = self.session.get(
                api_source["api_url"], 
                params=api_source["params"],
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different API response formats
            if api_type == "newsapi":
                if data.get("status") == "ok" and "articles" in data:
                    raw_articles = data["articles"]
                    
                    for article in raw_articles:
                        try:
                            title = article.get("title", "").strip()
                            description = article.get("description", "")
                            url = article.get("url", "").strip()
                            published_at = article.get("publishedAt", "")
                            source_name = article.get("source", {}).get("name", "Unknown")
                            
                            # Skip non-health articles
                            if not self.is_health_related(title, description):
                                continue
                            
                            # Process date
                            pub_date = datetime.now()
                            if published_at:
                                try:
                                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            if title and url:
                                article_data = {
                                    'title': title,
                                    'summary': description or "",
                                    'url': url,
                                    'date': pub_date.isoformat(),
                                    'author': article.get("author", ""),
                                    'source': f"{source_name} via {api_source['name']}",
                                    'priority': api_source.get("priority", 1),
                                    'category': api_source.get("category", "news")
                                }
                                
                                # Validate URL
                                if url_validator_available:
                                    is_valid, _ = self.url_validator.validate_article_url(article_data)
                                    if not is_valid:
                                        continue
                                
                                articles.append(article_data)
                        
                        except Exception as e:
                            logger.warning(f"Error processing NewsAPI article: {e}")
                            continue
            
            elif api_type == "gnews":
                if "articles" in data:
                    raw_articles = data["articles"]
                    
                    for article in raw_articles:
                        try:
                            title = article.get("title", "").strip()
                            description = article.get("description", "")
                            url = article.get("url", "").strip()
                            published_at = article.get("publishedAt", "")
                            source_name = article.get("source", {}).get("name", "Unknown")
                            
                            # Skip non-health articles
                            if not self.is_health_related(title, description):
                                continue
                            
                            # Process date
                            pub_date = datetime.now()
                            if published_at:
                                try:
                                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            if title and url:
                                article_data = {
                                    'title': title,
                                    'summary': description or "",
                                    'url': url,
                                    'date': pub_date.isoformat(),
                                    'author': "",  # GNews doesn't provide author
                                    'source': f"{source_name} via {api_source['name']}",
                                    'priority': api_source.get("priority", 1),
                                    'category': api_source.get("category", "news")
                                }
                                
                                # Validate URL
                                if url_validator_available:
                                    is_valid, _ = self.url_validator.validate_article_url(article_data)
                                    if not is_valid:
                                        continue
                                
                                articles.append(article_data)
                        
                        except Exception as e:
                            logger.warning(f"Error processing GNews article: {e}")
                            continue
            
            elif api_type == "newsdata":
                if data.get("status") == "success" and "results" in data:
                    raw_articles = data["results"]
                    
                    for article in raw_articles:
                        try:
                            title = article.get("title", "").strip()
                            description = article.get("description", "")
                            url = article.get("link", "").strip()
                            published_at = article.get("pubDate", "")
                            source_name = article.get("source_id", "Unknown")
                            
                            # Skip non-health articles
                            if not self.is_health_related(title, description):
                                continue
                            
                            # Process date
                            pub_date = datetime.now()
                            if published_at:
                                try:
                                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                except:
                                    pass
                            
                            if title and url:
                                article_data = {
                                    'title': title,
                                    'summary': description or "",
                                    'url': url,
                                    'date': pub_date.isoformat(),
                                    'author': article.get("creator", ""),
                                    'source': f"{source_name} via {api_source['name']}",
                                    'priority': api_source.get("priority", 1),
                                    'category': api_source.get("category", "news")
                                }
                                
                                # Validate URL
                                if url_validator_available:
                                    is_valid, _ = self.url_validator.validate_article_url(article_data)
                                    if not is_valid:
                                        continue
                                
                                articles.append(article_data)
                        
                        except Exception as e:
                            logger.warning(f"Error processing NewsData article: {e}")
                            continue
            
            logger.info(f"✅ Retrieved {len(articles)} articles from {api_source['name']}")
            
        except Exception as e:
            logger.error(f"Error fetching from {api_source['name']}: {e}")
        
        return articles
    
    def is_health_related(self, title: str, description: str = "") -> bool:
        """Check if an article is health-related using simple keyword matching"""
        health_keywords = [
            "health", "medical", "medicine", "disease", "treatment", "therapy",
            "doctor", "hospital", "clinic", "patient", "care", "wellness",
            "diet", "nutrition", "fitness", "exercise", "mental health",
            "vaccine", "vaccination", "pandemic", "epidemic", "virus", "infection",
            "research", "study", "trial", "drug", "pharmaceutical", "biotechnology",
            "diabetes", "cancer", "heart disease", "obesity", "weight", "surgery",
            "prevention", "diagnosis", "symptom", "condition", "disorder",
            "healthcare", "public health", "WHO", "CDC", "NIH", "FDA"
        ]
        
        # Men's health specific keywords
        mens_health_keywords = [
            "men's health", "male health", "prostate", "testosterone", "erectile", 
            "male fertility", "men's fitness", "baldness", "hair loss", "beard",
            "male pattern", "low-t", "male hormones", "male cancer", "testicular",
            "male menopause", "andropause", "male depression", "men's mental health",
            "men's sexual health", "male sexual health", "sperm count", "sperm quality", 
            "male reproductive", "father's health"
        ]
        
        text = f"{title.lower()} {description.lower()}"
        
        # Check general health keywords
        for keyword in health_keywords:
            if keyword.lower() in text:
                return True
        
        # Check men's health specific keywords
        for keyword in mens_health_keywords:
            if keyword.lower() in text:
                return True
        
        return False
    
    def save_articles_to_db(self, articles: List[Dict]) -> int:
        """Save articles to SQLite database, returning count of new articles"""
        if not articles:
            return 0
        
        # Connect to database
        DB_PATH.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ensure table exists
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
        
        # Track how many new articles were added
        new_articles_count = 0
        
        # Process and insert articles
        for article in articles:
            try:
                # Generate category and tags from title/summary
                category = article.get('category', 'news')
                subcategory = article.get('subcategory', None)
                
                # Special handling for men's health articles
                combined_text = f"{article['title']} {article.get('summary', '')}".lower()
                if any(term in combined_text for term in ['men\'s health', 'male health', 'prostate', 'testosterone']):
                    if 'men' not in tags:
                        category = 'audience'
                        subcategory = 'men'
                
                # Basic tag extraction
                tags = self.extract_tags(article['title'], article.get('summary', ''))
                
                # Ensure men's health articles are properly categorized
                if subcategory == 'men' and 'men' not in tags:
                    tags.append('men')
                
                # Build categories JSON - include subcategory if available
                categories_json = [category]
                
                # Insert article
                try:
                    cursor.execute("""
                        INSERT INTO articles 
                        (date, title, authors, summary, url, categories, tags, source, priority, news_score, subcategory)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article.get('date', datetime.now().isoformat()),
                        article['title'],
                        article.get('author', ''),
                        article.get('summary', ''),
                        article['url'],
                        json.dumps(categories_json),
                        json.dumps(tags),
                        article.get('source', 'Unknown'),
                        article.get('priority', 1),
                        article.get('news_score', 0.5),
                        subcategory
                    ))
                    new_articles_count += 1
                except sqlite3.IntegrityError:
                    # URL already exists, skip
                    pass
            
            except Exception as e:
                logger.warning(f"Error saving article {article.get('title', 'Unknown')}: {e}")
                continue
        
        # Commit changes
        conn.commit()
        conn.close()
        
        return new_articles_count
    
    def extract_tags(self, title: str, summary: str) -> List[str]:
        """Extract tags from article title and summary"""
        combined_text = f"{title} {summary}".lower()
        
        # Health condition tags
        health_conditions = [
            "diabetes", "cancer", "heart disease", "obesity", "alzheimer's",
            "dementia", "arthritis", "asthma", "covid", "hypertension",
            "depression", "anxiety", "stroke", "allergy", "inflammation",
            "disease", "infection", "virus"
        ]
        
        # Treatment tags
        treatments = [
            "vaccine", "medication", "therapy", "surgery", "treatment",
            "prevention", "screening", "diet", "exercise", "supplement"
        ]
        
        # Demographic tags
        demographics = [
            "children", "adults", "seniors", "elderly", "women",
            "men", "pregnant", "maternal", "baby", "infant"
        ]
        
        # Men's health specific tags
        mens_health_tags = [
            "prostate", "testosterone", "erectile dysfunction", "male fertility",
            "baldness", "hair loss", "male pattern", "andropause", "testicular",
            "male cancer", "male reproductive", "father's health", "men's health",
            "male health", "men's fitness", "beard", "male hormones", "sperm",
            "men's mental health", "male depression", "men's sexual health"
        ]
        
        # Research tags
        research_terms = [
            "study", "research", "trial", "clinical", "breakthrough",
            "discovery", "findings", "publication", "journal", "scientists"
        ]
        
        # Extract tags based on presence in text
        tags = ["health"]  # Always include health tag
        
        # Add source as tag (simplified)
        if "source" in combined_text:
            source_name = combined_text.split("source")[0].strip().split()[-1]
            if source_name and len(source_name) > 2:
                tags.append(source_name)
        
        # Add other tags based on keyword presence
        for category, keywords in [
            ("condition", health_conditions),
            ("treatment", treatments),
            ("demographic", demographics),
            ("research", research_terms),
            ("mens_health", mens_health_tags)
        ]:
            for keyword in keywords:
                if keyword in combined_text:
                    tags.append(keyword)
                    
                    # Ensure proper categorization for men's health articles
                    if category == "mens_health" and "men" not in tags:
                        tags.append("men")
        
        # Ensure we don't have too many tags
        return list(set(tags))[:8]  # Limit to 8 unique tags
    
    def scrape_all_sources(self) -> int:
        """Scrape all configured sources and return count of new articles"""
        all_articles = []
        total_sources = (
            len(self.international_sources) +
            len(self.indian_sources) +
            len(self.asian_sources) +
            len(self.health_organizations) +
            len(self.mens_health_sources)
        )
        
        logger.info(f"🌐 Starting scrape of {total_sources} RSS sources and {len(self.news_apis)} news APIs")
        
        # Scrape all RSS sources
        for source_group in [
            self.international_sources,
            self.indian_sources,
            self.asian_sources,
            self.health_organizations,
            self.mens_health_sources
        ]:
            for source in source_group:
                try:
                    articles = self.fetch_rss_feed(source)
                    all_articles.extend(articles)
                    # Small delay between requests
                    time.sleep(random.uniform(0.5, 2.0))
                except Exception as e:
                    logger.error(f"Failed to scrape {source['name']}: {e}")
        
        # Scrape news APIs if keys are available
        for api in self.news_apis:
            api_type = api["name"].split()[0].lower()
            if api_type in self.api_keys and self.api_keys[api_type]:
                try:
                    articles = self.fetch_news_api(api)
                    all_articles.extend(articles)
                    # Larger delay for API requests
                    time.sleep(random.uniform(1.0, 3.0))
                except Exception as e:
                    logger.error(f"Failed to query {api['name']}: {e}")
        
        # Save all articles to database
        new_articles = self.save_articles_to_db(all_articles)
        
        logger.info(f"✅ Scrape complete: {len(all_articles)} articles found, {new_articles} new articles added")
        return new_articles

# Main execution
if __name__ == "__main__":
    logging.info("📰 Starting Enhanced International Health News Scraper")
    
    # Configure with your API keys here (or pass them in)
    api_keys = {
        "newsapi": "",      # Get from https://newsapi.org/
        "gnews": "",        # Get from https://gnews.io/
        "newsdata": ""      # Get from https://newsdata.io/
    }
    
    scraper = EnhancedInternationalScraper(api_keys)
    new_articles = scraper.scrape_all_sources()
    
    logging.info(f"✅ Scraper complete: Added {new_articles} new articles")
