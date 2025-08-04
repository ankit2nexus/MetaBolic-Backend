#!/usr/bin/env python3
"""
Verify URL validation improvements
"""

import sys
from pathlib import Path
import requests

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import the utilities
from app.utils import is_valid_article_url
from app.url_validator import URLValidator

def test_url_validation():
    """Test the URL validation functions"""
    
    print("🧪 Testing URL Validation Functions")
    print("=" * 60)
    
    # Test cases
    test_urls = [
        # Valid URLs
        ("https://www.reuters.com/health/some-article", True, "Valid Reuters URL"),
        ("https://www.cnn.com/health/news", True, "Valid CNN URL"),
        ("https://www.who.int/news/item/2024-01-01-health-update", True, "Valid WHO URL"),
        
        # Invalid URLs
        ("https://www.example.com/health-news", False, "Example.com URL"),
        ("https://domain.com/article", False, "Domain.com URL"),
        ("javascript:alert('test')", False, "JavaScript URL"),
        ("mailto:test@example.com", False, "Mailto URL"),
        ("https://news.google.com/rss/articles/CBMi123", False, "Google News RSS URL"),
        ("", False, "Empty URL"),
        ("http://localhost/article", False, "Localhost URL"),
        ("https://test.com/health", False, "Test.com URL"),
    ]
    
    # Test the utility function
    print("\n🔧 Testing is_valid_article_url() function:")
    print("-" * 50)
    
    passed = 0
    total = len(test_urls)
    
    for url, expected, description in test_urls:
        result = is_valid_article_url(url)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} | {description}")
        print(f"    URL: {url}")
        print(f"    Expected: {expected}, Got: {result}")
        print()
        
        if result == expected:
            passed += 1
    
    print(f"📊 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    # Test the URLValidator class
    print("\n🛡️ Testing URLValidator class:")
    print("-" * 50)
    
    validator = URLValidator()
    
    test_articles = [
        {"url": "https://www.reuters.com/health/article", "title": "Test Article"},
        {"url": "https://www.example.com/health", "title": "Bad Article"},
        {"url": "https://news.google.com/rss/articles/123", "title": "Google RSS Article"},
    ]
    
    for article in test_articles:
        is_valid, info = validator.validate_article_url(article)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"{status} | {article['title']}")
        print(f"    URL: {article['url']}")
        print(f"    Info: {info}")
        print()

def test_api_response():
    """Test if API now filters out bad URLs"""
    
    print("\n🌐 Testing API Response (if server is running):")
    print("-" * 50)
    
    try:
        # Test the search endpoint
        response = requests.get("http://localhost:8000/api/v1/search?q=health&limit=5", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"✅ API Response successful")
            print(f"📊 Returned {len(articles)} articles")
            
            # Check if any articles have problematic URLs
            problematic_count = 0
            for article in articles:
                url = article.get('url', '')
                if not is_valid_article_url(url):
                    problematic_count += 1
                    print(f"⚠️  Found problematic URL: {url}")
            
            if problematic_count == 0:
                print("✅ No problematic URLs found in API response")
            else:
                print(f"❌ Found {problematic_count} problematic URLs in API response")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running - skipping API test")
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    test_url_validation()
    test_api_response()
