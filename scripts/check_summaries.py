#!/usr/bin/env python3
"""
Check summary data in the database
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def check_summaries():
    """Check summary data in the database"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Check summary statistics
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_articles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM articles WHERE summary IS NOT NULL AND summary != ''")
        articles_with_summary = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM articles WHERE summary IS NULL OR summary = ''")
        articles_without_summary = cursor.fetchone()[0]
        
        print(f"📊 Summary Statistics:")
        print(f"Total articles: {total_articles}")
        print(f"Articles with summary: {articles_with_summary}")
        print(f"Articles without summary: {articles_without_summary}")
        print(f"Percentage with summary: {(articles_with_summary/total_articles)*100:.1f}%")
        
        # Show some examples
        print(f"\n📝 Sample articles with summaries:")
        cursor.execute("SELECT id, title, summary FROM articles WHERE summary IS NOT NULL AND summary != '' LIMIT 3")
        rows = cursor.fetchall()
        
        for row in rows:
            print(f"\nID: {row[0]}")
            print(f"Title: {row[1][:80]}...")
            print(f"Summary: {row[2][:150]}...")
            print("-" * 40)
        
        # Show articles without summaries
        print(f"\n❌ Sample articles WITHOUT summaries:")
        cursor.execute("SELECT id, title, summary FROM articles WHERE summary IS NULL OR summary = '' LIMIT 3")
        rows = cursor.fetchall()
        
        for row in rows:
            print(f"\nID: {row[0]}")
            print(f"Title: {row[1][:80]}...")
            print(f"Summary: {row[2] or 'NULL'}")
            print("-" * 40)

if __name__ == "__main__":
    check_summaries()
