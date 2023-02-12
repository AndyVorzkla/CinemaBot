from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Movie:
    id: int
    movie_name: str
    details: str
    picture: str
    kinopoisk_url: str
    youtube_url: str



@dataclass
class C:
    x: int
    y: int = field(repr=False)
    z: int = field(repr=False, default=10)
    t: int = 20

a = C(10, 10)
print(a)

# CREATE TABLE IF NOT EXISTS movies (
#     id INTEGER PRIMARY KEY,
#     movie_name VARCHAR(60),
#     details TEXT,
#     picture BLOB,
#     kinopoisk_url TEXT,
#     youtube_url TEXT
# );