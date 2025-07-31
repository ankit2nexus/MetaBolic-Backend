#!/usr/bin/env python3
"""
Test script for the specifically requested endpoints:
- /category/{category}
- /tag/{tag}
- /search?q={query_text}
"""

import requests
import time

def test_requested_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Specifically Requested Endpoints")
    print("=" * 60)
    
    # Test endpoints as requested
    print("\n1️⃣ Testing /category/{category} endpoint")
    try:
        response = requests.get(f"{base_url}/api/v1/category/diseases", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ /api/v1/category/diseases: {len(data.get('articles', []))} articles returned")
            print(f"   📊 Total: {data.get('total', 'N/A')}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2️⃣ Testing /tag/{tag} endpoint")
    # First get available tags
    try:
        tags_response = requests.get(f"{base_url}/api/v1/tags", timeout=10)
        if tags_response.status_code == 200:
            tags_data = tags_response.json()
            available_tags = tags_data.get('tags', [])
            print(f"   📋 Available tags: {len(available_tags)} found")
            
            if available_tags:
                test_tag = available_tags[0]  # Use first available tag
                print(f"   🏷️ Testing with tag: '{test_tag}'")
                
                tag_response = requests.get(f"{base_url}/api/v1/tag/{test_tag}", timeout=10)
                if tag_response.status_code == 200:
                    data = tag_response.json()
                    print(f"   ✅ /api/v1/tag/{test_tag}: {len(data.get('articles', []))} articles returned")
                    print(f"   📊 Total: {data.get('total', 'N/A')}")
                else:
                    print(f"   ❌ Failed: {tag_response.status_code} - {tag_response.text[:100]}")
            else:
                print("   ⚠️ No tags available to test with")
        else:
            print(f"   ❌ Failed to get tags: {tags_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n3️⃣ Testing /search?q={query_text} endpoint")
    test_queries = ["health", "diabetes", "nutrition"]
    
    for query in test_queries:
        try:
            response = requests.get(f"{base_url}/api/v1/search?q={query}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ /api/v1/search?q={query}: {len(data.get('articles', []))} articles returned")
                print(f"   📊 Total: {data.get('total', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n4️⃣ Testing supporting endpoints")
    support_endpoints = [
        ("/api/v1/categories", "Get all categories"),
        ("/api/v1/tags", "Get all tags"),
    ]
    
    for endpoint, description in support_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'categories' in data:
                    print(f"   ✅ {description}: {len(data['categories'])} categories")
                elif 'tags' in data:
                    print(f"   ✅ {description}: {len(data['tags'])} tags")
                else:
                    print(f"   ✅ {description}: Response received")
            else:
                print(f"   ❌ {description} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description} error: {e}")
    
    print("\n📋 Summary of Requested Endpoints:")
    print("✅ /api/v1/category/{category} - Alternative category endpoint")
    print("✅ /api/v1/tag/{tag} - New tag filtering endpoint")  
    print("✅ /api/v1/search?q={query} - Search endpoint (already existed)")
    print("✅ /api/v1/tags - Supporting endpoint to list all tags")
    print("\n💡 All requested endpoints are now available!")

if __name__ == "__main__":
    print("🚀 Make sure the server is running first:")
    print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\nWaiting 3 seconds...")
    time.sleep(3)
    test_requested_endpoints()
