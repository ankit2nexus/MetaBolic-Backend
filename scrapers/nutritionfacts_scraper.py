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
CONTENT_PATH = BASE_DIR / "content" / "nutritionfacts"
DB_PATH = BASE_DIR / "db" / "articles.db"
CATEGORY_YAML_PATH = BASE_DIR / "config" / "category_keywords.yml"

RSS_URL = "https://nutritionfacts.org/feed/"
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
author: "{item['authors']}"
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

def fetch_nutrition_rss():
    feed = feedparser.parse(RSS_URL)
    items = feed.entries
    print(f"📥 Found {len(items)} RSS items")

    for entry in items:
        title = entry.get("title", "")
        url = entry.get("link", "")
        authors = entry.get("dc_creator", "")
        summary = entry.get("description", "")
        pub_date = entry.get("published")
        raw_tags = entry.get("tags", [])

        tag_list = [tag['term'] for tag in raw_tags if 'term' in tag]

        classification_text = f"{title} {summary} {' '.join(tag_list)}"

        categories, tags = get_zero_shot_categories(classification_text)

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

    print("🎉 Finished scraping NutritionFacts.org RSS.")

if __name__ == "__main__":
    fetch_nutrition_rss()