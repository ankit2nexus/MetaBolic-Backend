#!/usr/bin/env python3
"""
Test the improved summary and tags generation
"""

import sys
from pathlib import Path
import sqlite3
import json

# Add the app directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "app"))

# Import utils to test the improved functionality
from app.utils import get_articles_paginated_optimized

def test_improvements():
    print("=== TESTING IMPROVED SUMMARIES AND TAGS ===")
    
    # Get some articles to test the improvements
    result = get_articles_paginated_optimized(
        page=1,
        limit=10,
        search_query="",
        category="",
        tag=""
    )
    
    print(f"\nTesting with {len(result['articles'])} articles:")
    
    for i, article in enumerate(result['articles'], 1):
        print(f"\n{i}. {article['title'][:60]}...")
        print(f"   Source: {article['source']}")
        print(f"   Summary: {article['summary'][:150]}...")
        print(f"   Tags: {article['tags']}")
        print(f"   Category: {article['category']}")
        
        # Check if improvements were applied
        summary = article['summary']
        if any(phrase in summary.lower() for phrase in ['latest insights', 'important developments', 'new findings', 'stay informed']):
            print("   ✅ Enhanced summary generated!")
        elif 'health article summary' in summary.lower():
            print("   ⚠️  Still using old fallback")
        else:
            print("   ℹ️  Original summary retained")

if __name__ == "__main__":
    test_improvements()
