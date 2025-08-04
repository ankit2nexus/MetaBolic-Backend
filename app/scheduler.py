#!/usr/bin/env python3
"""
Background Scheduler for METABOLIC_BACKEND
Handles automatic scraping tasks using APScheduler
"""

import logging
import asyncio
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import sys

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup logging
logger = logging.getLogger(__name__)

class HealthNewsScheduler:
    """Background scheduler for health news scraping tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    async def scrape_health_news(self):
        """Background task to scrape health news"""
        try:
            logger.info("🕷️ Starting scheduled health news scraping...")
            
            # Try the main scraper first
            try:
                from app.scrapers.master_health_scraper import MasterHealthScraper
                scraper = MasterHealthScraper()
                result = scraper.run_scraping()
                
                logger.info(f"✅ Scheduled scraping completed: {result['total_saved']} articles saved")
                return result
                
            except ImportError as e:
                if "cgi" in str(e):
                    logger.warning("⚠️ Python 3.13 compatibility issue detected, using fallback scraper")
                    
                    # Use the compatible scraper as fallback
                    from app.scrapers.simple_compatible_scraper import SimpleHealthScraper
                    scraper = SimpleHealthScraper()
                    result = scraper.run_scraping()
                    
                    logger.info(f"✅ Fallback scraping completed: {result['total_saved']} articles saved")
                    return result
                else:
                    raise e
            
        except Exception as e:
            logger.error(f"❌ Scheduled scraping failed: {e}")
            return {"error": str(e), "total_saved": 0}
    
    async def cleanup_database(self):
        """Background task to clean up problematic URLs"""
        try:
            logger.info("🧹 Starting scheduled database cleanup...")
            
            import subprocess
            import sys
            
            # Run cleanup script
            result = subprocess.run([
                sys.executable, 
                str(BASE_DIR / "scripts" / "cleanup_urls.py")
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Database cleanup completed successfully")
            else:
                logger.error(f"❌ Database cleanup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Database cleanup error: {e}")
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            return
        
        try:
            # Schedule health news scraping every 6 hours
            self.scheduler.add_job(
                self.scrape_health_news,
                trigger=IntervalTrigger(hours=6),
                id='health_news_scraper',
                name='Health News Scraper',
                replace_existing=True,
                max_instances=1
            )
            
            # Schedule database cleanup daily at 2 AM
            self.scheduler.add_job(
                self.cleanup_database,
                trigger=CronTrigger(hour=2, minute=0),
                id='database_cleanup',
                name='Database Cleanup',
                replace_existing=True,
                max_instances=1
            )
            
            # Schedule an immediate run on startup (after 2 minutes)
            self.scheduler.add_job(
                self.scrape_health_news,
                trigger='date',
                run_date=datetime.now().replace(second=0, microsecond=0),
                id='startup_scraper',
                name='Startup Health News Scraper',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info("🚀 Background scheduler started successfully")
            logger.info("📅 Health news scraping: Every 6 hours")
            logger.info("🧹 Database cleanup: Daily at 2:00 AM")
            logger.info("⚡ Immediate scraping: Starting in 2 minutes")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("🛑 Background scheduler stopped")
    
    def get_scheduled_jobs(self):
        """Get information about scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
    
    async def run_scraper_now(self):
        """Manually trigger scraper immediately"""
        logger.info("🚀 Manual scraper trigger requested")
        return await self.scrape_health_news()

# Global scheduler instance
health_scheduler = HealthNewsScheduler()
