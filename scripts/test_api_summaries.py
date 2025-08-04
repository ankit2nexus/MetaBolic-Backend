#!/usr/bin/env python3
"""
Test API response to check if summaries are being sent properly
"""

import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.utils import get_articles_paginated_optimized
import json

def test_api_summaries():
    """Test if API is returning summaries correctly"""
    
    print("🧪 Testing API Summary Response...")
    print("=" * 50)
    
    # Test getting articles
    result = get_articles_paginated_optimized(page=1, limit=5)
    
    print(f"📊 API Response Stats:")
    print(f"Total articles: {result['total']}")
    print(f"Returned articles: {len(result['articles'])}")
    print(f"Page: {result['page']}")
    print(f"Has summaries: {sum(1 for article in result['articles'] if article.get('summary'))}")
    
    print(f"\n📝 Sample Articles with Summary Status:")
    print("-" * 60)
    
    for i, article in enumerate(result['articles'], 1):
        summary = article.get('summary', '')
        has_summary = bool(summary and summary.strip())
        
        print(f"\n{i}. ID: {article.get('id')}")
        print(f"   Title: {article.get('title', '')[:60]}...")
        print(f"   Has Summary: {'✅ YES' if has_summary else '❌ NO'}")
        
        if has_summary:
            print(f"   Summary Length: {len(summary)} chars")
            print(f"   Summary Preview: {summary[:100]}...")
        else:
            print(f"   Summary Value: {repr(summary)}")
        
        print(f"   URL: {article.get('url', '')[:60]}...")
        print("-" * 40)
    
    # Test JSON serialization
    print(f"\n🔄 Testing JSON Serialization:")
    try:
        json_response = json.dumps(result, default=str, indent=2)
        print("✅ JSON serialization successful")
        
        # Check if summaries are in the JSON
        summary_count = json_response.count('"summary":')
        print(f"📊 Found {summary_count} summary fields in JSON")
        
        # Check for null summaries
        null_summary_count = json_response.count('"summary": null')
        print(f"❌ Found {null_summary_count} null summary fields")
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    test_api_summaries()
