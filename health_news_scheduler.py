#!/usr/bin/env python3
"""
Automated Health News Scheduler

This scheduler runs scrapers at optimal intervals to keep the database fresh
with new health articles while avoiding rate limiting.
"""

import schedule
import time
import logging
import threading
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "articles.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "db" / "articles.db"

class HealthNewsScheduler:
    """Automated scheduler for health news scraping"""
    
    def __init__(self):
        self.stats = {
            'scheduler_start_time': None,
            'total_runs': 0,
            'successful_runs': 0,
            'last_run_time': None,
            'last_run_status': None,
            'articles_collected_today': 0
        }
        
        self.scraper_configs = {
            'quick': {
                'script': 'python313_compatible_scraper.py',
                'description': 'Quick RSS feeds (WHO, NIH, Reuters, CNN, BBC)',
                'interval_hours': 2,
                'max_runtime_minutes': 10
            },
            'comprehensive': {
                'script': 'ultra_comprehensive_scraper.py',
                'description': 'Comprehensive multi-source scraping',
                'interval_hours': 6,
                'max_runtime_minutes': 30
            },
            'social': {
                'script': 'social_media_scraper.py',
                'description': 'Social media and community sources',
                'interval_hours': 8,
                'max_runtime_minutes': 15
            },
            'cleanup': {
                'script': 'enhanced_url_validator.py',
                'description': 'URL validation and cleanup',
                'interval_hours': 24,
                'max_runtime_minutes': 20
            }
        }
        
        self.is_running = False
        self.should_stop = False
    
    def run_scraper(self, scraper_type: str) -> dict:
        """Run a specific scraper and return results"""
        config = self.scraper_configs.get(scraper_type)
        if not config:
            logger.error(f"Unknown scraper type: {scraper_type}")
            return {'success': False, 'error': 'Unknown scraper type'}
        
        script_path = BASE_DIR / "scrapers" / config['script']
        if scraper_type == 'cleanup':
            script_path = BASE_DIR / config['script']
        
        if not script_path.exists():
            logger.error(f"Scraper script not found: {script_path}")
            return {'success': False, 'error': 'Script not found'}
        
        try:
            logger.info(f"🚀 Running {scraper_type} scraper: {config['description']}")
            start_time = datetime.now()
            
            # Run the scraper with timeout
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=config['max_runtime_minutes'] * 60,
                cwd=BASE_DIR
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                # Parse output to extract statistics
                articles_added = self.extract_articles_count(result.stdout)
                
                logger.info(f"✅ {scraper_type} completed successfully in {duration:.1f}s")
                logger.info(f"📊 Articles added: {articles_added}")
                
                self.stats['articles_collected_today'] += articles_added
                
                return {
                    'success': True,
                    'duration_seconds': duration,
                    'articles_added': articles_added,
                    'output': result.stdout[-500:]  # Last 500 chars
                }
            else:
                logger.error(f"❌ {scraper_type} failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                
                return {
                    'success': False,
                    'error': result.stderr,
                    'return_code': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {scraper_type} timed out after {config['max_runtime_minutes']} minutes")
            return {'success': False, 'error': 'Timeout'}
        
        except Exception as e:
            logger.error(f"❌ Error running {scraper_type}: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_articles_count(self, output: str) -> int:
        """Extract article count from scraper output"""
        import re
        
        patterns = [
            r"Successfully scraped (\d+) .*articles",
            r"Total articles saved: (\d+)",
            r"(\d+) articles saved",
            r"saved (\d+) articles",
            r"Articles: (\d+) saved",
            r"Total Articles Saved: (\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Fallback: count lines with success indicators
        success_indicators = ["✅ Saved:", "✅ Found", "saved successfully"]
        count = sum(output.count(indicator) for indicator in success_indicators)
        return count if count > 0 else 0
    
    def get_database_stats(self) -> dict:
        """Get current database statistics"""
        try:
            if not DB_PATH.exists():
                return {'total_articles': 0, 'recent_articles': 0}
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute("SELECT COUNT(*) FROM articles")
            total = cursor.fetchone()[0]
            
            # Recent articles (last 24 hours)
            cursor.execute("SELECT COUNT(*) FROM articles WHERE created_at > datetime('now', '-1 day')")
            recent = cursor.fetchone()[0]
            
            # Articles by category
            cursor.execute("""
                SELECT categories, COUNT(*) 
                FROM articles 
                WHERE categories IS NOT NULL 
                GROUP BY categories 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            """)
            top_categories = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_articles': total,
                'recent_articles_24h': recent,
                'top_categories': top_categories
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'total_articles': 0, 'recent_articles': 0, 'error': str(e)}
    
    def quick_scraper_job(self):
        """Job for quick scraping (every 2 hours)"""
        logger.info("⚡ Running scheduled quick scraper job")
        result = self.run_scraper('quick')
        self.update_stats('quick', result)
    
    def comprehensive_scraper_job(self):
        """Job for comprehensive scraping (every 6 hours)"""
        logger.info("🌍 Running scheduled comprehensive scraper job")
        result = self.run_scraper('comprehensive')
        self.update_stats('comprehensive', result)
    
    def social_scraper_job(self):
        """Job for social media scraping (every 8 hours)"""
        logger.info("🗣️ Running scheduled social media scraper job")
        result = self.run_scraper('social')
        self.update_stats('social', result)
    
    def cleanup_job(self):
        """Job for URL cleanup (daily)"""
        logger.info("🧹 Running scheduled cleanup job")
        result = self.run_scraper('cleanup')
        self.update_stats('cleanup', result)
    
    def daily_report_job(self):
        """Generate daily summary report"""
        logger.info("📊 Generating daily report")
        
        db_stats = self.get_database_stats()
        
        logger.info("=" * 50)
        logger.info("📈 DAILY HEALTH NEWS SUMMARY")
        logger.info("=" * 50)
        logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        logger.info(f"📰 Total Articles in DB: {db_stats.get('total_articles', 0)}")
        logger.info(f"🆕 Articles Added Today: {self.stats['articles_collected_today']}")
        logger.info(f"🔄 Scraper Runs Today: {self.stats['total_runs']}")
        logger.info(f"✅ Successful Runs: {self.stats['successful_runs']}")
        
        if db_stats.get('top_categories'):
            logger.info("🏆 Top Categories:")
            for category, count in db_stats['top_categories']:
                try:
                    categories = json.loads(category)
                    if isinstance(categories, list) and categories:
                        category_name = categories[0]
                    else:
                        category_name = category
                except:
                    category_name = category
                logger.info(f"   • {category_name}: {count} articles")
        
        # Reset daily counters
        self.stats['articles_collected_today'] = 0
        self.stats['total_runs'] = 0
        self.stats['successful_runs'] = 0
    
    def update_stats(self, scraper_type: str, result: dict):
        """Update scheduler statistics"""
        self.stats['total_runs'] += 1
        self.stats['last_run_time'] = datetime.now()
        
        if result['success']:
            self.stats['successful_runs'] += 1
            self.stats['last_run_status'] = f"{scraper_type}: SUCCESS"
        else:
            self.stats['last_run_status'] = f"{scraper_type}: FAILED - {result.get('error', 'Unknown error')}"
    
    def setup_schedule(self):
        """Setup the scraping schedule"""
        logger.info("⏰ Setting up scraping schedule")
        
        # Quick scraper every 2 hours
        schedule.every(2).hours.do(self.quick_scraper_job)
        
        # Comprehensive scraper every 6 hours
        schedule.every(6).hours.do(self.comprehensive_scraper_job)
        
        # Social media scraper every 8 hours
        schedule.every(8).hours.do(self.social_scraper_job)
        
        # Cleanup job daily at 3 AM
        schedule.every().day.at("03:00").do(self.cleanup_job)
        
        # Daily report at 9 AM
        schedule.every().day.at("09:00").do(self.daily_report_job)
        
        logger.info("📅 Schedule configured:")
        logger.info("   ⚡ Quick scraping: Every 2 hours")
        logger.info("   🌍 Comprehensive scraping: Every 6 hours")
        logger.info("   🗣️ Social media scraping: Every 8 hours")
        logger.info("   🧹 URL cleanup: Daily at 3:00 AM")
        logger.info("   📊 Daily report: Daily at 9:00 AM")
    
    def run_initial_scraping(self):
        """Run initial scraping to populate database"""
        logger.info("🎯 Running initial comprehensive scraping...")
        
        # Run comprehensive scraper first
        result = self.run_scraper('comprehensive')
        if result['success']:
            logger.info("✅ Initial scraping completed successfully")
        else:
            logger.warning(f"⚠️ Initial scraping had issues: {result.get('error', 'Unknown')}")
        
        # Generate initial report
        self.daily_report_job()
    
    def start_scheduler(self, run_initial: bool = True):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.should_stop = False
        self.stats['scheduler_start_time'] = datetime.now()
        
        logger.info("🚀 Health News Scheduler Starting")
        logger.info("=" * 40)
        
        # Setup schedule
        self.setup_schedule()
        
        # Run initial scraping if requested
        if run_initial:
            self.run_initial_scraping()
        
        # Start scheduler loop
        logger.info("⏰ Scheduler is now running. Press Ctrl+C to stop.")
        
        try:
            while not self.should_stop:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⛔ Scheduler stop requested")
        
        self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.should_stop = True
        self.is_running = False
        
        duration = datetime.now() - self.stats['scheduler_start_time']
        
        logger.info("⛔ Health News Scheduler Stopped")
        logger.info(f"⏱️ Total runtime: {duration}")
        logger.info(f"🔄 Total runs: {self.stats['total_runs']}")
        logger.info(f"✅ Successful runs: {self.stats['successful_runs']}")
    
    def run_manual_scraping(self, scraper_type: str = 'comprehensive'):
        """Run manual scraping for testing"""
        logger.info(f"🔧 Manual scraping: {scraper_type}")
        result = self.run_scraper(scraper_type)
        
        if result['success']:
            logger.info(f"✅ Manual scraping completed: {result.get('articles_added', 0)} articles")
        else:
            logger.error(f"❌ Manual scraping failed: {result.get('error', 'Unknown error')}")
        
        return result

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Health News Scheduler")
    parser.add_argument("--start", action="store_true", help="Start the scheduler")
    parser.add_argument("--test", choices=['quick', 'comprehensive', 'social', 'cleanup'], 
                       help="Run a test scraping job")
    parser.add_argument("--no-initial", action="store_true", help="Skip initial scraping")
    parser.add_argument("--status", action="store_true", help="Show database status")
    
    args = parser.parse_args()
    
    scheduler = HealthNewsScheduler()
    
    if args.status:
        stats = scheduler.get_database_stats()
        print(f"\n📊 Database Status:")
        print(f"   Total Articles: {stats.get('total_articles', 0)}")
        print(f"   Recent Articles (24h): {stats.get('recent_articles_24h', 0)}")
        return
    
    if args.test:
        result = scheduler.run_manual_scraping(args.test)
        return result
    
    if args.start:
        run_initial = not args.no_initial
        scheduler.start_scheduler(run_initial=run_initial)
    else:
        print("Health News Scheduler")
        print("Options:")
        print("  --start          Start the scheduler")
        print("  --test TYPE      Test scraper (quick/comprehensive/social/cleanup)")
        print("  --no-initial     Skip initial scraping")
        print("  --status         Show database status")

if __name__ == "__main__":
    main()
