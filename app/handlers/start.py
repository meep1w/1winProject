from __future__ import annotations

import time
from typing import Optional
from pathlib import Path

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from app.db import upsert_user, get_user
from app.keyboards import lang_keyboard, main_menu_keyboard
from app.utils.i18n import t
from loguru import logger

router = Router()

ASSETS = Path(__file__).resolve().parent.parent / "assets"

def _find_asset(stem: str) -> Optional[Path]:
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = ASSETS / f"{stem}.{ext}"
        if p.exists():
            return p
    return None


def _extract_ref(msg: Message) -> Optional[str]:
    if not msg.text:
        return None
    parts = msg.text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].startswith("/start"):
        payload = parts[1].strip()
        return payload or None
    return None


@router.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    ts = int(time.time())
    user_id = msg.from_user.id
    payload_ref = _extract_ref(msg)

    existing = await get_user(user_id)
    ref_code_for_upsert = payload_ref if existing is None else None

    await upsert_user(
        user_id=user_id,
        username=msg.from_user.username,
        first_name=msg.from_user.first_name,
        last_name=msg.from_user.last_name,
        lang=None,
        ref_code=ref_code_for_upsert,
        ts=ts,
    )

    u = await get_user(user_id)
    lang = (u or {}).get("lang", "ru")
    ref_code = (u or {}).get("ref_code")
    is_first_visit = u and (u["created_at"] == u["updated_at"])

    if is_first_visit:
        caption = t("lang.title", lang="ru")
        kb = lang_keyboard()
        img = _find_asset("lang_screen")
        logger.debug("LANG image: {}", img if img else "not found")
        if img:
            await msg.answer_photo(FSInputFile(str(img)), caption=caption, reply_markup=kb)
        else:
            await msg.answer(caption, reply_markup=kb)
        return

    kb = await main_menu_keyboard(lang, ref_code=ref_code)
    caption = t("start.title", lang=lang)
    img = _find_asset("menu")
    logger.debug("MENU image: {}", img if img else "not found")
    if img:
        await msg.answer_photo(FSInputFile(str(img)), caption=caption, reply_markup=kb)
    else:
        await msg.answer(caption, reply_markup=kb)
