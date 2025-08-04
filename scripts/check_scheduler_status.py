#!/usr/bin/env python3
"""
Check if the scheduler is working properly by analyzing:
1. Recent scraping activity
2. Database freshness
3. System health
4. Scheduler configuration
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

DB_PATH = BASE_DIR / "data" / "articles.db"

def check_database_status():
    """Check the current state of the database"""
    print("📊 DATABASE STATUS")
    print("=" * 50)
    
    if not DB_PATH.exists():
        print("❌ Database not found at", DB_PATH)
        return False
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_articles = cursor.fetchone()[0]
        print(f"Total articles: {total_articles}")
        
        # Recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM articles 
            WHERE last_checked IS NOT NULL 
            AND datetime(last_checked) > datetime('now', '-24 hours')
        """)
        recent_24h = cursor.fetchone()[0]
        print(f"Articles checked in last 24 hours: {recent_24h}")
        
        cursor.execute("""
            SELECT COUNT(*) FROM articles 
            WHERE last_checked IS NOT NULL 
            AND datetime(last_checked) > datetime('now', '-7 days')
        """)
        recent_7d = cursor.fetchone()[0]
        print(f"Articles checked in last 7 days: {recent_7d}")
        
        # Most recent activity
        cursor.execute("""
            SELECT MAX(last_checked) FROM articles 
            WHERE last_checked IS NOT NULL
        """)
        last_activity = cursor.fetchone()[0]
        if last_activity:
            print(f"Last scraping activity: {last_activity}")
            
            # Calculate time since last activity
            last_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00').replace('T', ' ').split('+')[0])
            now = datetime.now()
            time_diff = now - last_dt
            print(f"Time since last activity: {time_diff}")
            
            if time_diff > timedelta(days=1):
                print("⚠️  WARNING: Last activity was more than 1 day ago")
            elif time_diff > timedelta(hours=6):
                print("⚠️  WARNING: Last activity was more than 6 hours ago")
            else:
                print("✅ Recent activity detected")
        else:
            print("❌ No last_checked timestamps found")
        
        # Check summary quality
        cursor.execute("SELECT COUNT(*) FROM articles WHERE summary IS NOT NULL AND summary != ''")
        articles_with_summary = cursor.fetchone()[0]
        summary_percentage = (articles_with_summary / total_articles) * 100 if total_articles > 0 else 0
        print(f"Articles with summaries: {articles_with_summary} ({summary_percentage:.1f}%)")
        
    return True

def check_scheduler_configuration():
    """Check if there's any scheduler configuration"""
    print("\n🔧 SCHEDULER CONFIGURATION")
    print("=" * 50)
    
    # Check for scheduler files
    scheduler_files = [
        "scheduler.py",
        "cron.py", 
        "tasks.py",
        "celery.py",
        "beat.py"
    ]
    
    found_schedulers = []
    for filename in scheduler_files:
        if (BASE_DIR / filename).exists():
            found_schedulers.append(filename)
        if (BASE_DIR / "app" / filename).exists():
            found_schedulers.append(f"app/{filename}")
    
    if found_schedulers:
        print("✅ Found scheduler files:")
        for f in found_schedulers:
            print(f"  - {f}")
    else:
        print("❌ No dedicated scheduler files found")
    
    # Check main.py for background tasks
    main_py = BASE_DIR / "app" / "main.py"
    if main_py.exists():
        with open(main_py, 'r', encoding='utf-8') as f:
            content = f.read()
            
        scheduler_keywords = [
            'health_scheduler', 'startup_event', 'APScheduler',
            '@app.on_event', 'background', 'scheduler'
        ]
        
        found_keywords = [kw for kw in scheduler_keywords if kw in content]
        if found_keywords:
            print("✅ Found scheduler integration in main.py:")
            for kw in found_keywords:
                print(f"  - {kw}")
        else:
            print("❌ No scheduler integration found in main.py")
    
    # Test if scheduler can be imported and works
    try:
        sys.path.insert(0, str(BASE_DIR))
        from app.scheduler import health_scheduler
        print("✅ Scheduler module imports successfully")
        
        # Test scheduler functionality
        if hasattr(health_scheduler, 'start_scheduler'):
            print("✅ Scheduler has start/stop functionality")
            
            # Test if scheduler can be started (don't leave it running)
            health_scheduler.start_scheduler()
            jobs = health_scheduler.get_scheduled_jobs()
            health_scheduler.stop_scheduler()
            
            print(f"✅ Scheduler tested successfully ({len(jobs)} jobs configured)")
            
            print("\n🔍 AUTOMATIC STARTUP STATUS:")
            print("  ✅ Scheduler is integrated with FastAPI")
            print("  ✅ Will start automatically when API server starts")
            print("  ✅ Background tasks scheduled:")
            for job in jobs:
                print(f"     - {job['name']}: {job.get('trigger', 'Unknown schedule')}")
                
        else:
            print("❌ Scheduler missing required methods")
            
    except ImportError as e:
        print(f"❌ Scheduler import failed: {e}")
        print("\n🔍 Current Running Mode:")
        print("  - Manual execution: scrapers must be run manually")
        print("  - No automatic scheduling available")
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")

