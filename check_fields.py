#!/usr/bin/env python3
import sqlite3

def check_article_fields():
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()

    # Get full schema
    cursor.execute('PRAGMA table_info(articles)')
    columns = cursor.fetchall()
    print('=== Full Database Schema ===')
    for col in columns:
        print(f'{col[1]}: {col[2]} (nullable: {not col[3]})')

    print('\n=== Sample article without summary - all fields ===')
    cursor.execute('SELECT * FROM articles WHERE summary IS NULL OR summary = "" LIMIT 1')
    row = cursor.fetchone()
    if row:
        for i, col in enumerate(columns):
            print(f'{col[1]}: {row[i]}')
    
    conn.close()

if __name__ == "__main__":
    check_article_fields()
