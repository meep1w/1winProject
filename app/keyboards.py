# app/keyboards.py
from __future__ import annotations

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from app.config import get_config
from app.utils.i18n import t
from app.db import get_links


# ===== Языки =====

def lang_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка (строгий порядок как в ТЗ).
    Колбэк-данные: set_lang:<code>
    """
    b = InlineKeyboardBuilder()
    row1 = ["ru", "en"]
    row2 = ["hi", "pt", "es"]
    row3 = ["ui", "tr", "in"]
    row4 = ["fr", "ozbek", "de"]

    for code in row1:
        b.button(text=t(f"lang.btn.{code}", lang="ru"), callback_data=f"set_lang:{code}")
    b.adjust(2)

    for code in row2:
        b.button(text=t(f"lang.btn.{code}", lang="ru"), callback_data=f"set_lang:{code}")
    b.adjust(2, 3)

    for code in row3:
        b.button(text=t(f"lang.btn.{code}", lang="ru"), callback_data=f"set_lang:{code}")
    b.adjust(2, 3, 3)

    for code in row4:
        b.button(text=t(f"lang.btn.{code}", lang="ru"), callback_data=f"set_lang:{code}")
    b.adjust(2, 3, 3, 3)

    return b.as_markup()


# ===== Главное меню =====

def _miniapp_url(lang: str, ref_code: str | None = None) -> str:
    """
    Конструктор URL для мини-аппа (+ язык и реф).
    Используется внутри WebAppInfo и при необходимости для fallback-ссылок.
    """
    cfg = get_config()
    base = f"https://{cfg.domain}/" if cfg.domain else "https://example.com/"
    qs = f"?lang={lang}"
    if ref_code:
        qs += f"&ref={ref_code}"
    return base + qs


async def main_menu_keyboard(lang: str, *, ref_code: str | None = None) -> InlineKeyboardMarkup:
    """
    Главное меню:
    [🚀 Открыть приложение (web_app)]
    [🛟 Поддержка]
    [🌐 1win Сайт] [🪙 1winToken]

    Ссылки тянем из БД (app_settings) с fallback на .env.
    """
    links = await get_links()

    b = InlineKeyboardBuilder()

    # URL мини-аппа с параметрами
    miniapp_url = _miniapp_url(lang, ref_code)

    # Кнопка, которая открывает мини-апп во встроенном WebView Telegram
    b.row(
        InlineKeyboardButton(
            text=t("menu.btn.open_app", lang=lang),
            web_app=WebAppInfo(url=miniapp_url),
        )
    )

    # Поддержка (внешняя ссылка)
    b.row(
        InlineKeyboardButton(
            text=t("menu.btn.support", lang=lang),
            url=links["support_url"],
        )
    )

    # Две внешние ссылки
    b.row(
        InlineKeyboardButton(
            text=t("menu.btn.site", lang=lang),
            url=links["ref_url"],
        ),
        InlineKeyboardButton(
            text=t("menu.btn.token", lang=lang),
            url=links["onewin_tok_url"],
        ),
    )

    return b.as_markup()
