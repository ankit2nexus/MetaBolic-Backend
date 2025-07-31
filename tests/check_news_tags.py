import sqlite3
import json
from collections import Counter

# Connect to database
conn = sqlite3.connect('data/articles.db')
cursor = conn.cursor()

# Check news subcategories (which are actually tags)
print("=== NEWS TAGS/SUBCATEGORIES ===")
cursor.execute('SELECT tags FROM articles WHERE categories LIKE "%news%" AND tags IS NOT NULL AND tags != ""')
rows = cursor.fetchall()

all_tags = []
for row in rows:
    try:
        if row[0]:
            tags = json.loads(row[0])
            if isinstance(tags, list):
                all_tags.extend(tags)
            else:
                all_tags.append(tags)
    except json.JSONDecodeError:
        # If not JSON, treat as single tag
        if row[0]:
            all_tags.append(row[0])

# Count tags
tag_counts = Counter(all_tags)
print("Tag frequency in news articles:")
for tag, count in tag_counts.most_common():
    print(f'{tag}: {count}')

# Check if the specific tags from the frontend exist
frontend_news_tags = ["latest", "policy and regulation", "govt schemes", "international"]
print(f"\n=== CHECKING FRONTEND TAGS IN DATABASE ===")
for tag in frontend_news_tags:
    cursor.execute('SELECT COUNT(*) FROM articles WHERE categories LIKE "%news%" AND tags LIKE ?', (f'%"{tag}"%',))
    count = cursor.fetchone()[0]
    print(f'"{tag}": {count} articles')
    
    # Also try variations
    variations = [tag.replace(" ", "_"), tag.replace(" ", ""), tag.lower()]
    for var in variations:
        cursor.execute('SELECT COUNT(*) FROM articles WHERE categories LIKE "%news%" AND tags LIKE ?', (f'%"{var}"%',))
        var_count = cursor.fetchone()[0]
        if var_count > 0:
            print(f'  -> "{var}": {var_count} articles')

conn.close()
