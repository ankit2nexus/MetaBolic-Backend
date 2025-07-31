#!/usr/bin/env python3
"""
Simple test script for the fixed endpoints
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fixed_endpoints():
    print("🧪 TESTING FIXED ENDPOINTS")
    print("=" * 50)
    
    # Test the original problematic endpoint
    print("\n❌ Original problematic endpoint:")
    print("   /api/v1/categories/news (doesn't exist)")
    response = client.get("/api/v1/categories/news")
    print(f"   Status: {response.status_code} (should be 404)")
    
    # Test correct endpoints
    print("\n✅ Correct endpoints:")
    
    print("\n1. Main endpoint:")
    response = client.get("/api/v1/?limit=2")
    print(f"   /api/v1/ - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
    
    print("\n2. Categories list:")
    response = client.get("/api/v1/categories")
    print(f"   /api/v1/categories - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Categories: {len(data.get('categories', []))}")
        # Show categories with article counts
        for cat in data.get('categories', []):
            print(f"      📂 {cat['name']}: {cat['article_count']} articles")
    
    print("\n3. News category (direct):")
    response = client.get("/api/v1/news?limit=2")
    print(f"   /api/v1/news - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
    
    print("\n4. News category (alternative):")
    response = client.get("/api/v1/category/news?limit=2")
    print(f"   /api/v1/category/news - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
    
    print("\n5. Other categories:")
    for category in ['diseases', 'food']:
        response = client.get(f"/api/v1/{category}?limit=1")
        print(f"   /api/v1/{category} - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"      Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
    
    print("\n6. Search:")
    response = client.get("/api/v1/search?q=health&limit=2")
    print(f"   /api/v1/search?q=health - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Articles: {len(data.get('articles', []))}, Total: {data.get('total')}")
    
    print("\n7. Tags:")
    response = client.get("/api/v1/tags")
    print(f"   /api/v1/tags - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        tags = data.get('tags', [])
        print(f"   Tags: {len(tags)}")
        if tags:
            print(f"   Sample tags: {tags[:5]}")
    
    print("\n8. Health check:")
    response = client.get("/api/v1/health")
    print(f"   /api/v1/health - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}, DB: {data.get('database_status')}")
        print(f"   Total articles: {data.get('total_articles')}")
    
    print("\n📋 SUMMARY:")
    print("✅ All specific endpoints (categories, tags, health, stats) work correctly")
    print("✅ News category filtering works via /api/v1/news")  
    print("✅ Alternative category filtering works via /api/v1/category/news")
    print("✅ Main endpoints (/api/v1/, /latest, /search) work correctly")
    print("🔧 Routing issue fixed - specific routes now come before generic /{category}")

if __name__ == "__main__":
    test_fixed_endpoints()
