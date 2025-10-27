# app/main.py
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from app.config import get_config
from app.utils.logging import setup_logging
from app.utils import i18n as i18n_utils
from app.db import get_db
from app.middlewares.language import LanguageMiddleware

# handlers
from app.handlers.start import router as start_router
from app.handlers.lang import router as lang_router
from app.handlers.info import router as info_router
from app.handlers.admin import router as admin_router

# services
from app.services.postbacks import build_web_app
from app.services.webapp import setup_webapp_routes


async def _set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="lang", description="Сменить язык"),
        BotCommand(command="info", description="Информация"),
        BotCommand(command="admin", description="Админка"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(dp: Dispatcher, bot: Bot) -> None:
    setup_logging()
    _ = get_config()
    i18n_utils.example_bootstrap()
    await get_db()
    await _set_bot_commands(bot)


def _build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # мидлварь языка
    lang_mw = LanguageMiddleware()
    dp.message.middleware(lang_mw)
    dp.callback_query.middleware(lang_mw)

    # роутеры
    dp.include_router(start_router)
    dp.include_router(lang_router)
    dp.include_router(info_router)
    dp.include_router(admin_router)

    return dp


async def main() -> None:
    cfg = get_config()
    bot = Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = _build_dispatcher()

    await on_startup(dp, bot)

    # === HTTP-сервер: постбэки + мини-апп/статик ===
    web_app = build_web_app(bot)       # /postback, /health
    setup_webapp_routes(web_app)       # /app, /api/settings, /static/*
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()

    try:
        # Telegram Polling
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
