from contextlib import contextmanager
from dataclasses import dataclass
import aiosqlite
import requests
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from bot import logger
import message_texts
import config, functions, data_class


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
            logger.info('Telegram_id already exists')

    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_texts.GREETINGS_not_ready.format(username=username), parse_mode='HTML')


async def movie_roll_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat
    user_telegram_id = update.message.from_user.id

    if not effective_chat:
        logger.warning('effective_chat is None')
    
    user_class = await functions.check_registration(user_telegram_id)
    if not user_class:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                text='Registration fail. Write /start')
        return False
    
    message = ''.join(context.args)
    
    try:
        id = functions.check_if_url_return_id(message)
        if id:
            movie_class = await functions.check_movie_in_db(id)
            if isinstance(movie_class, data_class.Movie):
                logger.info('Movie is already in db')
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'A movie: <b>{movie_class.movie_name}</b>, is already in DB', parse_mode='HTML')

            elif not movie_class:
                movie_class, genres = await functions.find_movie(id)

                await functions.insert_movie_in_db(movie_class, genres, user_telegram_id)
                # await functions.insert_movie_genre(genres, movie_class.id) 
                media_response = movie_class.youtube_url
                if media_response is None:
                    media_response = movie_class.picture
                await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f'A new movie: <b>{movie_class.movie_name}</b>, is added in DB', parse_mode='HTML')
                await context.bot.send_message(chat_id=update.effective_chat.id,
                text=media_response)
            else:
                logger.warning('Something wrong. We cant be here')
        else:
            # Logic of finding the movie by the key word
            pass
    except SyntaxWarning as e:
        error_message = str(e)
        if error_message:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message)
    
    await functions.insert_into_user_movie_relation(movie_class=movie_class, user_class=user_class)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                text=f'A new movie: <b>{movie_class.movie_name}</b>, is added in DB', parse_mode='HTML')






async def my_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat = update.effective_chat

    if not effective_chat:
        logger.warning('effective_chat is None')

    telegram_id = update.message.from_user.id


    

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