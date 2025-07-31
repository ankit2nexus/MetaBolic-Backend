import sqlite3
import json
from collections import Counter

# Connect to database
conn = sqlite3.connect('data/articles.db')
cursor = conn.cursor()

print("=== Checking 'latest' related tags ===")

# Check for variations of 'latest'
latest_variations = ['latest', 'recent', 'new', 'breaking_news', 'recent_developments']

for variation in latest_variations:
    cursor.execute('SELECT COUNT(*) FROM articles WHERE tags LIKE ?', (f'%"{variation}"%',))
    count = cursor.fetchone()[0]
    print(f"'{variation}': {count} articles")

# Get some sample recent news articles to see their tags
print("\n=== Recent news articles and their tags ===")
cursor.execute("""
    SELECT title, tags, date 
    FROM articles 
    WHERE categories LIKE '%"news"%' 
    ORDER BY date DESC 
    LIMIT 10
""")

for i, (title, tags, date) in enumerate(cursor.fetchall()):
    print(f"{i+1}. {title[:60]}...")
    try:
        tag_list = json.loads(tags) if tags else []
        print(f"   Tags: {tag_list}")
    except:
        print(f"   Tags: {tags}")
    print(f"   Date: {date}")
    print()

conn.close()
