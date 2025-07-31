#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

# Import and test the utils function
from app.utils import get_articles_paginated_optimized

def test_api_response():
    print('Testing API response...')
    result = get_articles_paginated_optimized(page=1, limit=3)

    print(f'Total articles: {result["total"]}')
    print(f'Articles returned: {len(result["articles"])}')

    for i, article in enumerate(result['articles']):
        print(f'\nArticle {i+1}:')
        print(f'  ID: {article["id"]}')
        print(f'  Title: {article["title"][:60]}...')
        summary = article["summary"]
        if summary:
            print(f'  Summary: {summary[:80]}...')
        else:
            print('  Summary: None')
        print(f'  Has Summary: {bool(summary)}')

if __name__ == "__main__":
    test_api_response()
