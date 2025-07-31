import requests
import json

# Test the API endpoints
base_url = "http://localhost:8000/api/v1"

def test_endpoints():
    print("=== Testing News Category and Subcategories ===\n")
    
    # Test 1: Get news category articles
    print("1. Testing /category/news")
    try:
        response = requests.get(f"{base_url}/category/news")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total articles: {data['total']}")
            print(f"   📄 Returned: {len(data['articles'])}")
            if data['articles']:
                sample_tags = data['articles'][0].get('tags', [])
                print(f"   🏷️ Sample tags: {sample_tags}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Test subcategory endpoints (these should be tag endpoints)
    subcategories = ["latest", "policy and regulation", "govt schemes", "international"]
    
    for subcategory in subcategories:
        print(f"2. Testing /tag/{subcategory}")
        try:
            response = requests.get(f"{base_url}/tag/{subcategory}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Total articles: {data['total']}")
                print(f"   📄 Returned: {len(data['articles'])}")
                if data['articles']:
                    sample_article = data['articles'][0]
                    print(f"   📰 Sample title: {sample_article.get('title', 'N/A')[:80]}...")
                    print(f"   🏷️ Tags: {sample_article.get('tags', [])}")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()
    
    # Test 3: Get all available tags
    print("3. Testing /tags endpoint")
    try:
        response = requests.get(f"{base_url}/tags")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🏷️ Total tags: {data['total_tags']}")
            news_related_tags = [tag for tag in data['tags'] if any(word in tag.lower() for word in ['news', 'policy', 'govt', 'international', 'latest'])]
            print(f"   📰 News-related tags: {news_related_tags}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()
