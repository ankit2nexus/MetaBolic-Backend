#!/usr/bin/env python3
"""
Database checker to identify broken URLs and data quality issues
"""

import sqlite3
import json
from pathlib import Path

def check_database():
    """Check database for data quality issues"""
    db_path = Path("data/articles.db")
    if not db_path.exists():
        db_path = Path("db/articles.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    print(f"📁 Database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total articles
    cursor.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    print(f"📊 Total articles: {total}")
    
    # Missing URLs
    cursor.execute("SELECT COUNT(*) FROM articles WHERE url IS NULL OR url = ''")
    missing_urls = cursor.fetchone()[0]
    print(f"🔗 Missing URLs: {missing_urls}")
    
    # Potentially broken URLs (with error indicators)
    cursor.execute("SELECT COUNT(*) FROM articles WHERE url LIKE '%error%' OR url LIKE '%404%' OR url LIKE '%not-found%'")
    broken_urls = cursor.fetchone()[0]
    print(f"❌ Potentially broken URLs: {broken_urls}")
    
    # Articles without summaries
    cursor.execute("SELECT COUNT(*) FROM articles WHERE summary IS NULL OR summary = '' OR summary = 'NULL'")
    missing_summaries = cursor.fetchone()[0]
    print(f"📝 Missing summaries: {missing_summaries}")
    
    # Articles without categories
    cursor.execute("SELECT COUNT(*) FROM articles WHERE categories IS NULL OR categories = '' OR categories = '[]'")
    missing_categories = cursor.fetchone()[0]
    print(f"📂 Missing categories: {missing_categories}")
    
    # Recent articles (last 7 days)
    cursor.execute("SELECT COUNT(*) FROM articles WHERE date > datetime('now', '-7 days')")
    recent = cursor.fetchone()[0]
    print(f"📅 Recent articles (7 days): {recent}")
    
    # Sample problematic articles
    print("\n🔍 Sample issues:")
    cursor.execute("SELECT id, title, url FROM articles WHERE url IS NULL OR url = '' LIMIT 3")
    no_url_articles = cursor.fetchall()
    if no_url_articles:
        print("   Articles without URLs:")
        for article in no_url_articles:
            print(f"   - ID {article[0]}: {article[1][:50]}...")
    
    cursor.execute("SELECT id, title, url FROM articles WHERE url LIKE '%error%' OR url LIKE '%404%' LIMIT 3")
    broken_articles = cursor.fetchall()
    if broken_articles:
        print("   Articles with broken URLs:")
        for article in broken_articles:
            print(f"   - ID {article[0]}: {article[2]}")
    
    # Top sources
    print("\n📰 Top sources:")
    cursor.execute("SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC LIMIT 5")
    sources = cursor.fetchall()
    for source, count in sources:
        print(f"   - {source}: {count} articles")
    
    conn.close()
    
    print(f"\n✅ Database check complete!")
    print(f"   Data quality score: {((total - missing_urls - broken_urls) / total * 100):.1f}%")

if __name__ == "__main__":
    check_database()
