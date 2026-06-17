"""
HTML scrapers for sources without usable RSS feeds.
Targets: Techmeme homepage, X/Twitter trending via trends24.in
"""

import hashlib
import logging
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def _story_id(url, title):
    return hashlib.md5(f"{url}{title}".encode()).hexdigest()


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _base_story(source, category, url, headline, summary=""):
    return {
        "id": _story_id(url, headline),
        "date": _today(),
        "source": source,
        "category": category,
        "link": url,
        "headline": headline,
        "summary": summary,
        "why_it_matters": "",
        "virality_signal": "",
        "nooks_angle": "",
        "scores": {},
        "keep": None,
    }


def scrape_techmeme():
    stories = []
    try:
        resp = requests.get("https://www.techmeme.com/", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        seen = set()
        for cluster in soup.select("div.clus"):
            lead = cluster.select_one("strong > a") or cluster.select_one(".ii a")
            if not lead:
                continue
            title = lead.get_text(strip=True)
            url = lead.get("href", "").strip()
            if not url or not title or url in seen:
                continue
            if not url.startswith("http"):
                url = "https://www.techmeme.com" + url
            seen.add(url)
            src_el = cluster.select_one(".src a") or cluster.select_one("cite")
            src_name = src_el.get_text(strip=True) if src_el else "Techmeme"
            discussion_items = cluster.select("li .ii a")
            related = "; ".join(a.get_text(strip=True) for a in discussion_items[:3])
            summary = f"Via {src_name}. Related: {related}" if related else f"Via {src_name}"
            stories.append(_base_story("Techmeme", "AI Startup", url, title, summary))
        log.info("Techmeme scrape -> %d stories", len(stories))
    except Exception as e:
        log.warning("Techmeme scrape failed: %s", e)
    return stories


def scrape_x_trends():
    stories = []
    try:
        resp = requests.get("https://trends24.in/united-states/", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        card = soup.select_one(".trend-card") or soup.select_one("#trend-list") or soup
        seen_names = set()
        items = card.select("ol li a") or card.select("ul.trend-list li a") or card.select("li a[href*='twitter']")
        for item in items[:40]:
            name = item.get_text(strip=True)
            if not name or name in seen_names or len(name) < 2:
                continue
            seen_names.add(name)
            count_el = (
                item.find_next_sibling("span")
                or item.parent.select_one(".tweet-count")
                or item.parent.select_one("span")
            )
            count_text = count_el.get_text(strip=True) if count_el else ""
            numeric = re.sub(r"[^\d.]", "", count_text.replace("K", "000").replace("M", "000000"))
            if numeric:
                try:
                    if float(numeric) < 5000:
                        continue
                except ValueError:
                    pass
            search_url = f"https://twitter.com/search?q={quote_plus(name)}&src=trend_click"
            summary = f"Trending on X (Twitter){f' -- {count_text}' if count_text else ''}. US trend as of {_today()}."
            stories.append(_base_story("X Trending", "Weird Internet", search_url, f"Trending on X: {name}", summary))
        log.info("X trends scrape -> %d trends", len(stories))
    except Exception as e:
        log.warning("X trends scrape failed: %s", e)
    return stories


def scrape_all():
    results = []
    results.extend(scrape_techmeme())
    results.extend(scrape_x_trends())
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stories = scrape_all()
    for s in stories[:10]:
        print(f"[{s['source']}] {s['headline']}")
    print(f"\nTotal: {len(stories)}")
