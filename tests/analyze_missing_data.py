#!/usr/bin/env python3
"""
Analyze sleep health and sexual wellness data in the database
"""
import sqlite3
import json

def analyze_missing_data():

    
    # Connect to database
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()
    
    print('🔍 INVESTIGATING SLEEP HEALTH AND SEXUAL WELLNESS DATA')
    print('=' * 60)
    
    # Check total articles
    cursor.execute('SELECT COUNT(*) FROM articles')
    total = cursor.fetchone()[0]
    print(f'📊 Total articles in database: {total}')
    
    # Check tags column structure
    cursor.execute('SELECT tags FROM articles WHERE tags IS NOT NULL LIMIT 5')
    sample_tags = cursor.fetchall()
    print(f'\n📋 Sample tags structure:')
    for i, (tags,) in enumerate(sample_tags[:3]):
        print(f'   {i+1}. {tags[:100]}...')
    
    # Search for sleep-related content
    print(f'\n🛌 SLEEP HEALTH ANALYSIS:')
    sleep_keywords = ['sleep', 'insomnia', 'sleep apnea', 'sleep disorder', 'sleep quality', 'sleep hygiene']
    sleep_total = 0
    for keyword in sleep_keywords:
        cursor.execute('SELECT COUNT(*) FROM articles WHERE LOWER(title) LIKE ? OR LOWER(summary) LIKE ?', 
                       (f'%{keyword}%', f'%{keyword}%'))
        count = cursor.fetchone()[0]
        sleep_total += count
        print(f'   "{keyword}": {count} articles')
    
    print(f'   Total sleep-related articles: {sleep_total}')
    
    # Search for sexual wellness content
    print(f'\n💕 SEXUAL WELLNESS ANALYSIS:')
    sexual_keywords = ['sexual', 'sexuality', 'reproductive', 'fertility', 'contraception', 'erectile', 'libido']
    sexual_total = 0
    for keyword in sexual_keywords:
        cursor.execute('SELECT COUNT(*) FROM articles WHERE LOWER(title) LIKE ? OR LOWER(summary) LIKE ?', 
                       (f'%{keyword}%', f'%{keyword}%'))
        count = cursor.fetchone()[0]
        sexual_total += count
        print(f'   "{keyword}": {count} articles')
    
    print(f'   Total sexual wellness articles: {sexual_total}')
    
    # Check if tags contain these terms
    print(f'\n🏷️ TAG ANALYSIS:')
    cursor.execute('SELECT COUNT(*) FROM articles WHERE tags LIKE ?', ('%sleep%',))
    sleep_tag_count = cursor.fetchone()[0]
    print(f'   Articles with "sleep" in tags: {sleep_tag_count}')
    
    cursor.execute('SELECT COUNT(*) FROM articles WHERE tags LIKE ?', ('%sexual%',))
    sexual_tag_count = cursor.fetchone()[0]
    print(f'   Articles with "sexual" in tags: {sexual_tag_count}')
    
    # Get some sample articles that might be relevant
    print(f'\n📰 SAMPLE RELEVANT ARTICLES:')
    cursor.execute('''SELECT title, tags FROM articles 
                      WHERE (LOWER(title) LIKE "%sleep%" OR LOWER(title) LIKE "%sexual%" 
                             OR LOWER(summary) LIKE "%sleep%" OR LOWER(summary) LIKE "%sexual%")
                      LIMIT 5''')
    samples = cursor.fetchall()
    if samples:
        for i, (title, tags) in enumerate(samples):
            print(f'   {i+1}. {title[:60]}...')
            print(f'      Tags: {tags[:80] if tags else "No tags"}...')
    else:
        print('   No relevant articles found')
    
    # Check current categories and their counts
    print(f'\n📁 CURRENT CATEGORIES:')
    cursor.execute('''SELECT categories, COUNT(*) as count 
                      FROM articles 
                      WHERE categories IS NOT NULL AND categories != '' 
                      GROUP BY categories 
                      ORDER BY count DESC''')
    categories = cursor.fetchall()
    for cat, count in categories[:10]:
        print(f'   {cat}: {count} articles')
    
    conn.close()
    
    # Provide solutions
    print(f'\n💡 SOLUTIONS:')
    print('=' * 30)
    
    if sleep_total == 0:
        print('❌ No sleep-related content found')
        print('✅ Solution 1: Add sleep health articles to database')
        print('✅ Solution 2: Create sleep health content scraper')
        print('✅ Solution 3: Tag existing articles with sleep keywords')
    else:
        print(f'✅ Found {sleep_total} sleep-related articles')
        print('🔧 Solution: Re-tag existing articles with "sleep health" tag')
    
    if sexual_total == 0:
        print('❌ No sexual wellness content found')
        print('✅ Solution 1: Add sexual wellness articles to database')
        print('✅ Solution 2: Create sexual wellness content scraper')
        print('✅ Solution 3: Tag existing articles with sexual wellness keywords')
    else:
        print(f'✅ Found {sexual_total} sexual wellness articles')
        print('🔧 Solution: Re-tag existing articles with "sexual wellness" tag')

if __name__ == "__main__":
    analyze_missing_data()
