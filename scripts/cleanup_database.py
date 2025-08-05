#!/usr/bin/env python3
"""
Database cleanup script to fix date formatting and categorization issues
"""

import sqlite3
import re
from datetime import datetime
import json

def clean_database():
    """Clean up the database by fixing dates and categories"""
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()
    
    print("🧹 Starting database cleanup...")
    
    # Get all articles with problematic dates
    cursor.execute("SELECT id, date, categories FROM articles WHERE date LIKE '0%' OR date LIKE '1%' OR date LIKE '2%'")
    articles = cursor.fetchall()
    
    print(f"Found {len(articles)} articles to potentially clean")
    
    cleaned_count = 0
    for article_id, date_str, categories in articles:
        updated = False
        new_date = date_str
        new_categories = categories
        
        # Fix dates that start with wrong years (0202, 1970, etc.)
        if date_str.startswith('0') or date_str.startswith('1') or date_str.startswith('2025-01-01'):
            # Replace with a reasonable default date (today)
            new_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            updated = True
            print(f"Fixed date for article {article_id}: {date_str} -> {new_date}")
        
        # Fix category capitalization inconsistencies
        if categories:
            try:
                cat_list = json.loads(categories)
                if isinstance(cat_list, list):
                    # Standardize to lowercase
                    new_cat_list = [cat.lower() for cat in cat_list]
                    new_categories = json.dumps(new_cat_list)
                    if new_categories != categories:
                        updated = True
                        print(f"Fixed categories for article {article_id}: {categories} -> {new_categories}")
            except:
                pass
        
        if updated:
            cursor.execute(
                "UPDATE articles SET date = ?, categories = ? WHERE id = ?",
                (new_date, new_categories, article_id)
            )
            cleaned_count += 1
    
    # Also clean up any articles with null or empty dates
    cursor.execute("UPDATE articles SET date = ? WHERE date IS NULL OR date = ''", 
                   (datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database cleanup complete. Updated {cleaned_count} articles.")
    print("📊 Database is now ready for improved categorization and date filtering!")

if __name__ == "__main__":
    clean_database()
