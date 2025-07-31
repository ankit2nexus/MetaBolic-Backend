#!/usr/bin/env python3
"""
Comprehensive endpoint testing script
Tests all endpoints with proper URLs and identifies issues
"""

import requests
import time
import json

def test_all_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ HEALTH CHECK")
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Database: {data.get('database_status')}")
            print(f"   📊 Total articles: {data.get('total_articles')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("   🚫 Make sure server is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: Main articles endpoint
    print("\n2️⃣ MAIN ARTICLES ENDPOINT")
    try:
        response = requests.get(f"{base_url}/api/v1/?limit=3", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Articles returned: {len(data.get('articles', []))}")
            print(f"   📊 Total: {data.get('total')}")
            print(f"   📄 Pages: {data.get('total_pages')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Categories list
    print("\n3️⃣ CATEGORIES LIST")
    available_categories = []
    try:
        response = requests.get(f"{base_url}/api/v1/categories", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            print(f"   ✅ Categories found: {len(categories)}")
            for cat in categories:
                print(f"      📂 {cat['name']}: {cat['article_count']} articles")
                available_categories.append(cat['name'])
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Category filtering (correct endpoints)
    print("\n4️⃣ CATEGORY FILTERING TESTS")
    
    test_categories = ['news', 'diseases', 'food']
    for category in test_categories:
        print(f"\n   Testing category: {category}")
        
        # Test direct category endpoint /api/v1/{category}
        try:
            response = requests.get(f"{base_url}/api/v1/{category}?limit=2", timeout=10)
            print(f"   📍 /api/v1/{category} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
            else:
                print(f"      ❌ Error: {response.text[:100]}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        # Test alternative category endpoint /api/v1/category/{category}
        try:
            response = requests.get(f"{base_url}/api/v1/category/{category}?limit=2", timeout=10)
            print(f"   📍 /api/v1/category/{category} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
            else:
                print(f"      ❌ Error: {response.text[:100]}")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Test 5: Wrong endpoint (the one user tested)
    print("\n5️⃣ TESTING INCORRECT ENDPOINT")
    try:
        response = requests.get(f"{base_url}/api/v1/categories/news", timeout=10)
        print(f"   📍 /api/v1/categories/news - Status: {response.status_code}")
        print(f"   ⚠️ This endpoint doesn't exist - 'categories' is for listing all categories")
        print(f"   💡 Correct endpoints for news category:")
        print(f"      ✅ /api/v1/news")
        print(f"      ✅ /api/v1/category/news")
        if response.status_code == 404:
            print(f"   ✅ Correctly returns 404 for non-existent endpoint")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Search endpoint
    print("\n6️⃣ SEARCH ENDPOINT")
    try:
        response = requests.get(f"{base_url}/api/v1/search?q=health&limit=3", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search results: {len(data.get('articles', []))}")
            print(f"   📊 Total: {data.get('total')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 7: Tags
    print("\n7️⃣ TAGS ENDPOINTS")
    
    # Get available tags
    available_tags = []
    try:
        response = requests.get(f"{base_url}/api/v1/tags", timeout=10)
        print(f"   📍 /api/v1/tags - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            available_tags = data.get('tags', [])
            print(f"   ✅ Tags found: {len(available_tags)}")
            if available_tags:
                print(f"   📋 Sample tags: {available_tags[:5]}")
            else:
                print(f"   ⚠️ No tags found in database")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test tag filtering
    if available_tags:
        test_tag = available_tags[0]
        try:
            response = requests.get(f"{base_url}/api/v1/tag/{test_tag}?limit=2", timeout=10)
            print(f"   📍 /api/v1/tag/{test_tag} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Tag results: {len(data.get('articles', []))}, Total: {data.get('total')}")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 8: Latest articles
    print("\n8️⃣ LATEST ARTICLES")
    try:
        response = requests.get(f"{base_url}/api/v1/latest?limit=3", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Latest articles: {len(data.get('articles', []))}")
            print(f"   📊 Total: {data.get('total')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 9: Statistics
    print("\n9️⃣ STATISTICS")
    try:
        response = requests.get(f"{base_url}/api/v1/stats", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stats retrieved")
            print(f"   📊 Available keys: {list(data.keys())}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📋 SUMMARY")
    print("=" * 40)
    print("🔍 ENDPOINT MAPPING:")
    print("   ✅ Main articles: /api/v1/")
    print("   ✅ Latest: /api/v1/latest")
    print("   ✅ Search: /api/v1/search?q={query}")
    print("   ✅ Category (direct): /api/v1/{category}")
    print("   ✅ Category (alt): /api/v1/category/{category}")
    print("   ✅ Tag filtering: /api/v1/tag/{tag}")
    print("   ✅ List categories: /api/v1/categories")
    print("   ✅ List tags: /api/v1/tags")
    print("   ✅ Health: /api/v1/health")
    print("   ✅ Stats: /api/v1/stats")
    print("\n❌ INCORRECT ENDPOINT:")
    print("   ❌ /api/v1/categories/news ← This doesn't exist!")
    print("   ✅ Use: /api/v1/news OR /api/v1/category/news")

if __name__ == "__main__":
    print("🚀 Starting comprehensive endpoint tests...")
    print("📝 Make sure server is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\nWaiting 3 seconds...")
    time.sleep(3)
    test_all_endpoints()
