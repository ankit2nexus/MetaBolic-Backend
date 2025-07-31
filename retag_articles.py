#!/usr/bin/env python3
"""
Script to add proper tags to existing sleep health and sexual wellness articles
"""
import sqlite3
import json

def retag_articles():
    conn = sqlite3.connect('data/articles.db')
    cursor = conn.cursor()
    
    print('🔧 RE-TAGGING ARTICLES FOR SLEEP HEALTH AND SEXUAL WELLNESS')
    print('=' * 60)
    
    # Sleep health keywords and their corresponding articles
    sleep_keywords = [
        'sleep', 'insomnia', 'sleep apnea', 'sleep disorder', 
        'sleep quality', 'sleep hygiene', 'sleeplessness', 'restless'
    ]
    
    # Sexual wellness keywords
    sexual_keywords = [
        'sexual', 'sexuality', 'reproductive', 'fertility', 
        'contraception', 'erectile', 'libido', 'intimate'
    ]
    
    # Function to update tags for articles
    def add_tag_to_articles(keywords, new_tag):
        updated_count = 0
        for keyword in keywords:
            # Find articles that match the keyword but don't already have the tag
            cursor.execute('''
                SELECT id, tags FROM articles 
                WHERE (LOWER(title) LIKE ? OR LOWER(summary) LIKE ?)
                AND (tags IS NULL OR tags NOT LIKE ?)
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{new_tag}%'))
            
            articles = cursor.fetchall()
            
            for article_id, current_tags in articles:
                # Parse current tags
                if current_tags:
                    try:
                        tags_list = json.loads(current_tags)
                    except:
                        tags_list = []
                else:
                    tags_list = []
                
                # Add new tag if not already present
                if new_tag not in tags_list:
                    tags_list.append(new_tag)
                    updated_tags = json.dumps(tags_list)
                    
                    # Update the article
                    cursor.execute('UPDATE articles SET tags = ? WHERE id = ?', 
                                   (updated_tags, article_id))
                    updated_count += 1
        
        return updated_count
    
    # Update sleep health articles
    print('🛌 Updating sleep health articles...')
    sleep_updated = add_tag_to_articles(sleep_keywords, 'sleep health')
    print(f'   ✅ Updated {sleep_updated} articles with "sleep health" tag')
    
    # Update sexual wellness articles
    print('💕 Updating sexual wellness articles...')
    sexual_updated = add_tag_to_articles(sexual_keywords, 'sexual wellness')
    print(f'   ✅ Updated {sexual_updated} articles with "sexual wellness" tag')
    
    # Commit changes
    conn.commit()
    
    # Verify the updates
    print('\n📊 VERIFICATION:')
    cursor.execute('SELECT COUNT(*) FROM articles WHERE tags LIKE ?', ('%sleep health%',))
    sleep_count = cursor.fetchone()[0]
    print(f'   Articles tagged with "sleep health": {sleep_count}')
    
    cursor.execute('SELECT COUNT(*) FROM articles WHERE tags LIKE ?', ('%sexual wellness%',))
    sexual_count = cursor.fetchone()[0]
    print(f'   Articles tagged with "sexual wellness": {sexual_count}')
    
    # Show sample articles
    print('\n📰 SAMPLE TAGGED ARTICLES:')
    cursor.execute('''
        SELECT title, tags FROM articles 
        WHERE tags LIKE "%sleep health%" OR tags LIKE "%sexual wellness%"
        LIMIT 5
    ''')
    samples = cursor.fetchall()
    
    for i, (title, tags) in enumerate(samples):
        print(f'   {i+1}. {title[:60]}...')
        print(f'      Tags: {tags}')
    
    conn.close()
    
    print(f'\n✅ TAGGING COMPLETE!')
    print(f'   Sleep health articles: {sleep_count}')
    print(f'   Sexual wellness articles: {sexual_count}')
    print(f'\n🎯 Test URLs now available:')
    print(f'   GET http://localhost:8000/api/v1/tag/sleep%20health')
    print(f'   GET http://localhost:8000/api/v1/tag/sexual%20wellness')

if __name__ == "__main__":
    retag_articles()
