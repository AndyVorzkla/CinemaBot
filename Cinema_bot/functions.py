import requests
import re
from urllib.parse import urlencode
from dotenv import load_dotenv
from os import getenv


# https://www.kinopoisk.ru/film/428/

load_dotenv()

KINOPOISK_TOKEN = getenv("KINOPOISK_TOKEN")

def find_movie(name_or_url: str):
    """
    Downloads details about movie from KinopoiskAPI
    """
    base_url = r'https://api.kinopoisk.dev/movie?'

    if 'kinopoisk.ru' in name_or_url:
        pattern = r'\/(?P<id>[\d]+)\/'
        match = re.search(pattern, name_or_url)
        if match is not None:
            id = match.group('id')
        url = base_url + urlencode(dict(token=KINOPOISK_TOKEN, field='id', search=id))

        response = requests.get(url)
    
    return response.json()
        

print(find_movie('https://www.kinopoisk.ru/film/428/'))

    # base_url = r'https://api.kinopoisk.dev/movie?'

    # url = 

