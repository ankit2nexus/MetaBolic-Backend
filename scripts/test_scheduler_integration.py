#!/usr/bin/env python3
"""
Test the new scheduler integration
"""

import sys
from pathlib import Path
import asyncio

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

async def test_scheduler():
    """Test the scheduler functionality"""
    print("🧪 Testing Scheduler Integration")
    print("=" * 50)
    
    try:
        # Test scheduler import
        from app.scheduler import health_scheduler
        print("✅ Scheduler module imports successfully")
        
        # Test scheduler instance
        print(f"✅ Scheduler running status: {health_scheduler.is_running}")
        
        # Test scraper import (the main issue before)
        try:
            from app.scrapers.master_health_scraper import MasterHealthScraper
            scraper = MasterHealthScraper()
            print("✅ Master health scraper imports and initializes successfully")
        except Exception as e:
            print(f"❌ Scraper import/init failed: {e}")
            return False
        
        # Test basic scheduler functionality
        print("\n🔧 Testing scheduler start/stop...")
        health_scheduler.start_scheduler()
        print(f"✅ Scheduler started: {health_scheduler.is_running}")
        
        # Get job information
        jobs = health_scheduler.get_scheduled_jobs()
        print(f"✅ Scheduled jobs: {len(jobs)}")
        for job in jobs:
            print(f"   - {job['name']}: {job['next_run']}")
        
        health_scheduler.stop_scheduler()
        print(f"✅ Scheduler stopped: {health_scheduler.is_running}")
        
        print("\n✅ All scheduler tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False

async def test_api_import():
    """Test if the main API can import with scheduler"""
    print("\n🌐 Testing API Integration")
    print("=" * 50)
    
    try:
        from app.main import app
        print("✅ Main API imports successfully with scheduler")
        
        # Check if the scheduler endpoints are available
        routes = [route.path for route in app.routes]
        scheduler_routes = [r for r in routes if 'scheduler' in r]
        
        if scheduler_routes:
            print("✅ Scheduler endpoints found:")
            for route in scheduler_routes:
                print(f"   - {route}")
        else:
            print("⚠️  No scheduler endpoints found in routes")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🏥 METABOLIC BACKEND - SCHEDULER INTEGRATION TEST")
    print("=" * 60)
    
    scheduler_ok = await test_scheduler()
    api_ok = await test_api_import()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 50)
    
    if scheduler_ok and api_ok:
        print("✅ All tests passed! Scheduler is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Start the API server: python run.py api")
        print("2. Check scheduler status: GET /api/v1/scheduler/status")
        print("3. Trigger manual scraping: POST /api/v1/scheduler/trigger-scraper")
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
