#!/usr/bin/env python3
"""
Update existing articles with poor summaries
"""

import sqlite3
from pathlib import Path
import re

DB_PATH = Path('data/articles.db')

def enhance_existing_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=== ENHANCING EXISTING SUMMARIES ===")
    
    # Find articles with poor summaries
    cursor.execute('''
        SELECT id, title, summary, source, categories
        FROM articles 
        WHERE (
            summary IS NULL OR 
            summary = "" OR
            LENGTH(summary) < 20 OR
            summary LIKE "%Health article summary%" OR
            summary = "recent developments" OR
            summary = "And more health news stories this Thursday"
        )
    ''')
    
    articles_to_update = cursor.fetchall()
    print(f"Found {len(articles_to_update)} articles with poor summaries to enhance...")
    
    updated_count = 0
    
    for article_id, title, old_summary, source, categories in articles_to_update:
        # Generate enhanced summary
        enhanced_summary = generate_enhanced_summary(title, source, categories)
        
        # Generate enhanced tags
        enhanced_tags = generate_enhanced_tags(title, categories)
        
        # Update the article
        cursor.execute('''
            UPDATE articles 
            SET summary = ?, tags = ?
            WHERE id = ?
        ''', (enhanced_summary, enhanced_tags, article_id))
        
        updated_count += 1
        
        if updated_count <= 5:  # Show first 5 examples
            print(f"\n✅ Updated Article {article_id}:")
            print(f"   Title: {title[:60]}...")
            print(f"   Old: {old_summary[:50]}..." if old_summary else "   Old: (empty)")
            print(f"   New: {enhanced_summary[:80]}...")
            print(f"   Tags: {enhanced_tags}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Successfully enhanced {updated_count} article summaries!")

def generate_enhanced_summary(title, source, categories):
    """Generate an enhanced summary based on title content"""
    title_lower = title.lower()
    
    # Health condition specific summaries
    if 'diabetes' in title_lower:
        return f"Latest insights on diabetes management and treatment options from {source}."
    elif any(word in title_lower for word in ['heart', 'cardiovascular', 'cardiac']):
        return f"Important developments in heart health and cardiovascular care from {source}."
    elif any(word in title_lower for word in ['nutrition', 'diet', 'food']):
        return f"New findings on nutrition and dietary recommendations from {source}."
    elif 'mental health' in title_lower or any(word in title_lower for word in ['depression', 'anxiety', 'stress']):
        return f"Mental health insights and wellness strategies from {source}."
    elif any(word in title_lower for word in ['covid', 'coronavirus', 'pandemic']):
        return f"COVID-19 updates and public health information from {source}."
    elif any(word in title_lower for word in ['cancer', 'tumor', 'oncology']):
        return f"Important cancer research and treatment updates from {source}."
    elif any(word in title_lower for word in ['vaccine', 'vaccination', 'immunization']):
        return f"Vaccination and immunization news and recommendations from {source}."
    elif any(word in title_lower for word in ['study', 'research', 'trial']):
        return f"New medical research findings and healthcare study results from {source}."
    elif any(word in title_lower for word in ['treatment', 'therapy']):
        return f"Medical treatment advances and therapeutic breakthroughs from {source}."
    elif any(word in title_lower for word in ['pregnancy', 'maternal', 'birth']):
        return f"Maternal health and pregnancy care information from {source}."
    elif any(word in title_lower for word in ['children', 'pediatric', 'kids']):
        return f"Pediatric health news and child wellness information from {source}."
    else:
        # Generic but informative fallback
        if len(title) > 80:
            return f"{title[:77]}... - Read more about this health development from {source}."
        else:
            return f"Important health news: {title}. Stay informed with the latest from {source}."

def generate_enhanced_tags(title, categories):
    """Generate meaningful tags based on title content"""
    title_lower = title.lower()
    generated_tags = []
    
    # Health condition tags
    if any(word in title_lower for word in ['diabetes', 'diabetic']):
        generated_tags.extend(['diabetes', 'blood sugar', 'endocrinology'])
    if any(word in title_lower for word in ['heart', 'cardiac', 'cardiovascular']):
        generated_tags.extend(['heart health', 'cardiovascular', 'cardiology'])
    if any(word in title_lower for word in ['mental health', 'depression', 'anxiety']):
        generated_tags.extend(['mental health', 'wellness', 'psychology'])
    if any(word in title_lower for word in ['nutrition', 'diet', 'food']):
        generated_tags.extend(['nutrition', 'diet', 'healthy eating'])
    if any(word in title_lower for word in ['cancer', 'tumor', 'oncology']):
        generated_tags.extend(['cancer', 'oncology', 'treatment'])
    if any(word in title_lower for word in ['covid', 'coronavirus', 'pandemic']):
        generated_tags.extend(['covid-19', 'pandemic', 'public health'])
    if any(word in title_lower for word in ['vaccine', 'vaccination', 'immunization']):
        generated_tags.extend(['vaccination', 'immunization', 'prevention'])
    
    # Research and news type tags
    if any(word in title_lower for word in ['study', 'research', 'trial']):
        generated_tags.append('medical research')
    if any(word in title_lower for word in ['breakthrough', 'discovery']):
        generated_tags.append('breakthrough research')
    if any(word in title_lower for word in ['treatment', 'therapy']):
        generated_tags.append('treatment')
    if any(word in title_lower for word in ['prevention', 'preventive']):
        generated_tags.append('prevention')
    
    # Default tags if none found
    if not generated_tags:
        generated_tags = ['health news', 'wellness']
    
    return ', '.join(list(set(generated_tags)))

if __name__ == "__main__":
    enhance_existing_summaries()
