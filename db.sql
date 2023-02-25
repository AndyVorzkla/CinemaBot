DROP TABLE IF EXISTS bot_user;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS user_movie;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS movies_genres;

CREATE TABLE IF NOT EXISTS bot_user (
    id INTEGER PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    user_first_name TEXT,
    user_second_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
    genre_name VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    kinopoisk_id INTEGER UNIQUE,
    movie_name VARCHAR(60) NOT NULL,
    details TEXT,
    picture TEXT,
    kinopoisk_url TEXT,
    youtube_url TEXT
);

CREATE TABLE IF NOT EXISTS user_movie (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    movie_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    watch_date DATETIME DEFAULT NULL,
    FOREIGN KEY(user_id) REFERENCES bot_user(id),
    FOREIGN KEY(movie_id) REFERENCES movies(id)

);
--     priority_weight TINYINT(1) DEFAULT 10,

CREATE TABLE IF NOT EXISTS movies_genres (
    movie_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    FOREIGN KEY(movie_id) REFERENCES movies(id),
    FOREIGN KEY(genre_id) REFERENCES genres(id)
);

INSERT INTO genres (genre_name)
VALUES
	("аниме"),
	("биография"),
	("боевик"),
    ("военный"),
	("детектив"),
	("детский"),
    ("для взрослых"),
	("документальный"),
	("драма"),
    ("игра"),
	("история"),
	("комедия"),
    ("концерт"),
	("короткометражка"),
	("криминал"),
    ("мелодрама"),
	("музыка"),
	("мультфильм"),
    ("мюзикл"),
    ("новости"),
	("приключения"),
	("реальное ТВ"),
    ("семейный"),
	("спорт"),
	("ток-шоу"),
    ("триллер"),
	("ужасы"),
	("фантастика"),
    ("фильм-нуар"),
    ("фэнтези"),
    ("церемония"),
    ("нет данных");

