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
CONTENT_PATH = BASE_DIR / "content" / "pubmed"
DB_PATH = BASE_DIR / "db" / "articles.db"
CATEGORY_YAML_PATH = BASE_DIR / "config" / "category_keywords.yml"

RSS_URL = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1fmfIeN4X5Q-Hdkw_Zel9wlu313Qu6Y7S0R_4gTI2id1yXK9M_/?limit=300&utm_campaign=pubmed-2&fc=20250715013751"
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

    return list(categories), list(tags)'''

def save_as_markdown(article_data):
    date_str = datetime.strptime(article_data["date"], "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
    title = article_data["title"]
    title = re.sub(r'[^\w\s-]', '', title).strip().lower()
    title = re.sub(r'[\s_-]+', '-', title)
    title = title[:90]

    slug = slugify(title if title else "untitled")
    filename = f"{date_str}-{slug}.md"
    filepath = CONTENT_PATH / filename

    CONTENT_PATH.mkdir(parents=True, exist_ok=True)

    markdown = f"""---
title: "{title}"
date: {date_str}
categories: {article_data['categories']}
tags: {article_data['tags']}
source_url: {article_data['url']}
summary: "{article_data['summary']}"
author: {article_data['authors']}
---

{article_data['summary']}

Read full details → [here]({article_data['url']})
"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Saved: {filepath}")

def save_to_db(article_data):
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

    categories_json = json.dumps(article_data["categories"])
    tags_json = json.dumps(article_data["tags"])

    cur.execute("""
        INSERT INTO articles (date, title, authors, summary, url, categories, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        normalize_datetime(article_data["date"]),
        article_data["title"],
        json.dumps(article_data["authors"]),
        article_data["summary"],
        article_data["url"],
        categories_json,
        tags_json
    ))

    conn.commit()
    conn.close()

def fetch_pubmed_articles():
    rss_url = "https://pubmed.ncbi.nlm.nih.gov/rss/search/14exR3zaRr4JG3vJxo7G7u-jOLuEnnUCPV7z8SYwVhC2w7dYBe/?limit=300&utm_campaign=pubmed-2&fc=20250722035645"
    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        title = entry.get("title", "Untitled")
        link = entry.get("link")
        summary = entry.get("description", "").strip()
        pubdate = entry.get("published", "")
        creators = entry.get("dc_creator")

        if isinstance(creators, list):
            authors = ", ".join(creators)
        elif isinstance(creators, str):
            authors = creators
        else:
            authors = entry.get("dc_creator", "") or entry.get("author", "")
        publisher = entry.get("dc_source", "PubMed")

        full_text = summary + " " + title
        categories,tags = get_zero_shot_categories(full_text)

        article_data = {
            "date": pubdate,
            "title":title,
            "authors": authors,
            "publisher": publisher,
            "summary": summary,
            "url": link,
            "categories": categories,
            "tags": tags
        }

        save_as_markdown(article_data)
        save_to_db(article_data)

if __name__ == "__main__":
    fetch_pubmed_articles()