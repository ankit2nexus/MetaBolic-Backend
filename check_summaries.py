#!/usr/bin/env python3
"""
Check article summaries in the database
"""

import sqlite3
from pathlib import Path

DB_PATH = Path('data/articles.db')

def check_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check the database schema
    cursor.execute('PRAGMA table_info(articles)')
    columns = cursor.fetchall()
    print('Database schema:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    print('\n--- Sample articles with summaries ---')
    cursor.execute('''
        SELECT title, summary, source 
        FROM articles 
        WHERE summary IS NOT NULL AND summary != "" 
        ORDER BY id DESC 
        LIMIT 10
    ''')
    articles = cursor.fetchall()
    
    for i, (title, summary, source) in enumerate(articles, 1):
        print(f'\n{i}. {title[:60]}...')
        print(f'   Source: {source}')
        print(f'   Summary: {summary[:150]}...')
    
    # Check for articles with placeholder summaries
    print('\n--- Articles with placeholder summaries ---')
    cursor.execute('''
        SELECT COUNT(*) FROM articles 
        WHERE summary LIKE "%Health article summary%" 
        OR summary LIKE "%recent developments%"
    ''')
    placeholder_count = cursor.fetchone()[0]
    print(f'Articles with placeholder summaries: {placeholder_count}')
    
    # Check total articles
    cursor.execute('SELECT COUNT(*) FROM articles')
    total_count = cursor.fetchone()[0]
    print(f'Total articles: {total_count}')
    
    conn.close()

if __name__ == "__main__":
    check_summaries()
