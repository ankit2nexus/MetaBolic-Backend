#!/usr/bin/env python3
"""
Check for problematic URLs in the database
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def check_problematic_urls():
    """Check for problematic URLs in the database"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Check for various problematic URL patterns
        problematic_patterns = [
            ("Empty URLs", "url = '' OR url IS NULL"),
            ("Example URLs", "url LIKE '%example%'"),
            ("Domain.com URLs", "url LIKE '%domain.com%'"),
            ("JavaScript URLs", "url LIKE 'javascript:%'"),
            ("Mailto URLs", "url LIKE 'mailto:%'"),
            ("Invalid protocols", "url NOT LIKE 'http%'"),
            ("404 URLs", "url LIKE '%404%'"),
            ("Error URLs", "url LIKE '%error%'"),
        ]
        
        total_articles = cursor.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        print(f"Total articles in database: {total_articles}")
        print("\nChecking for problematic URLs:")
        print("-" * 60)
        
        total_problematic = 0
        
        for pattern_name, sql_condition in problematic_patterns:
            query = f"SELECT COUNT(*), url, title FROM articles WHERE {sql_condition} GROUP BY url, title LIMIT 5"
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results and results[0][0] > 0:
                count = sum(row[0] for row in results)
                total_problematic += count
                print(f"\n{pattern_name}: {count} articles")
                for row in results[:3]:  # Show first 3 examples
                    print(f"  URL: {row[1] or 'NULL'}")
                    print(f"  Title: {row[2][:80]}...")
                    print()
        
        print(f"\nTotal problematic URLs: {total_problematic}")
        print(f"Percentage of problematic URLs: {(total_problematic/total_articles)*100:.2f}%")
        
        # Also check for duplicate URLs
        cursor.execute("""
            SELECT url, COUNT(*) as count 
            FROM articles 
            WHERE url IS NOT NULL AND url != ''
            GROUP BY url 
            HAVING COUNT(*) > 1 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"\nDuplicate URLs found:")
            for url, count in duplicates:
                print(f"  {count} copies: {url[:80]}...")

if __name__ == "__main__":
    check_problematic_urls()
