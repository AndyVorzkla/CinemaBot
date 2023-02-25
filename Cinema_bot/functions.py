from os import getenv
import requests, asyncio, aiohttp, aiosqlite
from urllib.parse import urlencode
from dataclasses import dataclass
import re
import json
from dotenv import load_dotenv
import data_class, config
from bot import logger


# https://www.kinopoisk.ru/film/428/

load_dotenv()

class FinderMovieInfo:

    def __init__(self, data: dict) -> None:
        self.data = data
        self.movie_dict = {}
        self.genre_set = None

    def _find_genres(self):
        is_genres_exist = self.data.get('genres', False)
        genres = set()
        if is_genres_exist:
            for genre_d in is_genres_exist:
                genre = genre_d.get('name', 'нет данных')
                if genre not in genres:
                    genres.add(genre)
        else:
            genres.add('нет данных')

        self.genre_set = tuple(genres)
    
    def _find_english_title_or_another(self):
        for dict_name in self.data['names']:
            name = dict_name['name']
            new_name = ''.join(filter(str.isalnum, name))
            pattern = r'[a-zA-Z]+'
            match_object = re.fullmatch(pattern, new_name)
            if match_object is not None:
                self.movie_dict['movie_name'] = name
                break
            else:
                continue
        else:
            self.movie_dict['movie_name'] = self.data['names'][-1]['name']

    def _find_official_trailer_or_any_youtube(self):
        video_url = None
        for dict_trailers in self.data['videos']['trailers']:
            if 'youtube' in dict_trailers.get('site', None).lower() and video_url is None:
                video_url = dict_trailers.get('url', None)

            if 'official trailer' in dict_trailers.get('name', '').lower():
                video_url = dict_trailers.get('url', video_url)
                self.movie_dict['youtube_url'] = video_url
                break
        else:
            self.movie_dict['youtube_url'] = video_url
    
    def _find_picture(self):
        is_poster_exist = self.data.get('poster', False)
        if is_poster_exist:
            self.movie_dict['picture'] = is_poster_exist.get('url', r'https://imgholder.ru/400x400/03001C/B6EADA&text=Unfortunately,+the+poster+is+missing&font=bebas&fz=28')
        else:
            self.movie_dict['picture']  = r'https://imgholder.ru/400x400/03001C/B6EADA&text=Unfortunately,+the+poster+is+missing&font=bebas&fz=28'
    
    def _find_kinopoisk_id(self):
        kinopoisk_id = self.data.get('id', None)
        self.movie_dict['kinopoisk_id'] = kinopoisk_id
    
    def _find_kinopoisk_url(self):
        kinopoisk_url = r'https://www.kinopoisk.ru/film/{}/'.format(self.data['id'])
        self.movie_dict['kinopoisk_url'] = kinopoisk_url
    
    def _find_details(self):
        details = self.data.get('description', None)
        self.movie_dict['details'] = details
    
    def create_movie_class(self):
        functions_ = [
            '_find_kinopoisk_id',
            '_find_english_title_or_another',
            '_find_details',
            '_find_picture',
            '_find_kinopoisk_url',
            '_find_official_trailer_or_any_youtube',
            '_find_genres']
        
        for function in functions_:
            getattr(self, function)()
        
        try:
            movie_class = data_class.Movie(**self.movie_dict)
        except TypeError:  
            logger.error("Can't add in database")

        return movie_class


    
def movie_class_from_json(data: dict):
    finder = FinderMovieInfo(data=data)
    movie_class = finder.create_movie_class()
    genres = finder.genre_set
    return (movie_class, genres)

async def check_registration(telegram_id: int):
    sql = """SELECT * FROM bot_user WHERE telegram_id = (?);"""

    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(sql, (telegram_id,)) as cursor:
                user_row = await cursor.fetchone()
                if user_row:
                    return data_class.User(**dict(user_row))
                else:
                    return False
    
