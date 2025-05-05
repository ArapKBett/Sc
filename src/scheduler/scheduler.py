import asyncio
import logging
from src.bot.shared import CATEGORIES

class Scheduler:
    def __init__(self, discord_bot, telegram_bot):
        self.discord_bot = discord_bot
        self.telegram_bot = telegram_bot

    async def post_job(self):
        """Post a tip for each category to both bots."""
        logger = logging.getLogger()
        for category in CATEGORIES:
            logger.info(f"Posting tip for category {category}")
            await self.discord_bot.post_tip(category)
            await self.telegram_bot.post_tip(category)
            await asyncio.sleep(10)  # Small delay between posts

    async def schedule_posts(self, interval_seconds):
        """Schedule periodic posts for each category."""
        while True:
            await self.post_job()
            await asyncio.sleep(interval_seconds)

    def run(self):
        """Run the scheduler in an asyncio event loop."""
        asyncio.run(self.schedule_posts(interval_seconds=60))  # Default interval, overridden by main.py