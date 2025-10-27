# app/db.py
from __future__ import annotations

import aiosqlite
from pathlib import Path
from typing import Optional, Any, Dict
import time

from app.config import get_config

_DB_CONN: aiosqlite.Connection | None = None


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    username       TEXT,
    first_name     TEXT,
    last_name      TEXT,
    lang           TEXT NOT NULL DEFAULT 'ru',
    ref_code       TEXT,
    created_at     INTEGER NOT NULL,
    updated_at     INTEGER NOT NULL,
    blocked        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS postbacks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    event_type    TEXT NOT NULL,
    payload       TEXT,
    created_at    INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS broadcasts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id     INTEGER NOT NULL,
    text          TEXT,
    markup_json   TEXT,
    filter_json   TEXT,
    status        TEXT NOT NULL DEFAULT 'draft',
    total         INTEGER DEFAULT 0,
    sent          INTEGER DEFAULT 0,
    failed        INTEGER DEFAULT 0,
    created_at    INTEGER NOT NULL,
    started_at    INTEGER,
    finished_at   INTEGER
);

-- Новая таблица настроек приложения (гибкие ссылки и не только)
CREATE TABLE IF NOT EXISTS app_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    updated_at  INTEGER NOT NULL
);

-- Профиль пользователя для мини-аппа (анкета "Проверить RTP")
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id     INTEGER PRIMARY KEY REFERENCES users(user_id),
    full_name   TEXT NOT NULL,
    account_id  TEXT NOT NULL,
    tg_handle   TEXT NOT NULL,
    geo         TEXT NOT NULL,
    created_at  INTEGER NOT NULL,
    updated_at  INTEGER NOT NULL
);
"""


async def get_db() -> aiosqlite.Connection:
    """
    Единый connection (aiosqlite). При первом вызове применяет схему и
    заливает дефолтные ссылки из .env, если их нет.
    """
    global _DB_CONN
    if _DB_CONN is None:
        cfg = get_config()
        db_path: Path = cfg.db_path
        _DB_CONN = await aiosqlite.connect(db_path.as_posix())
        await _DB_CONN.executescript(SCHEMA_SQL)
        await _DB_CONN.execute("PRAGMA foreign_keys = ON;")
        await _DB_CONN.commit()
        # гарантируем дефолтные ссылки в БД
        await _ensure_default_links(_DB_CONN)
    return _DB_CONN


# ===== Settings (generic) =====

async def set_setting(key: str, value: str) -> None:
    db = await get_db()
    ts = int(time.time())
    await db.execute(
        """
        INSERT INTO app_settings(key, value, updated_at)
        VALUES(?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """,
        (key, value, ts),
    )
    await db.commit()


async def get_setting(key: str) -> Optional[str]:
    db = await get_db()
    async with db.execute("SELECT value FROM app_settings WHERE key=?", (key,)) as cur:
        row = await cur.fetchone()
        return row[0] if row else None


# ===== Links in settings =====

_LINK_KEYS = ("support_url", "ref_url", "onewin_tok_url")


async def _ensure_default_links(db: aiosqlite.Connection) -> None:
    """
    При самом первом старте переносим значения из .env в app_settings,
    если записей ещё нет.
    """
    cfg = get_config()
    ts = int(time.time())

    async def _exists(k: str) -> bool:
        async with db.execute("SELECT 1 FROM app_settings WHERE key=?", (k,)) as cur:
            return (await cur.fetchone()) is not None

    defaults = {
        "support_url": cfg.support_url,
        "ref_url": cfg.ref_url,
        "onewin_tok_url": cfg.onewin_tok_url,
    }

    for k, v in defaults.items():
        if not await _exists(k):
            await db.execute(
                "INSERT INTO app_settings(key, value, updated_at) VALUES(?, ?, ?)",
                (k, v, ts),
            )
    await db.commit()


async def set_links(*, support_url: Optional[str] = None, ref_url: Optional[str] = None, onewin_tok_url: Optional[str] = None) -> None:
    """
    Обновить ссылки частично или полностью.
    """
    if support_url is not None:
        await set_setting("support_url", support_url)
    if ref_url is not None:
        await set_setting("ref_url", ref_url)
    if onewin_tok_url is not None:
        await set_setting("onewin_tok_url", onewin_tok_url)


async def get_links() -> Dict[str, str]:
    """
    Забрать актуальные ссылки из БД (fallback на .env для надёжности).
    """
    cfg = get_config()
    result = {
        "support_url": cfg.support_url,
        "ref_url": cfg.ref_url,
        "onewin_tok_url": cfg.onewin_tok_url,
    }
    for k in _LINK_KEYS:
        v = await get_setting(k)
        if v:
            result[k] = v
    return result


# ===== Users =====

async def upsert_user(
    user_id: int,
    *,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
    lang: Optional[str],
    ref_code: Optional[str],
    ts: int
) -> None:
    db = await get_db()
    await db.execute(
        """
        INSERT INTO users(user_id, username, first_name, last_name, lang, ref_code, created_at, updated_at, blocked)
        VALUES(?, ?, ?, ?, COALESCE(?, 'ru'), ?, ?, ?, 0)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            lang=COALESCE(excluded.lang, users.lang),
            updated_at=excluded.updated_at
        """,
        (user_id, username, first_name, last_name, lang, ref_code, ts, ts),
    )
    await db.commit()


async def set_user_lang(user_id: int, lang: str, ts: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE users SET lang=?, updated_at=? WHERE user_id=?",
        (lang, ts, user_id),
    )
    await db.commit()


async def get_user_lang(user_id: int) -> str:
    db = await get_db()
    async with db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)) as cur:
        row = await cur.fetchone()
        return row[0] if row and row[0] else "ru"


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    db = await get_db()
    async with db.execute(
        "SELECT user_id, username, first_name, last_name, lang, ref_code, created_at, updated_at, blocked FROM users WHERE user_id=?",
        (user_id,),
    ) as cur:
        row = await cur.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))


async def count_users_by_lang(lang: Optional[str] = None) -> int:
    db = await get_db()
    if lang:
        async with db.execute("SELECT COUNT(*) FROM users WHERE lang=? AND blocked=0", (lang,)) as cur:
            (n,) = await cur.fetchone()
            return int(n)
    async with db.execute("SELECT COUNT(*) FROM users WHERE blocked=0") as cur:
        (n,) = await cur.fetchone()
        return int(n)


async def set_blocked(user_id: int, blocked: bool) -> None:
    db = await get_db()
    await db.execute("UPDATE users SET blocked=? WHERE user_id=?", (1 if blocked else 0, user_id))
    await db.commit()


# ===== Postbacks =====

async def add_postback(user_id: int, event_type: str, payload: str, ts: int) -> int:
    db = await get_db()
    cur = await db.execute(
        "INSERT INTO postbacks(user_id, event_type, payload, created_at) VALUES(?, ?, ?, ?)",
        (user_id, event_type, payload, ts),
    )
    await db.commit()
    return cur.lastrowid


# ===== Broadcasts =====

async def create_broadcast(author_id: int, text: str, markup_json: str, filter_json: str, ts: int) -> int:
    db = await get_db()
    cur = await db.execute(
        """
        INSERT INTO broadcasts(author_id, text, markup_json, filter_json, status, total, sent, failed, created_at)
        VALUES(?, ?, ?, ?, 'draft', 0, 0, 0, ?)
        """,
        (author_id, text, markup_json, filter_json, ts),
    )
    await db.commit()
    return cur.lastrowid


async def set_broadcast_status(broadcast_id: int, status: str, *, started_at: Optional[int] = None, finished_at: Optional[int] = None) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE broadcasts SET status=?, started_at=COALESCE(?, started_at), finished_at=COALESCE(?, finished_at) WHERE id=?",
        (status, started_at, finished_at, broadcast_id),
    )
    await db.commit()


# ===== User Profiles ( анкета RTP ) =====

async def upsert_user_profile(
    user_id: int,
    full_name: str,
    account_id: str,
    tg_handle: str,
    geo: str,
) -> None:
    """
    Сохраняем/обновляем анкету пользователя для мини-аппа.
    """
    db = await get_db()
    ts = int(time.time())
    await db.execute(
        """
        INSERT INTO user_profiles(user_id, full_name, account_id, tg_handle, geo, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name=excluded.full_name,
            account_id=excluded.account_id,
            tg_handle=excluded.tg_handle,
            geo=excluded.geo,
            updated_at=excluded.updated_at
        """,
        (user_id, full_name, account_id, tg_handle, geo, ts, ts),
    )
    await db.commit()


async def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Вернёт словарь профиля или None.
    """
    db = await get_db()
    db.row_factory = aiosqlite.Row
    async with db.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)) as cur:
        row = await cur.fetchone()
        return dict(row) if row else None
