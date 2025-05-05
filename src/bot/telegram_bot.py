from telegram.ext import Updater, CommandHandler
from src.database.db import Database
from src.bot.shared import format_message, CATEGORIES

class TelegramBot:
    def __init__(self, token, chat_id, db_path):
        self.token = token
        self.chat_id = chat_id
        self.db = Database(db_path)
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        def tip(update, context):
            category = context.args[0] if context.args else None
            if category and category.lower() not in CATEGORIES:
                update.message.reply_text(f"Invalid category. Choose from: {', '.join(CATEGORIES)}")
                return
            content, source = self.db.get_random_tip(category.lower() if category else None)
            if content:
                update.message.reply_text(format_message(content, source))
            else:
                update.message.reply_text("No tips found.")

        self.dispatcher.add_handler(CommandHandler('tip', tip))

    async def post_tip(self, category=None):
        """Post a random tip to the configured Telegram chat."""
        content, source = self.db.get_random_tip(category)
        if content:
            self.updater.bot.send_message(
                chat_id=self.chat_id,
                text=format_message(content, source)
            )

    def run(self):
        """Run the Telegram bot."""
        self.updater.start_polling()
        self.updater.idle()
