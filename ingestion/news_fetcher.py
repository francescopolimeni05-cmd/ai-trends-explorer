import re
import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime

RSS_FEEDS = [
    {
        "url": "https://feeds.feedburner.com/venturebeat/SZYF",
        "name": "VentureBeat AI",
        "category": "news",
    },
    {
        "url": "https://www.technologyreview.com/feed/",
        "name": "MIT Technology Review",
        "category": "news",
    },
    {
        "url": "https://thegradient.pub/rss/",
        "name": "The Gradient",
        "category": "research",
    },
    {
        "url": "https://blog.research.google/feeds/posts/default",
        "name": "Google Research Blog",
        "category": "research",
    },
    {
        "url": "https://openai.com/news/rss.xml",
        "name": "OpenAI News",
        "category": "news",
    },
]

def _parse_date(entry) -> str:
    try:
        if hasattr(entry, "published"):
            return parsedate_to_datetime(entry.published).strftime("%Y-%m-%d")
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d")

def fetch_rss_articles(max_per_feed: int = 8) -> list[dict]:
    """
    Fetch recent articles from curated AI news RSS feeds.
    Returns list of dicts with keys: text, title, url, date, source_type, category, feed_name.
    """
    articles = []

    for feed_info in RSS_FEEDS:
        try:
            print(f"[RSS] Fetching: {feed_info['name']}...")
            feed = feedparser.parse(feed_info["url"])

            count = 0
            for entry in feed.entries[:max_per_feed]:
                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary
                elif hasattr(entry, "content"):
                    summary = entry.content[0].value

                summary = re.sub(r"<[^>]+>", "", summary).strip()

                if not summary:
                    continue

                text = f"TITLE: {entry.get('title', 'Untitled')}\n\nSUMMARY: {summary}"

                articles.append({
                    "text": text,
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", ""),
                    "date": _parse_date(entry),
                    "source_type": "news",
                    "category": feed_info["category"],
                    "feed_name": feed_info["name"],
                })
                count += 1

            print(f"[RSS] {feed_info['name']}: {count} articles")

        except Exception as e:
            print(f"[RSS] Failed to fetch {feed_info['name']}: {e}")

    print(f"[RSS] Done. Fetched {len(articles)} articles total.")
    return articles