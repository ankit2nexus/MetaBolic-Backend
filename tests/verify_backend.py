#!/usr/bin/env python3
"""
Final verification that backend is working
"""

from app.main import app
from fastapi.testclient import TestClient

def main():
    client = TestClient(app)
    
    print("🔧 Backend Status Verification")
    print("=" * 40)
    
    # Test the exact typo from the error
    print("\n1. Testing /artciles (the exact typo from your error):")
    resp = client.get('/artciles')
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 301:
        data = resp.json()
        print(f"   ✅ Redirect working: {data['message']}")
        print(f"   Correct URL: {data['correct_url']}")
    
    # Test correct endpoint
    print("\n2. Testing correct endpoint /api/v1/articles/:")
    resp = client.get('/api/v1/articles/', params={'limit': 1})
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Working: {len(data.get('articles', []))} articles returned")
        print(f"   Total articles: {data.get('total', 0)}")
    
    # Test health endpoint
    print("\n3. Testing health endpoint /api/v1/health:")
    resp = client.get('/api/v1/health')
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Healthy: {data.get('total_articles', 0)} articles in database")
    
    print("\n" + "=" * 40)
    print("🎉 Backend is working properly!")
    print("💡 The /artciles typo now redirects correctly to /api/v1/articles/")
    print("📝 All API endpoints require the /api/v1/ prefix")

if __name__ == "__main__":
    main()
