# db/database.py
import aiosqlite
from config import SQLITE_PATH


class Database:
    def __init__(self):
        self._conn = None

    async def initialize(self):
        self._conn = await aiosqlite.connect(SQLITE_PATH)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self._conn.execute("PRAGMA journal_mode = WAL")
        await self._conn.execute("PRAGMA busy_timeout = 5000")
        return self._conn

    @property
    def conn(self):
        if self._conn is None:
            raise RuntimeError("База не инициализирована. Вызови await db.initialize()")
        return self._conn

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def commit(self):
        await self.conn.commit()

    async def execute(self, sql, *params):
        if not params:
            cursor = await self.conn.execute(sql)
        elif len(params) == 1 and isinstance(params[0], (tuple, list)):
            cursor = await self.conn.execute(sql, params[0])
        else:
            cursor = await self.conn.execute(sql, params)
        await self.conn.commit()
        return cursor

    async def fetchall(self, sql, *params):
        if not params:
            cursor = await self.conn.execute(sql)
        elif len(params) == 1 and isinstance(params[0], (tuple, list)):
            cursor = await self.conn.execute(sql, params[0])
        else:
            cursor = await self.conn.execute(sql, params)
        return await cursor.fetchall()

    async def fetchone(self, sql, *params):
        if not params:
            cursor = await self.conn.execute(sql)
        elif len(params) == 1 and isinstance(params[0], (tuple, list)):
            cursor = await self.conn.execute(sql, params[0])
        else:
            cursor = await self.conn.execute(sql, params)
        return await cursor.fetchone()

    async def executemany(self, sql, params_list):
        cursor = await self.conn.executemany(sql, params_list)
        await self.conn.commit()
        return cursor


db = Database()