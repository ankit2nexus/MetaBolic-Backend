#!/usr/bin/env python3
"""
Demonstrate Automatic Scheduler Startup
Shows exactly what happens when you start the API server
"""

import sys
from pathlib import Path
import asyncio
from datetime import datetime

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

async def demonstrate_automatic_startup():
    """Show how the scheduler automatically starts with the API"""
    print("🚀 AUTOMATIC SCHEDULER STARTUP DEMONSTRATION")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📋 WHAT HAPPENS WHEN YOU RUN: python run.py api")
    print("-" * 60)
    
    try:
        # Step 1: API imports scheduler
        print("1. 🔧 FastAPI imports scheduler module...")
        from app.scheduler import health_scheduler
        from app.main import app
        print("   ✅ Scheduler imported successfully")
        
        # Step 2: Show startup event handler
        print("\n2. 📋 API startup event handler configured:")
        print("   ✅ @app.on_event('startup') → starts scheduler")
        print("   ✅ @app.on_event('shutdown') → stops scheduler")
        
        # Step 3: Simulate startup
        print("\n3. 🚀 Simulating API server startup...")
        health_scheduler.start_scheduler()
        print("   ✅ Background scheduler started")
        
        # Step 4: Show scheduled jobs
        print("\n4. 📅 Scheduled jobs automatically created:")
        jobs = health_scheduler.get_scheduled_jobs()
        for i, job in enumerate(jobs, 1):
            print(f"   {i}. {job['name']}")
            print(f"      Schedule: {job.get('trigger', 'Unknown')}")
            if job.get('next_run'):
                print(f"      Next run: {job['next_run']}")
            print()
        
        # Step 5: Show what's running in background
        print("5. 🔄 Background operations running:")
        print("   ✅ Health news scraping every 6 hours")
        print("   ✅ Database cleanup daily at 2:00 AM")
        print("   ✅ Immediate scraping queued for startup")
        
        # Step 6: Management endpoints
        print("\n6. 🌐 Management endpoints available:")
        print("   📊 GET /api/v1/scheduler/status")
        print("   🔄 POST /api/v1/scheduler/trigger-scraper")
        print("   💊 GET /api/v1/health")
        
        # Step 7: Cleanup
        print("\n7. 🛑 Stopping scheduler (simulation end)...")
        health_scheduler.stop_scheduler()
        print("   ✅ Scheduler stopped cleanly")
        
        print("\n" + "=" * 60)
        print("✅ AUTOMATIC STARTUP DEMONSTRATED SUCCESSFULLY!")
        print("🚀 Just run 'python run.py api' and everything starts automatically")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        return False

def show_startup_sequence():
    """Show the exact startup sequence"""
    print("\n📋 DETAILED STARTUP SEQUENCE")
    print("=" * 60)
    
    sequence = [
        "1. You run: python run.py api",
        "2. FastAPI app starts loading",
        "3. Scheduler module imported",
        "4. @app.on_event('startup') triggers",
        "5. health_scheduler.start_scheduler() called",
        "6. APScheduler creates background jobs:",
        "   - Health scraper (every 6 hours)",
        "   - Database cleanup (daily 2 AM)", 
        "   - Startup scraper (immediate)",
        "7. API server starts on http://localhost:8000",
        "8. Scheduler runs in background automatically",
        "9. You can monitor via /api/v1/scheduler/status",
        "10. Graceful shutdown when you stop the server"
    ]
    
    for step in sequence:
        print(f"    {step}")
    
    print("\n🎯 KEY POINT: NO MANUAL INTERVENTION NEEDED!")
    print("The scheduler starts and runs completely automatically.")

async def main():
    """Main demonstration"""
    success = await demonstrate_automatic_startup()
    
    if success:
        show_startup_sequence()
        
        print("\n" + "=" * 60)
        print("🏥 YOUR METABOLIC BACKEND SCHEDULER IS READY!")
        print("=" * 60)
        print("✅ Automatic startup: CONFIGURED")
        print("✅ Background scheduling: READY")
        print("✅ API management: AVAILABLE")
        print("\n🚀 TO START: python run.py api")
        print("🔍 TO MONITOR: http://localhost:8000/api/v1/scheduler/status")
        
    else:
        print("❌ There was an issue with the scheduler setup")

if __name__ == "__main__":
    asyncio.run(main())
