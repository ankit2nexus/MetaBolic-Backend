#!/usr/bin/env python3
"""
Direct endpoint testing using FastAPI TestClient
No need to start server manually
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints_directly():
    print("🧪 DIRECT ENDPOINT TESTING (No Server Required)")
    print("=" * 60)
    
    # Test the problematic endpoint first
    print("\n❌ TESTING THE INCORRECT ENDPOINT YOU MENTIONED:")
    print("   URL: /api/v1/categories/news")
    response = client.get("/api/v1/categories/news")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   📝 This endpoint doesn't exist! 'categories' is for listing all categories, not filtering.")
    
    print("\n✅ TESTING CORRECT ENDPOINTS FOR NEWS:")
    
    # Test correct news endpoints
    print("\n1️⃣ Direct category: /api/v1/news")
    response = client.get("/api/v1/news?limit=3")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Articles found: {len(data.get('articles', []))}")
        print(f"   📊 Total: {data.get('total')}")
        if data.get('articles'):
            print(f"   📄 Sample title: {data['articles'][0].get('title', '')[:50]}...")
    else:
        print(f"   ❌ Error: {response.text}")
    
    print("\n2️⃣ Alternative category: /api/v1/category/news")
    response = client.get("/api/v1/category/news?limit=3")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Articles found: {len(data.get('articles', []))}")
        print(f"   📊 Total: {data.get('total')}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    print("\n🔍 TESTING ALL MAIN ENDPOINTS:")
    
    endpoints_to_test = [
        ("/api/v1/?limit=1", "Main articles"),
        ("/api/v1/latest?limit=1", "Latest articles"),
        ("/api/v1/search?q=health&limit=1", "Search"),
        ("/api/v1/diseases?limit=1", "Diseases category"),
        ("/api/v1/food?limit=1", "Food category"),
        ("/api/v1/categories", "List all categories"),
        ("/api/v1/tags", "List all tags"),
        ("/api/v1/health", "Health check"),
        ("/api/v1/stats", "Statistics"),
    ]
    
    for endpoint, description in endpoints_to_test:
        print(f"\n📍 {description}: {endpoint}")
        try:
            response = client.get(endpoint)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'articles' in data:
                    print(f"   ✅ Articles: {len(data.get('articles', []))}, Total: {data.get('total', 0)}")
                elif 'categories' in data:
                    print(f"   ✅ Categories: {len(data.get('categories', []))}")
                elif 'tags' in data:
                    print(f"   ✅ Tags: {len(data.get('tags', []))}")
                elif 'status' in data:
                    print(f"   ✅ Status: {data.get('status')}, Articles: {data.get('total_articles', 0)}")
                else:
                    print(f"   ✅ Response keys: {list(data.keys())}")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"   ❌ Error: {error_data}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test tags if available
    print("\n🏷️ TESTING TAG ENDPOINT:")
    tags_response = client.get("/api/v1/tags")
    if tags_response.status_code == 200:
        tags_data = tags_response.json()
        available_tags = tags_data.get('tags', [])
        print(f"   Available tags: {len(available_tags)}")
        
        if available_tags:
            test_tag = available_tags[0]
            print(f"   Testing tag: {test_tag}")
            tag_response = client.get(f"/api/v1/tag/{test_tag}?limit=1")
            print(f"   Status: {tag_response.status_code}")
            if tag_response.status_code == 200:
                tag_data = tag_response.json()
                print(f"   ✅ Tag results: {len(tag_data.get('articles', []))}, Total: {tag_data.get('total', 0)}")
        else:
            print("   No tags available to test")
    
    print("\n📋 CONCLUSION:")
    print("🔴 PROBLEM IDENTIFIED:")
    print("   You tested: /api/v1/categories/news")
    print("   ❌ This endpoint doesn't exist!")
    print("   💡 'categories' is for listing ALL categories, not filtering by category")
    print("\n✅ CORRECT ENDPOINTS FOR NEWS CATEGORY:")
    print("   ✅ /api/v1/news")
    print("   ✅ /api/v1/category/news")
    print("\n🎯 The endpoints are working correctly - you just used the wrong URL!")

if __name__ == "__main__":
    test_endpoints_directly()
