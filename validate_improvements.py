#!/usr/bin/env python3
"""
Validate the summary and tag improvements
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('data/articles.db')

def validate_improvements():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== VALIDATING SUMMARY IMPROVEMENTS ===")
    
    # Check articles that should have received enhanced summaries
    cursor.execute('''
        SELECT title, summary, tags, source 
        FROM articles 
        WHERE (
            summary LIKE "%Latest insights%" OR
            summary LIKE "%Important developments%" OR
            summary LIKE "%New findings%" OR
            summary LIKE "%Stay informed%" OR
            summary LIKE "%COVID-19 updates%"
        )
        LIMIT 10
    ''')
    
    improved_articles = cursor.fetchall()
    
    print(f"\n✅ Found {len(improved_articles)} articles with enhanced summaries:")
    for title, summary, tags, source in improved_articles:
        print(f"\nTitle: {title[:50]}...")
        print(f"Source: {source}")
        print(f"Enhanced Summary: {summary[:100]}...")
        print(f"Tags: {tags}")
    
    # Check for remaining placeholder summaries
    cursor.execute('''
        SELECT COUNT(*) FROM articles 
        WHERE summary LIKE "%Health article summary%"
    ''')
    placeholder_count = cursor.fetchone()[0]
    
    print(f"\n📊 Remaining placeholder summaries: {placeholder_count}")
    
    # Check summary quality distribution
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN LENGTH(summary) < 30 THEN 1 END) as very_short,
            COUNT(CASE WHEN LENGTH(summary) BETWEEN 30 AND 100 THEN 1 END) as medium,
            COUNT(CASE WHEN LENGTH(summary) > 100 THEN 1 END) as long,
            COUNT(*) as total
        FROM articles 
        WHERE summary IS NOT NULL AND summary != ""
    ''')
    
    stats = cursor.fetchone()
    print(f"\n📈 Summary Length Distribution:")
    print(f"   Very short (< 30 chars): {stats[0]}")
    print(f"   Medium (30-100 chars): {stats[1]}")
    print(f"   Long (> 100 chars): {stats[2]}")
    print(f"   Total: {stats[3]}")
    
    conn.close()

if __name__ == "__main__":
    validate_improvements()
