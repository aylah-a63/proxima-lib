import asyncio
import os

import aiosqlite

from proxima_lib.paths import data_dir

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id      TEXT NOT NULL UNIQUE,
    channel_id      TEXT NOT NULL,
    user_id         TEXT NOT NULL,
    username        TEXT NOT NULL,
    nickname        TEXT,
    message_content TEXT NOT NULL,
    prompt_content  TEXT NOT NULL,
    timestamp       TEXT NOT NULL,
    deleted         INTEGER NOT NULL DEFAULT 0
)
"""


class Database:
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn
        self._conn.row_factory = aiosqlite.Row
        self._lock = asyncio.Lock()

    @classmethod
    async def create(cls) -> "Database":
        path = data_dir() / "messages.db"
        conn = await aiosqlite.connect(path)
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute(CREATE_TABLE)
        await conn.commit()
        try:
            os.chmod(path, 0o640)
        except OSError:
            pass
        return cls(conn)

    async def insert_message(
        self,
        message_id: str,
        channel_id: str,
        user_id: str,
        username: str,
        nickname: str | None,
        message_content: str,
        prompt_content: str,
        timestamp: str,
    ) -> None:
        async with self._lock:
            await self._conn.execute(
                """INSERT OR IGNORE INTO messages
                   (message_id, channel_id, user_id, username, nickname,
                    message_content, prompt_content, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (message_id, channel_id, user_id, username, nickname,
                 message_content, prompt_content, timestamp),
            )
            await self._conn.commit()

    async def mark_deleted(self, message_id: str) -> None:
        async with self._lock:
            await self._conn.execute(
                "UPDATE messages SET deleted = 1 WHERE message_id = ?",
                (message_id,),
            )
            await self._conn.commit()

    async def fetch_all(self, query: str, params: tuple = ()) -> list[aiosqlite.Row]:
        cursor = await self._conn.execute(query, params)
        return await cursor.fetchall()

    async def close(self) -> None:
        await self._conn.close()
