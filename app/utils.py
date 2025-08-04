"""
Metabolical Backend Utilities - Simplified and Clean
Database operations and utility functions for the health articles API.
"""

import sqlite3
import json
import threading
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
from contextlib import contextmanager
import logging
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path - adjusted for new structure
DB_PATH = str(Path(__file__).parent.parent / "data" / "articles.db")

# Fallback to old path if new doesn't exist
if not Path(DB_PATH).exists():
    DB_PATH = str(Path(__file__).parent.parent / "db" / "articles.db")

# Category keywords file path - updated to use new unified config
CATEGORY_YAML_PATH = Path(__file__).parent / "health_categories.yml"

# Simple connection pool
class SQLiteConnectionPool:
    def __init__(self, database: str):
        self.database = database
        self._lock = threading.Lock()
        
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.database, timeout=30.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        try:
            yield conn
        finally:
            conn.close()

# Global connection pool
connection_pool = SQLiteConnectionPool(DB_PATH)

def is_valid_article_url(url: str) -> bool:
    """
    Check if an article URL is valid and accessible
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url or url == '' or url == 'NULL':
        return False
    
    # Check for problematic URL patterns
    invalid_url_patterns = [
        'example.com', 'example.org', 'example.net',
        'domain.com', 'test.com', 'localhost',
        'javascript:', 'mailto:', 'file:', 'ftp:',
        '404', 'not-found', 'error',
        'google.com/rss/articles/',
        'dummy.com', 'sample.com'
    ]
    
    url_lower = url.lower()
    for pattern in invalid_url_patterns:
        if pattern in url_lower:
            return False
    
    # Check if URL has proper format
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Must be HTTP or HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
            
    except Exception:
        return False
    
    return True

# Cache for category keywords
_category_cache = {}
_stats_cache = {}
_cache_timestamp = None

def get_cached_category_keywords() -> Dict:
    """Load and cache category keywords from YAML file"""
    global _category_cache
    
    if _category_cache:
        return _category_cache
        
    try:
        if CATEGORY_YAML_PATH.exists():
            with open(CATEGORY_YAML_PATH, 'r', encoding='utf-8') as file:
                _category_cache = yaml.safe_load(file) or {}
                logger.info(f"Loaded {len(_category_cache)} categories from {CATEGORY_YAML_PATH}")
        else:
            logger.warning(f"Category file not found: {CATEGORY_YAML_PATH}")
            _category_cache = {
                "diseases": {"diabetes": [], "obesity": [], "cardiovascular": []},
                "news": {"recent_developments": [], "policy_and_regulation": []},
                "solutions": {"medical_treatments": [], "preventive_care": []},
                "food": {"nutrition_basics": [], "superfoods": []},
                "audience": {"women": [], "men": [], "children": []},
                "blogs_and_opinions": {"expert_opinions": [], "patient_stories": []}
            }
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        _category_cache = {}
        
    return _category_cache

def get_total_articles_count() -> int:
    """Get total number of articles in database"""
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error getting article count: {e}")
        return 0

def get_articles_paginated_optimized(
    page: int = 1,
    limit: int = 20,
    sort_by: str = "desc",
    search_query: Optional[str] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    tag: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """
    Optimized paginated article retrieval with search and filtering
    """
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if search_query:
                # Search in title, summary, AND tags for better results
                where_conditions.append("(title LIKE ? OR summary LIKE ? OR tags LIKE ?)")
                search_term = f"%{search_query}%"
                params.extend([search_term, search_term, search_term])
                
            if category:
                # Since categories is stored as JSON array, we need to search within it
                where_conditions.append("categories LIKE ?")
                params.append(f'%"{category}"%')
                logger.info(f"🔍 Filtering by category: '{category}'")
                
            if tag:
                # Since tags is stored as JSON array, we need to search within it
                # Handle both frontend format (with spaces) and database format (with underscores)
                tag_underscore = tag.replace(" ", "_")
                
                # Special handling for "latest" - also search for related terms
                if tag.lower() == "latest":
                    where_conditions.append("(tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ?)")
                    params.extend([f'%"{tag}"%', f'%"{tag_underscore}"%', f'%"breaking_news"%', f'%"recent_developments"%', f'%"indian_health_news"%', f'%"trending"%', f'%"smartnews_aggregated"%'])
                    logger.info(f"🏷️ Filtering by tag: '{tag}' (also checking related terms: breaking_news, recent_developments, trending, smartnews_aggregated)")
                # Special handling for "lifestyle" - also search for related terms
                elif tag.lower() == "lifestyle":
                    where_conditions.append("(tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ?)")
                    params.extend([f'%"{tag}"%', f'%"{tag_underscore}"%', f'%"lifestyle_changes"%', f'%"health_lifestyle"%', f'%"wellness"%'])
                    logger.info(f"🏷️ Filtering by tag: '{tag}' (also checking related terms: lifestyle_changes, health_lifestyle, wellness)")
                else:
                    where_conditions.append("(tags LIKE ? OR tags LIKE ?)")
                    params.extend([f'%"{tag}"%', f'%"{tag_underscore}"%'])
                    logger.info(f"🏷️ Filtering by tag: '{tag}' (also checking '{tag_underscore}')")
                
            if subcategory:
                # Treat subcategory as a tag since there's no separate subcategory column
                # Handle both frontend format (with spaces) and database format (with underscores)
                subcategory_underscore = subcategory.replace(" ", "_")
                where_conditions.append("(tags LIKE ? OR tags LIKE ?)")
                params.extend([f'%"{subcategory}"%', f'%"{subcategory_underscore}"%'])
                logger.info(f"🏷️ Filtering by subcategory as tag: '{subcategory}' (also checking '{subcategory_underscore}')")
                
            if start_date:
                where_conditions.append("date >= ?")
                params.append(start_date)
                
            if end_date:
                where_conditions.append("date <= ?")
                params.append(end_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Order clause - ensure deterministic ordering
            if sort_by.upper() == "DESC":
                order_clause = f"ORDER BY date DESC, id DESC"
            else:
                order_clause = f"ORDER BY date ASC, id ASC"
            
            # Count total articles
            count_query = f"SELECT COUNT(*) FROM articles {where_clause}"
            logger.info(f"🔍 Count query: {count_query} with params: {params}")
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            logger.info(f"📊 Found {total} articles matching criteria")
            
            # Calculate pagination
            offset = (page - 1) * limit
            total_pages = (total + limit - 1) // limit
            
            logger.info(f"📄 Pagination: page={page}, limit={limit}, offset={offset}, total={total}, total_pages={total_pages}")
            
            # Get articles
            query = f"""
                SELECT id, title, summary, NULL as content, url, source, date, categories as category, 
                       NULL as subcategory, tags, NULL as image_url, authors as author 
                FROM articles 
                {where_clause} 
                {order_clause} 
                LIMIT ? OFFSET ?
            """
            
            cursor.execute(query, params + [limit, offset])
            rows = cursor.fetchall()
            
            # Log the IDs returned for debugging
            returned_ids = [dict(row)['id'] for row in rows]
            logger.info(f"📋 Returned article IDs: {returned_ids}")
            
            # Convert to dictionaries
            articles = []
            for row in rows:
                article = dict(row)
                
                # Clean data - handle None/NULL values for required and optional fields
                # Ensure required fields have proper defaults if None
                if article.get('source') is None or article.get('source') == '':
                    # Set a default source based on category if possible
                    if article.get('category'):
                        if isinstance(article['category'], str) and article['category'].lower() in ["news", "diseases", "solutions", "food"]:
                            article['source'] = f"{article['category'].capitalize()} Information"
                        else:
                            article['source'] = "Health Information Source"
                    else:
                        article['source'] = "Health Information Source"
                
                # Enhanced URL validation - exclude articles with broken URLs
                url = article.get('url', '')
                if not is_valid_article_url(url):
                    logger.warning(f"Skipping article with invalid URL: {url} - Title: {article.get('title', 'Unknown')[:50]}")
                    continue
                
                if article.get('title') is None or article.get('title') == '':
                    article['title'] = 'Untitled'  # Required field
                
                # Clean optional fields - convert empty strings to None
                for optional_field in ['content', 'category', 'subcategory', 'image_url', 'author']:
                    if article.get(optional_field) == '' or article.get(optional_field) == 'NULL':
                        article[optional_field] = None
                
                # Special handling for summary - ensure it's never empty
                if not article.get('summary') or article.get('summary') in ['', 'NULL', None]:
                    # Generate a fallback summary from the title
                    title = article.get('title', 'Health Article')
                    if len(title) > 100:
                        article['summary'] = title[:97] + "..."
                    else:
                        article['summary'] = f"{title} - Health article summary."
                    logger.info(f"Generated fallback summary for article {article.get('id')}: {article['summary'][:50]}...")
                else:
                    # Clean summary text by removing source references
                    summary = article['summary']
                    if summary:
                        # Remove source references like "Source: XYZ" or "(Source: XYZ)" from the summary
                        import re
                        summary = re.sub(r'\(Source:.*?\)', '', summary)
                        summary = re.sub(r'Source:.*?(\.|$)', '', summary)
                        summary = re.sub(r'\(From:.*?\)', '', summary)
                        summary = re.sub(r'From:.*?(\.|$)', '', summary)
                        summary = summary.strip()
                        article['summary'] = summary
                
                # Ensure tags is always a list
                if not article.get('tags') or article.get('tags') in ['', 'NULL', None]:
                    article['tags'] = []
                
                # Parse categories if they're stored as JSON string
                if article.get('category'):
                    try:
                        if isinstance(article['category'], str):
                            categories_list = json.loads(article['category'])
                            # For backward compatibility, use the first category as 'category'
                            if categories_list and len(categories_list) > 0:
                                article['category'] = categories_list[0]
                            else:
                                article['category'] = None
                    except (json.JSONDecodeError, TypeError):
                        # If it's not JSON, keep as is
                        pass
                
                # Parse tags if they're stored as JSON string
                if article.get('tags'):
                    try:
                        if isinstance(article['tags'], str):
                            article['tags'] = json.loads(article['tags'])
                            # Convert underscores back to spaces for frontend compatibility
                            article['tags'] = [tag.replace("_", " ") if isinstance(tag, str) else tag for tag in article['tags']]
                    except (json.JSONDecodeError, TypeError):
                        article['tags'] = []
                else:
                    article['tags'] = []
                    
                # Parse date
                if article.get('date'):
                    try:
                        article['date'] = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        article['date'] = datetime.now()
                        
                articles.append(article)
            
            return {
                "articles": articles,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
            
    except Exception as e:
        logger.error(f"Error in get_articles_paginated_optimized: {e}")
        return {
            "articles": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "total_pages": 0,
            "has_next": False,
            "has_previous": False
        }

def get_category_stats_cached() -> Dict[str, int]:
    """Get cached category statistics"""
    global _stats_cache, _cache_timestamp
    
    # Cache for 5 minutes
    if _cache_timestamp and (datetime.now() - _cache_timestamp).seconds < 300:
        return _stats_cache.get('categories', {})
    
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT categories, COUNT(*) as count 
                FROM articles 
                WHERE categories IS NOT NULL AND categories != '' 
                GROUP BY categories
            """)
            
            category_stats = {}
            for row in cursor.fetchall():
                categories_json = row['categories']
                if categories_json:
                    try:
                        # Parse the JSON array of categories
                        if isinstance(categories_json, str):
                            categories_list = json.loads(categories_json)
                        else:
                            categories_list = categories_json
                        
                        # Count each category
                        for category in categories_list:
                            if category in category_stats:
                                category_stats[category] += row['count']
                            else:
                                category_stats[category] = row['count']
                    except (json.JSONDecodeError, TypeError):
                        # If it's not JSON, treat as single category
                        category_stats[categories_json] = row['count']
                
            _stats_cache['categories'] = category_stats
            _cache_timestamp = datetime.now()
            
            return category_stats
            
    except Exception as e:
        logger.error(f"Error getting category stats: {e}")
        return {}

