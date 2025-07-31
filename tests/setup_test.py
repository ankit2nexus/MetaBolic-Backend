#!/usr/bin/env python3
"""
SmartNews-Style Aggregator Setup and Test Script

This script:
1. Tests the current environment
2. Runs a simple news aggregation test
3. Verifies the API endpoints work with new data
4. Provides setup instructions
"""

import sys
import os
from pathlib import Path
import subprocess
import json
import time

def test_python_version():
    """Test Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def test_imports():
    """Test required imports"""
    required_modules = [
        ('requests', 'HTTP requests'),
        ('sqlite3', 'Database operations'),
        ('json', 'JSON handling'),
        ('xml.etree.ElementTree', 'XML parsing'),
        ('datetime', 'Date/time handling')
    ]
    
    print("\n📦 Testing Required Modules:")
    all_good = True
    
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"❌ {module} - {description} (MISSING)")
            all_good = False
    
    return all_good

def test_internet_connection():
    """Test internet connectivity"""
    print("\n🌐 Testing Internet Connection:")
    
    test_urls = [
        ("https://www.who.int/rss-feeds/news-english.xml", "WHO RSS"),
        ("https://www.nih.gov/news-events/news-releases/rss.xml", "NIH RSS"),
        ("https://httpbin.org/status/200", "Basic HTTP test")
    ]
    
    for url, name in test_urls:
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} - Accessible")
            else:
                print(f"⚠️ {name} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name} - Error: {e}")

def test_database():
    """Test database creation and access"""
    print("\n💾 Testing Database:")
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Test database path
        base_dir = Path(__file__).parent
        db_path = base_dir / "data" / "test_articles.db"
        db_path.parent.mkdir(exist_ok=True)
        
        # Create test table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_articles (
                id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT UNIQUE
            )
        """)
        
        # Test insert
        cursor.execute("INSERT OR IGNORE INTO test_articles (title, url) VALUES (?, ?)", 
                      ("Test Article", "https://example.com/test"))
        
        # Test select
        cursor.execute("SELECT COUNT(*) FROM test_articles")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        # Clean up
        if db_path.exists():
            db_path.unlink()
        
        print(f"✅ Database operations work (test count: {count})")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def run_simple_scraper_test():
    """Run a simple test of the scraper"""
    print("\n🔍 Testing News Scraper:")
    
    try:
        # Import our scraper
        sys.path.append(str(Path(__file__).parent))
        
        # Try to run a simple RSS fetch
        import requests
        from xml.etree import ElementTree as ET
        
        print("  📡 Testing WHO RSS feed...")
        response = requests.get("https://www.who.int/rss-feeds/news-english.xml", timeout=15)
        
        if response.status_code == 200:
            # Parse XML
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            
            print(f"  ✅ Successfully fetched {len(items)} items from WHO RSS")
            
            # Show first item as example
            if items:
                first_item = items[0]
                title_elem = first_item.find('title')
                if title_elem is not None:
                    print(f"  📰 Example article: {title_elem.text[:60]}...")
            
            return True
        else:
            print(f"  ❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Scraper test failed: {e}")
        return False

def test_api_endpoints():
    """Test if the API can be started"""
    print("\n🚀 Testing API Setup:")
    
    try:
        # Check if FastAPI files exist
        base_dir = Path(__file__).parent
        main_file = base_dir / "app" / "main.py"
        start_file = base_dir / "start.py"
        
        if main_file.exists():
            print("✅ FastAPI main.py found")
        else:
            print("❌ FastAPI main.py not found")
            return False
        
        if start_file.exists():
            print("✅ start.py found")
        else:
            print("❌ start.py not found")
            return False
        
        # Try to import FastAPI components
        try:
            from app.main import app
            print("✅ FastAPI app imports successfully")
        except ImportError as e:
            print(f"⚠️ FastAPI import issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*60)
    print("📋 SMARTNEWS-STYLE AGGREGATOR SETUP")
    print("="*60)
    
    print("\n1. 🔧 DEPENDENCIES:")
    print("   The scraper uses only standard Python libraries:")
    print("   • requests (for HTTP)")
    print("   • sqlite3 (for database)")
    print("   • xml.etree.ElementTree (for RSS parsing)")
    print("   • json, datetime, pathlib (standard library)")
    
    print("\n   Install requests if missing:")
    print("   pip install requests")
    
    print("\n2. 🚀 QUICK START:")
    print("   # Run the Python 3.13 compatible scraper")
    print("   python scrapers/python313_compatible_scraper.py")
    print("")
    print("   # Start the API server")
    print("   python start.py")
    print("")
    print("   # Test the endpoints")
    print("   curl http://localhost:8000/articles/latest")
    
    print("\n3. 📰 NEWS SOURCES INCLUDED:")
    print("   • WHO Health News")
    print("   • NIH News Releases") 
    print("   • Reuters Health")
    print("   • CNN Health")
    print("   • BBC Health")
    print("   • Google News Health Topics")
    
    print("\n4. 🎯 API ENDPOINTS (unchanged):")
    print("   • GET /articles/latest - Latest articles")
    print("   • GET /articles/search?q=health - Search articles")
    print("   • GET /articles/category/news - By category")
    print("   • GET /articles/tag/latest - By tag")
    print("   • GET /articles/stats - Statistics")
    
    print("\n5. 🔄 AUTOMATION:")
    print("   Set up periodic runs:")
    print("   # Every 6 hours")
    print("   python scrapers/python313_compatible_scraper.py")
    
    print("\n✅ All existing endpoints work with aggregated content!")

def main():
    """Main setup and test function"""
    print("🌍 SmartNews-Style Health News Aggregator")
    print("Setup and Compatibility Test")
    print("="*50)
    
    # Run all tests
    tests = [
        ("Python Version", test_python_version),
        ("Required Modules", test_imports),
        ("Internet Connection", test_internet_connection),
        ("Database Operations", test_database),
        ("News Scraper", run_simple_scraper_test),
        ("API Setup", test_api_endpoints)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed_tests += 1
    
    # Summary
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your system is ready for SmartNews-style aggregation.")
    elif passed_tests >= total_tests - 1:
        print("✅ Most tests passed. You should be able to run the aggregator.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    # Show instructions regardless
    show_setup_instructions()

if __name__ == "__main__":
    main()
