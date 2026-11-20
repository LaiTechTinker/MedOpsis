from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path

from ai_services.core.config import settings


def _database_path() -> Path:
    prefix = "sqlite:///"
    uri = settings.DATABASE_URI
    if not uri.startswith(prefix):
        raise RuntimeError("Only sqlite DATABASE_URI is supported by the voice service.")
    location = uri[len(prefix):]
    if location == ":memory:":
        return Path(":memory:")
    path = Path(location)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_database_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS voice_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_voice_messages_conversation "
            "ON voice_messages(conversation_id, created_at)"
        )


def close_database() -> None:
    return None


async def save_voice_message(
    conversation_id: str,
    user_id: str,
    role: str,
    content: str,
) -> None:
    def save() -> None:
        with _connection() as connection:
            connection.execute(
                """
                INSERT INTO voice_messages(conversation_id, user_id, role, content)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, user_id, role, content),
            )

    await asyncio.to_thread(save)
