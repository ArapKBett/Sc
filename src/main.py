import asyncio
import threading
from src.bot.discord_bot import DiscordBot
from src.bot.telegram_bot import TelegramBot
from src.scheduler.scheduler import Scheduler
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.collector.scraper import scrape_website
from src.collector.rss_feed import parse_rss_feed
from src.collector.api_client import VirusTotalClient, GitHubClient
from src.database.db import Database

async def collect_content(config, db, logger):
    """Collect content from various sources and store in the database."""
    sources = config.get_sources()
    
    # RSS Feeds
    for feed in sources['rss_feeds']:
        tips = parse_rss_feed(feed)
        for tip in tips:
            db.insert_tip('general', tip['content'], tip['source'])
            logger.info(f"Inserted RSS tip from {feed}")

    # GitHub Repos
    github_client = GitHubClient(config.get('APIs', 'github_token'))
    for repo in sources['github_repos']:
        result = github_client.get_repo_readme(repo)
        db.insert_tip('general', result['content'], result['source'])
        logger.info(f"Inserted GitHub README from {repo}")

    # VirusTotal (example with a sample IP)
    vt_client = VirusTotalClient(config.get('APIs', 'virustotal_key'))
    report = vt_client.get_ip_report('8.8.8.8')  # Example IP
    db.insert_tip('threat_intelligence', report, 'VirusTotal')
    logger.info("Inserted VirusTotal report")

def main():
    # Initialize logger and configuration
    logger = setup_logger()
    config = Config()
    db = Database('data/cybersecurity.db')

    # Collect initial content
    asyncio.run(collect_content(config, db, logger))

    # Initialize bots
    discord_bot = DiscordBot(
        config.get('Bot', 'discord_token'),
        config.get('Bot', 'discord_channel_id'),
        'data/cybersecurity.db'
    )
    telegram_bot = TelegramBot(
        config.get('Bot', 'telegram_token'),
        config.get('Bot', 'telegram_chat_id'),
        'data/cybersecurity.db'
    )

    # Setup scheduler
    scheduler = Scheduler(discord_bot, telegram_bot)
    scheduler.schedule_posts(int(config.get('Settings', 'post_interval')))

    # Run bots and scheduler in separate threads
    discord_thread = threading.Thread(target=discord_bot.run)
    telegram_thread = threading.Thread(target=telegram_bot.run)
    scheduler_thread = threading.Thread(target=scheduler.run)

    discord_thread.start()
    telegram_thread.start()
    scheduler_thread.start()

    discord_thread.join()
    telegram_thread.join()
    scheduler_thread.join()

if __name__ == "__main__":
    main()
