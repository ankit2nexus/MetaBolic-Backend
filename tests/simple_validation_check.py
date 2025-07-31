import sqlite3

# Quick database check
conn = sqlite3.connect('data/articles.db')
cursor = conn.cursor()

# Check the specific articles that had None source values
cursor.execute("SELECT id, title, source, url FROM articles WHERE source IS NULL LIMIT 5")
rows = cursor.fetchall()

print("Articles with NULL source values:")
for row in rows:
    print(f"ID: {row[0]}, Title: {row[1][:50]}, Source: {row[2]}, URL: {row[3][:50] if row[3] else 'None'}")

conn.close()
