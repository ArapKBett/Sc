import logging
from telegram.ext import Application, CommandHandler
from src.database.db import Database
from src.bot.shared import format_message, CATEGORIES
from src.collector.api_client import VirusTotalClient, OTXClient, AbuseIPDBClient

class TelegramBot:
    def __init__(self, token, chat_id, db_path, vt_key, otx_key=None, abuseipdb_key=None):
        self.token = token
        self.chat_id = chat_id
        self.db = Database(db_path)
        self.vt_client = VirusTotalClient(vt_key)
        self.otx_client = OTXClient(otx_key) if otx_key else None
        self.abuse_client = AbuseIPDBClient(abuseipdb_key) if abuseipdb_key else None
        self.application = Application.builder().token(self.token).build()

        async def tip(update, context):
            category = context.args[0] if context.args else None
            if category and category.lower() not in CATEGORIES:
                await update.message.reply_text(f"Invalid category. Choose from: {', '.join(CATEGORIES)}")
                return
            content, source = self.db.get_random_tip(category.lower() if category else None)
            if content:
                await update.message.reply_text(format_message(content, source))
            else:
                await update.message.reply_text("No tips found.")

        async def ip_check(update, context):
            ip_address = context.args[0] if context.args else None
            if not ip_address:
                await update.message.reply_text("Please provide an IP address, e.g., /ip 8.8.8.8")
                return
            try:
                report = self.vt_client.get_ip_report(ip_address)
                await update.message.reply_text(format_message(report, 'VirusTotal'))
            except Exception as e:
                await update.message.reply_text(f"Error fetching report for IP {ip_address}: {e}")

        async def abuseip_check(update, context):
            ip_address = context.args[0] if context.args else None
            if not ip_address:
                await update.message.reply_text("Please provide an IP address, e.g., /abuseip 185.230.125.1")
                return
            if not self.abuse_client:
                await update.message.reply_text("AbuseIPDB API not configured.")
                return
            try:
                report = self.abuse_client.get_ip_report(ip_address)
                await update.message.reply_text(format_message(report, 'AbuseIPDB'))
            except Exception as e:
                await update.message.reply_text(f"Error fetching report for IP {ip_address}: {e}")

        async def otx_pulse(update, context):
            if not self.otx_client:
                await update.message.reply_text("OTX API not configured.")
                return
            try:
                pulse = self.otx_client.get_pulse()
                await update.message.reply_text(format_message(pulse, 'AlienVault OTX'))
            except Exception as e:
                await update.message.reply_text(f"Error fetching OTX pulse: {e}")

        self.application.add_handler(CommandHandler('tip', tip))
        self.application.add_handler(CommandHandler('ip', ip_check))
        self.application.add_handler(CommandHandler('abuseip', abuseip_check))
        self.application.add_handler(CommandHandler('otx', otx_pulse))

    async def post_tip(self, category=None):
        logger = logging.getLogger()
        content, source = self.db.get_random_tip(category)
        if content:
            try:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=format_message(content, source)
                )
                logger.info(f"Posted tip to Telegram chat {self.chat_id} for category {category}")
            except Exception as e:
                logger.error(f"Error posting to Telegram chat {self.chat_id}: {e}")
        else:
            logger.warning(f"No tip found for category {category}")

    async def start_polling(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await self.application.updater.running.wait()

    def run(self):
        self.application.run_polling()