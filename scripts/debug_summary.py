#!/usr/bin/env python3
"""
Debug summary issue by examining the exact database query and response
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "articles.db"

def debug_summary_query():
    """Debug the exact query used by the API"""
    
    print("🔍 Debugging Summary Query...")
    print("=" * 50)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # This is the exact query used by the API
        query = """
            SELECT id, title, summary, NULL as content, url, source, date, categories as category, 
                   NULL as subcategory, tags, NULL as image_url, authors as author 
            FROM articles 
            ORDER BY date DESC, id DESC 
            LIMIT 3
        """
        
        print(f"📝 Executing query:")
        print(query)
        print()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"📊 Query returned {len(rows)} rows")
        print()
        
        # Process each row like the API does
        articles = []
        for i, row in enumerate(rows, 1):
            article = dict(row)
            
            print(f"🔍 Article {i} (ID: {article['id']}):")
            print(f"   Title: {article['title'][:60]}...")
            
            # Check summary field
            raw_summary = article.get('summary')
            print(f"   Raw Summary Type: {type(raw_summary)}")
            print(f"   Raw Summary Value: {repr(raw_summary)}")
            
            # Apply the same processing as the API
            if not raw_summary or raw_summary in ['', 'NULL', None]:
                title = article.get('title', 'Health Article')
                if len(title) > 100:
                    processed_summary = title[:97] + "..."
                else:
                    processed_summary = f"{title} - Health article summary."
                print(f"   ⚠️  Generated fallback summary")
            else:
                # Clean summary text
                processed_summary = raw_summary
                if processed_summary:
                    import re
                    processed_summary = re.sub(r'\(Source:.*?\)', '', processed_summary)
                    processed_summary = re.sub(r'Source:.*?(\.|$)', '', processed_summary)
                    processed_summary = re.sub(r'\(From:.*?\)', '', processed_summary)
                    processed_summary = re.sub(r'From:.*?(\.|$)', '', processed_summary)
                    processed_summary = processed_summary.strip()
                print(f"   ✅ Using original summary")
            
            article['summary'] = processed_summary
            
            print(f"   Final Summary Length: {len(processed_summary)}")
            print(f"   Final Summary Preview: {processed_summary[:100]}...")
            print()
            
            # Clean other fields as API does
            if article.get('source') is None or article.get('source') == '':
                article['source'] = "Health Information Source"
            
            if article.get('title') is None or article.get('title') == '':
                article['title'] = 'Untitled'
            
            # Parse tags
            if article.get('tags'):
                try:
                    if isinstance(article['tags'], str):
                        article['tags'] = json.loads(article['tags'])
                        article['tags'] = [tag.replace("_", " ") if isinstance(tag, str) else tag for tag in article['tags']]
                except (json.JSONDecodeError, TypeError):
                    article['tags'] = []
            else:
                article['tags'] = []
            
            # Parse date
            if article.get('date'):
                try:
                    article['date'] = datetime.fromisoformat(article['date'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    article['date'] = datetime.now()
            
            articles.append(article)
        
        # Test JSON serialization
        print("🔄 Testing JSON Serialization:")
        try:
            response_data = {
                "articles": articles,
                "total": len(articles),
                "page": 1,
                "limit": 3,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
            
            json_str = json.dumps(response_data, default=str, indent=2)
            print("✅ JSON serialization successful")
            print(f"📊 JSON length: {len(json_str)} characters")
            
            # Show the JSON structure for the first article
            if articles:
                first_article_json = json.dumps(articles[0], default=str, indent=2)
                print(f"\n📝 First article JSON structure:")
                print(first_article_json)
            
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")

if __name__ == "__main__":
    debug_summary_query()
