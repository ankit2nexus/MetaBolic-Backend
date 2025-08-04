#!/usr/bin/env python3
"""
Test the scraper fix by simulating article creation with summaries
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

DB_PATH = BASE_DIR / "data" / "articles.db"

def test_scraper_fix():
    """Test if the scraper fix works by adding test articles"""
    
    print("🧪 Testing Scraper Fix for Summary Field...")
    print("=" * 50)
    
    # Create test articles with summaries
    test_articles = [
        {
            'title': 'TEST: New Diabetes Treatment Shows Promise',
            'summary': 'This is a test summary for a diabetes treatment article. It contains meaningful content about the treatment and its potential benefits for patients.',
            'url': 'https://example-test.com/diabetes-treatment-1',
            'published_date': datetime.now().isoformat(),
            'source': 'Test Health News',
            'category': 'medical_research',
            'tags': 'diabetes,treatment,test',
            'image_url': '',
            'author': 'Test Author',
            'read_time': 3
        },
        {
            'title': 'TEST: Heart Health Study Results',
            'summary': 'Test summary about heart health research findings. This summary provides details about cardiovascular health improvements and lifestyle changes.',
            'url': 'https://example-test.com/heart-health-2',
            'published_date': datetime.now().isoformat(),
            'source': 'Test Medical Journal',
            'category': 'medical_research',
            'tags': 'heart,health,research,test',
            'image_url': '',
            'author': 'Test Researcher',
            'read_time': 4
        }
    ]
    
    # Save test articles using the corrected field names
    saved_count = 0
    
    with sqlite3.connect(DB_PATH) as conn:
        for article in test_articles:
            try:
                # Use the corrected INSERT statement
                conn.execute("""
                    INSERT OR IGNORE INTO articles 
                    (title, summary, url, published_date, source, category, tags, image_url, author, read_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article['title'],
                    article['summary'],
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
                    print(f"✅ Saved: {article['title']}")
                else:
                    print(f"⚠️  Already exists: {article['title']}")
                    
            except Exception as e:
                print(f"❌ Error saving article '{article['title']}': {e}")
        
        conn.commit()
    
    print(f"\n📊 Saved {saved_count} new test articles")
    
    # Test API retrieval of the new articles
    print(f"\n🔍 Testing API retrieval of new articles...")
    
    from app.utils import get_articles_paginated_optimized
    
    # Search for our test articles
    result = get_articles_paginated_optimized(page=1, limit=5, search_query="TEST:")
    
    print(f"📊 API Search Results:")
    print(f"   Total matching articles: {result['total']}")
    print(f"   Returned articles: {len(result['articles'])}")
    
    for i, article in enumerate(result['articles'], 1):
        if 'TEST:' in article.get('title', ''):
            summary = article.get('summary', '')
            has_good_summary = bool(summary and len(summary) > 50 and 'Test summary' in summary)
            
            print(f"\n   Test Article {i}:")
            print(f"   - ID: {article.get('id')}")
            print(f"   - Title: {article.get('title', '')}")
            print(f"   - Summary Quality: {'✅ GOOD' if has_good_summary else '❌ POOR'}")
            print(f"   - Summary Length: {len(summary)} chars")
            print(f"   - Summary: {summary[:100]}...")
    
    # Clean up test articles
    print(f"\n🧹 Cleaning up test articles...")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM articles WHERE title LIKE 'TEST:%'")
        deleted = conn.total_changes
        conn.commit()
        print(f"🗑️  Deleted {deleted} test articles")

if __name__ == "__main__":
    test_scraper_fix()
