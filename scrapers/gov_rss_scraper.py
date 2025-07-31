import feedparser
import os
import re
import sqlite3
import yaml
import json
from datetime import datetime
from pathlib import Path 
from slugify import slugify
from api.utils import normalize_datetime, get_zero_shot_categories

BASE_DIR = Path(__file__).resolve().parent.parent 
CONTENT_PATH = BASE_DIR / "content" / "gov_rss"
DB_PATH = BASE_DIR / "db" / "articles.db"
CATEGORY_YAML_PATH = BASE_DIR / "config" / "category_keywords.yml"

RSS_URL = "https://services.india.gov.in/feed/rss?cat_id=5&ln=en"
'''def load_category_keywords():
    with open(CATEGORY_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CATEGORY_KEYWORDS = load_category_keywords()

def get_fuzzy_categories(text):
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
        tags.add("Govt_Schemes_and_Announcements")

    return list(categories), list(tags)'''

def save_as_markdown(item):
    date_str = datetime.today().strftime("%Y-%m-%d")
    title = item["title"]
    slug = slugify(title if title else "untitled")
    filename = f"{date_str}-{slug}.md"
    filepath = CONTENT_PATH / filename

    CONTENT_PATH.mkdir(parents=True, exist_ok=True)

    markdown = f"""---
title: "{title}"
date: {date_str}
categories: {item['categories']}
tags: {item['tags']}
source_url: {item['url']}
summary: "{item['summary']}"
author: "Govt of India"
---

{item['summary']}

Read full details → [here]({item['url']})
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Saved: {filepath}")

def save_to_db(item):
    os.makedirs(CONTENT_PATH, exist_ok=True)
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

    cur.execute("""
        INSERT INTO articles (date, title, authors, summary, url, categories,tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        normalize_datetime(item["date"]),
        item["title"],
        item["authors"],
        item["summary"],
        item["url"],
        json.dumps(item["categories"]),
        json.dumps(item["tags"])
    ))

    conn.commit()
    conn.close()

def fetch_gov_rss():
    feed = feedparser.parse(RSS_URL)
    items = feed.entries
    print(f"📥 Found {len(items)} RSS items")

    for entry in items:
        title = entry.get("title", "")
        url = entry.get("link", "")
        authors = ""
        summary = entry.get("description", "")
        pub_date = entry.get("published")
        categories, tags = get_zero_shot_categories(title + " " + summary)

        item = {
            "title": title,
            "url": url,
            "authors": authors,
            "summary": summary,
            "date": pub_date,
            "categories": categories,
            "tags": tags
        }

        save_as_markdown(item)
        save_to_db(item)

    print("🎉 Finished scraping Government RSS.")

if __name__ == "__main__":
    fetch_gov_rss()