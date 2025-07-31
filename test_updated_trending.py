import requests

print('🧪 TESTING UPDATED TRENDING URLS')
print('=' * 45)

base_url = 'http://localhost:8000'

# Test gut health
try:
    r = requests.get(f'{base_url}/api/v1/tag/gut%20health?limit=5')
    print(f'Gut Health (tag) - Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total", 0)} articles')
        if data.get('articles'):
            print(f'   📰 Sample: {data["articles"][0].get("title", "N/A")[:50]}...')
    else:
        print(f'   ❌ Error: {r.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()

# Test trending gut health
try:
    r = requests.get(f'{base_url}/api/v1/trending/gut%20health?limit=5')
    print(f'Trending Gut Health - Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total", 0)} articles')
        if data.get('articles'):
            print(f'   📰 Sample: {data["articles"][0].get("title", "N/A")[:50]}...')
    else:
        print(f'   ❌ Error: {r.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()

# Test addiction
try:
    r = requests.get(f'{base_url}/api/v1/tag/addiction?limit=5')
    print(f'Addiction (tag) - Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total", 0)} articles')
        if data.get('articles'):
            print(f'   📰 Sample: {data["articles"][0].get("title", "N/A")[:50]}...')
    else:
        print(f'   ❌ Error: {r.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()

# Test trending addiction
try:
    r = requests.get(f'{base_url}/api/v1/trending/addiction?limit=5')
    print(f'Trending Addiction - Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total", 0)} articles')
        if data.get('articles'):
            print(f'   📰 Sample: {data["articles"][0].get("title", "N/A")[:50]}...')
    else:
        print(f'   ❌ Error: {r.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print()

# Test main trending category
try:
    r = requests.get(f'{base_url}/api/v1/trending?limit=5')
    print(f'Main Trending Category - Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'   ✅ Found {data.get("total", 0)} articles')
        if data.get('articles'):
            print(f'   📰 Sample: {data["articles"][0].get("title", "N/A")[:50]}...')
    else:
        print(f'   ❌ Error: {r.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print('\n📋 SUMMARY:')
print('Expected results based on script output:')
print('   - Gut Health: 8 articles')
print('   - Addiction: 2 articles')
print('   - Main Trending: 139 articles')
print('   - Mental Health: 85 articles')
print('   - Sleep Health: 23 articles')
print('   - Sexual Wellness: 12 articles')
