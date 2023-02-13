from os import getenv
import requests, asyncio, aiohttp
from urllib.parse import urlencode
from dataclasses import dataclass
import re
import json
from dotenv import load_dotenv
import data_class
from bot import logger


# https://www.kinopoisk.ru/film/428/

load_dotenv()

def movie_class_from_json(data: dict):
    movie_dict = {}

    # find english title
    for dict_name in data['names']:
        name = dict_name['name']
        pattern = r'[a-zA-Z0-9_ -]+'
        match_object = re.fullmatch(pattern, name)
        if match_object is not None:
            movie_name = match_object[0]
            movie_dict['movie_name'] = movie_name
            break
        else:
            continue

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
        
    movie_class = data_class.Movie(**movie_dict)

    return movie_class
    
async def find_movie(name_or_url: str):
    """
    Downloads details about movie from KinopoiskAPI
    """
    KINOPOISK_TOKEN = getenv("KINOPOISK_TOKEN") 

    base_url = r'https://api.kinopoisk.dev/movie?'

    if 'kinopoisk.ru' in name_or_url:
        pattern = r'\/(?P<id>[\d]+)'
        match = re.search(pattern, name_or_url)

        if match is not None:
            id = match.group('id')
            async with aiohttp.ClientSession() as session:
                url = base_url + urlencode(dict(token=KINOPOISK_TOKEN, field='id', search=id))
                async with session.get(url) as response:
                    # response = requests.get(url)
                    data = await response.json()
                    movie_class = movie_class_from_json(data)
                    return movie_class
            
        else:
            return 'Url is not correct'
    else:
        return 'It is not URL'
        



# movie_class = find_movie('https://www.kinopoisk.ru/film/428/')
# print(movie_class)
