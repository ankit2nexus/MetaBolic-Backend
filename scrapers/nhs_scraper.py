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
CONTENT_PATH = BASE_DIR / "content" / "nhsUK"
DB_PATH = BASE_DIR / "db" / "articles.db"
CATEGORY_YAML_PATH = BASE_DIR / "config" / "category_keywords.yml"

class NHSscraper:
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

        # === Title ===
        title_el = soup.select_one('h1')
        if title_el:
            data['title'] = title_el.get_text(strip=True)
        else:
            title_tag = soup.find('title')
            data['title'] = title_tag.get_text(strip=True) if title_tag else "Title not found"

        # === Content Paragraphs ===
        paragraphs = []
        article_container = soup.find("article")
        if article_container:
            for section in article_container.find_all("section"):
                for p in section.find_all("p"):
                    text = p.get_text(strip=True)
                    if text and len(text) > 50:
                        paragraphs.append(text)

        # Fallback: check all <p> if still insufficient
        if len(paragraphs) < 3:
            all_paras = soup.find_all('p')
            for p in all_paras:
                text = p.get_text(strip=True)
                if text and len(text) > 50:
                    paragraphs.append(text)

        data['content_paragraphs'] = paragraphs

        # === Date ===
        date_meta = soup.find("meta", attrs={"property": "article:modified_time"})
        if date_meta and date_meta.get("content"):
            data['date'] = date_meta["content"][:10]
        else:
            data['date'] = datetime.today().strftime("%Y-%m-%d")

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

def fetch_nhs_articles():
    urls = [
        "https://www.nhs.uk/mental-health/conditions/depression/",
        "https://www.nhs.uk/mental-health/conditions/depression-in-adults/",
        "https://www.nhs.uk/conditions/diabetes/",
        "https://www.nhs.uk/conditions/type-1-diabetes/"
        "https://www.nhs.uk/conditions/type-2-diabetes/",
       "https://www.nhs.uk/conditions/gestational-diabetes/",
        "https://www.nhs.uk/conditions/diabetes-insipidus/",
        "https://www.nhs.uk/conditions/diabetic-ketoacidosis/",
        "https://www.nhs.uk/conditions/diabetic-retinopathy/",
        "https://www.nhs.uk/conditions/diverticular-disease-and-diverticulitis/",
        "https://www.nhs.uk/conditions/ear-infections/",
        "https://www.nhs.uk/conditions/earwax-build-up/",
        "https://www.nhs.uk/conditions/contact-dermatitis/",
        "https://www.nhs.uk/conditions/erection-problems-erectile-dysfunction/",
        "https://www.nhs.uk/conditions/herpes-simplex-eye-infections/",
        "https://www.nhs.uk/conditions/eye-injuries/",
        "https://www.nhs.uk/conditions/food-allergy/",
        "https://www.nhs.uk/conditions/food-intolerance/",
        "https://www.nhs.uk/conditions/heartburn-and-acid-reflux/",
        "https://www.nhs.uk/mental-health/conditions/generalised-anxiety-disorder-gad/",
        "https://www.nhs.uk/conditions/gestational-diabetes/",
        "https://www.nhs.uk/conditions/haemochromatosis/",
        "https://www.nhs.uk/conditions/haemophilia/",
        "https://www.nhs.uk/conditions/hib/",
        "https://www.nhs.uk/conditions/hearing-loss/",
        "https://www.nhs.uk/conditions/heart-attack/",
        "https://www.nhs.uk/conditions/heart-block/",
        "https://www.nhs.uk/conditions/coronary-heart-disease/",
        "https://www.nhs.uk/conditions/heart-failure/",
        "https://www.nhs.uk/conditions/heart-valve-disease/",
        "https://www.nhs.uk/conditions/heartburn-and-acid-reflux/",
        "https://www.nhs.uk/conditions/heat-exhaustion-heatstroke/",
        "https://www.nhs.uk/conditions/high-blood-pressure/",
        "https://www.nhs.uk/conditions/low-blood-pressure-hypotension/",
        "https://www.nhs.uk/conditions/hypoparathyroidism/",
        "https://www.nhs.uk/conditions/overactive-thyroid-hyperthyroidism/",
        "https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/",
        "https://www.nhs.uk/conditions/underactive-thyroid-hypothyroidism/",
        "https://www.nhs.uk/conditions/infertility/",
        "https://www.nhs.uk/conditions/insomnia/",
        "https://www.nhs.uk/conditions/iron-deficiency-anaemia/",
        "https://www.nhs.uk/conditions/keratosis-pilaris/",
        "https://www.nhs.uk/conditions/kidney-disease/",
        "https://www.nhs.uk/conditions/kidney-infection/",
        "https://www.nhs.uk/conditions/liver-disease/",
        "https://www.nhs.uk/conditions/alcohol-related-liver-disease-arld/",
        "https://www.nhs.uk/conditions/melanoma-skin-cancer/",
        "https://www.nhs.uk/conditions/metabolic-syndrome/",
        "https://www.nhs.uk/conditions/non-alcoholic-fatty-liver-disease/",
        "https://www.nhs.uk/conditions/non-melanoma-skin-cancer/",
        "https://www.nhs.uk/conditions/obesity/",
        "https://www.nhs.uk/mental-health/conditions/personality-disorder/",
        "https://www.nhs.uk/conditions/polycystic-ovary-syndrome-pcos/",
        "https://www.nhs.uk/mental-health/conditions/post-natal-depression/",
        "https://www.nhs.uk/mental-health/conditions/post-partum-psychosis/",
        "https://www.nhs.uk/conditions/sleep-apnoea/",
        "https://www.nhs.uk/conditions/sleep-paralysis/",
        "https://www.nhs.uk/mental-health/conditions/social-anxiety/",
        "https://www.nhs.uk/conditions/thyroid-cancer/",
        "https://www.nhs.uk/conditions/vitamin-b12-or-folate-deficiency-anaemia/",
        "https://www.nhs.uk/womens-health/",
        "https://www.nhs.uk/conditions/adhd-adults/",
        "https://www.nhs.uk/conditions/adhd-children-teenagers/",
        "https://www.nhs.uk/conditions/alcohol-misuse/",
        "https://www.nhs.uk/conditions/alcohol-poisoning/",
        "https://www.nhs.uk/conditions/alcohol-related-liver-disease-arld/",
        "https://www.nhs.uk/conditions/iron-deficiency-anaemia/",
        "https://www.nhs.uk/conditions/vitamin-b12-or-folate-deficiency-anaemia/",
        "https://www.nhs.uk/mental-health/children-and-young-adults/advice-for-parents/anxiety-disorders-in-children/",
        "https://www.nhs.uk/mental-health/conditions/bipolar-disorder/",
        "https://www.nhs.uk/mental-health/conditions/binge-eating/",
        "https://www.nhs.uk/conditions/high-blood-pressure/",
        "https://www.nhs.uk/conditions/low-blood-pressure-hypotension/",
        "https://www.nhs.uk/conditions/cardiomyopathy/",
        "https://www.nhs.uk/conditions/cardiovascular-disease/",
        "https://www.nhs.uk/conditions/high-cholesterol/",
        "https://www.nhs.uk/conditions/cirrhosis/",
        "https://www.nhs.uk/conditions/contact-dermatitis/"
    ]

    scraper = NHSscraper(headless=True)
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
    fetch_nhs_articles()