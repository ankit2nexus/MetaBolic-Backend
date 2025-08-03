#!/usr/bin/env python3
"""
Comprehensive Category Coverage Scraper

This script ensures all categories and subcategories in the Metabolical frontend
have sufficient content by targeting specific RSS feeds and API queries for each category.
"""

import sys
import logging
import time
import json
import os
import random
import re
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
from urllib.parse import urljoin, quote_plus
from xml.etree import ElementTree as ET
from html import unescape
import requests
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up one more level to get project root
sys.path.append(str(BASE_DIR))

# Import URL validator if available
try:
    from app.url_validator import URLValidator
    url_validator_available = True
except ImportError:
    url_validator_available = False
    class URLValidator:
        def validate_article_url(self, article):
            return True, {"status": "valid"}

# Database path
DB_PATH = BASE_DIR / "data" / "articles.db"

# Frontend menu categories and tags (matching the frontend structure)
MENU_CATEGORIES = {
    "News": ["Latest", "Policy and Regulation", "Government Schemes", "International", "Breaking News", "Health Updates"],
    "Diseases": ["Diabetes", "Obesity", "Inflammation", "Cardiovascular", "Liver Disease", "Kidney Disease", 
                "Thyroid Disorders", "Metabolic Disorders", "Sleep Disorders", "Skin Conditions", "Eye and Ear Health", 
                "Reproductive Health", "Cancer", "Mental Health Disorders", "Infectious Diseases"],
    "Solutions": ["Nutrition", "Fitness", "Lifestyle Changes", "Wellness Programs", "Prevention Strategies", 
                 "Treatment Options", "Natural Remedies", "Medical Treatments", "Therapy", "Rehabilitation"],
    "Food": ["Natural Food", "Organic Food", "Processed Food", "Fish and Seafood", "Food Safety", 
            "Dietary Guidelines", "Superfoods", "Food Allergies", "Meal Planning", "Healthy Recipes"],
    "Audience": ["Women", "Men", "Children", "Teenagers", "Seniors", "Athletes", "Families", 
                "Pregnant Women", "New Mothers", "Working Professionals", "Students"],
    "Trending": ["Gut Health", "Mental Health", "Hormones", "Addiction Recovery", "Sleep Health", 
                "Sexual Wellness", "Immune System", "Anti-Aging", "Detox", "Mindfulness"],
    "Blogs & Opinion": ["Expert Opinions", "Medical Blogs", "Health Commentary", "Research Analysis", 
                       "Patient Stories", "Doctor Insights", "Health Myths", "Wellness Tips"]
}

