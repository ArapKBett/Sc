import discord
import logging
from discord.ext import commands
from src.database.db import Database
from src.bot.shared import format_message, CATEGORIES
from src.collector.api_client import VirusTotalClient, OTXClient, AbuseIPDBClient

class DiscordBot:
    def __init__(self, token, channel_id, db_path, vt_key, otx_key=None, abuseipdb_key=None):
        self.token = token
        self.channel_id = channel_id
        self.db = Database(db_path)
        self.vt_client = VirusTotalClient(vt_key)
        self.otx_client = OTXClient(otx_key) if otx_key else None
        self.abuse_client = AbuseIPDBClient(abuseipdb_key) if abuseipdb_key else None
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)

        @self.bot.event
        async def on_ready():
            logging.getLogger().info(f"Discord bot logged in as {self.bot.user}")

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

        @self.bot.command(name='ip')
        async def ip_check(ctx, ip_address=None):
            if not ip_address:
                await ctx.send("Please provide an IP address, e.g., !ip 8.8.8.8")
                return
            try:
                report = self.vt_client.get_ip_report(ip_address)
                await ctx.send(format_message(report, 'VirusTotal'))
            except Exception as e:
                await ctx.send(f"Error fetching report for IP {ip_address}: {e}")

        @self.bot.command(name='abuseip')
        async def abuseip_check(ctx, ip_address=None):
            if not ip_address:
                await ctx.send("Please provide an IP address, e.g., !abuseip 185.230.125.1")
                return
            if not self.abuse_client:
                await ctx.send("AbuseIPDB API not configured.")
                return
            try:
                report = self.abuse_client.get_ip_report(ip_address)
                await ctx.send(format_message(report, 'AbuseIPDB'))
            except Exception as e:
                await ctx.send(f"Error fetching report for IP {ip_address}: {e}")

        @self.bot.command(name='otx')
        async def otx_pulse(ctx):
            if not self.otx_client:
                await ctx.send("OTX API not configured.")
                return
            try:
                pulse = self.otx_client.get_pulse()
                await ctx.send(format_message(pulse, 'AlienVault OTX'))
            except Exception as e:
                await ctx.send(f"Error fetching OTX pulse: {e}")

    async def post_tip(self, category=None):
        logger = logging.getLogger()
        content, source = self.db.get_random_tip(category)
        if content:
            channel = self.bot.get_channel(int(self.channel_id))
            if channel:
                try:
                    await channel.send(format_message(content, source))
                    logger.info(f"Posted tip to Discord channel {self.channel_id} for category {category}")
                except discord.errors.Forbidden as e:
                    logger.error(f"Permission error posting to Discord channel {self.channel_id}: {e}")
                except discord.errors.HTTPException as e:
                    logger.error(f"HTTP error posting to Discord channel {self.channel_id}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error posting to Discord channel {self.channel_id}: {e}")
            else:
                logger.error(f"Invalid Discord channel ID: {self.channel_id}")
        else:
            logger.warning(f"No tip found for category {category}")

    async def start(self):
        await self.bot.start(self.token)

    def run(self):
        self.bot.run(self.token)