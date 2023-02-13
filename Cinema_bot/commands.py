from contextlib import contextmanager
from dataclasses import dataclass
import aiosqlite
import requests
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from bot import logger
import message_texts
import config, functions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('effective_chat is None')
        return
    
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
         
        telegram_id = update.message.from_user.id
        username = update.message.from_user.username
        user_first_name = update.message.from_user.first_name
        user_second_name = update.message.from_user.last_name

        try:
            await conn.execute(
                'INSERT OR ABORT INTO bot_user \
                (telegram_id, username, user_first_name, user_second_name)\
                VALUES (?, ?, ?, ?);', (telegram_id, username, user_first_name, user_second_name))
            
            await conn.commit()
        except aiosqlite.IntegrityError:
            logger.error('Telegram_id already exists')

    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_texts.GREETINGS.format(username=username), parse_mode='HTML')


async def movie_roll_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat

    if not effective_chat:
        logger.warning('effective_chat is None')
    
    message = ''.join(context.args)
    movie_class = await functions.find_movie(message)
    if isinstance(movie_class, str):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f'<b>{movie_class}</b>', parse_mode='HTML')
    else:
        async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:

            try:
                await conn.execute(
                    'INSERT OR ABORT INTO movies \
                    (kinopoisk_id, movie_name, details, picture, kinopoisk_url, youtube_url)\
                    VALUES (?, ?, ?, ?, ?, ?);', (
                        movie_class.kinopoisk_id,
                        movie_class.movie_name,
                        movie_class.details,
                        movie_class.picture,
                        movie_class.kinopoisk_url,
                        movie_class.youtube_url))
                
                await conn.commit()
                await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f'A new movie: <b>{movie_class.movie_name}</b>, is added in DB', parse_mode='HTML')
                await context.bot.send_message(chat_id=update.effective_chat.id,
                text=movie_class.youtube_url)
                
            except aiosqlite.IntegrityError:
                logger.error('Movie is already in db')
                await context.bot.send_message(chat_id=update.effective_chat.id,
                        text=f'A movie: <b>{movie_class.movie_name}</b>, is already in DB', parse_mode='HTML')




async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    if not effective_chat:
        logger.warning('effective_chat is None')
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message_texts.HELP
    )


# async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     text_caps = ' '.join(context.args).upper()
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=context.args)
# # async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
# #     await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)