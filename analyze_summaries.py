#!/usr/bin/env python3
"""
Analyze summary quality issues
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('data/articles.db')

def analyze_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== SUMMARY QUALITY ANALYSIS ===")
    
    # Check for articles with "recent developments"
    cursor.execute('''
        SELECT title, summary, tags, source 
        FROM articles 
        WHERE summary LIKE "%recent developments%" 
        LIMIT 5
    ''')
    articles = cursor.fetchall()
    
    print('\n1. Articles with "recent developments" in summary:')
    for title, summary, tags, source in articles:
        print(f'   Title: {title[:50]}...')
        print(f'   Summary: {summary[:100]}...')
        print(f'   Tags: {tags}')
        print(f'   Source: {source}')
        print()
    
    # Check for articles with "Health article summary"
    cursor.execute('''
        SELECT title, summary, tags, source 
        FROM articles 
        WHERE summary LIKE "%Health article summary%" 
        LIMIT 5
    ''')
    articles = cursor.fetchall()
    
    print('\n2. Articles with "Health article summary" (fallback):')
    for title, summary, tags, source in articles:
        print(f'   Title: {title[:50]}...')
        print(f'   Summary: {summary[:100]}...')
        print(f'   Tags: {tags}')
        print(f'   Source: {source}')
        print()
    
    # Check for articles with very short summaries
    cursor.execute('''
        SELECT title, summary, LENGTH(summary) as len, source 
        FROM articles 
        WHERE summary IS NOT NULL 
        AND LENGTH(summary) < 50 
        LIMIT 5
    ''')
    articles = cursor.fetchall()
    
    print('\n3. Articles with very short summaries (< 50 chars):')
    for title, summary, length, source in articles:
        print(f'   Title: {title[:50]}...')
        print(f'   Summary ({length} chars): {summary}')
        print(f'   Source: {source}')
        print()
    
    # Check summary length distribution
    cursor.execute('''
        SELECT 
            AVG(LENGTH(summary)) as avg_len,
            MIN(LENGTH(summary)) as min_len,
            MAX(LENGTH(summary)) as max_len,
            COUNT(*) as total
        FROM articles 
        WHERE summary IS NOT NULL
    ''')
    stats = cursor.fetchone()
    
    print('\n4. Summary Length Statistics:')
    print(f'   Average length: {stats[0]:.1f} characters')
    print(f'   Minimum length: {stats[1]} characters')
    print(f'   Maximum length: {stats[2]} characters')
    print(f'   Total articles with summaries: {stats[3]}')
    
    conn.close()

if __name__ == "__main__":
    analyze_summaries()
