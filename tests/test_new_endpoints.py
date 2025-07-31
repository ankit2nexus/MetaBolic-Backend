#!/usr/bin/env python3
"""
Test script for the new simplified endpoints (without 'articles' in URLs)
"""

import requests
import time

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing New Simplified Endpoints (no 'articles' in URLs)")
    print("=" * 60)
    
    # Test new endpoints
    endpoints_to_test = [
        ("/api/v1/", "Main articles endpoint"),
        ("/api/v1/latest", "Latest articles"),
        ("/api/v1/search?q=health", "Search articles"),
        ("/api/v1/diseases", "Articles by category"),
        ("/api/v1/health", "Health check"),
        ("/api/v1/categories", "Get categories"),
        ("/api/v1/stats", "Get statistics"),
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            print(f"\n📍 Testing: {description}")
            print(f"   URL: {endpoint}")
            
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'articles' in data:
                    print(f"   ✅ Success: {len(data['articles'])} articles returned")
                    print(f"   📊 Total: {data.get('total', 'N/A')}")
                elif 'status' in data:
                    print(f"   ✅ Success: {data['status']}")
                elif 'categories' in data:
                    print(f"   ✅ Success: {len(data['categories'])} categories")
                else:
                    print(f"   ✅ Success: Response received")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🔄 Testing Redirects from Old Endpoints")
    print("=" * 50)
    
    # Test redirects
    redirect_tests = [
        ("/articles/", "Old articles endpoint"),
        ("/api/v1/articles/", "Old API articles endpoint"),
        ("/api/v1/articles/latest", "Old API latest endpoint"),
        ("/api/v1/articles/search", "Old API search endpoint"),
        ("/artciles/", "Common typo"),
    ]
    
    for endpoint, description in redirect_tests:
        try:
            print(f"\n🔀 Testing redirect: {description}")
            print(f"   URL: {endpoint}")
            
            response = requests.get(f"{base_url}{endpoint}", timeout=10, allow_redirects=False)
            
            if response.status_code in [301, 302]:
                location = response.headers.get('Location', 'No location header')
                print(f"   ✅ Redirect: {response.status_code} → {location}")
                
                # Test the redirect destination
                if location.startswith('/'):
                    final_response = requests.get(f"{base_url}{location}", timeout=10)
                    if final_response.status_code == 200:
                        print(f"   ✅ Destination working: {final_response.status_code}")
                    else:
                        print(f"   ⚠️ Destination issues: {final_response.status_code}")
            else:
                print(f"   ❌ No redirect: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Make sure the server is running first:")
    print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\nWaiting 3 seconds...")
    time.sleep(3)
    test_endpoints()
