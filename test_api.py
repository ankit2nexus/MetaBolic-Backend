#!/usr/bin/env python3
"""
Test script for Metabolical Backend API
Tests all major endpoints to ensure deployment is working
"""

import requests
import json
import sys
from datetime import datetime

def test_api(base_url):
    """Test the API endpoints"""
    print(f"🧪 Testing API at: {base_url}")
    print("=" * 50)
    
    tests = [
        ("Health Check", "/api/v1/health", "GET"),
        ("Root Endpoint", "/", "GET"),
        ("API Root", "/api/v1/", "GET"),
        ("Categories", "/api/v1/categories", "GET"),
        ("Tags", "/api/v1/tags", "GET"),
        ("Stats", "/api/v1/stats", "GET"),
        ("Search", "/api/v1/search?q=diabetes&limit=5", "GET"),
        ("Category Articles", "/api/v1/category/diseases?limit=5", "GET"),
        ("Tag Articles", "/api/v1/tag/prevention?limit=5", "GET"),
    ]
    
    results = []
    
    for test_name, endpoint, method in tests:
        try:
            url = f"{base_url}{endpoint}"
            print(f"🔍 Testing {test_name}: {method} {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {test_name}: SUCCESS (200)")
                try:
                    data = response.json()
                    if endpoint == "/api/v1/search" and "articles" in data:
                        print(f"   Found {len(data['articles'])} articles")
                    elif endpoint.startswith("/api/v1/category") and "articles" in data:
                        print(f"   Found {len(data['articles'])} articles")
                    elif endpoint.startswith("/api/v1/tag") and "articles" in data:
                        print(f"   Found {len(data['articles'])} articles")
                    elif endpoint == "/api/v1/categories" and "categories" in data:
                        print(f"   Found {len(data['categories'])} categories")
                    elif endpoint == "/api/v1/tags" and "tags" in data:
                        print(f"   Found {len(data['tags'])} tags")
                except:
                    pass
                results.append((test_name, "PASS", response.status_code))
            else:
                print(f"❌ {test_name}: FAILED ({response.status_code})")
                print(f"   Response: {response.text[:100]}...")
                results.append((test_name, "FAIL", response.status_code))
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, "ERROR", str(e)))
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, status, _ in results if status == "PASS")
    total = len(results)
    
    for test_name, status, code in results:
        status_emoji = "✅" if status == "PASS" else "❌"
        print(f"{status_emoji} {test_name}: {status} ({code})")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
        return False

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Metabolical Backend API")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the API (default: http://localhost:8000)")
    args = parser.parse_args()
    
    print("🚀 METABOLICAL BACKEND API TESTER")
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print()
    
    success = test_api(args.url)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
