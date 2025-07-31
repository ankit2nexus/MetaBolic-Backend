#!/usr/bin/env python3
"""
Test the updated 'latest' tag functionality
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.utils import get_articles_paginated_optimized

def test_latest_tag():
    print("=== Testing 'latest' tag with related terms ===")
    
    result = get_articles_paginated_optimized(page=1, limit=10, tag='latest')
    print(f"Latest tag result: {result['total']} articles found")
    
    if result['articles']:
        print(f"Returned {len(result['articles'])} articles:")
        for i, article in enumerate(result['articles'][:5]):
            print(f"{i+1}. {article['title'][:70]}...")
            print(f"   Tags: {article['tags']}")
            print(f"   Date: {article['date']}")
            print()
    else:
        print("No articles found for 'latest' tag")

if __name__ == "__main__":
    test_latest_tag()
