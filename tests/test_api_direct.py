#!/usr/bin/env python3
"""
Test the main.py endpoints directly using FastAPI TestClient
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("=== Testing API Endpoints ===\n")
    
    # Test 1: Health endpoint
    print("1. Testing /api/v1/health")
    response = client.get("/api/v1/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Database status: {data.get('database_status')}")
        print(f"   📊 Total articles: {data.get('total_articles')}")
    print()
    
    # Test 2: News category
    print("2. Testing /api/v1/category/news")
    response = client.get("/api/v1/category/news?limit=3")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total articles: {data.get('total')}")
        print(f"   📄 Returned: {len(data.get('articles', []))}")
        if data.get('articles'):
            sample = data['articles'][0]
            print(f"   📰 Sample: {sample.get('title', 'N/A')[:60]}...")
            print(f"   🏷️ Tags: {sample.get('tags', [])}")
    print()
    
    # Test 3: News subcategories (tags)
    subcategories = ["policy and regulation", "govt schemes", "international"]
    
    for subcategory in subcategories:
        print(f"3. Testing /api/v1/tag/{subcategory}")
        response = client.get(f"/api/v1/tag/{subcategory}?limit=2")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total articles: {data.get('total')}")
            print(f"   📄 Returned: {len(data.get('articles', []))}")
            if data.get('articles'):
                sample = data['articles'][0]
                print(f"   📰 Sample: {sample.get('title', 'N/A')[:60]}...")
                print(f"   🏷️ Tags: {sample.get('tags', [])}")
        else:
            print(f"   ❌ Error: {response.text}")
        print()
    
    # Test 4: Get all tags
    print("4. Testing /api/v1/tags")
    response = client.get("/api/v1/tags")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total tags: {data.get('total_tags')}")
        tags = data.get('tags', [])
        news_tags = [tag for tag in tags if any(word in tag.lower() for word in ['news', 'policy', 'govt', 'international', 'latest'])]
        print(f"   📰 News-related tags: {news_tags}")
    print()
    
    # Test 5: Categories endpoint
    print("5. Testing /api/v1/categories")
    response = client.get("/api/v1/categories")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Total categories: {data.get('total_categories')}")
        categories = data.get('categories', [])
        news_category = next((cat for cat in categories if cat['name'] == 'news'), None)
        if news_category:
            print(f"   📰 News category articles: {news_category.get('article_count')}")
            print(f"   🏷️ News subcategories: {news_category.get('subcategories', [])}")

if __name__ == "__main__":
    test_endpoints()
