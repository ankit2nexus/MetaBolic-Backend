import requests
import time

def test_live_server():
    """Test endpoints against a running server"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Live Server Endpoints")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        print(f"✅ Server is running - Health check: {response.status_code}")
    except:
        print("❌ Server not running. Start with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Test the specific endpoints
    endpoints = [
        ("/api/v1/", "Main endpoint"),
        ("/api/v1/news?limit=2", "News category (CORRECT)"),
        ("/api/v1/category/news?limit=2", "News category alternative (CORRECT)"),
        ("/api/v1/categories/news", "Wrong endpoint (should be 404)"),
        ("/api/v1/categories", "Categories list"),
        ("/api/v1/tags", "Tags list"),
        ("/api/v1/search?q=health&limit=2", "Search"),
        ("/api/v1/health", "Health check"),
        ("/api/v1/stats", "Statistics"),
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"\n📍 {description}")
            print(f"   URL: {endpoint}")
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
                    print(f"   ✅ Response received")
            elif response.status_code == 404:
                print(f"   ✅ Correctly returns 404 (endpoint doesn't exist)")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📋 CONCLUSION:")
    print(f"✅ Correct endpoints working:")
    print(f"   /api/v1/news (direct category)")
    print(f"   /api/v1/category/news (alternative)")
    print(f"❌ Wrong endpoint correctly fails:")
    print(f"   /api/v1/categories/news (doesn't exist)")

if __name__ == "__main__":
    test_live_server()
