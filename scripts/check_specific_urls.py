#!/usr/bin/env python3
"""
Check for specific problematic URL patterns
"""

import sqlite3
import requests
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def check_google_news_urls():
    """Check for Google News RSS URLs that are problematic"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Check for Google News RSS URLs
        cursor.execute("""
            SELECT url, title, source FROM articles 
            WHERE url LIKE '%google.com/rss/articles/%' 
            OR url LIKE '%news.google.com/rss/articles/%'
            LIMIT 20
        """)
        
        google_urls = cursor.fetchall()
        
        print(f"Found {len(google_urls)} Google News RSS URLs:")
        print("-" * 80)
        
        for url, title, source in google_urls:
            print(f"Source: {source}")
            print(f"Title: {title[:80]}...")
            print(f"URL: {url}")
            
            # Test if URL is accessible
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    print("✅ URL is accessible")
                else:
                    print(f"❌ URL returns status {response.status_code}")
            except Exception as e:
                print(f"❌ URL not accessible: {str(e)[:50]}...")
            
            print("-" * 40)

def check_invalid_urls():
    """Check for other invalid URL patterns"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Check for various invalid patterns
        cursor.execute("""
            SELECT url, title, source FROM articles 
            WHERE url LIKE '%example%' 
            OR url LIKE '%domain.com%' 
            OR url LIKE '%test%' 
            OR url LIKE '%localhost%'
            OR url = '' 
            OR url IS NULL
            LIMIT 10
        """)
        
        invalid_urls = cursor.fetchall()
        
        if invalid_urls:
            print(f"\nFound {len(invalid_urls)} invalid URLs:")
            print("-" * 80)
            
            for url, title, source in invalid_urls:
                print(f"Source: {source}")
                print(f"Title: {title[:80]}...")
                print(f"URL: {url or 'NULL'}")
                print("-" * 40)
        else:
            print("\nNo invalid URLs found.")

if __name__ == "__main__":
    check_google_news_urls()
    check_invalid_urls()
