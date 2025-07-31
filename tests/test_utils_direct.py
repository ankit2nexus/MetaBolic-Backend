#!/usr/bin/env python3
"""
Test the updated utility functions directly
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from utils import get_articles_paginated_optimized, get_all_tags

def test_functions():
    print("=== Testing Updated Functions ===\n")
    
    # Test 1: Get news category articles
    print("1. Testing news category")
    result = get_articles_paginated_optimized(page=1, limit=5, category="news")
    print(f"   📊 Total articles: {result['total']}")
    print(f"   📄 Returned: {len(result['articles'])}")
    
    if result['articles']:
        for i, article in enumerate(result['articles'][:2]):
            print(f"   📰 Article {i+1}: {article.get('title', 'N/A')[:60]}...")
            print(f"   🏷️ Tags: {article.get('tags', [])}")
            print(f"   📂 Category: {article.get('category', 'N/A')}")
    print()
    
    # Test 2: Test specific tag searches
    test_tags = ["policy and regulation", "govt schemes", "international"]
    
    for tag in test_tags:
        print(f"2. Testing tag: '{tag}'")
        result = get_articles_paginated_optimized(page=1, limit=3, tag=tag)
        print(f"   📊 Total articles: {result['total']}")
        print(f"   📄 Returned: {len(result['articles'])}")
        
        if result['articles']:
            sample_article = result['articles'][0]
            print(f"   📰 Sample: {sample_article.get('title', 'N/A')[:60]}...")
            print(f"   🏷️ Tags: {sample_article.get('tags', [])}")
        print()
    
    # Test 3: Get all tags
    print("3. Testing get_all_tags()")
    all_tags = get_all_tags()
    print(f"   🏷️ Total tags: {len(all_tags)}")
    
    # Find news-related tags
    news_tags = [tag for tag in all_tags if any(word in tag.lower() for word in ['news', 'policy', 'govt', 'international', 'latest', 'regulation'])]
    print(f"   📰 News-related tags: {news_tags}")

if __name__ == "__main__":
    test_functions()
