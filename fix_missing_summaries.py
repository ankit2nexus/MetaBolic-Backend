#!/usr/bin/env python3
"""
Fix Missing Summaries - Generate summaries for articles that don't have them
"""

import sqlite3
import re
from datetime import datetime

def clean_title_for_summary(title):
    """
    Clean and format a title to be used as a summary
    """
    if not title:
        return "Health article summary not available"
    
    # Remove common prefixes/suffixes that don't add value to summary
    prefixes_to_remove = [
        "BREAKING:",
        "UPDATE:",
        "EXCLUSIVE:",
        "WATCH:",
        "READ:",
        "LIVE:",
        "VIDEO:",
        "PHOTO:",
    ]
    
    cleaned = title.strip()
    
    # Remove prefixes
    for prefix in prefixes_to_remove:
        if cleaned.upper().startswith(prefix.upper()):
            cleaned = cleaned[len(prefix):].strip()
    
    # If title is too short, add context
    if len(cleaned) < 30:
        cleaned = f"Health News: {cleaned}"
    
    # Ensure it ends with a period if it doesn't already have punctuation
    if cleaned and not cleaned[-1] in '.!?':
        cleaned += "."
    
    return cleaned

def generate_smart_summary(title, categories, tags, source):
    """
    Generate a more informative summary based on available metadata
    """
    if not title:
        return "Health article summary not available."
    
    # Clean the title
    base_summary = clean_title_for_summary(title)
    
    # Add context based on categories
    if categories:
        try:
            import json
            if isinstance(categories, str):
                cat_list = json.loads(categories)
            else:
                cat_list = categories
            
            if cat_list and len(cat_list) > 0:
                category = cat_list[0]
                if category == "news":
                    base_summary = f"Latest health news: {base_summary}"
                elif category == "diseases":
                    base_summary = f"Medical information: {base_summary}"
                elif category == "food":
                    base_summary = f"Nutrition and diet: {base_summary}"
                elif category == "solutions":
                    base_summary = f"Health solutions: {base_summary}"
        except:
            pass
    
    # Add source context if available
    if source and source not in base_summary:
        base_summary = f"{base_summary} (Source: {source})"
    
    return base_summary

def fix_missing_summaries():
    """
    Fix articles that don't have summaries
    """
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()
    
    print("=== Fixing Missing Summaries ===")
    
    # Get articles without summaries
    cursor.execute('''
        SELECT id, title, categories, tags, source 
        FROM articles 
        WHERE summary IS NULL OR summary = ""
    ''')
    
    articles_to_fix = cursor.fetchall()
    
    print(f"Found {len(articles_to_fix)} articles without summaries")
    
    fixed_count = 0
    
    for article in articles_to_fix:
        article_id, title, categories, tags, source = article
        
        # Generate summary
        new_summary = generate_smart_summary(title, categories, tags, source)
        
        # Update the article
        cursor.execute('''
            UPDATE articles 
            SET summary = ? 
            WHERE id = ?
        ''', (new_summary, article_id))
        
        fixed_count += 1
        
        if fixed_count <= 5:  # Show first 5 examples
            print(f"\nFixed article {article_id}:")
            print(f"  Title: {title[:80]}...")
            print(f"  New Summary: {new_summary}")
    
    # Commit changes
    conn.commit()
    
    print(f"\n✅ Successfully fixed {fixed_count} articles")
    
    # Verify the fix
    cursor.execute('SELECT COUNT(*) FROM articles WHERE summary IS NULL OR summary = ""')
    remaining = cursor.fetchone()[0]
    
    print(f"Articles still without summary: {remaining}")
    
    conn.close()
    
    return fixed_count

if __name__ == "__main__":
    fixed = fix_missing_summaries()
    print(f"\n🎉 Summary fix complete! Fixed {fixed} articles.")
