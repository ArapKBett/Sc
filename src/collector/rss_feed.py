import feedparser

def parse_rss_feed(url):
    """Parse an RSS feed and extract recent entries."""
    try:
        feed = feedparser.parse(url)
        tips = []
        for entry in feed.entries[:5]:  # Limit to 5 recent entries
            content = entry.get('summary', entry.get('title', ''))
            if content:
                tips.append({'content': content, 'source': entry.get('link', url)})
        return tips
    except Exception as e:
        print(f"Error parsing RSS feed {url}: {e}")
        return []
