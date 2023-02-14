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


def movie_class_from_json(data: dict):
    movie_dict = {}

    # find english title
    for dict_name in data['names']:
        name = dict_name['name']
        new_name = ''.join(filter(str.isalnum, name))
        pattern = r'[a-zA-Z]+'
        match_object = re.fullmatch(pattern, new_name)
        if match_object is not None:
            movie_dict['movie_name'] = name
            break
        else:
            continue
    else:
        movie_dict['movie_name'] = data['names'][-1]['name']

    movie_dict['kinopoisk_id'] = data['id']
    movie_dict['kinopoisk_url'] = r'https://www.kinopoisk.ru/film/{}/'.format(data['id'])
    movie_dict['details'] = data['description']
    movie_dict['picture'] = data['poster']['url']
    
    # find official trailer
    video_url = None
    for dict_trailers in data['videos']['trailers']:
        if 'youtube' in dict_trailers.get('site', None).lower() and video_url is None:
            video_url = dict_trailers.get('url', None)

        if 'official trailer' in dict_trailers.get('name', '').lower():
            video_url = dict_trailers.get('url', video_url)
            movie_dict['youtube_url'] = video_url
            break
    else:
        movie_dict['youtube_url'] = video_url

    try:
        movie_class = data_class.Movie(**movie_dict)
    except TypeError:
        logger.error("Cam't add in database")

    return movie_class
    
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
            movie_class = movie_class_from_json(data)
            return movie_class

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
                False
            
async def insert_movie_in_db(movie_class: data_class.Movie):
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
                
            except aiosqlite.IntegrityError:
                logger.error('Already ib DB sqlite exception')



# movie_class = find_movie('https://www.kinopoisk.ru/film/428/')
# print(movie_class)