async def find_movie(id: str):
    """
    Downloads details about movie from KinopoiskAPI
    """
    KINOPOISK_TOKEN = getenv("KINOPOISK_TOKEN") 

    base_url = r'https://api.kinopoisk.dev/movie?'


    async with aiohttp.ClientSession() as session:
        url = base_url + urlencode(dict(token=KINOPOISK_TOKEN, field='id', search=id))
        async with session.get(url) as response:
            # response = requests.get(url)
            data = await response.json()
            if data.get('message') == 'id not found':
                raise SyntaxWarning("I didn't find this movie on https://www.kinopoisk.ru")
            movie_class, genres = movie_class_from_json(data)
            return (movie_class, genres)

def check_if_url_return_id(url: str):
    """
    Return id from string if it is correct kinopoisk URL or ErrorMessage
    """
    if 'kinopoisk.ru' in url:
        pattern = r'\/(?P<id>[\d]+)'
        match = re.search(pattern, url)
        if match is not None:
            id = match.group('id')
            return id
        else:
            raise SyntaxWarning('Url is not correct. Example "https://www.kinopoisk.ru/film/100/"')
    else:
        return False
    
async def check_movie_in_db(kinopoisk_id: str): 
    """
    Return Movie data_class if movie already in DB, False if not
    """
    sql = """SELECT * FROM movies WHERE kinopoisk_id = (?);"""
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(sql, (kinopoisk_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return data_class.Movie(**dict(row))
            else:
                return False
                       
async def insert_movie_in_db(movie_class: data_class.Movie, genres: tuple, user_telegram_id: int):
    questionmarks = '?' * len(genres)
    sql_0 = """INSERT OR ABORT INTO movies (kinopoisk_id, movie_name, details, picture, kinopoisk_url, youtube_url) VALUES (?, ?, ?, ?, ?, ?);"""
    sql_1 = """SELECT id FROM movies WHERE kinopoisk_id = (?);"""
    sql_2 = """SELECT id FROM genres WHERE genre_name IN ({});""".format(','.join(questionmarks))
    sql_3 = """INSERT OR ABORT INTO movies_genres (movie_id, genre_id) VALUES (?, ?);"""
    # sql_5 = """INSERT OT ABORT INTO user_movie (user_id, movie_id, priority_weight) VALUES (?, ?, ?);"""

    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            try:
                await conn.execute(sql_0, (
                        movie_class.kinopoisk_id,
                        movie_class.movie_name,
                        movie_class.details,
                        movie_class.picture,
                        movie_class.kinopoisk_url,
                        movie_class.youtube_url))
                
                await conn.commit()
                
            except aiosqlite.IntegrityError:
                logger.error('Already in DB sqlite exception')
            
            async with conn.execute(sql_1, (movie_class.kinopoisk_id,)) as cursor:
                movie_row = await cursor.fetchone()

            async with conn.execute(sql_2, genres) as cursor:
                """
                Return ids of genres in genre DB
                """
                rows =  await cursor.fetchall()

            movie_id = dict(movie_row)['id']

            # Genres ids of current movie
            ids = tuple(dict(row)['id'] for row in rows)
            movie_genres_data = [(movie_id, id) for id in ids]

            try:
                await conn.executemany(sql_3, movie_genres_data)
                await conn.commit()
            except aiosqlite.IntegrityError:
                logger.error('Already in GenreMovies (M-T-M) sqlite exception')

                            

async def insert_into_user_movie_relation(movie_class: data_class.Movie, user_class: data_class.User):
    sql = """INSERT OR ABORT INTO user_movie (user_id, movie_id) VALUES (?, ?);"""

    async with aiosqlite.connect(config.SQLITE_DB_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        try:
            await conn.execute(sql, (user_class.id, movie_class.id,))
            await conn.commit()
        except aiosqlite.IntegrityError:
                logger.error('User movie reference error sqlite exception')

    


# movie_class = find_movie('https://www.kinopoisk.ru/film/428/')
# print(movie_class)
