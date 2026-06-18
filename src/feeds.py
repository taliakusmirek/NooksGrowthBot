"""
RSS/Atom feed definitions for all monitored sources.

GOOGLE ALERTS SETUP (do this once):
  1. Go to google.com/alerts
  2. Create alerts → Deliver to RSS feed → copy URL
  3. Paste into GOOGLE_ALERTS_FEEDS below
"""

AI_STARTUP_FEEDS = [
    {"name": "Techmeme", "url": "https://www.techmeme.com/feed.xml", "category": "AI Startup"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage?count=30", "category": "AI Startup"},
    {"name": "Hacker News Ask", "url": "https://hnrss.org/ask?count=15", "category": "AI Startup"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/feed", "category": "AI Startup"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI Startup"},
    {"name": "Vercel Blog", "url": "https://vercel.com/atom", "category": "AI Startup"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "AI Startup"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "AI Startup"},
    {"name": "YC Blog", "url": "https://www.ycombinator.com/blog/rss.xml", "category": "AI Startup"},
        {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/feed/", "category": "AI Startup"},
    {"name": "TLDR AI", "url": "https://tldr.tech/rss/ai.rss", "category": "AI Startup"},
    {"name": "Import AI", "url": "https://jack-clark.net/feed/", "category": "AI Startup"},
    ]

GTM_SALES_FEEDS = [
    {"name": "Sales Hacker", "url": "https://www.saleshacker.com/feed/", "category": "GTM/Sales"},
    {"name": "HubSpot Sales", "url": "https://blog.hubspot.com/sales/rss.xml", "category": "GTM/Sales"},
    {"name": "Clay Blog", "url": "https://www.clay.com/blog/rss.xml", "category": "GTM/Sales"},
    {"name": "Lenny's Newsletter", "url": "https://www.lennysnewsletter.com/feed", "category": "GTM/Sales"},
    {"name": "The GTM Newsletter", "url": "https://thegtmnewsletter.substack.com/feed", "category": "GTM/Sales"},
    {"name": "Kyle Poyar Growth Unhinged", "url": "https://kylepoyar.substack.com/feed", "category": "GTM/Sales"},
]

CULTURE_FEEDS = [
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "Culture"},
    {"name": "Mashable", "url": "https://mashable.com/feeds/rss/all", "category": "Weird Internet"},
    {"name": "Defector", "url": "https://defector.com/feed", "category": "Culture"},
    {"name": "Know Your Meme", "url": "https://knowyourmeme.com/newsfeed.rss", "category": "Weird Internet"},
    {"name": "Billboard", "url": "https://www.billboard.com/feed/", "category": "Culture"},
    {"name": "Pitchfork News", "url": "https://pitchfork.com/rss/news/", "category": "Culture"},
]

NOOKS_FEEDS = []

GOOGLE_ALERTS_FEEDS = [
    # {"name": "Alert: AI sales dialer", "url": "https://www.google.com/alerts/feeds/...", "category": "GTM/Sales"},
    # {"name": "Alert: Nooks mentions", "url": "https://www.google.com/alerts/feeds/...", "category": "Nooks Customer"},
]

ALL_FEEDS = AI_STARTUP_FEEDS + GTM_SALES_FEEDS + CULTURE_FEEDS + NOOKS_FEEDS + GOOGLE_ALERTS_FEEDS
