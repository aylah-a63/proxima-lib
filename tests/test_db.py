import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import patch
from proxima_lib.db import Database


@pytest_asyncio.fixture
async def db(tmp_path):
    with patch("proxima_lib.db.data_dir", return_value=tmp_path):
        database = await Database.create()
        yield database
        await database.close()


@pytest.mark.asyncio
async def test_insert_message(db):
    await db.insert_message(
        message_id="msg1",
        channel_id="ch1",
        user_id="u1",
        username="alice",
        nickname="Ali",
        message_content="hello",
        prompt_content="hello",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    rows = await db.fetch_all("SELECT * FROM messages WHERE message_id = ?", ("msg1",))
    assert len(rows) == 1
    assert rows[0]["username"] == "alice"
    assert rows[0]["deleted"] == 0


@pytest.mark.asyncio
async def test_mark_deleted(db):
    ts = datetime.now(timezone.utc).isoformat()
    await db.insert_message("msg2", "ch1", "u1", "bob", None, "bye", "bye", ts)
    await db.mark_deleted("msg2")
    rows = await db.fetch_all("SELECT * FROM messages WHERE message_id = ?", ("msg2",))
    assert rows[0]["deleted"] == 1


@pytest.mark.asyncio
async def test_duplicate_message_id_ignored(db):
    ts = datetime.now(timezone.utc).isoformat()
    await db.insert_message("msg3", "ch1", "u1", "carol", None, "hi", "hi", ts)
    await db.insert_message("msg3", "ch1", "u1", "carol", None, "hi", "hi", ts)
    rows = await db.fetch_all("SELECT * FROM messages WHERE message_id = ?", ("msg3",))
    assert len(rows) == 1