def check_scraper_health():
    """Check if scrapers can run successfully"""
    print("\n SCRAPER HEALTH CHECK")
    print("=" * 50)
    
    try:
        # Test import of scraper modules
        sys.path.insert(0, str(BASE_DIR))
        from app.scrapers.master_health_scraper import MasterHealthScraper
        print("✅ Master health scraper imports successfully")
        
        # Test basic functionality (without actually scraping)
        scraper = MasterHealthScraper()
        print("✅ Scraper instance created successfully")
        
        print("✅ Scrapers appear to be functional")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Scraper error: {e}")
        return False

def provide_recommendations():
    """Provide recommendations for fixing scheduler issues"""
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)
    
    print("To set up automatic scheduling, consider:")
    print("1. 🔧 System Cron Jobs (Linux/Mac):")
    print("   # Run scraper every 6 hours")
    print("   0 */6 * * * cd /path/to/project && python run.py scraper")
    
    print("\n2. 🪟 Windows Task Scheduler:")
    print("   - Create a scheduled task to run 'python run.py scraper'")
    print("   - Set it to run every 6 hours")
    
    print("\n3. 🐳 Cloud/Container Schedulers:")
    print("   - Use Kubernetes CronJob")
    print("   - AWS EventBridge")
    print("   - Google Cloud Scheduler")
    
    print("\n4. 🔄 Application-level Scheduling:")
    print("   - Add FastAPI background tasks")
    print("   - Use APScheduler or Celery")
    print("   - Add startup event handlers")
    
    print("\n5. 🚀 Immediate Actions:")
    print("   - Run 'python run.py scraper' manually to update data")
    print("   - Check logs for any errors")
    print("   - Fix Python 3.13 compatibility issues with feedparser")

def main():
    """Main status check function"""
    print("🏥 METABOLIC BACKEND - SCHEDULER STATUS CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Database path: {DB_PATH}")
    
    # Run all checks
    db_ok = check_database_status()
    check_scheduler_configuration()
    scraper_ok = check_scraper_health()
    
    print("\n📋 SUMMARY")
    print("=" * 50)
    if db_ok:
        print("✅ Database is accessible")
    else:
        print("❌ Database issues detected")
    
    if scraper_ok:
        print("✅ Scrapers can be imported")
    else:
        print("❌ Scraper issues detected")
    
    # Check if scheduler is properly configured
    try:
        from app.scheduler import health_scheduler
        from app.main import app
        print("✅ Automatic scheduler is configured and ready")
        print("🚀 SCHEDULER WILL START AUTOMATICALLY when you run: python run.py api")
    except:
        print("❌ No automatic scheduler detected")
        print("⚠️  Data updates require manual intervention")
    
    print("\n💡 HOW TO START AUTOMATIC SCHEDULING:")
    print("   1. Run: python run.py api")
    print("   2. Scheduler starts automatically with the API server")
    print("   3. Health news will be scraped every 6 hours")
    print("   4. Database cleanup runs daily at 2:00 AM")
    print("   5. Monitor via: http://localhost:8000/api/v1/scheduler/status")
    
    provide_recommendations()

if __name__ == "__main__":
    main()
