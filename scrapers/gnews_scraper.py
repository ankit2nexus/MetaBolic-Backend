import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config.scraper_config import LANGUAGE, COUNTRY, SCRAPE_KEYWORDS
from datetime import datetime, timedelta
import time
import sqlite3
import json
import re
import feedparser
import requests
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import undetected_chromedriver as uc
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available, using requests for scraping")

try:
    from newspaper import Article, Config
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    print("⚠️ Newspaper3k not available, using BeautifulSoup for content extraction")

# Import categorization function
try:
    from api.utils import normalize_datetime, get_zero_shot_categories
except ImportError:
    try:
        sys.path.append(str(BASE_DIR / "api"))
        from utils import normalize_datetime, get_zero_shot_categories
    except ImportError:
        print("⚠️ Could not import categorization functions, using basic categorization")
        
        def normalize_datetime(date_str):
            return datetime.now().isoformat()
            
        def get_zero_shot_categories(text):
            return ["news"], ["general"]

BASE_DIR = Path(__file__).resolve().parent.parent 
CONTENT_PATH = BASE_DIR / "content" / "news"
DB_PATH = BASE_DIR / "db" / "articles.db"
def get_real_url_with_selenium(google_news_url, wait_time=5):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--headless=new") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        driver = uc.Chrome(version_main=138, options=options, use_subprocess=True)

        driver.get(google_news_url)
        
        time.sleep(wait_time)            
        return driver.current_url, driver.page_source
    
    except Exception as e:
        print("Error resolving real URL:", e)
        return None, None
        
    finally:
        try:
            driver.quit()
        except:
            pass

def extract_article_content(url, html=None):
    try:
        article = Article(url)
        if html:
            article.download(input_html=html)
            article.parse()
            article.nlp()
        else:
            article.download()
            article.parse()
            article.nlp()

        article.download()
        article.parse()
        article.nlp()
        return {
            "headline": article.title,
            "author": ", ".join(article.authors),
            "text": article.text,
            "summary": article.summary
        }
    except Exception as e:
        print(f"Failed to extract article at {url}: {e}")
        return None

def save_as_markdown(article_data):
    date_str = datetime.today().strftime("%Y-%m-%d")
    title = article_data["title"]
    title = re.sub(r'[^\w\s-]', '', title).strip().lower()
    title = re.sub(r'[\s_-]+', '-', title)
    title = title[:90]
    slug = slugify(title if title else "untitled")
    filename = f"{date_str}-{slug}.md"
    filepath = CONTENT_PATH / filename

    CONTENT_PATH.mkdir(parents=True, exist_ok=True)

    categories_yaml = article_data.get("categories", ["News"])
    tags_yaml = article_data.get("tags", ["Latest"])

    markdown = f"""---
title: \"{title}\"
date: {date_str}
categories: {categories_yaml}
tags: {tags_yaml}
source_url: {article_data["url"]}
summary: \"{article_data['summary']}\"
author: {article_data["authors"]}
---

{article_data["summary"]}

Read full article → [here]({article_data["url"]})
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Saved: {filepath}")

def save_to_db(article_data):
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            authors TEXT,
            summary TEXT,
            url TEXT,
            categories TEXT,
            tags TEXT
        )
    """)
    
    categories_json = json.dumps(article_data["categories"]) if isinstance(article_data["categories"], list) else article_data["categories"]
    tags_json = json.dumps(article_data["tags"]) if isinstance(article_data["tags"], list) else article_data["tags"]
    
    cur.execute("""
        INSERT INTO articles (date, title, authors, summary, url, categories, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        normalize_datetime(article_data["date"]),
        article_data["title"],
        article_data["authors"],
        article_data["summary"],
        article_data["url"],
        categories_json,
        tags_json
    ))

    conn.commit()
    conn.close()

#CATEGORY_YAML_PATH = BASE_DIR / "config" / "category_keywords.yml"

#def load_category_keywords():
#    with open(CATEGORY_YAML_PATH, "r", encoding="utf-8") as f:
#        return yaml.safe_load(f)

#CATEGORY_KEYWORDS = load_category_keywords()

'''def get_fuzzy_categories(text):
    categories = set()
    tags = set()
    text_lower = text.lower()
    for category, subcats in CATEGORY_KEYWORDS.items():
        for subcategory, keywords in subcats.items():
            
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    categories.add(category)
                    tags.add(subcategory)
                    break

    if not categories:
        categories.add("News")
        tags.add("Latest")

    return list(categories),list(tags)'''

def fetch_articles(max_articles=None, priority=False):
    """
    Fetch articles from Google News
    
    Args:
        max_articles: Maximum number of articles to fetch (None for unlimited)
        priority: If True, focus on breaking news and urgent updates
    """
    all_data = {}
    
    # Adjust cutoff date based on priority mode  
    if priority:
        cutoff_date = datetime.utcnow() - timedelta(hours=2)  # Only very recent for priority
        keywords = ["breaking health news", "urgent health alert", "health emergency"]
    else:
        cutoff_date = datetime.utcnow() - timedelta(days=10)
        keywords = SCRAPE_KEYWORDS
    
    total_articles = 0

    for keyword in keywords:
        rss_url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(rss_url)
        entries = feed.entries
        print(f"Found {len(entries)} results")
        time.sleep(1)
        
        articles = []
        for entry in entries:
            if hasattr(entry, "published_parsed"):
                published = datetime(*entry.published_parsed[:6])
                if published < cutoff_date:
                    continue  # Skip old articles
            else:
                continue

            original_link = entry.get("link")
            real_url, html = get_real_url_with_selenium(original_link)
            if not real_url or not html:
                continue

            content = extract_article_content(real_url, html)
            if content:
                categories,tags = get_zero_shot_categories(content["text"] + " " + content["headline"])
                
                # Check for breaking news indicators
                title_lower = content["headline"].lower()
                breaking_indicators = ["breaking", "urgent", "alert", "emergency", "critical", "just in"]
                
                if any(indicator in title_lower for indicator in breaking_indicators):
                    if "breaking_news" not in tags:
                        tags.append("breaking_news")
                    if "news" not in categories:
                        categories.append("news")
                
                # Check for recent developments (within last 24 hours)
                if published > datetime.utcnow() - timedelta(hours=24):
                    if "recent_developments" not in tags:
                        tags.append("recent_developments")
                    if "news" not in categories:
                        categories.append("news")
                
                article_data = {
                    "date": published.strftime("%Y-%m-%d"),
                    "title": content["headline"],
                    "authors": content["author"] or entry.get("source", {}).get("title", ""),
                    "summary": content["summary"],
                    "url": real_url,
                    "categories": categories,
                    "tags": tags
                }
                save_as_markdown(article_data)
                save_to_db(article_data)
                articles.append(article_data)
                
                total_articles += 1
                if max_articles and total_articles >= max_articles:
                    all_data[keyword] = articles
                    return all_data

        all_data[keyword] = articles
        time.sleep(1)
        
        # Check if we've reached the max articles limit
        if max_articles and total_articles >= max_articles:
            break

    return all_data

if __name__ == "__main__":
    fetch_articles()
