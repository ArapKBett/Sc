import feedparser
import logging

def parse_rss_feed(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        tips = []
        for entry in feed.entries[:5]:  # Limit to 5 entries
            content = (entry.get('summary') or entry.get('description') or entry.get('title') or '')[:500]
            # Remove markup
            content = content.replace('`', '').replace('[', '').replace(']', '').replace('<', '').replace('>', '')
            tips.append({
                'content': f"This article discusses {content.split('.')[0].lower()}.",
                'source': entry.get('link', feed_url)
            })
        return tips
    except Exception as e:
        logging.getLogger().error(f"Error parsing RSS feed {feed_url}: {e}")
        return []