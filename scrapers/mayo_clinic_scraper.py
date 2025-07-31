import time
import re
import os
import json
import sqlite3
import yaml
from datetime import datetime
from pathlib import Path
from slugify import slugify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import hashlib
from api.utils import normalize_datetime, get_zero_shot_categories

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_PATH = BASE_DIR / "content" / "mayo_clinic"
DB_PATH = BASE_DIR / "db" / "articles.db"
CATEGORY_YAML_PATH = BASE_DIR / "config" / "category_keywords.yml"

class MayoClinicScraper:
    def __init__(self, headless=True):
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

    '''@staticmethod
    def load_category_keywords():
        with open(CATEGORY_YAML_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    CATEGORY_KEYWORDS = load_category_keywords.__func__()

    @staticmethod
    def get_fuzzy_categories(text):
        categories = set()
        tags = set()
        text_lower = text.lower()
        for category, subcats in MayoClinicScraper.CATEGORY_KEYWORDS.items():
            for subcategory, keywords in subcats.items():
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                        categories.add(category)
                        tags.add(subcategory)
                        break
        if not categories:
            categories.add("Solutions")
            tags.add(["Nutrition","Fitness","Wellness","Lifestyle"])

        return list(categories), list(tags)'''

    @staticmethod
    def save_as_markdown(article_data):
        date_str = article_data.get('date', datetime.today().strftime("%Y-%m-%d"))[:10]
        title = article_data.get('title', 'Untitled')
        slug = slugify(title)
        url_hash = hashlib.md5(article_data.get('url').encode('utf-8')).hexdigest()[:8]
        filename = f"{date_str}-{slug}-{url_hash}.md"

        filepath = CONTENT_PATH / filename
        CONTENT_PATH.mkdir(parents=True, exist_ok=True)

        categories = article_data.get('categories', ["Solutions"])
        tags = article_data.get('tags', ["Nutrition","Fitness","Wellness","Lifestyle"])
        authors = article_data.get('authors', "")
        summary = article_data.get('summary', '')

        markdown = f"""---
title: \"{title}\"
date: {date_str}
categories: {categories}
tags: {tags}
source_url: {article_data.get('url')}
author: \"{authors}\"
summary: \"{summary}\"
---

{summary}

Read full article → [here]({article_data.get('url')})
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"✅ Saved: {filepath}")

    @staticmethod
    def save_to_db(article_data):
        os.makedirs(DB_PATH.parent, exist_ok=True)
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
        categories_json = json.dumps(article_data.get('categories', []))
        tags_json = json.dumps(article_data.get('tags', []))
        cur.execute(
            """
            INSERT INTO articles (date, title, authors, summary, url, categories, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalize_datetime(article_data.get('date')),
                article_data.get('title'),
                article_data.get('authors'),
                article_data.get('summary'),
                article_data.get('url'),
                categories_json,
                tags_json
            )
        )
        conn.commit()
        conn.close()

    def scrape_article(self, url):
        driver = webdriver.Chrome(options=self.chrome_options)
        try:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            article_data = self.extract_article_data(soup)
            return article_data
        finally:
            driver.quit()

    def extract_article_data(self, soup):
        data = {}
        
        # Title
        byline_title = soup.select_one('div.by > h2')
        if byline_title:
            data['title'] = byline_title.get_text(strip=True)
        else:
            # Fallbacks
            title_el = soup.select_one('main h2') or soup.select_one('article h2') or soup.select_one('h1')
            if title_el and len(title_el.get_text(strip=True)) > 10:
                data['title'] = title_el.get_text(strip=True)
            else:
                title_tag = soup.find('title')
                data['title'] = title_tag.get_text(strip=True) if title_tag else "Title not found"
        
        # Content paragraphs
        paragraphs = []
        # Target article content divs more specifically
        content_selectors = ['.content', '.main-content', '.article', 'article', 'main']
        skip_terms = ['appointment', 'subscribe', 'newsletter', 'request appointment']
        for selector in content_selectors:
            container = soup.select_one(selector)
            if container:
                for p in container.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 50 and not any(term in text.lower() for term in skip_terms):
                        paragraphs.append(text)
                if len(paragraphs) >= 3:
                    break

        # Fallback: check all <p> tags if still not enough
        if len(paragraphs) < 3:
            all_paras = soup.find_all('p')
            for p in all_paras:
                text = p.get_text(strip=True)
                if text and len(text) > 50 and not any(term in text.lower() for term in skip_terms):
                    paragraphs.append(text)

        data['content_paragraphs'] = paragraphs
        # Date
        date_el = soup.select_one('time[datetime]')
        data['date'] = date_el.get('datetime', '')[:10] if date_el else datetime.today().strftime("%Y-%m-%d")
        return data

    def summarize_content(self, article_data):
        summary = {}
        headings_text = [h['text'] for h in article_data.get('headings', [])]
        summary['main_topics'] = headings_text[:10]

        summary['title'] = headings_text[2] if len(headings_text) >= 3 else article_data.get('title', 'Title not available')
        summary['date'] = article_data.get('date')
        preview = article_data.get('content_paragraphs', [])[:3]
        summary['content_preview'] = preview
        return summary

    def store_info(self, summary, url):
        title = summary['title']
        date = summary['date']
        preview_list = summary.get('content_preview', [])
        content = " ".join(
            (para[:300] + ('...' if len(para) > 300 else ''))
            for para in preview_list
        )
        categories,tags = get_zero_shot_categories(title + " " + content)
        authors = ""
        return {
            'title': title,
            'date': date,
            'summary': content,
            'url': url,
            'categories': categories,
            'tags': tags,
            'authors': authors
        }

