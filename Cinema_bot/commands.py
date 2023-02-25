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

            elif not movie_class:
                movie_class, genres = await functions.find_movie(id)

                await functions.insert_movie_in_db(movie_class, genres, user_telegram_id)
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
    media_response = movie_class.youtube_url
    if media_response is None:
        media_response = movie_class.picture
    await context.bot.send_message(chat_id=update.effective_chat.id,
                    text=media_response)





async def my_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Нужно зарефакторить
    effective_chat = update.effective_chat

    if not effective_chat:
        logger.warning('effective_chat is None')

    telegram_id = update.message.from_user.id

    sql = """SELECT * FROM bot_user WHERE telegram_id = (?);"""
    sql_2 = """
            SELECT \
              a.movie_id, \
              b.movie_name, \
              b.picture, \
              b.details, \
              group_concat(g.genre_name, ' ') as genres \
            FROM user_movie as a \
            LEFT JOIN movies as b \
            ON a.movie_id = b.id \
            LEFT JOIN movies_genres mg \
            ON a.movie_id = mg.movie_id \
            LEFT JOIN genres g \
            ON mg.genre_id = g.id \
            WHERE a.user_id = (?) \
            GROUP BY a.movie_id \
    """

    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(sql, (telegram_id,)) as cursor:
            user_row = await cursor.fetchone()
            if user_row:
                user_class = data_class.User(**dict(user_row))
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Registration fail. Write /start')
                return False
        async with conn.execute(sql_2, (user_class.id,)) as cursor:
            movie_rows = await cursor.fetchall()
            movies = [dict(movie_row) for movie_row in movie_rows]
    
    for movie in movies:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_texts.MOVIE.format(
                  movie_name=movie['movie_name'],
                  details=movie['details'],
                  genres=movie['genres'].title()
                ),
            parse_mode='HTML'
            )
        media_response = movie['picture']
        # if media_response is None:
        #     media_response = movie_class.picture
        await context.bot.send_message(chat_id=update.effective_chat.id,
                        text=media_response)



    

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