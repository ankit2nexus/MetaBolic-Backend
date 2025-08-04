#!/usr/bin/env python3
"""
Find articles with good summaries
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def find_good_summaries():
    """Find articles with proper summaries"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Find articles with good summaries
        cursor.execute("""
            SELECT id, title, summary, date, source 
            FROM articles 
            WHERE summary IS NOT NULL 
            AND summary != '' 
            AND LENGTH(summary) > 50 
            ORDER BY date DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        
        print("📝 Articles with good summaries:")
        print("=" * 60)
        
        for row in rows:
            print(f"\nID: {row[0]}")
            print(f"Title: {row[1][:70]}...")
            print(f"Summary: {row[2][:150]}...")
            print(f"Source: {row[4]}")
            print(f"Date: {row[3]}")
            print("-" * 40)
        
        # Check recent articles summary status
        print(f"\n📊 Recent Articles Summary Status:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN summary IS NOT NULL AND summary != '' AND LENGTH(summary) > 10 THEN 1 ELSE 0 END) as with_good_summary,
                SUM(CASE WHEN summary IS NULL OR summary = '' OR LENGTH(summary) <= 10 THEN 1 ELSE 0 END) as without_summary
            FROM articles 
            WHERE date >= date('now', '-7 days')
        """)
        
        stats = cursor.fetchone()
        total, with_summary, without_summary = stats
        
        print(f"Recent articles (last 7 days): {total}")
        print(f"With good summaries: {with_summary} ({(with_summary/total)*100:.1f}%)")
        print(f"Without good summaries: {without_summary} ({(without_summary/total)*100:.1f}%)")

if __name__ == "__main__":
    find_good_summaries()
