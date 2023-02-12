from contextlib import contextmanager
import aiosqlite
import config
import sqlite3
import asyncio


# # with sqlite3.connect(config.SQLITE_DB_FILE) as conn:
#     conn.row_factory = sqlite3.Row
#     curs = conn.cursor()
#     curs.execute('SELECT * FROM genres')
#     data = curs.fetchall()
#     for row in data:
#         print(dict(row))
#     curs.close()

async def get_range(n):
    for i in range(n):
        await print(i)


get_range(10)