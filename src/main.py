import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import logging
from src.bot.discord_bot import DiscordBot
from src.bot.telegram_bot import TelegramBot
from src.scheduler.scheduler import Scheduler
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.collector.rss_feed import parse_rss_feed
from src.collector.api_client import VirusTotalClient, GitHubClient, OTXClient, AbuseIPDBClient
from src.database.db import Database

async def collect_content(config, db, logger):
    """Collect content from various sources and store in the database."""
    sources = config.get_sources()
    
    # RSS Feeds
    rss_feeds = {
        'general': ['https://www.sentinelone.com/feed/'],
        'blue_teaming': ['https://www.sans.org/blog/feed/'],
        'ethical_hacking': ['https://www.tryhackme.com/blog/rss.xml'],
        'forensics': ['https://www.magnetforensics.com/feed/'],
        'soc_analysis': ['https://www.elastic.co/security-labs/feed.xml']
    }
    for category, feeds in rss_feeds.items():
        for feed in feeds:
            try:
                tips = parse_rss_feed(feed)
                for tip in tips:
                    content = tip['content'][:500]
                    if ']' in content or '`' in content:
                        content = f"Learn about {category.replace('_', ' ')} from this article: {content.split('.')[0]}."
                    db.insert_tip(category, content, tip['source'])
                    logger.info(f"Inserted RSS tip for {category} from {feed}")
            except Exception as e:
                logger.error(f"Error parsing RSS feed {feed}: {e}")

    # GitHub Repos (red_teaming)
    github_client = GitHubClient(config.get('APIs', 'github_token'))
    for repo in sources['github_repos']:
        try:
            result = github_client.get_repo_readme(repo)
            db.insert_tip('red_teaming', result['content'], result['source'])
            logger.info(f"Inserted GitHub README for red_teaming from {repo}")
        except Exception as e:
            logger.error(f"Error fetching GitHub repo {repo}: {e}")

    # VirusTotal (threat_intelligence)
    vt_client = VirusTotalClient(config.get('APIs', 'virustotal_key'))
    for ip in ['8.8.8.8', '1.1.1.1', '185.230.125.1']:
        try:
            report = vt_client.get_ip_report(ip)
            db.insert_tip('threat_intelligence', report, 'VirusTotal')
            logger.info(f"Inserted VirusTotal report for {ip}")
        except Exception as e:
            logger.error(f"Error fetching VirusTotal report for {ip}: {e}")

    # AbuseIPDB (threat_intelligence)
    abuse_client = AbuseIPDBClient(config.get('APIs', 'abuseipdb_key'))
    for ip in ['185.230.125.1', '45.33.32.156']:
        try:
            report = abuse_client.get_ip_report(ip)
            db.insert_tip('threat_intelligence', report, 'AbuseIPDB')
            logger.info(f"Inserted AbuseIPDB report for {ip}")
        except Exception as e:
            logger.error(f"Error fetching AbuseIPDB report for {ip}: {e}")

    # AlienVault OTX (soc_analysis)
    otx_key = config.get('APIs', 'otx_key')
    if otx_key:
        otx_client = OTXClient(otx_key)
        try:
            pulse = otx_client.get_pulse()
            if pulse:
                db.insert_tip('soc_analysis', pulse, 'AlienVault OTX')
                logger.info("Inserted OTX pulse")
            else:
                logger.warning("No OTX pulses returned")
        except Exception as e:
            logger.error(f"Error fetching OTX pulse: {e}")
    else:
        logger.warning("OTX API key not configured")

async def main():
    logger = setup_logger()
    config = Config()
    db = Database('data/cybersecurity.db')

    try:
        await collect_content(config, db, logger)
    except Exception as e:
        logger.error(f"Content collection failed: {e}")
        return

    try:
        discord_bot = DiscordBot(
            config.get('Bot', 'discord_token'),
            config.get('Bot', 'discord_channel_id'),
            'data/cybersecurity.db',
            config.get('APIs', 'virustotal_key'),
            config.get('APIs', 'otx_key'),
            config.get('APIs', 'abuseipdb_key')
        )
        telegram_bot = TelegramBot(
            config.get('Bot', 'telegram_token'),
            config.get('Bot', 'telegram_chat_id'),
            'data/cybersecurity.db',
            config.get('APIs', 'virustotal_key'),
            config.get('APIs', 'otx_key'),
            config.get('APIs', 'abuseipdb_key')
        )
    except Exception as e:
        logger.error(f"Bot initialization failed: {e}")
        return

    scheduler = Scheduler(discord_bot, telegram_bot)
    interval_seconds = int(config.get('Settings', 'post_interval'))

    try:
        discord_task = asyncio.create_task(discord_bot.start())
        telegram_task = asyncio.create_task(telegram_bot.start_polling())
        scheduler_task = asyncio.create_task(scheduler.schedule_posts(interval_seconds))
        await asyncio.gather(discord_task, telegram_task, scheduler_task, return_exceptions=True)
    except Exception as e:
        logger.error(f"Execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())