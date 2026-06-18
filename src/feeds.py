"""
RSS/Atom feed definitions for all monitored sources.

GOOGLE ALERTS SETUP (do this once, ~10 minutes):
  1. Go to google.com/alerts
  2. Create an alert for each keyword below
  3. In alert settings -> "Deliver to" -> select "RSS feed"
  4. Click the RSS icon that appears -> copy the URL
  5. Paste into GOOGLE_ALERTS_FEEDS below
  Suggested keywords:
    - "AI sales" OR "AI dialer"
    - "sales development" trend
    - Clay OR Gong OR Outreach GTM
    - Nooks site:linkedin.com
    - viral startup
    - "revenue intelligence"
"""

AI_STARTUP_FEEDS = [
    {"name": "Techmeme", "url": "https://www.techmeme.com/feed.xml", "category": "AI Startup"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage?count=30", "category": "AI Startup"},
    {"name": "Hacker News Ask", "url": "https://hnrss.org/ask?count=15", "category": "AI Startup"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/feed", "category": "AI Startup"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI Startup"},
    {"name": "Anthropic News", "url": "https://www.anthropic.com/rss.xml", "category": "AI Startup"},
    {"name": "Vercel Blog", "url": "https://vercel.com/atom", "category": "AI Startup"},
    {"name": "The Rundown AI", "url": "https://www.therundown.ai/feed", "category": "AI Startup"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "AI Startup"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "AI Startup"},
    {"name": "YC Blog", "url": "https://www.ycombinator.com/blog/rss.xml", "category": "AI Startup"},
    {"name": "a16z", "url": "https://a16z.com/feed/", "category": "AI Startup"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/feed/", "category": "AI Startup"},
    {"name": "r/artificial", "url": "https://www.reddit.com/r/artificial/.rss?limit=25", "category": "AI Startup"},
    {"name": "r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/.rss?limit=25", "category": "AI Startup"},
    {"name": "r/startups", "url": "https://www.reddit.com/r/startups/.rss?limit=25", "category": "AI Startup"},
    {"name": "r/LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA/.rss?limit=25", "category": "AI Startup"},
    {"name": "TLDR AI", "url": "https://tldr.tech/rss/ai.rss", "category": "AI Startup"},
    {"name": "The Batch", "url": "https://www.deeplearning.ai/the-batch/feed/", "category": "AI Startup"},
    {"name": "Import AI", "url": "https://jack-clark.net/feed/", "category": "AI Startup"},
    {"name": "AI Breakfast", "url": "https://aibreakfast.beehiiv.com/feed", "category": "AI Startup"},
]

GTM_SALES_FEEDS = [
    {"name": "Sales Hacker", "url": "https://www.saleshacker.com/feed/", "category": "GTM/Sales"},
    {"name": "Gong Blog", "url": "https://www.gong.io/blog/rss/", "category": "GTM/Sales"},
    {"name": "HubSpot Sales", "url": "https://blog.hubspot.com/sales/rss.xml", "category": "GTM/Sales"},
    {"name": "Clay Blog", "url": "https://www.clay.com/blog/rss.xml", "category": "GTM/Sales"},
    {"name": "r/sales", "url": "https://www.reddit.com/r/sales/.rss?limit=25", "category": "GTM/Sales"},
    {"name": "r/salesforce", "url": "https://www.reddit.com/r/salesforce/.rss?limit=15", "category": "GTM/Sales"},
    {"name": "Lenny's Newsletter", "url": "https://www.lennysnewsletter.com/feed", "category": "GTM/Sales"},
    {"name": "Mostly Metrics", "url": "https://mostlymetrics.substack.com/feed", "category": "GTM/Sales"},
    {"name": "The GTM Newsletter", "url": "https://thegtmnewsletter.substack.com/feed", "category": "GTM/Sales"},
    {"name": "Demand Curve", "url": "https://newsletter.demandcurve.com/feed", "category": "GTM/Sales"},
    {"name": "Kyle Poyar Growth Unhinged", "url": "https://kylepoyar.substack.com/feed", "category": "GTM/Sales"},
]

CULTURE_FEEDS = [
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "Culture"},
    {"name": "Mashable", "url": "https://mashable.com/feeds/rss/all", "category": "Weird Internet"},
    {"name": "IFL Science", "url": "https://www.iflscience.com/rss.xml", "category": "Weird Internet"},
    {"name": "Defector", "url": "https://defector.com/feed", "category": "Culture"},
    {"name": "Vulture", "url": "https://www.vulture.com/rss/news.xml", "category": "Culture"},
    {"name": "Know Your Meme", "url": "https://knowyourmeme.com/newsfeed.rss", "category": "Weird Internet"},
    {"name": "Weird Universe", "url": "https://www.weirduniverse.net/blog/atom.xml", "category": "Weird Internet"},
    {"name": "r/OutOfTheLoop", "url": "https://www.reddit.com/r/OutOfTheLoop/.rss?limit=25", "category": "Weird Internet"},
    {"name": "r/todayilearned", "url": "https://www.reddit.com/r/todayilearned/.rss?limit=25", "category": "Weird Internet"},
    {"name": "r/interestingasfuck", "url": "https://www.reddit.com/r/interestingasfuck/.rss?limit=25", "category": "Weird Internet"},
    {"name": "r/worldnews", "url": "https://www.reddit.com/r/worldnews/.rss?limit=15", "category": "Culture"},
    {"name": "r/nba", "url": "https://www.reddit.com/r/nba/.rss?limit=15", "category": "Culture"},
    {"name": "r/formula1", "url": "https://www.reddit.com/r/formula1/.rss?limit=15", "category": "Culture"},
    {"name": "Billboard", "url": "https://www.billboard.com/feed/", "category": "Culture"},
    {"name": "Pitchfork News", "url": "https://pitchfork.com/rss/news/", "category": "Culture"},
]

NOOKS_FEEDS = [
    {"name": "Nooks Blog", "url": "https://www.nooks.in/blog/rss.xml", "category": "Nooks Product"},
]

GOOGLE_ALERTS_FEEDS = [
    # {"name": "Alert: AI sales dialer", "url": "https://www.google.com/alerts/feeds/...", "category": "GTM/Sales"},
    # {"name": "Alert: Nooks mentions", "url": "https://www.google.com/alerts/feeds/...", "category": "Nooks Customer"},
    # {"name": "Alert: GTM trends", "url": "https://www.google.com/alerts/feeds/...", "category": "GTM/Sales"},
    # {"name": "Alert: viral startup", "url": "https://www.google.com/alerts/feeds/...", "category": "AI Startup"},
]

ALL_FEEDS = (
    AI_STARTUP_FEEDS
    + GTM_SALES_FEEDS
    + CULTURE_FEEDS
    + NOOKS_FEEDS
    + GOOGLE_ALERTS_FEEDS
)
