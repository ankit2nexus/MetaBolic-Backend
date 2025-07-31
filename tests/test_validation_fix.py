#!/usr/bin/env python3
"""
Test script to verify Pydantic validation fixes
"""
import sqlite3
import json
from typing import Optional
from pydantic import BaseModel, ValidationError

# Define the updated ArticleSchema
class ArticleSchema(BaseModel):
    id: int
    title: str
    url: str
    source: Optional[str] = None  # Made optional to handle None values
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: list = []
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    created_at: Optional[str] = None

def test_articles_with_none_values():
    """Test articles that previously caused validation errors"""
    
    # Connect to database
    conn = sqlite3.connect('data/articles.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get articles from category 'news' page 2 (where errors occurred)
    offset = 10  # page 2 with 10 items per page
    cursor.execute("""
        SELECT * FROM articles 
        WHERE LOWER(category) LIKE ? OR JSON_EXTRACT(category, '$[*]') LIKE ?
        ORDER BY created_at DESC
        LIMIT 10 OFFSET ?
    """, ('%news%', '%news%', offset))
    
    rows = cursor.fetchall()
    
    print(f"Testing {len(rows)} articles from news category (page 2)...")
    
    validation_errors = []
    successful_validations = 0
    
    for row in rows:
        article = dict(row)
        
        # Clean data - handle None/NULL values for required and optional fields
        if article.get('source') is None or article.get('source') == '':
            article['source'] = None  # Now optional
        if article.get('url') is None or article.get('url') == '':
            article['url'] = ''  # Required field, use empty string as fallback
        if article.get('title') is None or article.get('title') == '':
            article['title'] = 'Untitled'  # Required field
        
        # Clean optional fields - convert empty strings to None
        for optional_field in ['summary', 'content', 'category', 'subcategory', 'image_url', 'author']:
            if article.get(optional_field) == '' or article.get(optional_field) == 'NULL':
                article[optional_field] = None
        
        # Ensure tags is always a list
        if not article.get('tags') or article.get('tags') in ['', 'NULL', None]:
            article['tags'] = []
        
        try:
            # Try to validate with Pydantic
            validated_article = ArticleSchema(**article)
            successful_validations += 1
            print(f"✅ Article {article['id']}: {article['title'][:50]}...")
            
        except ValidationError as e:
            validation_errors.append({
                'id': article.get('id'),
                'title': article.get('title', 'Unknown'),
                'error': str(e)
            })
            print(f"❌ Article {article['id']}: Validation failed")
            print(f"   Error: {e}")
            print(f"   Raw data: {article}")
    
    conn.close()
    
    print(f"\n📊 Results:")
    print(f"✅ Successful validations: {successful_validations}")
    print(f"❌ Validation errors: {len(validation_errors)}")
    
    if validation_errors:
        print(f"\n❌ Failed articles:")
        for error in validation_errors:
            print(f"   ID {error['id']}: {error['title'][:50]}...")
            print(f"   Error: {error['error']}")
    
    return len(validation_errors) == 0

if __name__ == "__main__":
    print("🧪 Testing Pydantic validation fixes...")
    success = test_articles_with_none_values()
    
    if success:
        print("\n🎉 All validation tests passed! The fix is working.")
    else:
        print("\n⚠️ Some validation errors still exist. Need further investigation.")
