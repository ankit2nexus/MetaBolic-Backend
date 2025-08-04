#!/usr/bin/env python3
"""
Test actual API endpoints to verify summary data
"""

import sys
from pathlib import Path
import json

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app

def test_api_endpoints():
    """Test actual API endpoints"""
    
    client = TestClient(app)
    
    print("🧪 Testing API Endpoints for Summary Data...")
    print("=" * 60)
    
    # Test search endpoint
    print("\n1️⃣ Testing /api/v1/search endpoint:")
    response = client.get("/api/v1/search?q=health&limit=3")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total articles: {data.get('total', 0)}")
        print(f"📋 Returned articles: {len(articles)}")
        
        for i, article in enumerate(articles, 1):
            summary = article.get('summary')
            print(f"\n   Article {i}:")
            print(f"   - ID: {article.get('id')}")
            print(f"   - Title: {article.get('title', '')[:50]}...")
            print(f"   - Summary: {'✅ Present' if summary else '❌ Missing'}")
            if summary:
                print(f"   - Summary Preview: {summary[:80]}...")
            print(f"   - URL: {article.get('url', '')[:50]}...")
    else:
        print(f"❌ Search endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test category endpoint
    print("\n2️⃣ Testing /api/v1/category/diseases endpoint:")
    response = client.get("/api/v1/category/diseases?limit=2")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total articles: {data.get('total', 0)}")
        print(f"📋 Returned articles: {len(articles)}")
        
        for i, article in enumerate(articles, 1):
            summary = article.get('summary')
            print(f"\n   Article {i}:")
            print(f"   - ID: {article.get('id')}")
            print(f"   - Title: {article.get('title', '')[:50]}...")
            print(f"   - Summary: {'✅ Present' if summary else '❌ Missing'}")
            if summary:
                print(f"   - Summary Length: {len(summary)} chars")
                print(f"   - Summary Preview: {summary[:80]}...")
    else:
        print(f"❌ Category endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test health endpoint
    print("\n3️⃣ Testing /api/v1/health endpoint:")
    response = client.get("/api/v1/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed")
        print(f"📊 Total articles in DB: {data.get('total_articles')}")
    else:
        print(f"❌ Health check failed: {response.status_code}")

def test_raw_response():
    """Test raw response structure"""
    
    client = TestClient(app)
    
    print("\n🔍 Testing Raw Response Structure:")
    print("-" * 40)
    
    response = client.get("/api/v1/search?q=diabetes&limit=1")
    
    if response.status_code == 200:
        # Get raw response text
        raw_text = response.text
        print(f"✅ Raw response received ({len(raw_text)} chars)")
        
        # Parse and pretty print
        try:
            data = response.json()
            pretty_json = json.dumps(data, indent=2, default=str)
            print("\n📝 Pretty JSON Response:")
            print(pretty_json[:1000] + "..." if len(pretty_json) > 1000 else pretty_json)
            
            # Specifically check summary field
            if data.get('articles'):
                first_article = data['articles'][0]
                summary_field = first_article.get('summary')
                
                print(f"\n🔍 Summary Field Analysis:")
                print(f"   Type: {type(summary_field)}")
                print(f"   Value: {repr(summary_field)}")
                print(f"   Length: {len(str(summary_field)) if summary_field else 0}")
                
        except Exception as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Raw response: {raw_text[:500]}...")

if __name__ == "__main__":
    test_api_endpoints()
    test_raw_response()
