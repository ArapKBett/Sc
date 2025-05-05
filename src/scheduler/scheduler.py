import schedule
import time
import asyncio
from src.bot.shared import CATEGORIES

class Scheduler:
    def __init__(self, discord_bot, telegram_bot):
        self.discord_bot = discord_bot
        self.telegram_bot = telegram_bot

    def schedule_posts(self, interval_seconds):
        """Schedule periodic posts for each category."""
        async def post_job():
            for category in CATEGORIES:
                await self.discord_bot.post_tip(category)
                await self.telegram_bot.post_tip(category)
                await asyncio.sleep(10)  # Small delay between posts

        schedule.every(interval_seconds).seconds.do(lambda: asyncio.create_task(post_job()))

    def run(self):
        """Run the scheduler loop."""
        while True:
            schedule.run_pending()
            time.sleep(1)
