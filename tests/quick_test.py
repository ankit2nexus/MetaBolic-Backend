import requests

# Test categories
print("=== TESTING CATEGORIES ===")
try:
    r = requests.get('http://localhost:8000/api/v1/categories')
    if r.status_code == 200:
        data = r.json()
        print("Available categories:")
        for cat in data['categories']:
            print(f"  - {cat['name']} ({cat['article_count']} articles)")
        
        categories = [c['name'] for c in data['categories']]
        if 'trending' in categories:
            print("✅ 'trending' category FOUND!")
        else:
            print("❌ 'trending' category NOT found")
    else:
        print(f"Error: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== TESTING TAGS ===")
try:
    r = requests.get('http://localhost:8000/api/v1/tags')
    if r.status_code == 200:
        data = r.json()
        tags = data['tags']
        print(f"Total tags available: {len(tags)}")
        
        # Check target tags
        target_tags = ["gut health", "mental health", "hormones", "addiction", "sleep health", "sexual wellness"]
        
        for tag in target_tags:
            if tag in tags:
                print(f"✅ '{tag}' tag FOUND")
            else:
                print(f"❌ '{tag}' tag NOT found")
    else:
        print(f"Error: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== TRENDING CATEGORY TEST ===")
try:
    r = requests.get('http://localhost:8000/api/v1/trending')
    print(f"GET /api/v1/trending - Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Found {data.get('total', 0)} trending articles")
except Exception as e:
    print(f"Error: {e}")

try:
    r = requests.get('http://localhost:8000/api/v1/category/trending')
    print(f"GET /api/v1/category/trending - Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Found {data.get('total', 0)} trending articles")
except Exception as e:
    print(f"Error: {e}")
