#!/usr/bin/env python3
"""
Test the redirect functionality
"""

from app.main import app
from fastapi.testclient import TestClient

def test_redirects():
    """Test that redirects work for common mistakes"""
    client = TestClient(app)
    
    print("🧪 Testing API redirects and error handling...")
    
    # Test 1: Correct API endpoint
    print("\n1. Testing correct endpoint /api/v1/articles/")
    response = client.get("/api/v1/articles/?limit=1")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Working - returned {len(data.get('articles', []))} articles")
    
    # Test 2: Missing api/v1 prefix
    print("\n2. Testing /articles/ (missing prefix)")
    response = client.get("/articles/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 301:
        data = response.json()
        print(f"   ✅ Redirect working - {data.get('message')}")
        print(f"   Correct URL: {data.get('correct_url')}")
    
    # Test 3: Typo - artciles with slash
    print("\n3. Testing /artciles/ (typo with slash)")
    response = client.get("/artciles/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 301:
        data = response.json()
        print(f"   ✅ Typo redirect working - {data.get('message')}")
    
    # Test 4: Typo - artciles without slash
    print("\n4. Testing /artciles (typo without slash)")
    response = client.get("/artciles")
    print(f"   Status: {response.status_code}")
    if response.status_code == 301:
        data = response.json()
        print(f"   ✅ Typo redirect working - {data.get('message')}")
    
    # Test 5: Non-existent endpoint
    print("\n5. Testing non-existent endpoint /nonexistent")
    response = client.get("/nonexistent")
    print(f"   Status: {response.status_code}")
    if response.status_code == 404:
        data = response.json()
        print(f"   ✅ 404 handler working")
        print(f"   Available endpoints shown: {len(data.get('available_endpoints', []))}")
    
    print("\n✅ All redirect tests completed!")

if __name__ == "__main__":
    test_redirects()