def get_cached_stats() -> Dict:
    """Get cached general statistics"""
    global _stats_cache, _cache_timestamp
    
    # Cache for 5 minutes
    if _cache_timestamp and (datetime.now() - _cache_timestamp).seconds < 300:
        return _stats_cache.get('general', {})
    
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]
            
            # Recent articles (last 7 days)
            cursor.execute("SELECT COUNT(*) FROM articles WHERE date > date('now', '-7 days')")
            recent_articles = cursor.fetchone()[0]
            
            # Total sources
            cursor.execute("SELECT COUNT(DISTINCT source) FROM articles")
            total_sources = cursor.fetchone()[0]
            
            # Category stats
            category_stats = get_category_stats_cached()
            
            stats = {
                "total_articles": total_articles,
                "recent_articles_7_days": recent_articles,
                "total_sources": total_sources,
                "total_categories": len(category_stats),
                "category_distribution": dict(list(category_stats.items())[:10]),
                "last_updated": datetime.now().isoformat()
            }
            
            _stats_cache['general'] = stats
            _cache_timestamp = datetime.now()
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "total_articles": 0,
            "recent_articles_7_days": 0,
            "total_sources": 0,
            "total_categories": 0,
            "category_distribution": {},
            "last_updated": datetime.now().isoformat()
        }

