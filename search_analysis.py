import sqlite3

conn = sqlite3.connect('data/articles.db')
cursor = conn.cursor()

print('🔍 ANALYZING SEARCH ISSUE')
print('=' * 40)

# Check for exact phrase 'sleep health' in title/summary
cursor.execute('''SELECT COUNT(*) FROM articles 
                  WHERE LOWER(title) LIKE '%sleep health%' 
                  OR LOWER(summary) LIKE '%sleep health%' ''')
sleep_health_content = cursor.fetchone()[0]

cursor.execute('''SELECT COUNT(*) FROM articles 
                  WHERE LOWER(title) LIKE '%sexual wellness%' 
                  OR LOWER(summary) LIKE '%sexual wellness%' ''')
sexual_wellness_content = cursor.fetchone()[0]

print(f'Articles with "sleep health" in title/summary: {sleep_health_content}')
print(f'Articles with "sexual wellness" in title/summary: {sexual_wellness_content}')

# Check what we DO have in title/summary
print('\n🔍 What we have in titles/summaries:')
cursor.execute('''SELECT title, summary FROM articles 
                  WHERE LOWER(title) LIKE '%sleep%' 
                  OR LOWER(summary) LIKE '%sleep%' 
                  LIMIT 3''')
sleep_samples = cursor.fetchall()

for i, (title, summary) in enumerate(sleep_samples):
    print(f'   Sleep {i+1}: {title[:60]}...')
    print(f'           Summary: {(summary or "")[:60]}...')

cursor.execute('''SELECT title, summary FROM articles 
                  WHERE LOWER(title) LIKE '%sexual%' 
                  OR LOWER(summary) LIKE '%sexual%' 
                  LIMIT 3''')
sexual_samples = cursor.fetchall()

for i, (title, summary) in enumerate(sexual_samples):
    print(f'   Sexual {i+1}: {title[:60]}...')
    print(f'            Summary: {(summary or "")[:60]}...')

# Check tags
cursor.execute('''SELECT COUNT(*) FROM articles WHERE tags LIKE '%sleep health%' ''')
sleep_tag_count = cursor.fetchone()[0]

cursor.execute('''SELECT COUNT(*) FROM articles WHERE tags LIKE '%sexual wellness%' ''')
sexual_tag_count = cursor.fetchone()[0]

print(f'\n🏷️ Articles tagged with "sleep health": {sleep_tag_count}')
print(f'🏷️ Articles tagged with "sexual wellness": {sexual_tag_count}')

# The issue: Search looks in title/summary, but "sleep health" and "sexual wellness" 
# are only in tags, not in the actual content

print('\n💡 SOLUTION NEEDED:')
print('Search endpoint only looks in title/summary fields')
print('But "sleep health" and "sexual wellness" are only in tags')
print('Need to update article titles/summaries to include these terms')

conn.close()