class CategoryContentScraper:
    """Scraper focused on ensuring all categories and subcategories have content"""
    
    def __init__(self, api_keys=None):
        """Initialize the scraper with API keys"""
        self.url_validator = URLValidator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Load API keys from config file if not provided
        if api_keys is None:
            api_keys = self.load_api_keys()
        
        self.api_keys = api_keys or {}
        
        # Configure sources for each category and subcategory
        self.setup_category_sources()
    
    def load_api_keys(self):
        """Load API keys from the configuration file"""
        import json
        import os
        
        try:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # Go up one level from scrapers/
            config_path = os.path.join(project_root, 'config', 'scraper_api_keys.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"✅ Loaded API keys from {config_path}")
                    return config.get('api_keys', {})
            else:
                logger.warning(f"⚠️ API keys config file not found at {config_path}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading API keys: {e}")
            return {}
    
    def setup_category_sources(self):
        """Set up sources for each category and subcategory"""
        # Initialize sources containers
        self.category_sources = {}
        
        # === NEWS CATEGORY ===
        self.category_sources["News"] = {
            "main": [
                # General health news sources
                {"name": "Reuters Health", "rss_url": "https://feeds.reuters.com/reuters/healthNews", "base_url": "https://www.reuters.com"},
                {"name": "BBC Health", "rss_url": "http://feeds.bbci.co.uk/news/health/rss.xml", "base_url": "https://www.bbc.com"},
                {"name": "CNN Health", "rss_url": "http://rss.cnn.com/rss/edition_health.rss", "base_url": "https://www.cnn.com"},
                {"name": "NPR Health", "rss_url": "https://feeds.npr.org/1001/rss.xml", "base_url": "https://www.npr.org"},
                {"name": "Associated Press Health", "rss_url": "https://apnews.com/apf-health", "base_url": "https://apnews.com"}
            ],
            "Latest": [
                {"name": "Medical News Today", "rss_url": "https://www.medicalnewstoday.com/rss", "base_url": "https://www.medicalnewstoday.com"},
                {"name": "Healthline News", "rss_url": "https://www.healthline.com/rss/health-news", "base_url": "https://www.healthline.com"},
                {"name": "WebMD News", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC", "base_url": "https://www.webmd.com"}
            ],
            "Policy and Regulation": [
                {"name": "FDA News", "rss_url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-announcements/rss.xml", "base_url": "https://www.fda.gov"},
                {"name": "WHO News", "rss_url": "https://www.who.int/rss-feeds/news-english.xml", "base_url": "https://www.who.int"},
                {"name": "CDC News", "rss_url": "https://tools.cdc.gov/api/v2/resources/media/316422.rss", "base_url": "https://www.cdc.gov"}
            ],
            "Government Schemes": [
                {"name": "NIH News", "rss_url": "https://www.nih.gov/news-events/news-releases/rss.xml", "base_url": "https://www.nih.gov"},
                {"name": "HHS News", "rss_url": "https://www.hhs.gov/rss/news.xml", "base_url": "https://www.hhs.gov"},
                {"name": "Indian Health Ministry", "rss_url": "https://pib.gov.in/rss/pib.xml", "base_url": "https://pib.gov.in"}
            ],
            "International": [
                {"name": "The Hindu Health", "rss_url": "https://www.thehindu.com/sci-tech/health/feeder/default.rss", "base_url": "https://www.thehindu.com"},
                {"name": "Times of India Health", "rss_url": "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms", "base_url": "https://timesofindia.indiatimes.com"},
                {"name": "Guardian Health", "rss_url": "https://www.theguardian.com/society/health/rss", "base_url": "https://www.theguardian.com"},
                {"name": "Reuters Global Health", "rss_url": "https://feeds.reuters.com/reuters/healthNews", "base_url": "https://www.reuters.com"}
            ],
            "Breaking News": [
                {"name": "STAT News", "rss_url": "https://www.statnews.com/feed/", "base_url": "https://www.statnews.com"},
                {"name": "Fierce Healthcare", "rss_url": "https://www.fiercehealthcare.com/rss/xml", "base_url": "https://www.fiercehealthcare.com"}
            ],
            "Health Updates": [
                {"name": "Harvard Health", "rss_url": "https://www.health.harvard.edu/blog/feed", "base_url": "https://www.health.harvard.edu"},
                {"name": "Mayo Clinic News", "rss_url": "https://newsnetwork.mayoclinic.org/feed/", "base_url": "https://newsnetwork.mayoclinic.org"}
            ]
        }
        
        # === DISEASES CATEGORY ===
        self.category_sources["Diseases"] = {
            "main": [
                {"name": "WebMD Diseases", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=conditions", "base_url": "https://www.webmd.com"},
                {"name": "MedlinePlus Health Topics", "rss_url": "https://medlineplus.gov/feeds/topics.xml", "base_url": "https://medlineplus.gov"},
                {"name": "Mayo Clinic Diseases", "rss_url": "https://www.mayoclinic.org/rss/diseases-conditions", "base_url": "https://www.mayoclinic.org"}
            ],
            "Diabetes": [
                {"name": "American Diabetes Association", "rss_url": "https://diabetes.org/feeds/blog", "base_url": "https://diabetes.org"},
                {"name": "Healthline Diabetes", "rss_url": "https://www.healthline.com/health/diabetes/rss", "base_url": "https://www.healthline.com"},
                {"name": "Diabetes Self-Management", "rss_url": "https://www.diabetesselfmanagement.com/feed/", "base_url": "https://www.diabetesselfmanagement.com"}
            ],
            "Obesity": [
                {"name": "WebMD Weight Management", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=weight-loss-obesity", "base_url": "https://www.webmd.com"},
                {"name": "Medical News Today Obesity", "rss_url": "https://www.medicalnewstoday.com/categories/obesity/feed", "base_url": "https://www.medicalnewstoday.com"},
                {"name": "Obesity Society", "rss_url": "https://www.obesity.org/rss.xml", "base_url": "https://www.obesity.org"}
            ],
            "Cardiovascular": [
                {"name": "American Heart Association", "rss_url": "https://newsroom.heart.org/blog_rss.xml", "base_url": "https://newsroom.heart.org"},
                {"name": "WebMD Heart Disease", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=heart-disease", "base_url": "https://www.webmd.com"},
                {"name": "Healthline Heart Health", "rss_url": "https://www.healthline.com/health/heart-disease/rss", "base_url": "https://www.healthline.com"}
            ],
            "Liver Disease": [
                {"name": "American Liver Foundation", "rss_url": "https://liverfoundation.org/feed/", "base_url": "https://liverfoundation.org"},
                {"name": "Healthline Liver Health", "rss_url": "https://www.healthline.com/health/liver-health/feed", "base_url": "https://www.healthline.com"}
            ],
            "Kidney Disease": [
                {"name": "National Kidney Foundation", "rss_url": "https://www.kidney.org/rss.xml", "base_url": "https://www.kidney.org"},
                {"name": "Medical News Today Kidney", "rss_url": "https://www.medicalnewstoday.com/categories/urology-nephrology/feed", "base_url": "https://www.medicalnewstoday.com"}
            ],
            "Thyroid Disorders": [
                {"name": "American Thyroid Association", "rss_url": "https://www.thyroid.org/feed/", "base_url": "https://www.thyroid.org"},
                {"name": "Healthline Thyroid", "rss_url": "https://www.healthline.com/health/thyroid-disorders/rss", "base_url": "https://www.healthline.com"}
            ],
            "Sleep Disorders": [
                {"name": "Sleep Foundation", "rss_url": "https://www.sleepfoundation.org/feed", "base_url": "https://www.sleepfoundation.org"},
                {"name": "WebMD Sleep Disorders", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=sleep-disorders", "base_url": "https://www.webmd.com"},
                {"name": "American Sleep Association", "rss_url": "https://www.sleepassociation.org/feed/", "base_url": "https://www.sleepassociation.org"}
            ],
            "Cancer": [
                {"name": "American Cancer Society", "rss_url": "https://www.cancer.org/latest-news.rss", "base_url": "https://www.cancer.org"},
                {"name": "National Cancer Institute", "rss_url": "https://www.cancer.gov/rss/news.xml", "base_url": "https://www.cancer.gov"},
                {"name": "Healthline Cancer", "rss_url": "https://www.healthline.com/health/cancer/rss", "base_url": "https://www.healthline.com"}
            ],
            "Mental Health Disorders": [
                {"name": "NAMI Mental Health", "rss_url": "https://www.nami.org/rss", "base_url": "https://www.nami.org"},
                {"name": "Psychology Today", "rss_url": "https://www.psychologytoday.com/us/rss.xml", "base_url": "https://www.psychologytoday.com"},
                {"name": "Mental Health America", "rss_url": "https://www.mentalhealthamerica.net/rss.xml", "base_url": "https://www.mentalhealthamerica.net"}
            ],
            "Eye and Ear Health": [
                {"name": "WebMD Eye Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=eye-health", "base_url": "https://www.webmd.com"},
                {"name": "Healthline ENT", "rss_url": "https://www.healthline.com/health/ear-nose-throat/rss", "base_url": "https://www.healthline.com"},
                {"name": "American Academy of Ophthalmology", "rss_url": "https://www.aao.org/rss.xml", "base_url": "https://www.aao.org"}
            ],
            "Reproductive Health": [
                {"name": "WebMD Sexual Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=sexual-conditions", "base_url": "https://www.webmd.com"},
                {"name": "Healthline Reproductive Health", "rss_url": "https://www.healthline.com/health/reproductive-health/feed", "base_url": "https://www.healthline.com"},
                {"name": "Planned Parenthood Health", "rss_url": "https://www.plannedparenthood.org/rss.xml", "base_url": "https://www.plannedparenthood.org"}
            ],
            "Infectious Diseases": [
                {"name": "CDC Infectious Diseases", "rss_url": "https://tools.cdc.gov/api/v2/resources/media/132608.rss", "base_url": "https://www.cdc.gov"},
                {"name": "WHO Disease Outbreaks", "rss_url": "https://www.who.int/rss-feeds/disease-outbreak-news-english.xml", "base_url": "https://www.who.int"},
                {"name": "Johns Hopkins Infectious Disease", "rss_url": "https://www.hopkinsmedicine.org/news/rss", "base_url": "https://www.hopkinsmedicine.org"}
            ]
        }
        
        # === SOLUTIONS CATEGORY ===
        self.category_sources["Solutions"] = {
            "main": [
                {"name": "Mayo Clinic", "rss_url": "https://www.mayoclinic.org/rss/all-health-information-topics", "base_url": "https://www.mayoclinic.org"},
                {"name": "Harvard Health", "rss_url": "https://www.health.harvard.edu/blog/feed", "base_url": "https://www.health.harvard.edu"},
                {"name": "WebMD Treatment", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=treatment", "base_url": "https://www.webmd.com"}
            ],
            "Nutrition": [
                {"name": "Academy of Nutrition", "rss_url": "https://www.eatright.org/rss.xml", "base_url": "https://www.eatright.org"},
                {"name": "Healthline Nutrition", "rss_url": "https://www.healthline.com/nutrition/feed", "base_url": "https://www.healthline.com"},
                {"name": "Nutrition.gov", "rss_url": "https://www.nutrition.gov/rss", "base_url": "https://www.nutrition.gov"}
            ],
            "Fitness": [
                {"name": "Men's Health Fitness", "rss_url": "https://www.menshealth.com/fitness/rss", "base_url": "https://www.menshealth.com"},
                {"name": "Women's Health Fitness", "rss_url": "https://www.womenshealthmag.com/fitness/rss", "base_url": "https://www.womenshealthmag.com"},
                {"name": "ACE Fitness", "rss_url": "https://www.acefitness.org/resources/feed/", "base_url": "https://www.acefitness.org"}
            ],
            "Lifestyle Changes": [
                {"name": "Mayo Clinic Healthy Lifestyle", "rss_url": "https://www.mayoclinic.org/rss/healthy-living", "base_url": "https://www.mayoclinic.org"},
                {"name": "Healthline Lifestyle", "rss_url": "https://www.healthline.com/health/healthy-living/feed", "base_url": "https://www.healthline.com"}
            ],
            "Wellness Programs": [
                {"name": "Well+Good", "rss_url": "https://www.wellandgood.com/feed/", "base_url": "https://www.wellandgood.com"},
                {"name": "WebMD Wellness", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=health-wellness", "base_url": "https://www.webmd.com"}
            ],
            "Prevention Strategies": [
                {"name": "CDC Prevention", "rss_url": "https://tools.cdc.gov/api/v2/resources/media/415620.rss", "base_url": "https://www.cdc.gov"},
                {"name": "WebMD Prevention", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=prevention-wellness", "base_url": "https://www.webmd.com"}
            ],
            "Treatment Options": [
                {"name": "Mayo Clinic Treatment", "rss_url": "https://www.mayoclinic.org/rss/tests-procedures", "base_url": "https://www.mayoclinic.org"},
                {"name": "Healthline Treatment", "rss_url": "https://www.healthline.com/health/treatment/rss", "base_url": "https://www.healthline.com"}
            ],
            "Natural Remedies": [
                {"name": "NCCIH Natural Products", "rss_url": "https://www.nccih.nih.gov/rss.xml", "base_url": "https://www.nccih.nih.gov"},
                {"name": "Medical News Today Alternative", "rss_url": "https://www.medicalnewstoday.com/categories/complementary_medicine/feed", "base_url": "https://www.medicalnewstoday.com"}
            ],
            "Medical Treatments": [
                {"name": "FDA Medical Devices", "rss_url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medical-devices/rss.xml", "base_url": "https://www.fda.gov"},
                {"name": "Healthline Medical Procedures", "rss_url": "https://www.healthline.com/health/procedures/rss", "base_url": "https://www.healthline.com"}
            ],
            "Therapy": [
                {"name": "Psychology Today Therapy", "rss_url": "https://www.psychologytoday.com/us/therapists/rss", "base_url": "https://www.psychologytoday.com"},
                {"name": "WebMD Mental Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=mental-health", "base_url": "https://www.webmd.com"}
            ],
            "Rehabilitation": [
                {"name": "Archives of Physical Medicine", "rss_url": "https://www.archives-pmr.org/rss", "base_url": "https://www.archives-pmr.org"},
                {"name": "Healthline Rehabilitation", "rss_url": "https://www.healthline.com/health/rehabilitation/rss", "base_url": "https://www.healthline.com"}
            ]
        }
        
        # === FOOD CATEGORY ===
        self.category_sources["Food"] = {
            "main": [
                {"name": "Food Network Health", "rss_url": "https://www.foodnetwork.com/healthy/rss.xml", "base_url": "https://www.foodnetwork.com"},
                {"name": "EatingWell", "rss_url": "https://www.eatingwell.com/rss.xml", "base_url": "https://www.eatingwell.com"},
                {"name": "Healthline Nutrition", "rss_url": "https://www.healthline.com/nutrition/feed", "base_url": "https://www.healthline.com"}
            ],
            "Nutritional Information": [
                {"name": "USDA FoodData Central", "rss_url": "https://fdc.nal.usda.gov/rss.xml", "base_url": "https://fdc.nal.usda.gov"},
                {"name": "Nutrition.gov", "rss_url": "https://www.nutrition.gov/rss", "base_url": "https://www.nutrition.gov"},
                {"name": "Harvard Nutrition", "rss_url": "https://www.hsph.harvard.edu/nutritionsource/feed/", "base_url": "https://www.hsph.harvard.edu"}
            ],
            "Healthy Recipes": [
                {"name": "EatingWell Healthy Recipes", "rss_url": "https://www.eatingwell.com/category/healthy-recipes/rss.xml", "base_url": "https://www.eatingwell.com"},
                {"name": "Cooking Light", "rss_url": "https://www.cookinglight.com/rss.xml", "base_url": "https://www.cookinglight.com"},
                {"name": "MyFitnessPal Recipes", "rss_url": "https://blog.myfitnesspal.com/category/recipes/feed/", "base_url": "https://blog.myfitnesspal.com"}
            ],
            "Dietary Guidelines": [
                {"name": "USDA Dietary Guidelines", "rss_url": "https://www.dietaryguidelines.gov/rss.xml", "base_url": "https://www.dietaryguidelines.gov"},
                {"name": "Academy of Nutrition", "rss_url": "https://www.eatright.org/rss.xml", "base_url": "https://www.eatright.org"}
            ],
            "Special Diets": [
                {"name": "Diabetic Living", "rss_url": "https://www.diabeticlivingonline.com/rss.xml", "base_url": "https://www.diabeticlivingonline.com"},
                {"name": "Celiac.org", "rss_url": "https://celiac.org/feed/", "base_url": "https://celiac.org"},
                {"name": "Heart Healthy Diet", "rss_url": "https://www.heart.org/en/healthy-living/healthy-eating/rss", "base_url": "https://www.heart.org"}
            ],
            "Food Safety": [
                {"name": "FDA Food Safety", "rss_url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food/rss.xml", "base_url": "https://www.fda.gov"},
                {"name": "USDA Food Safety", "rss_url": "https://www.fsis.usda.gov/rss.xml", "base_url": "https://www.fsis.usda.gov"},
                {"name": "Food Safety News", "rss_url": "https://www.foodsafetynews.com/feed/", "base_url": "https://www.foodsafetynews.com"}
            ],
            "Superfoods": [
                {"name": "WebMD Superfoods", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=diet", "base_url": "https://www.webmd.com"},
                {"name": "Healthline Superfoods", "rss_url": "https://www.healthline.com/health/food-nutrition/feed", "base_url": "https://www.healthline.com"}
            ],
            "Supplements": [
                {"name": "NIH Supplements", "rss_url": "https://ods.od.nih.gov/rss.xml", "base_url": "https://ods.od.nih.gov"},
                {"name": "Examine.com", "rss_url": "https://examine.com/rss/", "base_url": "https://examine.com"}
            ],
            "Organic Food": [
                {"name": "USDA Organic", "rss_url": "https://www.usda.gov/media/rss/organic", "base_url": "https://www.usda.gov"},
                {"name": "Rodale Institute", "rss_url": "https://rodaleinstitute.org/feed/", "base_url": "https://rodaleinstitute.org"}
            ],
            "Fish and Seafood": [
                {"name": "Seafood Health Facts", "rss_url": "https://www.seafoodhealthfacts.org/rss.xml", "base_url": "https://www.seafoodhealthfacts.org"},
                {"name": "NOAA Fisheries", "rss_url": "https://www.fisheries.noaa.gov/rss", "base_url": "https://www.fisheries.noaa.gov"}
            ]
        }
        
        # === AUDIENCE CATEGORY ===
        self.category_sources["Audience"] = {
            "main": [
                {"name": "Consumer Health News", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC", "base_url": "https://www.webmd.com"},
                {"name": "Everyday Health", "rss_url": "https://www.everydayhealth.com/rss/all-articles.xml", "base_url": "https://www.everydayhealth.com"},
                {"name": "Healthline General", "rss_url": "https://www.healthline.com/feed", "base_url": "https://www.healthline.com"}
            ],
            "Women": [
                {"name": "Women's Health Magazine", "rss_url": "https://www.womenshealthmag.com/feeds/all.rss/", "base_url": "https://www.womenshealthmag.com"},
                {"name": "WebMD Women's Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=womens-health", "base_url": "https://www.webmd.com"},
                {"name": "Healthline Women's Health", "rss_url": "https://www.healthline.com/health/womens-health/feed", "base_url": "https://www.healthline.com"}
            ],
            "Men": [
                {"name": "Men's Health Magazine", "rss_url": "https://www.menshealth.com/rss/all.xml", "base_url": "https://www.menshealth.com"},
                {"name": "WebMD Men's Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=mens-health", "base_url": "https://www.webmd.com"},
                {"name": "Healthline Men's Health", "rss_url": "https://www.healthline.com/health/mens-health/feed", "base_url": "https://www.healthline.com"}
            ],
            "Children": [
                {"name": "KidsHealth", "rss_url": "https://kidshealth.org/rss/index.xml", "base_url": "https://kidshealth.org"},
                {"name": "American Academy of Pediatrics", "rss_url": "https://www.aap.org/en/news-room/news-releases/rss", "base_url": "https://www.aap.org"},
                {"name": "WebMD Children's Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=children", "base_url": "https://www.webmd.com"}
            ],
            "Seniors": [
                {"name": "AARP Health", "rss_url": "https://www.aarp.org/health/rss.xml", "base_url": "https://www.aarp.org"},
                {"name": "National Institute on Aging", "rss_url": "https://www.nia.nih.gov/rss.xml", "base_url": "https://www.nia.nih.gov"},
                {"name": "WebMD Healthy Aging", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=healthy-aging", "base_url": "https://www.webmd.com"}
            ],
            "Teens": [
                {"name": "TeensHealth", "rss_url": "https://teenshealth.org/rss/index.xml", "base_url": "https://teenshealth.org"},
                {"name": "Healthline Teen Health", "rss_url": "https://www.healthline.com/health/teens/feed", "base_url": "https://www.healthline.com"}
            ],
            "Athletes": [
                {"name": "Sports Medicine Research", "rss_url": "https://www.nata.org/rss.xml", "base_url": "https://www.nata.org"},
                {"name": "American College of Sports Medicine", "rss_url": "https://www.acsm.org/rss.xml", "base_url": "https://www.acsm.org"}
            ],
            "Pregnant Women": [
                {"name": "What to Expect", "rss_url": "https://www.whattoexpect.com/rss.xml", "base_url": "https://www.whattoexpect.com"},
                {"name": "American Pregnancy Association", "rss_url": "https://americanpregnancy.org/feed/", "base_url": "https://americanpregnancy.org"}
            ],
            "Parents": [
                {"name": "Parents Magazine Health", "rss_url": "https://www.parents.com/health/rss.xml", "base_url": "https://www.parents.com"},
                {"name": "KidsHealth for Parents", "rss_url": "https://kidshealth.org/parent/rss/index.xml", "base_url": "https://kidshealth.org"}
            ],
            "Caregivers": [
                {"name": "Family Caregiver Alliance", "rss_url": "https://www.caregiver.org/rss.xml", "base_url": "https://www.caregiver.org"},
                {"name": "AARP Caregiving", "rss_url": "https://www.aarp.org/caregiving/rss.xml", "base_url": "https://www.aarp.org"}
            ],
            "Healthcare Workers": [
                {"name": "Medscape News", "rss_url": "https://www.medscape.com/rss/medical-news", "base_url": "https://www.medscape.com"},
                {"name": "Modern Healthcare", "rss_url": "https://www.modernhealthcare.com/rss", "base_url": "https://www.modernhealthcare.com"}
            ]
        }
        
        # === TRENDING CATEGORY ===
        self.category_sources["Trending"] = {
            "main": [
                {"name": "STAT News", "rss_url": "https://www.statnews.com/feed/", "base_url": "https://www.statnews.com"},
                {"name": "Science Daily Health", "rss_url": "https://www.sciencedaily.com/rss/health_medicine.xml", "base_url": "https://www.sciencedaily.com"},
                {"name": "Reuters Health", "rss_url": "https://www.reuters.com/sector/health/rss.xml", "base_url": "https://www.reuters.com"}
            ],
            "Gut Health": [
                {"name": "Gut Microbiota News", "rss_url": "https://www.gutmicrobiotaforhealth.com/feed/", "base_url": "https://www.gutmicrobiotaforhealth.com"},
                {"name": "Medical News Today - GI", "rss_url": "https://www.medicalnewstoday.com/categories/gastrointestinal/feed", "base_url": "https://www.medicalnewstoday.com"},
                {"name": "Harvard Gut Health", "rss_url": "https://www.health.harvard.edu/digestive-health/feed", "base_url": "https://www.health.harvard.edu"}
            ],
            "Mental Health": [
                {"name": "NAMI Blog", "rss_url": "https://www.nami.org/rss", "base_url": "https://www.nami.org"},
                {"name": "Psychology Today", "rss_url": "https://www.psychologytoday.com/us/rss.xml", "base_url": "https://www.psychologytoday.com"},
                {"name": "Mental Health America", "rss_url": "https://www.mhanational.org/rss.xml", "base_url": "https://www.mhanational.org"}
            ],
            "Hormones": [
                {"name": "Hormone Health Network", "rss_url": "https://www.hormone.org/rss", "base_url": "https://www.hormone.org"},
                {"name": "EndocrineWeb", "rss_url": "https://www.endocrineweb.com/feed", "base_url": "https://www.endocrineweb.com"},
                {"name": "Endocrine Society", "rss_url": "https://www.endocrine.org/news/rss", "base_url": "https://www.endocrine.org"}
            ],
            "Addiction": [
                {"name": "NIDA News", "rss_url": "https://www.drugabuse.gov/news-events/rss", "base_url": "https://www.drugabuse.gov"},
                {"name": "Addiction Center", "rss_url": "https://www.addictioncenter.com/rss", "base_url": "https://www.addictioncenter.com"},
                {"name": "SAMHSA News", "rss_url": "https://www.samhsa.gov/rss", "base_url": "https://www.samhsa.gov"}
            ],
            "Sleep Health": [
                {"name": "Sleep Foundation", "rss_url": "https://www.sleepfoundation.org/feed", "base_url": "https://www.sleepfoundation.org"},
                {"name": "Medical News Today - Sleep", "rss_url": "https://www.medicalnewstoday.com/categories/sleep/feed", "base_url": "https://www.medicalnewstoday.com"},
                {"name": "American Sleep Association", "rss_url": "https://www.sleepassociation.org/feed/", "base_url": "https://www.sleepassociation.org"}
            ],
            "Sexual Wellness": [
                {"name": "WebMD Sexual Health", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=sex", "base_url": "https://www.webmd.com"},
                {"name": "Medical News Today - Sexual", "rss_url": "https://www.medicalnewstoday.com/categories/sexual_health/feed", "base_url": "https://www.medicalnewstoday.com"},
                {"name": "Healthline Sexual Health", "rss_url": "https://www.healthline.com/health/sexual-health/feed", "base_url": "https://www.healthline.com"}
            ],
            "Longevity": [
                {"name": "Blue Zones", "rss_url": "https://www.bluezones.com/feed/", "base_url": "https://www.bluezones.com"},
                {"name": "Harvard Aging", "rss_url": "https://www.health.harvard.edu/blog/category/aging/feed", "base_url": "https://www.health.harvard.edu"}
            ],
            "Biohacking": [
                {"name": "Biohacker.com", "rss_url": "https://biohacker.com/feed/", "base_url": "https://biohacker.com"},
                {"name": "Self Hacked", "rss_url": "https://selfhacked.com/feed/", "base_url": "https://selfhacked.com"}
            ],
            "Mindfulness": [
                {"name": "Mindful Magazine", "rss_url": "https://www.mindful.org/feed/", "base_url": "https://www.mindful.org"},
                {"name": "Greater Good Science Center", "rss_url": "https://greatergood.berkeley.edu/feed", "base_url": "https://greatergood.berkeley.edu"}
            ],
            "Stress Management": [
                {"name": "Mayo Clinic Stress", "rss_url": "https://www.mayoclinic.org/healthy-lifestyle/stress-management/rss", "base_url": "https://www.mayoclinic.org"},
                {"name": "WebMD Stress", "rss_url": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC&Category=stress-management", "base_url": "https://www.webmd.com"}
            ]
        }
        
        # === BLOGS & OPINION CATEGORY ===
        self.category_sources["Blogs & Opinion"] = {
            "main": [
                {"name": "KevinMD", "rss_url": "https://www.kevinmd.com/blog/feed", "base_url": "https://www.kevinmd.com"},
                {"name": "Health Affairs Blog", "rss_url": "https://www.healthaffairs.org/blog/feed", "base_url": "https://www.healthaffairs.org"},
                {"name": "The Health Care Blog", "rss_url": "https://thehealthcareblog.com/feed/", "base_url": "https://thehealthcareblog.com"},
                {"name": "Science-Based Medicine", "rss_url": "https://sciencebasedmedicine.org/feed/", "base_url": "https://sciencebasedmedicine.org"},
                {"name": "Harvard Health Blog", "rss_url": "https://www.health.harvard.edu/blog/feed", "base_url": "https://www.health.harvard.edu"}
            ],
            "Expert Opinions": [
                {"name": "NEJM Perspective", "rss_url": "https://www.nejm.org/action/showFeed?type=etoc&feed=rss", "base_url": "https://www.nejm.org"},
                {"name": "JAMA Opinion", "rss_url": "https://jamanetwork.com/rss/opinion.xml", "base_url": "https://jamanetwork.com"},
                {"name": "Medscape Commentary", "rss_url": "https://www.medscape.com/rss/viewpoint", "base_url": "https://www.medscape.com"}
            ],
            "Patient Stories": [
                {"name": "The Mighty Health", "rss_url": "https://themighty.com/health/feed/", "base_url": "https://themighty.com"},
                {"name": "Patient Power", "rss_url": "https://www.patientpower.info/feed/", "base_url": "https://www.patientpower.info"}
            ],
            "Healthcare Commentary": [
                {"name": "Modern Healthcare Opinion", "rss_url": "https://www.modernhealthcare.com/opinion/rss", "base_url": "https://www.modernhealthcare.com"},
                {"name": "Healthcare Dive Opinion", "rss_url": "https://www.healthcaredive.com/feeds/news/", "base_url": "https://www.healthcaredive.com"}
            ],
            "Doctor Blogs": [
                {"name": "White Coat Rants", "rss_url": "https://www.whitecoatrants.com/feed/", "base_url": "https://www.whitecoatrants.com"},
                {"name": "The Nerd's Guide to Pre-Med", "rss_url": "https://blog.mynerdytutor.com/feed/", "base_url": "https://blog.mynerdytutor.com"}
            ],
            "Health Policy": [
                {"name": "Kaiser Health News", "rss_url": "https://khn.org/feed/", "base_url": "https://khn.org"},
                {"name": "Health Affairs Forefront", "rss_url": "https://www.healthaffairs.org/do/10.1377/forefront/rss", "base_url": "https://www.healthaffairs.org"}
            ],
            "Alternative Medicine Views": [
                {"name": "Integrative Medicine Research", "rss_url": "https://www.imjournal.com/rss.xml", "base_url": "https://www.imjournal.com"},
                {"name": "Natural Health 365", "rss_url": "https://www.naturalhealth365.com/feed/", "base_url": "https://www.naturalhealth365.com"}
            ],
            "Medical Ethics": [
                {"name": "Bioethics.net", "rss_url": "https://www.bioethics.net/feed/", "base_url": "https://www.bioethics.net"},
                {"name": "Hastings Center", "rss_url": "https://www.thehastingscenter.org/feed/", "base_url": "https://www.thehastingscenter.org"}
            ],
            "Global Health": [
                {"name": "Global Health NOW", "rss_url": "https://www.globalhealthnow.org/rss.xml", "base_url": "https://www.globalhealthnow.org"},
                {"name": "Think Global Health", "rss_url": "https://www.thinkglobalhealth.org/rss.xml", "base_url": "https://www.thinkglobalhealth.org"}
            ],
            "Public Health": [
                {"name": "APHA News", "rss_url": "https://www.apha.org/rss.xml", "base_url": "https://www.apha.org"},
                {"name": "Public Health Post", "rss_url": "https://www.publichealthpost.org/feed/", "base_url": "https://www.publichealthpost.org"}
            ]
        }
        
        # === NEWS API QUERIES FOR EACH CATEGORY ===
        self.news_api_queries = {
            "News": {
                "main": "health news OR medical news",
                "Latest": "latest health news OR recent medical discovery",
                "Policy and Regulation": "health policy OR healthcare regulation OR medical policy",
                "Govt Schemes": "government health program OR health initiative OR public health scheme",
                "International": "global health OR international health policy OR WHO health"
            },
            "Diseases": {
                "main": "disease OR health condition OR medical condition",
                "Diabetes": "diabetes OR blood sugar OR insulin resistance",
                "Obesity": "obesity OR weight management OR BMI high",
                "Inflammation": "inflammation OR inflammatory disease OR chronic inflammation",
                "Cardiovascular": "heart disease OR cardiovascular OR heart health",
                "Liver": "liver disease OR fatty liver OR hepatitis",
                "Kidney": "kidney disease OR renal health OR kidney function",
                "Thyroid": "thyroid disorder OR hypothyroidism OR hyperthyroidism",
                "Metabolic": "metabolic syndrome OR metabolism disorder OR metabolic health",
                "Sleep Disorders": "sleep apnea OR insomnia OR sleep disorder",
                "Skin": "dermatology OR skin condition OR skin health",
                "Eyes and Ears": "vision problem OR hearing loss OR eye disease OR ear infection",
                "Reproductive Health": "fertility OR reproductive health OR sexual health"
            },
            "Solutions": {
                "main": "health solution OR medical treatment OR therapy",
                "Nutrition": "nutrition OR healthy diet OR dietary guidelines",
                "Fitness": "fitness OR exercise OR physical activity OR workout",
                "Lifestyle Changes": "healthy lifestyle OR lifestyle change OR daily habits",
                "Wellness Programs": "wellness OR wellbeing OR holistic health",
                "Prevention Strategies": "disease prevention OR preventive care OR health screening",
                "Treatment Options": "medical treatment OR therapy options OR treatment plan",
                "Natural Remedies": "natural remedy OR herbal medicine OR alternative treatment",
                "Medical Treatments": "medical procedure OR clinical treatment OR medical intervention",
                "Therapy": "therapy OR counseling OR psychological treatment",
                "Rehabilitation": "rehabilitation OR recovery therapy OR physical therapy"
            },
            "Food": {
                "main": "food health OR nutrition OR diet",
                "Nutritional Information": "nutritional value OR food nutrition facts OR vitamin mineral",
                "Healthy Recipes": "healthy recipe OR nutritious cooking OR diet friendly food",
                "Dietary Guidelines": "dietary guideline OR nutrition recommendation OR healthy eating",
                "Special Diets": "special diet OR dietary restriction OR medical diet",
                "Food Safety": "food safety OR foodborne illness OR food contamination",
                "Superfoods": "superfood OR nutrient dense food OR health food",
                "Supplements": "dietary supplement OR vitamin OR mineral supplement",
                "Organic Food": "organic food OR organic farming OR pesticide free",
                "Fish and Seafood": "fish health benefits OR seafood nutrition OR omega 3"
            },
            "Audience": {
                "main": "health demographic OR population health",
                "Women": "women's health OR female health OR women medical",
                "Men": "men's health OR male health OR men medical",
                "Children": "children's health OR pediatric health OR kids health",
                "Seniors": "senior health OR elderly health OR aging health",
                "Teens": "teen health OR adolescent health OR youth health",
                "Athletes": "sports medicine OR athletic health OR exercise performance",
                "Pregnant Women": "pregnancy health OR prenatal care OR maternal health",
                "Parents": "parenting health OR family health OR child care health",
                "Caregivers": "caregiver health OR caregiver support OR eldercare",
                "Healthcare Workers": "healthcare professional OR medical worker OR nurse health"
            },
            "Trending": {
                "main": "health trend OR medical trend OR wellness trend",
                "Gut Health": "gut health OR microbiome OR digestive health",
                "Mental Health": "mental health OR psychological wellbeing OR mental wellness",
                "Hormones": "hormone health OR endocrine health OR hormone balance",
                "Addiction": "addiction health OR substance dependency OR recovery health",
                "Sleep Health": "sleep quality OR sleep science OR sleep hygiene",
                "Sexual Wellness": "sexual health OR sexual wellness OR intimacy health",
                "Longevity": "longevity OR life extension OR healthy aging",
                "Biohacking": "biohacking OR health optimization OR self improvement",
                "Mindfulness": "mindfulness OR meditation OR mental wellness",
                "Stress Management": "stress management OR stress relief OR anxiety management"
            },
            "Blogs & Opinion": {
                "main": "health opinion OR medical blog OR health expert opinion",
                "Expert Opinions": "medical expert opinion OR doctor opinion OR healthcare expert",
                "Patient Stories": "patient story OR health journey OR medical experience",
                "Healthcare Commentary": "healthcare commentary OR medical analysis OR health policy opinion",
                "Doctor Blogs": "doctor blog OR physician blog OR medical professional blog",
                "Health Policy": "health policy opinion OR healthcare policy analysis OR medical policy",
                "Alternative Medicine Views": "alternative medicine opinion OR complementary medicine OR holistic health",
                "Medical Ethics": "medical ethics OR bioethics OR healthcare ethics",
                "Global Health": "global health opinion OR international health OR world health",
                "Public Health": "public health opinion OR community health OR population health"
            }
        }
    
    def fetch_rss_feed(self, source):
        """Fetch articles from an RSS feed without feedparser dependency"""
        articles = []
        
        try:
            logger.info(f"📰 Fetching from: {source['name']}")
            response = self.session.get(source["rss_url"], timeout=15)
            response.raise_for_status()
            
            # Parse XML content
            root = ET.fromstring(response.content)
            
            # Handle different RSS formats (RSS 2.0, Atom, etc.)
            if root.tag.endswith('rss'):
                # RSS 2.0 format
                for item in root.findall('.//item'):
                    try:
                        # Extract basic info
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        pub_date_elem = item.find('pubDate')
                        description_elem = item.find('description')
                        
                        if title_elem is None or link_elem is None:
                            continue
                            
                        title = unescape(title_elem.text.strip()) if title_elem.text else ""
                        link = link_elem.text.strip() if link_elem.text else ""
                        
                        # Fix relative URLs
                        if link and not link.startswith(('http://', 'https://')):
                            link = urljoin(source["base_url"], link)
                        
                        # Process date
                        pub_date = datetime.now()
                        if pub_date_elem is not None and pub_date_elem.text:
                            try:
                                # Try various date formats
                                date_formats = [
                                    '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
                                    '%a, %d %b %Y %H:%M:%S %Z',
                                    '%a, %d %b %Y %H:%M:%S',
                                    '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601
                                    '%Y-%m-%dT%H:%M:%S.%f%z',
                                    '%Y-%m-%d %H:%M:%S',
                                ]
                                
                                for fmt in date_formats:
                                    try:
                                        pub_date = datetime.strptime(pub_date_elem.text.strip(), fmt)
                                        break
                                    except ValueError:
                                        continue
                            except Exception:
                                # Keep default date on failure
                                pass
                        
                        # Process description/summary
                        summary = ""
                        if description_elem is not None and description_elem.text:
                            summary = description_elem.text
                            # Strip HTML
                            summary = re.sub(r'<[^>]+>', '', summary)
                            summary = re.sub(r'\s+', ' ', summary).strip()
                            summary = unescape(summary)
                            # Limit summary length
                            summary = summary[:500] + ('...' if len(summary) > 500 else '')
                        
                        # Extract author if available
                        author_elem = item.find('author') or item.find('dc:creator', {'dc': 'http://purl.org/dc/elements/1.1/'})
                        author = author_elem.text.strip() if author_elem is not None and author_elem.text else ""
                        
                        # Store article
                        article_data = {
                            'title': title,
                            'summary': summary,
                            'url': link,
                            'date': pub_date.isoformat(),
                            'author': author,
                            'source': source["name"]
                        }
                        
                        # Validate URL if validator available
                        if url_validator_available:
                            is_valid, _ = self.url_validator.validate_article_url(article_data)
                            if not is_valid:
                                continue
                        
                        articles.append(article_data)
                    
                    except Exception as e:
                        logger.warning(f"Error processing RSS item: {e}")
                        continue
            
            elif root.tag.endswith('feed'):  # Atom format
                # Handle Atom format
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('.//atom:entry', namespace):
                    try:
                        # Extract basic info
                        title_elem = entry.find('atom:title', namespace)
                        link_elem = entry.find('atom:link[@rel="alternate"]', namespace) or entry.find('atom:link', namespace)
                        published_elem = entry.find('atom:published', namespace) or entry.find('atom:updated', namespace)
                        content_elem = entry.find('atom:content', namespace) or entry.find('atom:summary', namespace)
                        
                        if title_elem is None or link_elem is None:
                            continue
                            
                        title = unescape(title_elem.text.strip()) if title_elem.text else ""
                        link = link_elem.get('href', '').strip()
                        
                        # Fix relative URLs
                        if link and not link.startswith(('http://', 'https://')):
                            link = urljoin(source["base_url"], link)
                        
                        # Process date
                        pub_date = datetime.now()
                        if published_elem is not None and published_elem.text:
                            try:
                                # ISO 8601 format is common in Atom feeds
                                pub_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                            except:
                                # Keep default date on failure
                                pass
                        
                        # Process content/summary
                        summary = ""
                        if content_elem is not None:
                            if content_elem.text:
                                summary = content_elem.text
                            elif content_elem.get('type') == 'html' or content_elem.get('type') == 'xhtml':
                                summary = ET.tostring(content_elem, encoding='unicode')
                        
                        # Strip HTML
                        summary = re.sub(r'<[^>]+>', '', summary)
                        summary = re.sub(r'\s+', ' ', summary).strip()
                        summary = unescape(summary)
                        # Limit summary length
                        summary = summary[:500] + ('...' if len(summary) > 500 else '')
                        
                        # Extract author if available
                        author_elem = entry.find('atom:author/atom:name', namespace)
                        author = author_elem.text.strip() if author_elem is not None and author_elem.text else ""
                        
                        # Store article
                        article_data = {
                            'title': title,
                            'summary': summary,
                            'url': link,
                            'date': pub_date.isoformat(),
                            'author': author,
                            'source': source["name"]
                        }
                        
                        # Validate URL if validator available
                        if url_validator_available:
                            is_valid, _ = self.url_validator.validate_article_url(article_data)
                            if not is_valid:
                                continue
                        
                        articles.append(article_data)
                    
                    except Exception as e:
                        logger.warning(f"Error processing Atom entry: {e}")
                        continue
            
            logger.info(f"✅ Retrieved {len(articles)} articles from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source['name']}: {e}")
        
        return articles
    
    def query_news_api(self, category, subcategory=None):
        """Query NewsAPI for articles for a specific category/subcategory"""
        if "newsapi" not in self.api_keys or not self.api_keys["newsapi"]:
            logger.warning("⚠️ No NewsAPI key provided, skipping")
            return []
        
        articles = []
        query = ""
        
        if subcategory and subcategory in self.news_api_queries.get(category, {}):
            query = self.news_api_queries[category][subcategory]
        elif "main" in self.news_api_queries.get(category, {}):
            query = self.news_api_queries[category]["main"]
        else:
            logger.warning(f"⚠️ No NewsAPI query found for {category}/{subcategory}")
            return []
        
        try:
            logger.info(f"🔍 Querying NewsAPI for: {category}/{subcategory or 'main'}")
            
            api_url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.api_keys["newsapi"]
            }
            
            response = self.session.get(api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok" and "articles" in data:
                raw_articles = data["articles"]
                
                for article in raw_articles:
                    try:
                        title = article.get("title", "").strip()
                        description = article.get("description", "")
                        url = article.get("url", "").strip()
                        published_at = article.get("publishedAt", "")
                        source_name = article.get("source", {}).get("name", "Unknown")
                        
                        # Process date
                        pub_date = datetime.now()
                        if published_at:
                            try:
                                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        if title and url:
                            article_data = {
                                'title': title,
                                'summary': description or "",
                                'url': url,
                                'date': pub_date.isoformat(),
                                'author': article.get("author", ""),
                                'source': f"{source_name} via NewsAPI"
                            }
                            
                            # Validate URL
                            if url_validator_available:
                                is_valid, _ = self.url_validator.validate_article_url(article_data)
                                if not is_valid:
                                    continue
                            
                            articles.append(article_data)
                    
                    except Exception as e:
                        logger.warning(f"Error processing NewsAPI article: {e}")
                        continue
            
            logger.info(f"📰 Found {len(articles)} articles from NewsAPI for {category}/{subcategory or 'main'}")
            
        except Exception as e:
            logger.error(f"Error querying NewsAPI for {category}/{subcategory or 'main'}: {e}")
        
        return articles
    
    def extract_tags(self, title, summary, category=None, subcategory=None):
        """Extract tags from article content"""
        tags = []
        combined_text = f"{title} {summary}".lower()
        
        # Always add category as a tag if provided
        if category and category not in tags:
            tags.append(category)
            
        # Always add subcategory as a tag if provided
        if subcategory and subcategory not in tags:
            tags.append(subcategory)
        
        # Extract additional tags based on content
        all_subcategories = []
        for cat, subcats in MENU_CATEGORIES.items():
            all_subcategories.extend(subcats)
        
        # Check for subcategory mentions in text
        for subcat in all_subcategories:
            if subcat.lower() in combined_text and subcat not in tags:
                tags.append(subcat)
        
        # Add some common health-related tags if found in text
        health_keywords = [
            "health", "medical", "wellness", "nutrition", "fitness", "diet",
            "disease", "treatment", "prevention", "research", "study"
        ]
        
        for keyword in health_keywords:
            if keyword in combined_text and keyword not in tags:
                tags.append(keyword)
        
        # Limit number of tags
        return tags[:8]  # Maximum 8 tags
    
    def determine_category(self, title, summary, source_category=None, source_subcategory=None):
        """Determine the best category and subcategory for an article based on content"""
        if source_category and source_subcategory:
            # If both category and subcategory are provided by the source, use them
            return source_category, source_subcategory
        
        if source_category:
            # If only category is provided, try to determine subcategory
            combined_text = f"{title} {summary}".lower()
            
            # Check if any subcategory keywords are in the text
            if source_category in MENU_CATEGORIES:
                for subcategory in MENU_CATEGORIES[source_category]:
                    if subcategory.lower() in combined_text:
                        return source_category, subcategory
            
            # No matching subcategory found, use category only
            return source_category, None
        
        # If no category is provided, try to determine both
        combined_text = f"{title} {summary}".lower()
        
        # Check each category and subcategory for matches
        for category, subcategories in MENU_CATEGORIES.items():
            if category.lower() in combined_text:
                # Found a category match, now check subcategories
                for subcategory in subcategories:
                    if subcategory.lower() in combined_text:
                        return category, subcategory
                
                # Category match but no subcategory match
                return category, None
            
            # Check subcategories even if category isn't explicitly mentioned
            for subcategory in subcategories:
                if subcategory.lower() in combined_text:
                    return category, subcategory
        
        # Fallback to news category if nothing specific found
        return "news", None
    
    def save_articles_to_db(self, articles, category=None, subcategory=None):
        """Save articles to the database with proper categorization"""
        if not articles:
            return 0
        
        # Connect to database
        DB_PATH.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                title TEXT,
                authors TEXT,
                summary TEXT,
                url TEXT UNIQUE,
                categories TEXT,
                subcategory TEXT,
                tags TEXT,
                source TEXT,
                priority INTEGER DEFAULT 1,
                url_health TEXT,
                url_accessible INTEGER DEFAULT 1,
                last_checked TIMESTAMP,
                news_score REAL DEFAULT 0.0,
                trending_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        # Track new articles
        new_articles = 0
        
        for article in articles:
            try:
                # Determine category and subcategory if not provided
                article_category = category
                article_subcategory = subcategory
                
                if not article_category or not article_subcategory:
                    art_cat, art_subcat = self.determine_category(
                        article['title'], 
                        article.get('summary', ''),
                        article_category,
                        article_subcategory
                    )
                    article_category = art_cat or "news"
                    article_subcategory = art_subcat
                
                # Generate tags
                tags = self.extract_tags(
                    article['title'], 
                    article.get('summary', ''),
                    article_category,
                    article_subcategory
                )
                
                # Insert article
                try:
                    cursor.execute("""
                        INSERT INTO articles 
                        (date, title, authors, summary, url, categories, subcategory, tags, source, priority)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article.get('date', datetime.now().isoformat()),
                        article['title'],
                        article.get('author', ''),
                        article.get('summary', ''),
                        article['url'],
                        json.dumps([article_category]),
                        article_subcategory,
                        json.dumps(tags),
                        article.get('source', 'Unknown'),
                        article.get('priority', 1)
                    ))
                    new_articles += 1
                except sqlite3.IntegrityError:
                    # URL already exists, update the categories and tags instead
                    cursor.execute("""
                        SELECT id, categories, tags FROM articles WHERE url = ?
                    """, (article['url'],))
                    row = cursor.fetchone()
                    if row:
                        article_id, existing_categories_json, existing_tags_json = row
                        
                        # Parse existing data
                        try:
                            existing_categories = json.loads(existing_categories_json)
                        except:
                            existing_categories = []
                        
                        try:
                            existing_tags = json.loads(existing_tags_json)
                        except:
                            existing_tags = []
                        
                        # Add new category if not already present
                        if article_category and article_category not in existing_categories:
                            existing_categories.append(article_category)
                        
                        # Add new tags if not already present
                        for tag in tags:
                            if tag not in existing_tags:
                                existing_tags.append(tag)
                        
                        # Update the record
                        cursor.execute("""
                            UPDATE articles 
                            SET categories = ?, tags = ?, subcategory = COALESCE(subcategory, ?)
                            WHERE id = ?
                        """, (
                            json.dumps(existing_categories),
                            json.dumps(existing_tags),
                            article_subcategory or None,
                            article_id
                        ))
            
            except Exception as e:
                logger.warning(f"Error saving article {article.get('title', 'Unknown')}: {e}")
                continue
        
        # Commit changes
        conn.commit()
        conn.close()
        
        return new_articles
    
    def scrape_category(self, category):
        """Scrape all sources for a specific category"""
        if category not in self.category_sources:
            logger.warning(f"❌ Category '{category}' not configured")
            return 0
        
        total_new_articles = 0
        logger.info(f"🔍 Scraping category: {category}")
        
        # Scrape main sources for the category
        if "main" in self.category_sources[category]:
            for source in self.category_sources[category]["main"]:
                try:
                    articles = self.fetch_rss_feed(source)
                    new_articles = self.save_articles_to_db(articles, category)
                    total_new_articles += new_articles
                    logger.info(f"✅ Added {new_articles} articles from {source['name']} to {category}")
                    time.sleep(random.uniform(0.5, 2.0))  # Random delay to avoid rate limiting
                except Exception as e:
                    logger.error(f"❌ Error scraping {source['name']}: {e}")
        
        # Query NewsAPI for the category
        try:
            articles = self.query_news_api(category)
            new_articles = self.save_articles_to_db(articles, category)
            total_new_articles += new_articles
            logger.info(f"✅ Added {new_articles} articles from NewsAPI to {category}")
        except Exception as e:
            logger.error(f"❌ Error querying NewsAPI for {category}: {e}")
        
        # Scrape each subcategory
        for subcategory in MENU_CATEGORIES.get(category, []):
            if subcategory in self.category_sources[category]:
                logger.info(f"🔍 Scraping subcategory: {category}/{subcategory}")
                
                for source in self.category_sources[category][subcategory]:
                    try:
                        articles = self.fetch_rss_feed(source)
                        new_articles = self.save_articles_to_db(articles, category, subcategory)
                        total_new_articles += new_articles
                        logger.info(f"✅ Added {new_articles} articles from {source['name']} to {category}/{subcategory}")
                        time.sleep(random.uniform(0.5, 2.0))  # Random delay to avoid rate limiting
                    except Exception as e:
                        logger.error(f"❌ Error scraping {source['name']}: {e}")
                
                # Query NewsAPI for the subcategory
                try:
                    articles = self.query_news_api(category, subcategory)
                    new_articles = self.save_articles_to_db(articles, category, subcategory)
                    total_new_articles += new_articles
                    logger.info(f"✅ Added {new_articles} articles from NewsAPI to {category}/{subcategory}")
                except Exception as e:
                    logger.error(f"❌ Error querying NewsAPI for {category}/{subcategory}: {e}")
        
        return total_new_articles
    
    def scrape_all_categories(self):
        """Scrape all categories and subcategories"""
        total_new_articles = 0
        
        for category in MENU_CATEGORIES.keys():
            try:
                new_articles = self.scrape_category(category)
                total_new_articles += new_articles
                logger.info(f"✅ Added {new_articles} articles to {category}")
                time.sleep(random.uniform(1.0, 3.0))  # Random delay between categories
            except Exception as e:
                logger.error(f"❌ Error scraping category {category}: {e}")
        
        return total_new_articles

def load_api_keys():
    """Load API keys from config file or environment variables"""
    api_keys = {
        "newsapi": os.environ.get("NEWSAPI_KEY", ""),
        "gnews": os.environ.get("GNEWS_KEY", ""),
        "newsdata": os.environ.get("NEWSDATA_KEY", "")
    }
    
    # Try loading from config file
    config_path = BASE_DIR / "config" / "scraper_api_keys.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                if "api_keys" in config:
                    for key, value in config["api_keys"].items():
                        if value:  # Only override if value is not empty
                            api_keys[key] = value
            logger.info(f"Loaded API keys from {config_path}")
        except Exception as e:
            logger.error(f"Error loading API keys from config: {e}")
    
    return api_keys

def update_database_schema():
    """Update database schema if needed"""
    # Connect to database
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if subcategory column exists
    cursor.execute("PRAGMA table_info(articles)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    # Add subcategory column if it doesn't exist
    if "subcategory" not in column_names:
        try:
            cursor.execute("ALTER TABLE articles ADD COLUMN subcategory TEXT")
            conn.commit()
            logger.info("✅ Added subcategory column to articles table")
        except Exception as e:
            logger.error(f"❌ Error adding subcategory column: {e}")
    
    conn.close()

def main():
    """Main function to run the scraper"""
    start_time = datetime.now()
    logger.info("🚀 Starting Comprehensive Category Coverage Scraper")
    
    # Update database schema if needed
    update_database_schema()
    
    # Load API keys
    api_keys = load_api_keys()
    
    # Create and run scraper
    scraper = CategoryContentScraper(api_keys)
    new_articles = scraper.scrape_all_categories()
    
    # Report results
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"✅ Scraper completed in {duration:.2f} seconds")
    logger.info(f"📊 Added {new_articles} new articles to the database")
    
    # Show category breakdown
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logger.info("📋 Category breakdown:")
        for category in MENU_CATEGORIES.keys():
            cursor.execute("""
                SELECT COUNT(*) FROM articles 
                WHERE categories LIKE ?
            """, (f'%"{category}"%',))
            count = cursor.fetchone()[0]
            logger.info(f"  • {category}: {count} articles")
            
            for subcategory in MENU_CATEGORIES.get(category, []):
                cursor.execute("""
                    SELECT COUNT(*) FROM articles 
                    WHERE subcategory = ?
                """, (subcategory,))
                subcount = cursor.fetchone()[0]
                logger.info(f"    - {subcategory}: {subcount} articles")
        
        conn.close()
    except Exception as e:
        logger.error(f"❌ Error getting category breakdown: {e}")
    
    return new_articles

if __name__ == "__main__":
    main()