def get_articles_by_ids(article_ids: List[int]) -> List[Dict]:
    """Get multiple articles by their IDs"""
    if not article_ids:
        return []
        
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create placeholders for IN clause
            placeholders = ','.join(['?'] * len(article_ids))
            query = f"""
                SELECT id, title, summary, NULL as content, url, source, date, categories as category, 
                       NULL as subcategory, tags, NULL as image_url, authors as author 
                FROM articles 
                WHERE id IN ({placeholders})
                ORDER BY date DESC
            """
            
            cursor.execute(query, article_ids)
            rows = cursor.fetchall()
            
            articles = []
            for row in rows:
                article = dict(row)
                
                # Parse categories if they're stored as JSON string
                if article.get('category'):
                    try:
                        if isinstance(article['category'], str):
                            categories_list = json.loads(article['category'])
                            # For backward compatibility, use the first category as 'category'
                            if categories_list and len(categories_list) > 0:
                                article['category'] = categories_list[0]
                            else:
                                article['category'] = None
                    except (json.JSONDecodeError, TypeError):
                        # If it's not JSON, keep as is
                        pass
                
                # Parse tags if they're stored as JSON string
                if article.get('tags'):
                    try:
                        if isinstance(article['tags'], str):
                            article['tags'] = json.loads(article['tags'])
                    except (json.JSONDecodeError, TypeError):
                        article['tags'] = []
                else:
                    article['tags'] = []
                    
                # Parse date
                if article.get('date'):
                    try:
                        article['date'] = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        article['date'] = datetime.now()
                        
                articles.append(article)
            
            return articles
            
    except Exception as e:
        logger.error(f"Error getting articles by IDs: {e}")
        return []