def fetch_mayo_articles():
    urls = [
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/alcohol/art-20044551",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/add-antioxidants-to-your-diet/art-20546814",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/artificial-sweeteners/art-20046936",
        "https://www.mayoclinic.org/healthy-lifestyle/infant-and-toddler-health/in-depth/breastfeeding-nutrition/art-20046912",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/caffeine/art-20049372",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/caffeine/art-20045678",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/calcium-supplements/art-20047097",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/carbohydrates/art-20045705",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/high-fiber-foods/art-20050948",
        "https://www.mayoclinic.org/diseases-conditions/high-blood-cholesterol/in-depth/cholesterol/art-20045192",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/clear-liquid-diet/art-20048505",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/cuts-of-beef/art-20043833",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/dash-diet/art-20048456",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/dash-diet/art-20050989",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/fat/art-20045550",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/fiber/art-20043983",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/diverticulitis-diet/art-20048499",
        "https://www.mayoclinic.org/first-aid/first-aid-food-borne-illness/basics/art-20056689",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/gluten-free-diet/art-20048530",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/gout-diet/art-20048524",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/spices/art-20546798",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/10-great-health-foods/art-20546837",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/healthy-meals/art-20546806",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/low-fiber-diet/art-20048511",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/low-glycemic-index-diet/art-20048478",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/meatless-meals/art-20048193",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/mediterranean-diet/art-20047801",
        "https://www.mayoclinic.org/diseases-conditions/heart-disease/in-depth/heart-healthy-diet/art-200467020,"
        "https://www.mayoclinic.org/nutrition-and-pain/art-20208638",
        "https://www.mayoclinic.org/diseases-conditions/heart-disease/in-depth/nuts/art-20046635",
        "https://www.mayoclinic.org/diseases-conditions/heart-disease/in-depth/omega-3/art-20045614",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/organic-food/art-20043880",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/paleo-diet/art-201111820",
        "https://www.mayoclinic.org/healthy-lifestyle/weight-loss/in-depth/portion-control/art-20546800",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/dash-diet/art-20047110",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/sodium/art-20045479",
        "https://www.mayoclinic.org/diseases-conditions/high-blood-cholesterol/in-depth/trans-fat/art-20046114",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/vegetarian-diet/art-20046446",
        "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/whole-grains/art-20047826"                
        ]
    
    scraper = MayoClinicScraper(headless=True)
    for url in urls:
        data = scraper.scrape_article(url)
        if data:
            summary = scraper.summarize_content(data)
            item = scraper.store_info(summary, url)
            scraper.save_as_markdown(item)
            scraper.save_to_db(item)
        else:
            print(f"❌ Failed to extract data from {url}")

if __name__ == "__main__":
    fetch_mayo_articles()
