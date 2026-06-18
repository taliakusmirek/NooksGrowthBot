"""
HTML scrapers for sources without usable RSS feeds.
"""

import hashlib
import logging
import re
import time
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
}


def _story_id(url, title):
    return hashlib.md5("{}{}".format(url, title).encode()).hexdigest()

def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def _base(source, category, url, headline, summary=""):
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
            stories.append(_base("Techmeme", "AI Startup", url, title, "Via {}".format(src_name)))
        log.info("Techmeme scrape -> %d stories", len(stories))
    except Exception as e:
        log.warning("Techmeme scrape failed: %s", e)
    return stories


def scrape_anthropic():
    stories = []
    try:
        resp = requests.get("https://www.anthropic.com/news", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        seen = set()
        for a in soup.select("a[href*='/news/']"):
            title = a.get_text(strip=True)
            href = a.get("href", "")
            if not title or not href or len(title) < 10:
                continue
            url = href if href.startswith("http") else "https://www.anthropic.com" + href
            if url in seen:
                continue
            seen.add(url)
            stories.append(_base("Anthropic News", "AI Startup", url, title))
            if len(stories) >= 10:
                break
        log.info("Anthropic scrape -> %d stories", len(stories))
    except Exception as e:
        log.warning("Anthropic scrape failed: %s", e)
    return stories


def scrape_a16z():
    stories = []
    try:
        resp = requests.get("https://a16z.com/news-content/", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        seen = set()
        for a in soup.select("a[href*='a16z.com']"):
            title = a.get_text(strip=True)
            url = a.get("href", "")
            if not title or not url or len(title) < 10:
                continue
            if url in seen or "/news-content/" in url or url == "https://a16z.com/":
                continue
            seen.add(url)
            stories.append(_base("a16z", "AI Startup", url, title))
            if len(stories) >= 10:
                break
        log.info("a16z scrape -> %d stories", len(stories))
    except Exception as e:
        log.warning("a16z scrape failed: %s", e)
    return stories


def scrape_rundown():
    stories = []
    try:
        resp = requests.get("https://www.therundown.ai/", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        seen = set()
        for a in soup.select("a[href]"):
            title = a.get_text(strip=True)
            url = a.get("href", "")
            if not title or not url or len(title) < 15:
                continue
            if not url.startswith("http"):
                continue
            if url in seen:
                continue
            seen.add(url)
            stories.append(_base("The Rundown AI", "AI Startup", url, title))
            if len(stories) >= 8:
                break
        log.info("Rundown scrape -> %d stories", len(stories))
    except Exception as e:
        log.warning("Rundown scrape failed: %s", e)
    return stories


def scrape_reddit_oauth():
    """
    Fetch Reddit posts using OAuth (required for reliable access).
    Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET in .env to enable.
    Without these, Reddit blocks anonymous RSS requests with 429.
    """
    client_id = __import__("os").environ.get("REDDIT_CLIENT_ID", "")
    client_secret = __import__("os").environ.get("REDDIT_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        log.info("Reddit OAuth not configured — skipping (set REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET)")
        return []

    stories = []
    subreddits = [
        ("r/artificial", "AI Startup"),
        ("r/MachineLearning", "AI Startup"),
        ("r/LocalLLaMA", "AI Startup"),
        ("r/startups", "AI Startup"),
        ("r/sales", "GTM/Sales"),
        ("r/salesforce", "GTM/Sales"),
        ("r/OutOfTheLoop", "Weird Internet"),
        ("r/todayilearned", "Weird Internet"),
        ("r/worldnews", "Culture"),
        ("r/nba", "Culture"),
        ("r/formula1", "Culture"),
    ]

    try:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        token_resp = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": "NooksGrowthBot/1.0 by nooks_growth"},
            timeout=10,
        )
        token_resp.raise_for_status()
        token = token_resp.json().get("access_token", "")
        if not token:
            log.warning("Reddit OAuth token empty")
            return []

        api_headers = {
            "Authorization": "Bearer {}".format(token),
            "User-Agent": "NooksGrowthBot/1.0 by nooks_growth",
        }

        for sub, category in subreddits:
            try:
                r = requests.get(
                    "https://oauth.reddit.com/{}/hot.json?limit=10".format(sub),
                    headers=api_headers,
                    timeout=10,
                )
                r.raise_for_status()
                for post in r.json().get("data", {}).get("children", []):
                    d = post.get("data", {})
                    title = d.get("title", "")
                    url = d.get("url", "")
                    permalink = "https://reddit.com" + d.get("permalink", "")
                    if title and url:
                        stories.append(_base(sub, category, url, title, "Via {}".format(permalink)))
                time.sleep(1)
            except Exception as e:
                log.warning("Reddit %s failed: %s", sub, e)

        log.info("Reddit OAuth -> %d stories", len(stories))
    except Exception as e:
        log.warning("Reddit OAuth setup failed: %s", e)

    return stories


def scrape_x_trends():
    stories = []
    try:
        resp = requests.get("https://trends24.in/united-states/", headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        card = soup.select_one(".trend-card") or soup
        seen = set()
        for item in (card.select("ol li a") or card.select("li a"))[:40]:
            name = item.get_text(strip=True)
            if not name or name in seen or len(name) < 2:
                continue
            seen.add(name)
            url = "https://twitter.com/search?q={}&src=trend_click".format(quote_plus(name))
            stories.append(_base("X Trending", "Weird Internet", url, "Trending on X: {}".format(name)))
        log.info("X trends scrape -> %d trends", len(stories))
    except Exception as e:
        log.warning("X trends scrape failed: %s", e)
    return stories


def scrape_all():
    results = []
    results.extend(scrape_techmeme())
    results.extend(scrape_anthropic())
    results.extend(scrape_a16z())
    results.extend(scrape_rundown())
    results.extend(scrape_reddit_oauth())
    results.extend(scrape_x_trends())
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stories = scrape_all()
    for s in stories[:10]:
        print("[{}] {}".format(s["source"], s["headline"]))
    print("Total: {}".format(len(stories)))
