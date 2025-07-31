import sqlite3
import json

# Connect to database
conn = sqlite3.connect('data/articles.db')
cursor = conn.cursor()

# Check news category data
print("=== NEWS CATEGORY DATA ===")
cursor.execute('SELECT categories, tags FROM articles WHERE categories LIKE "%news%" LIMIT 5')
rows = cursor.fetchall()

for i, row in enumerate(rows):
    print(f'Sample {i+1}:')
    print(f'Categories: {row[0]}')
    print(f'Tags: {row[1]}')
    print('---')

# Check distinct categories
print("\n=== ALL DISTINCT CATEGORIES ===")
cursor.execute('SELECT DISTINCT categories FROM articles WHERE categories IS NOT NULL AND categories != "" LIMIT 10')
categories = cursor.fetchall()

for cat in categories:
    print(f'Category: {cat[0]}')

# Check total count of news articles
print("\n=== NEWS ARTICLES COUNT ===")
cursor.execute('SELECT COUNT(*) FROM articles WHERE categories LIKE "%news%"')
count = cursor.fetchone()[0]
print(f'Total news articles: {count}')

conn.close()
