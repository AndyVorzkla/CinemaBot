from contextlib import contextmanager
from dataclasses import dataclass
import aiosqlite
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from bot import logger
import message_texts
import config

@dataclass
class Category:
    id: int
    name: str

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('effective_chat is None')
        return
    
    categorys = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
         
        telegram_id = update.message.from_user.id
        username = update.message.from_user.username
        user_first_name = update.message.from_user.first_name
        user_second_name = update.message.from_user.last_name

        await conn.execute(
            'INSERT INTO bot_user \
            (telegram_id, username, user_first_name, user_second_name)\
             VALUES (?, ?, ?, ?);', (telegram_id, username, user_first_name, user_second_name))
        
        await conn.commit()

async def save_to_db(city, weather):
    async with aiosqlite.connect('weather.db') as db:
        await db.execute('INSERT INTO requests VALUES (?, ?, ?)',
                         (datetime.now(), city, weather))
        await db.commit()



    response = "\n".join((book.name for book in categorys)) 
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message_texts.GREETINGS
        )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('effective_chat is None')
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message_texts.HELP
    )



 