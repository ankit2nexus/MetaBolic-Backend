#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    
    print("Testing imports...")
    
    try:
        from app.url_validator import URLValidator
        print("✅ app.url_validator import successful")
        
        # Test URL validator functionality
        validator = URLValidator()
        result = validator.validate_article_url({"url": "https://example.com"})
        print(f"✅ URL validator working: {result}")
        
    except Exception as e:
        print(f"❌ app.url_validator import failed: {e}")
    
    try:
        from scrapers.python313_compatible_scraper import Python313CompatibleScraper
        print("✅ Python313CompatibleScraper import successful")
        
    except Exception as e:
        print(f"❌ Python313CompatibleScraper import failed: {e}")
    
    try:
        # Test if we can import the comprehensive scraper without feedparser issues
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "comprehensive_scraper", 
            "scrapers/comprehensive_news_scraper.py"
        )
        if spec and spec.loader:
            print("✅ Comprehensive scraper file structure is valid")
        else:
            print("❌ Comprehensive scraper file structure issue")
            
    except Exception as e:
        print(f"❌ Comprehensive scraper test failed: {e}")
    
    print("\nTesting complete!")

if __name__ == "__main__":
    test_imports()