def initialize_optimizations():
    """Initialize database optimizations"""
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create indexes if they don't exist
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date)",
                "CREATE INDEX IF NOT EXISTS idx_articles_categories ON articles(categories)",
                "CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)",
                "CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title)",
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
                
            conn.commit()
            logger.info("Database indexes initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing optimizations: {e}")

def get_all_tags() -> List[str]:
    """Get all unique tags from the database"""
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all non-null tags
            cursor.execute("SELECT DISTINCT tags FROM articles WHERE tags IS NOT NULL AND tags != '' AND tags != '[]'")
            rows = cursor.fetchall()
            
            # Parse JSON tags and collect unique ones
            all_tags = set()
            for row in rows:
                try:
                    if row[0]:
                        tags = json.loads(row[0])
                        if isinstance(tags, list):
                            # Convert underscores back to spaces for frontend compatibility
                            formatted_tags = [tag.replace("_", " ") if isinstance(tag, str) else tag for tag in tags]
                            all_tags.update(formatted_tags)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return sorted(list(all_tags))
            
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        return []

@lru_cache(maxsize=1)
def get_tags_cached() -> List[str]:
    """Get cached list of all tags"""
    return get_all_tags()

def search_articles_optimized(
    query: str,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "desc",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """
    Optimized search for articles
    """
    return get_articles_paginated_optimized(
        page=page,
        limit=limit,
        sort_by=sort_by,
        search_query=query,
        start_date=start_date,
        end_date=end_date
    )

def get_all_categories() -> List[Dict]:
    """Get all available categories with article counts"""
    try:
        category_stats = get_category_stats_cached()
        categories = []
        
        for category, count in category_stats.items():
            categories.append({
                "name": category,
                "article_count": count
            })
        
        # Sort by article count descending
        categories.sort(key=lambda x: x["article_count"], reverse=True)
        
        return categories
        
    except Exception as e:
        logger.error(f"Error getting all categories: {e}")
        return []

def get_api_statistics() -> Dict:
    """Get comprehensive API statistics"""
    try:
        stats = get_cached_stats()
        tags = get_all_tags()
        categories = get_all_categories()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                **stats,
                "total_tags": len(tags),
                "available_categories": len(categories)
            },
            "categories": categories[:10],  # Top 10 categories
            "sample_tags": tags[:20] if tags else []  # First 20 tags
        }
        
    except Exception as e:
        logger.error(f"Error getting API statistics: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Initialize on import
try:
    initialize_optimizations()
    # Pre-load categories
    get_cached_category_keywords()
except Exception as e:
    logger.warning(f"Could not initialize optimizations: {e}")
