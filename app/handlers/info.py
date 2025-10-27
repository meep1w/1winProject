# app/handlers/info.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.utils.i18n import t
from app.keyboards import main_menu_keyboard
from app.db import get_user

router = Router()


@router.message(Command("info", "Info"))
async def cmd_info(msg: Message) -> None:
    user_id = msg.from_user.id
    u = await get_user(user_id)
    lang = (u or {}).get("lang", "ru")
    ref_code = (u or {}).get("ref_code")

    kb = await main_menu_keyboard(lang, ref_code=ref_code)
    await msg.answer(
        f"<b>{t('info.title', lang=lang)}</b>\n\n{t('info.text', lang=lang)}",
        reply_markup=kb
    )
