import discord
from discord.ext import commands
from src.database.db import Database
from src.bot.shared import format_message, CATEGORIES

class DiscordBot:
    def __init__(self, token, channel_id, db_path):
        self.token = token
        self.channel_id = channel_id
        self.db = Database(db_path)
        self.bot = commands.Bot(command_prefix='!')

        @self.bot.event
        async def on_ready():
            print(f"Discord bot logged in as {self.bot.user}")

        @self.bot.command(name='tip')
        async def tip(ctx, category=None):
            if category and category.lower() not in CATEGORIES:
                await ctx.send(f"Invalid category. Choose from: {', '.join(CATEGORIES)}")
                return
            content, source = self.db.get_random_tip(category.lower() if category else None)
            if content:
                await ctx.send(format_message(content, source))
            else:
                await ctx.send("No tips found.")

    async def post_tip(self, category=None):
        """Post a random tip to the configured Discord channel."""
        content, source = self.db.get_random_tip(category)
        if content:
            channel = self.bot.get_channel(int(self.channel_id))
            if channel:
                await channel.send(format_message(content, source))

    def run(self):
        """Run the Discord bot."""
        self.bot.run(self.token)
