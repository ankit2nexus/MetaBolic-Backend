#!/usr/bin/env python3
"""
Test API endpoints to ensure summaries are being sent correctly
"""

import requests
import json
import time

def test_api_endpoints():
    base_url = "http://localhost:8000/api/v1"
    
    endpoints_to_test = [
        "/",
        "/latest?limit=5",
        "/search?q=health&limit=3",
        "/news?limit=3",
        "/diseases?limit=3"
    ]
    
    print("=== Testing API Endpoints ===")
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\nTesting: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Articles returned: {len(articles)}")
                
                # Check if summaries are present
                articles_with_summary = sum(1 for article in articles if article.get('summary'))
                print(f"📝 Articles with summary: {articles_with_summary}/{len(articles)}")
                
                # Show sample summary
                if articles and articles[0].get('summary'):
                    sample_summary = articles[0]['summary'][:80] + "..." if len(articles[0]['summary']) > 80 else articles[0]['summary']
                    print(f"📄 Sample summary: {sample_summary}")
                
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - server not running?")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Starting API endpoint tests...")
    print("Make sure the server is running with: python start.py")
    test_api_endpoints()
