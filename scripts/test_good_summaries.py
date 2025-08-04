#!/usr/bin/env python3
"""
Test API with articles that should have good summaries
"""

import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.utils import get_articles_paginated_optimized
import json

def test_api_with_good_summaries():
    """Test API with articles that should have good summaries"""
    
    print("🧪 Testing API with Different Parameters...")
    print("=" * 60)
    
    # Test 1: Get articles from page 10 (older articles more likely to have summaries)
    print("1️⃣ Testing older articles (page 10):")
    result = get_articles_paginated_optimized(page=10, limit=3)
    
    print(f"📊 Page 10 Results:")
    print(f"   Total articles: {result['total']}")
    print(f"   Returned: {len(result['articles'])}")
    
    for i, article in enumerate(result['articles'], 1):
        summary = article.get('summary', '')
        has_good_summary = bool(summary and len(summary) > 50)
        
        print(f"\n   Article {i}:")
        print(f"   - ID: {article.get('id')}")
        print(f"   - Title: {article.get('title', '')[:50]}...")
        print(f"   - Summary Quality: {'✅ GOOD' if has_good_summary else '❌ POOR/FALLBACK'}")
        print(f"   - Summary Length: {len(summary)} chars")
        if has_good_summary:
            print(f"   - Summary: {summary[:100]}...")
    
    # Test 2: Search for specific terms (might return articles with better summaries)
    print(f"\n2️⃣ Testing search for 'diabetes':")
    result = get_articles_paginated_optimized(page=1, limit=3, search_query="diabetes")
    
    print(f"📊 Search Results:")
    print(f"   Total articles: {result['total']}")
    print(f"   Returned: {len(result['articles'])}")
    
    for i, article in enumerate(result['articles'], 1):
        summary = article.get('summary', '')
        has_good_summary = bool(summary and len(summary) > 50)
        
        print(f"\n   Article {i}:")
        print(f"   - ID: {article.get('id')}")
        print(f"   - Title: {article.get('title', '')[:50]}...")
        print(f"   - Summary Quality: {'✅ GOOD' if has_good_summary else '❌ POOR/FALLBACK'}")
        print(f"   - Summary Length: {len(summary)} chars")
        if has_good_summary:
            print(f"   - Summary: {summary[:100]}...")
    
    # Test 3: Get articles by category
    print(f"\n3️⃣ Testing category 'diseases':")
    result = get_articles_paginated_optimized(page=1, limit=3, category="diseases")
    
    print(f"📊 Category Results:")
    print(f"   Total articles: {result['total']}")
    print(f"   Returned: {len(result['articles'])}")
    
    for i, article in enumerate(result['articles'], 1):
        summary = article.get('summary', '')
        has_good_summary = bool(summary and len(summary) > 50)
        
        print(f"\n   Article {i}:")
        print(f"   - ID: {article.get('id')}")
        print(f"   - Title: {article.get('title', '')[:50]}...")
        print(f"   - Summary Quality: {'✅ GOOD' if has_good_summary else '❌ POOR/FALLBACK'}")
        print(f"   - Summary Length: {len(summary)} chars")
        if has_good_summary:
            print(f"   - Summary: {summary[:100]}...")

if __name__ == "__main__":
    test_api_with_good_summaries()
