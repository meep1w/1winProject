# app/middlewares/language.py
from __future__ import annotations

from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from functools import partial

from app.db import get_user_lang
from app.utils.i18n import t


class LanguageMiddleware(BaseMiddleware):
    """
    Достаём язык пользователя из БД и кладём в data:
      - data["user_lang"] = 'ru' | 'en' | ...
      - data["t"] = partial(t, lang=data["user_lang"])
    Без лишних сообщений.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        from_user = data.get("event_from_user")  # aiogram v3 раскладывает это в data
        lang = "ru"
        if from_user:
            lang = await get_user_lang(from_user.id)
        data["user_lang"] = lang
        data["t"] = partial(t, lang=lang)
        return await handler(event, data)
