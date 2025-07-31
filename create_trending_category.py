#!/usr/bin/env python3
"""
Script to create trending category with proper tagging
"""
import sqlite3
import json

def create_trending_category():
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()
    
    print('🔥 CREATING TRENDING CATEGORY')
    print('=' * 40)
    
    # Define trending keywords by subcategory
    trending_mapping = {
        'gut health': ['gut health', 'microbiome', 'probiotics', 'digestive'],
        'mental health': ['mental health', 'depression', 'anxiety', 'stress'],
        'hormones': ['hormones', 'testosterone', 'estrogen', 'thyroid'],
        'addiction': ['addiction', 'substance abuse', 'dependency'],
        'sleep health': ['sleep', 'insomnia', 'sleep apnea'],
        'sexual wellness': ['sexual', 'reproductive', 'fertility', 'libido']
    }
    
    trending_articles = 0
    
    for subcategory, keywords in trending_mapping.items():
        for keyword in keywords:
            # Find articles matching keywords
            cursor.execute('''
                SELECT id, categories, tags FROM articles 
                WHERE LOWER(title) LIKE ? OR LOWER(summary) LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%'))
            
            articles = cursor.fetchall()
            
            for article_id, current_categories, current_tags in articles:
                # Update categories to include trending
                try:
                    categories = json.loads(current_categories) if current_categories else []
                except:
                    categories = []
                
                if 'trending' not in categories:
                    categories.append('trending')
                    updated_categories = json.dumps(categories)
                    
                    # Update tags to include subcategory
                    try:
                        tags = json.loads(current_tags) if current_tags else []
                    except:
                        tags = []
                    
                    if subcategory not in tags:
                        tags.append(subcategory)
                    
                    updated_tags = json.dumps(tags)
                    
                    # Update the article
                    cursor.execute('''
                        UPDATE articles 
                        SET categories = ?, tags = ? 
                        WHERE id = ?
                    ''', (updated_categories, updated_tags, article_id))
                    
                    trending_articles += 1
    
    conn.commit()
    
    # Verify trending category
    cursor.execute('SELECT COUNT(*) FROM articles WHERE categories LIKE ?', ('%trending%',))
    trending_count = cursor.fetchone()[0]
    
    print(f'✅ Created trending category with {trending_count} articles')
    print(f'📊 Updated {trending_articles} article assignments')
    
    # Show breakdown by subcategory
    print('\n📋 Trending Subcategories:')
    for subcategory in trending_mapping.keys():
        cursor.execute('SELECT COUNT(*) FROM articles WHERE tags LIKE ?', (f'%{subcategory}%',))
        count = cursor.fetchone()[0]
        print(f'   {subcategory}: {count} articles')
    
    conn.close()
    
    print('\n🎯 Trending Category URLs:')
    print('   GET http://localhost:8000/api/v1/trending')
    print('   GET http://localhost:8000/api/v1/category/trending')

if __name__ == "__main__":
    create_trending_category()
