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
    
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', commands.start)
    help_handler = CommandHandler('help', commands.help)
    movie_roll_add_handler = CommandHandler('add', commands.movie_roll_add)
    my_movie_handler = CommandHandler('my', commands.my_movies)
    roll_handler = CommandHandler('roll', commands.roll)
    
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(movie_roll_add_handler)
    application.add_handler(my_movie_handler)
    application.add_handler(roll_handler)

    application.run_polling()
