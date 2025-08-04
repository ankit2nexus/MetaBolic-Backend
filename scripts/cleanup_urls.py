#!/usr/bin/env python3
"""
Clean up problematic URLs from the database
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def clean_problematic_urls():
    """Remove articles with problematic URLs from the database"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Get total articles before cleanup
        total_before = cursor.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        logger.info(f"Total articles before cleanup: {total_before}")
        
        # Define problematic URL patterns
        problematic_patterns = [
            "url LIKE '%example.com%'",
            "url LIKE '%example.org%'", 
            "url LIKE '%example.net%'",
            "url LIKE '%domain.com%'",
            "url LIKE '%test.com%'",
            "url LIKE '%localhost%'",
            "url LIKE 'javascript:%'",
            "url LIKE 'mailto:%'",
            "url LIKE '%google.com/rss/articles/%'",
            "url = '' OR url IS NULL",
            "url LIKE '%404%'",
            "url LIKE '%error%'",
            "url LIKE '%not-found%'"
        ]
        
        # Count articles to be removed
        where_clause = " OR ".join(problematic_patterns)
        count_query = f"SELECT COUNT(*) FROM articles WHERE {where_clause}"
        articles_to_remove = cursor.execute(count_query).fetchone()[0]
        
        logger.info(f"Articles with problematic URLs to remove: {articles_to_remove}")
        
        if articles_to_remove > 0:
            # Show some examples before deletion
            example_query = f"SELECT url, title FROM articles WHERE {where_clause} LIMIT 10"
            examples = cursor.execute(example_query).fetchall()
            
            logger.info("Examples of articles to be removed:")
            for url, title in examples:
                logger.info(f"  URL: {url}")
                logger.info(f"  Title: {title[:80]}...")
                logger.info("")
            
            # Delete problematic articles
            delete_query = f"DELETE FROM articles WHERE {where_clause}"
            cursor.execute(delete_query)
            
            # Get total articles after cleanup
            total_after = cursor.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
            
            logger.info(f"Total articles after cleanup: {total_after}")
            logger.info(f"Removed {total_before - total_after} articles")
            
            # Commit changes
            conn.commit()
            logger.info("✅ Database cleanup completed successfully")
        else:
            logger.info("✅ No problematic URLs found - database is clean")

def update_google_news_urls():
    """Update Google News RSS URLs to direct article URLs if possible"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Find Google News RSS URLs
        cursor.execute("""
            SELECT id, url, title FROM articles 
            WHERE url LIKE '%google.com/rss/articles/%'
        """)
        
        google_urls = cursor.fetchall()
        
        if google_urls:
            logger.info(f"Found {len(google_urls)} Google News RSS URLs to process")
            
            # For now, we'll just remove these as they're not accessible
            # In a more sophisticated implementation, we could try to extract
            # the actual article URL from the RSS content
            cursor.execute("DELETE FROM articles WHERE url LIKE '%google.com/rss/articles/%'")
            
            removed_count = cursor.rowcount
            logger.info(f"Removed {removed_count} Google News RSS URLs")
            conn.commit()
        else:
            logger.info("No Google News RSS URLs found")

def optimize_database():
    """Optimize database after cleanup"""
    
    with sqlite3.connect(DB_PATH) as conn:
        logger.info("Optimizing database...")
        
        # Update statistics and optimize
        conn.execute("ANALYZE")
        conn.execute("VACUUM")
        
        logger.info("✅ Database optimization completed")

if __name__ == "__main__":
    logger.info("🧹 Starting database cleanup...")
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"Timestamp: {datetime.now()}")
    
    try:
        clean_problematic_urls()
        update_google_news_urls()
        optimize_database()
        
        logger.info("🎉 All cleanup operations completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        raise
