from dataclasses import dataclass

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
