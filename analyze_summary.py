#!/usr/bin/env python3
import sqlite3

def analyze_summary_data():
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()

    print('=== Analyzing Summary Field ===')
    
    # Total articles
    cursor.execute('SELECT COUNT(*) FROM articles')
    total = cursor.fetchone()[0]
    print(f'Total articles: {total}')

    # Articles with summary
    cursor.execute('SELECT COUNT(*) FROM articles WHERE summary IS NOT NULL AND summary != ""')
    with_summary = cursor.fetchone()[0]
    print(f'Articles with summary: {with_summary}')

    # Articles without summary
    cursor.execute('SELECT COUNT(*) FROM articles WHERE summary IS NULL OR summary = ""')
    without_summary = cursor.fetchone()[0]
    print(f'Articles without summary: {without_summary}')

    print(f'\nPercentage with summary: {(with_summary/total)*100:.1f}%')
    print(f'Percentage without summary: {(without_summary/total)*100:.1f}%')

    print('\n=== Sample Articles Without Summary ===')
    cursor.execute('SELECT id, title, summary FROM articles WHERE summary IS NULL OR summary = "" LIMIT 5')
    rows = cursor.fetchall()

    for row in rows:
        print(f'ID: {row[0]}')
        print(f'Title: {row[1][:80]}...' if row[1] and len(row[1]) > 80 else f'Title: {row[1]}')
        print(f'Summary: [EMPTY]')
        print('---')

    print('\n=== Sample Articles With Summary ===')
    cursor.execute('SELECT id, title, summary FROM articles WHERE summary IS NOT NULL AND summary != "" LIMIT 5')
    rows = cursor.fetchall()

    for row in rows:
        print(f'ID: {row[0]}')
        print(f'Title: {row[1][:80]}...' if row[1] and len(row[1]) > 80 else f'Title: {row[1]}')
        print(f'Summary: {row[2][:120]}...' if row[2] and len(row[2]) > 120 else f'Summary: {row[2]}')
        print('---')

    conn.close()

if __name__ == "__main__":
    analyze_summary_data()
