#!/usr/bin/env python3
"""
Direct test of database insertion and retrieval
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def test_direct_database():
    """Test database operations directly"""
    
    print("🧪 Testing Direct Database Operations...")
    print("=" * 50)
    
    # Insert a test article
    test_article = {
        'title': 'DIRECT_TEST: Summary Field Verification',
        'summary': 'This is a direct test summary to verify that the summary field is working correctly in the database. This summary should be retrieved by the API.',
        'url': 'https://test-direct.com/summary-test',
        'published_date': datetime.now().isoformat(),
        'source': 'Direct Test',
        'category': '["test"]',
        'tags': '["test", "summary", "verification"]',
        'image_url': '',
        'author': 'Test Direct',
        'read_time': 3
    }
    
    with sqlite3.connect(DB_PATH) as conn:
        # Insert the test article
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO articles 
            (title, summary, url, date, source, categories, tags, authors)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_article['title'],
            test_article['summary'],
            test_article['url'],
            test_article['published_date'],
            test_article['source'],
            test_article['category'],
            test_article['tags'],
            test_article['author']
        ))
        
        article_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Inserted test article with ID: {article_id}")
        
        # Retrieve the article directly
        cursor.execute("""
            SELECT id, title, summary, url, source 
            FROM articles 
            WHERE title LIKE 'DIRECT_TEST:%'
        """)
        
        rows = cursor.fetchall()
        
        print(f"\n📊 Direct database retrieval:")
        print(f"Found {len(rows)} test articles")
        
        for row in rows:
            print(f"\nID: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Summary: {row[2][:100]}..." if row[2] else "No summary")
            print(f"Summary Length: {len(row[2]) if row[2] else 0}")
            print(f"URL: {row[3]}")
            print(f"Source: {row[4]}")
        
        # Test the API query structure
        print(f"\n🔍 Testing API-style query:")
        cursor.execute("""
            SELECT id, title, summary, NULL as content, url, source, date, categories as category, 
                   NULL as subcategory, tags, NULL as image_url, authors as author 
            FROM articles 
            WHERE title LIKE 'DIRECT_TEST:%'
            ORDER BY date DESC, id DESC
        """)
        
        api_rows = cursor.fetchall()
        
        print(f"API-style query returned {len(api_rows)} rows")
        
        for row in api_rows:
            print(f"\nAPI Result:")
            print(f"  ID: {row[0]}")
            print(f"  Title: {row[1]}")
            print(f"  Summary: {row[2][:100]}..." if row[2] else "No summary")
            print(f"  Summary Present: {'✅ YES' if row[2] and len(row[2]) > 10 else '❌ NO'}")
        
        # Clean up
        cursor.execute("DELETE FROM articles WHERE title LIKE 'DIRECT_TEST:%'")
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"\n🧹 Cleaned up {deleted} test articles")

if __name__ == "__main__":
    test_direct_database()
