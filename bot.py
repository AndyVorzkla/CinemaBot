import os
import logging
import telegram
import requests
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
import asyncio
from dotenv import load_dotenv
import commands

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    exit("Specify TELEGRAM_TOKEN")

# async def main():
#     bot = telegram.Bot(TELEGRAM_TOKEN)
    
#     async with bot:
#         print(await bot.get_me())

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', commands.start)
    help_handler = CommandHandler('help', commands.help)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    
    application.run_polling()
