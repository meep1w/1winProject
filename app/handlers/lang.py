from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from app.keyboards import lang_keyboard, main_menu_keyboard
from app.db import set_user_lang, get_user
from app.utils.i18n import t
from loguru import logger

router = Router()

ASSETS = Path(__file__).resolve().parent.parent / "assets"

def _find_asset(stem: str) -> Optional[Path]:
    """Ищем файл по имени без расширения: png/jpg/jpeg/webp"""
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = ASSETS / f"{stem}.{ext}"
        if p.exists():
            return p
    return None


@router.message(Command("lang"))
async def cmd_lang(msg: Message) -> None:
    u = await get_user(msg.from_user.id)
    lang = (u or {}).get("lang", "ru")
    caption = t("lang.title", lang=lang)
    kb = lang_keyboard()

    img = _find_asset("lang_screen")
    logger.debug("LANG image: {}", img if img else "not found")
    if img:
        await msg.answer_photo(FSInputFile(str(img)), caption=caption, reply_markup=kb)
    else:
        await msg.answer(caption, reply_markup=kb)


@router.callback_query(F.data.startswith("set_lang:"))
async def on_set_lang(cb: CallbackQuery) -> None:
    user_id = cb.from_user.id
    new_lang = cb.data.split(":", 1)[1].strip()
    await set_user_lang(user_id, new_lang, int(time.time()))

    try:
        await cb.message.delete()
    except Exception:
        pass

    u = await get_user(user_id)
    ref_code = u.get("ref_code") if u else None
    kb = await main_menu_keyboard(new_lang, ref_code=ref_code)
    caption = t("start.title", lang=new_lang)

    img = _find_asset("menu")
    logger.debug("MENU image: {}", img if img else "not found")
    if img:
        await cb.message.answer_photo(FSInputFile(str(img)), caption=caption, reply_markup=kb)
    else:
        await cb.message.answer(caption, reply_markup=kb)

    await cb.answer()
