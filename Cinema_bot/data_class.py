from dataclasses import dataclass
from datetime import datetime

@dataclass(kw_only=True)
class Category:
    id: int
    name: str

@dataclass(kw_only=True)
class Movie:
    id: int = None
    kinopoisk_id: int
    movie_name: str
    details: str = None
    picture: str = None
    kinopoisk_url: str = None
    youtube_url: str = None

@dataclass(kw_only=True)
class User:
    id: int
    telegram_id: int
    username : str = None
    user_first_name: str = None
    user_second_name: str = None
    created_at: datetime
