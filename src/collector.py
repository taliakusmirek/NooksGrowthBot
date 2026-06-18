"""
Daily feed collector -- fetches RSS/Atom feeds, deduplicates, and returns
raw story dicts ready for scoring.
"""

import hashlib
import time
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

from feeds import ALL_FEEDS
from scraper import scrape_all

log = logging.getLogger(__name__)

SEEN_FILE = Path(__file__).parent.parent / "data" / "seen_stories.json"
INBOX_FILE = Path(__file__).parent.parent / "data" / "trend_inbox.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; NooksGrowthBot/1.0; "
        "+https://github.com/taliakusmirek/nooksgrowthbot)"
    )
}
REDDIT_HEADERS = {
    "User-Agent": "NooksGrowthBot/1.0 by nooks_growth_bot"
}


def _story_id(url, title):
    return hashlib.md5(f"{url}{title}".encode()).hexdigest()


def _load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def _save_seen(seen):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(list(seen)))


def _cutoff():
    return datetime.now(timezone.utc) - timedelta(hours=48)


def _parse_date(entry):
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def _clean_summary(raw):
    soup = BeautifulSoup(raw or "", "lxml")
    text = soup.get_text(separator=" ").strip()
    return text[:500]


def fetch_feed(feed_def, seen, cutoff):
    stories = []
    try:
        hdrs = REDDIT_HEADERS if "reddit.com" in feed_def["url"] else HEADERS
        resp = requests.get(feed_def["url"], headers=hdrs, timeout=15)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.text)
    except Exception as e:
        log.warning("Feed %s failed: %s", feed_def["name"], e)
        return stories

    for entry in parsed.entries:
        url = getattr(entry, "link", "")
        title = getattr(entry, "title", "").strip()
        if not url or not title:
            continue
        sid = _story_id(url, title)
        if sid in seen:
            continue
        pub = _parse_date(entry)
        if pub < cutoff:
            continue
        summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
        stories.append({
            "id": sid,
            "date": pub.strftime("%Y-%m-%d"),
            "source": feed_def["name"],
            "category": feed_def["category"],
            "link": url,
            "headline": title,
            "summary": _clean_summary(summary_raw),
            "why_it_matters": "",
            "virality_signal": "",
            "nooks_angle": "",
            "scores": {},
            "keep": None,
        })
        seen.add(sid)

    log.info("Feed %-25s -> %d new stories", feed_def["name"], len(stories))
    return stories


def collect_all():
    seen = _load_seen()
    cutoff = _cutoff()
    all_stories = []

    for feed_def in ALL_FEEDS:
        all_stories.extend(fetch_feed(feed_def, seen, cutoff))

    scraped = scrape_all()
    for story in scraped:
        if story["id"] in seen:
            continue
        seen.add(story["id"])
        all_stories.append(story)
    log.info("Scrapers -> %d new stories", len(scraped))

    _save_seen(seen)

    INBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if INBOX_FILE.exists():
        existing = json.loads(INBOX_FILE.read_text())
    existing.extend(all_stories)
    INBOX_FILE.write_text(json.dumps(existing, indent=2))

    log.info("Collected %d new stories total", len(all_stories))
    return all_stories


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stories = collect_all()
    print(f"Fetched {len(stories)} new stories")
