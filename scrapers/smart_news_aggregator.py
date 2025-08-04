#!/usr/bin/env python3
"""
Smart News Aggregator - Master Scraper

This master scraper combines all news sources to provide SmartNews-style aggregation:
- Comprehensive news scraper (major outlets, health sources, institutional)
- Social media scraper (Reddit, YouTube, blogs)
- Existing project scrapers (Indian health, enhanced health, etc.)

All content is aggregated and made available through existing endpoints.
No changes to API endpoints required.
"""

import sys
from pathlib import Path
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import subprocess

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartNewsAggregator:
    """Master aggregator for SmartNews-style health news collection"""
    
    def __init__(self):
        self.scrapers_dir = BASE_DIR / "scrapers"
        
        # Define scraper execution order (priority-based)
        self.scraper_sequence = [
            {
                "name": "Master Health Scraper",
                "file": "master_health_scraper.py",
                "priority": 1,
                "description": "Unified scraper for all RSS feeds, news sources, and health content"
            },
            {
                "name": "Social Media Scraper",
                "file": "social_media_scraper.py",
                "priority": 3,
                "description": "Social media and alternative health news sources"
            },
            {
                "name": "Simple Health Scraper",
                "file": "simple_health_scraper.py",
                "priority": 3,
                "description": "Basic health news scraper"
            }
        ]
        
        # Statistics tracking
        self.stats = {
            "total_articles": 0,
            "scrapers_run": 0,
            "scrapers_successful": 0,
            "start_time": None,
            "end_time": None,
            "sources_processed": []
        }
    
    def run_scraper(self, scraper_config: Dict) -> Dict:
        """Run a single scraper and return results"""
        scraper_file = self.scrapers_dir / scraper_config["file"]
        
        if not scraper_file.exists():
            logger.warning(f"⚠️ Scraper not found: {scraper_file}")
            return {
                "success": False,
                "articles_added": 0,
                "error": "Scraper file not found"
            }
        
        try:
            logger.info(f"🚀 Running {scraper_config['name']}...")
            logger.info(f"   📄 Description: {scraper_config['description']}")
            
            # Run the scraper
            result = subprocess.run(
                [sys.executable, str(scraper_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per scraper
            )
            
            if result.returncode == 0:
                # Parse output to extract number of articles
                output = result.stdout
                articles_added = self.extract_articles_count(output)
                
                logger.info(f"✅ {scraper_config['name']} completed successfully")
                logger.info(f"   📊 Articles added: {articles_added}")
                
                return {
                    "success": True,
                    "articles_added": articles_added,
                    "output": output
                }
            else:
                logger.error(f"❌ {scraper_config['name']} failed")
                logger.error(f"   Error: {result.stderr}")
                
                return {
                    "success": False,
                    "articles_added": 0,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {scraper_config['name']} timed out")
            return {
                "success": False,
                "articles_added": 0,
                "error": "Scraper timed out"
            }
        except Exception as e:
            logger.error(f"❌ Error running {scraper_config['name']}: {e}")
            return {
                "success": False,
                "articles_added": 0,
                "error": str(e)
            }
    
    def extract_articles_count(self, output: str) -> int:
        """Extract the number of articles from scraper output"""
        try:
            # Look for patterns like "Successfully scraped X articles"
            import re
            patterns = [
                r"Successfully scraped (\d+) .*articles",
                r"Total articles saved: (\d+)",
                r"(\d+) articles saved",
                r"saved (\d+) articles"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            # Fallback: count lines with "✅ Saved:"
            saved_count = output.count("✅ Saved:")
            if saved_count > 0:
                return saved_count
                
        except Exception as e:
            logger.warning(f"Could not extract article count: {e}")
        
        return 0
    
    def run_all_scrapers(self, max_scrapers: Optional[int] = None) -> Dict:
        """Run all scrapers in sequence"""
        self.stats["start_time"] = datetime.now()
        
        logger.info("🌍 SmartNews-Style Health News Aggregator")
        logger.info("=" * 60)
        logger.info(f"📅 Started at: {self.stats['start_time']}")
        
        if max_scrapers:
            scrapers_to_run = self.scraper_sequence[:max_scrapers]
            logger.info(f"🔧 Running first {max_scrapers} scrapers only")
        else:
            scrapers_to_run = self.scraper_sequence
            logger.info(f"🔧 Running all {len(scrapers_to_run)} scrapers")
        
        results = {}
        
        for scraper_config in scrapers_to_run:
            self.stats["scrapers_run"] += 1
            
            logger.info(f"\n📡 [{self.stats['scrapers_run']}/{len(scrapers_to_run)}] {scraper_config['name']}")
            logger.info(f"   Priority: {scraper_config['priority']}")
            
            result = self.run_scraper(scraper_config)
            results[scraper_config["name"]] = result
            
            if result["success"]:
                self.stats["scrapers_successful"] += 1
                self.stats["total_articles"] += result["articles_added"]
                self.stats["sources_processed"].append(scraper_config["name"])
            
            # Small delay between scrapers to be respectful
            import time
            time.sleep(2)
        
        self.stats["end_time"] = datetime.now()
        
        # Generate final report
        self.generate_final_report(results)
        
        return {
            "stats": self.stats,
            "results": results
        }
    
    def generate_final_report(self, results: Dict):
        """Generate and display final aggregation report"""
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 SMARTNEWS-STYLE AGGREGATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"⏱️  Total Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"📰 Total Articles Collected: {self.stats['total_articles']}")
        logger.info(f"✅ Successful Scrapers: {self.stats['scrapers_successful']}/{self.stats['scrapers_run']}")
        
        logger.info(f"\n📋 Sources Successfully Processed:")
        for source in self.stats["sources_processed"]:
            logger.info(f"   ✅ {source}")
        
        # Show failed scrapers
        failed_scrapers = []
        for name, result in results.items():
            if not result["success"]:
                failed_scrapers.append(name)
        
        if failed_scrapers:
            logger.info(f"\n⚠️  Failed Scrapers:")
            for scraper in failed_scrapers:
                logger.info(f"   ❌ {scraper}: {results[scraper].get('error', 'Unknown error')}")
        
        logger.info(f"\n🎯 SmartNews-Style Features Enabled:")
        logger.info(f"   📊 Multi-source aggregation from {len(self.stats['sources_processed'])} sources")
        logger.info(f"   🏷️  Smart categorization and tagging")
        logger.info(f"   📱 Social media integration (Reddit, YouTube)")
        logger.info(f"   🌍 International and local health news")
        logger.info(f"   🔍 Search and filtering across all sources")
        
        logger.info(f"\n💡 All existing API endpoints now serve aggregated content!")
        logger.info(f"   🌐 GET /articles/latest - Latest from all sources")
        logger.info(f"   🔍 GET /articles/search?q=health - Search across all content")
        logger.info(f"   🏷️  GET /articles/tag/latest - Trending content")
        logger.info(f"   📂 GET /articles/category/news - Categorized content")
        
        if self.stats['total_articles'] > 0:
            logger.info(f"\n🎉 SUCCESS: SmartNews-style aggregation completed!")
            logger.info(f"   💾 Database updated with {self.stats['total_articles']} new articles")
            logger.info(f"   🚀 Start your API server to access the content")
        else:
            logger.info(f"\n⚠️  No new articles were added")
            logger.info(f"   🔧 Check your internet connection and source availability")
    
    def run_quick_update(self) -> Dict:
        """Run only high-priority scrapers for quick updates"""
        logger.info("⚡ Running quick update (high-priority sources only)")
        
        quick_scrapers = [s for s in self.scraper_sequence if s["priority"] <= 2]
        self.scraper_sequence = quick_scrapers
        
        return self.run_all_scrapers()
    
    def run_comprehensive_update(self) -> Dict:
        """Run all scrapers for comprehensive coverage"""
        logger.info("🌍 Running comprehensive update (all sources)")
        return self.run_all_scrapers()

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SmartNews-Style Health News Aggregator")
    parser.add_argument("--quick", action="store_true", help="Run only high-priority scrapers")
    parser.add_argument("--max-scrapers", type=int, help="Maximum number of scrapers to run")
    parser.add_argument("--list-scrapers", action="store_true", help="List available scrapers")
    
    args = parser.parse_args()
    
    aggregator = SmartNewsAggregator()
    
    if args.list_scrapers:
        print("\n📋 Available Scrapers:")
        for i, scraper in enumerate(aggregator.scraper_sequence, 1):
            print(f"   {i}. {scraper['name']} (Priority: {scraper['priority']})")
            print(f"      📄 {scraper['description']}")
        return
    
    if args.quick:
        result = aggregator.run_quick_update()
    else:
        result = aggregator.run_all_scrapers(args.max_scrapers)
    
    # Return summary for potential integration
    return result

if __name__ == "__main__":
    main()
