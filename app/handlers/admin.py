# app/handlers/admin.py
from __future__ import annotations

import asyncio
from typing import Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.config import get_config, SUPPORTED_LANGS
from app.db import (
    get_db,
    count_users_by_lang,
    set_blocked,
    set_links,
    get_links,
)

router = Router()

# --- простейшее состояние для диалогов (без FSM) ---
_ADMIN_STATE: dict[int, str] = {}  # "await_broadcast_text" | "await_link_support" | "await_link_ref" | "await_link_token"
_ADMIN_BROADCAST_LANG: dict[int, Optional[str]] = {}


def _ensure_admin(user_id: int) -> bool:
    return user_id == get_config().admin_id


# ===== Клавиатуры админки =====

def _admin_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="📣 Рассылка", callback_data="admin:broadcast")
    kb.button(text="📊 Статистика", callback_data="admin:stats")
    kb.button(text="🔗 Ссылки", callback_data="admin:links")
    kb.adjust(2, 1)
    return kb


def _broadcast_lang_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="🌍 Всем языкам", callback_data="admin:broadcast:lang:all")
    for code in SUPPORTED_LANGS:
        flag = {
            "ru": "🇷🇺", "en": "🇬🇧", "hi": "🇮🇳", "pt": "🇵🇹", "es": "🇪🇸",
            "ui": "🇺🇦", "tr": "🇹🇷", "in": "🇮🇩", "fr": "🇫🇷", "ozbek": "🇺🇿", "de": "🇩🇪"
        }.get(code, "🗂")
        kb.button(text=f"{flag} {code}", callback_data=f"admin:broadcast:lang:{code}")
    kb.button(text="⬅ Назад", callback_data="admin:back")
    kb.adjust(2, 3, 3, 3, 1)
    return kb


def _links_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛠 Изменить Поддержку", callback_data="admin:links:edit:support")
    kb.button(text="🛠 Изменить 1win Сайт", callback_data="admin:links:edit:ref")
    kb.button(text="🛠 Изменить 1winToken", callback_data="admin:links:edit:token")
    kb.button(text="⬅ Назад", callback_data="admin:back")
    kb.adjust(1, 1, 1, 1)
    return kb


# ===== Вход в админку =====

@router.message(Command("admin"))
async def cmd_admin(msg: Message) -> None:
    if not _ensure_admin(msg.from_user.id):
        await msg.answer("Доступ запрещён.")
        return
    _ADMIN_STATE.pop(msg.from_user.id, None)
    _ADMIN_BROADCAST_LANG.pop(msg.from_user.id, None)

    await msg.answer(
        "<b>Админка</b>\nВыберите раздел:",
        reply_markup=_admin_menu_kb().as_markup(),
    )


@router.callback_query(F.data == "admin:back")
async def on_admin_back(cb: CallbackQuery) -> None:
    if not _ensure_admin(cb.from_user.id):
        await cb.answer("Нет доступа", show_alert=True)
        return
    _ADMIN_STATE.pop(cb.from_user.id, None)
    await cb.message.edit_text(
        "<b>Админка</b>\nВыберите раздел:",
        reply_markup=_admin_menu_kb().as_markup(),
    )
    await cb.answer()


# ===== Статистика =====
@router.callback_query(F.data == "admin:stats")
async def on_admin_stats(cb: CallbackQuery) -> None:
    if not _ensure_admin(cb.from_user.id):
        await cb.answer("Нет доступа", show_alert=True)
        return

    total = await count_users_by_lang(None)
    lines = [f"👥 Пользователей: <b>{total}</b>"]

    lang_counts = []
    for code in SUPPORTED_LANGS:
        n = await count_users_by_lang(code)
        if n:
            flag = {
                "ru": "🇷🇺", "en": "🇬🇧", "hi": "🇮🇳", "pt": "🇵🇹", "es": "🇪🇸",
                "ui": "🇺🇦", "tr": "🇹🇷", "in": "🇮🇩", "fr": "🇫🇷", "ozbek": "🇺🇿", "de": "🇩🇪"
            }.get(code, "🏳️")
            lang_counts.append(f"{flag} <code>{code}</code>: <b>{n}</b>")
    if lang_counts:
        lines.append("📌 По языкам:\n" + "\n".join(lang_counts))

    await cb.message.edit_text(
        "📊 <b>Статистика</b>\n\n" + "\n".join(lines),
        reply_markup=_admin_menu_kb().as_markup(),
    )
    await cb.answer()


# ===== Рассылка =====
@router.callback_query(F.data == "admin:broadcast")
async def on_admin_broadcast(cb: CallbackQuery) -> None:
    if not _ensure_admin(cb.from_user.id):
        await cb.answer("Нет доступа", show_alert=True)
        return

    _ADMIN_STATE[cb.from_user.id] = "await_broadcast_text"
    _ADMIN_BROADCAST_LANG[cb.from_user.id] = None

    await cb.message.edit_text(
        "📣 <b>Рассылка</b>\n\n"
        "1) Выберите аудиторию по языку или всем.\n"
        "2) Отправьте текст одним сообщением (HTML поддерживается).\n",
        reply_markup=_broadcast_lang_kb().as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("admin:broadcast:lang:"))
async def on_broadcast_pick_lang(cb: CallbackQuery) -> None:
    if not _ensure_admin(cb.from_user.id):
        await cb.answer("Нет доступа", show_alert=True)
        return

    lang = cb.data.split(":")[-1]
    _ADMIN_BROADCAST_LANG[cb.from_user.id] = None if lang == "all" else lang

    picked = "🌍 всем" if lang == "all" else f"<code>{lang}</code>"
    await cb.message.edit_text(
        f"📣 <b>Рассылка</b>\nВыбрано: {picked}\n\n"
        "Теперь пришлите <b>текст рассылки</b> одним сообщением.\n"
        "Отмена — /admin.",
        reply_markup=_broadcast_lang_kb().as_markup(),
    )
    await cb.answer()


@router.message(F.text, ~Command("admin"))
async def on_admin_maybe_broadcast_text(msg: Message) -> None:
    # если это не режим рассылки — обработка ниже для ссылок
    if not _ensure_admin(msg.from_user.id):
        return

    state = _ADMIN_STATE.get(msg.from_user.id)
    if state != "await_broadcast_text":
        # передадим обработку блоку редактирования ссылок
        await _maybe_handle_link_edit(msg, state)
        return

    text = msg.html_text
    target_lang = _ADMIN_BROADCAST_LANG.get(msg.from_user.id)

    _ADMIN_STATE.pop(msg.from_user.id, None)
    _ADMIN_BROADCAST_LANG.pop(msg.from_user.id, None)

    # получатели
    db = await get_db()
    if target_lang:
        async with db.execute("SELECT user_id FROM users WHERE blocked=0 AND lang=?", (target_lang,)) as cur:
            rows = await cur.fetchall()
    else:
        async with db.execute("SELECT user_id FROM users WHERE blocked=0") as cur:
            rows = await cur.fetchall()

    user_ids = [r[0] for r in rows]
    total = len(user_ids)
    if total == 0:
        await msg.answer("Ни одного получателя не найдено.")
        return

    sent = failed = 0
    bot = msg.bot
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            await set_blocked(uid, True)
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.03)

    await msg.answer(
        f"✅ Рассылка завершена.\nВсего: {total}\nУспешно: {sent}\nОшибок: {failed}"
    )


# ===== Ссылки (редактирование) =====

@router.callback_query(F.data == "admin:links")
async def on_admin_links(cb: CallbackQuery) -> None:
    if not _ensure_admin(cb.from_user.id):
        await cb.answer("Нет доступа", show_alert=True)
        return

    links = await get_links()
    await cb.message.edit_text(
        "🔗 <b>Ссылки</b>\n"
        f"• Поддержка: <code>{links['support_url']}</code>\n"
        f"• 1win Сайт: <code>{links['ref_url']}</code>\n"
        f"• 1winToken: <code>{links['onewin_tok_url']}</code>\n\n"
        "Выберите, что изменить:",
        reply_markup=_links_menu_kb().as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("admin:links:edit:"))
async def on_admin_links_edit(cb: CallbackQuery) -> None:
    if not _ensure_admin(cb.from_user.id):
        await cb.answer("Нет доступа", show_alert=True)
        return

    key = cb.data.split(":")[-1]  # support|ref|token
    label = {"support": "Поддержка", "ref": "1win Сайт", "token": "1winToken"}[key]
    _ADMIN_STATE[cb.from_user.id] = {
        "support": "await_link_support",
        "ref": "await_link_ref",
        "token": "await_link_token",
    }[key]

    await cb.message.edit_text(
        f"✏️ Введите новую ссылку для <b>{label}</b>.\n"
        "Требования: начинается с http:// или https://\n"
        "Отмена — /admin.",
        reply_markup=_links_menu_kb().as_markup(),
    )
    await cb.answer()


async def _maybe_handle_link_edit(msg: Message, state: Optional[str]) -> None:
    if state not in {"await_link_support", "await_link_ref", "await_link_token"}:
        return

    url = (msg.text or "").strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await msg.answer("⚠️ Неверный формат. Ссылка должна начинаться с http:// или https://\nПовторите или /admin для отмены.")
        return

    if state == "await_link_support":
        await set_links(support_url=url)
    elif state == "await_link_ref":
        await set_links(ref_url=url)
    else:
        await set_links(onewin_tok_url=url)

    _ADMIN_STATE.pop(msg.from_user.id, None)

    links = await get_links()
    await msg.answer(
        "✅ Ссылка обновлена.\n\n"
        "Текущие значения:\n"
        f"• Поддержка: <code>{links['support_url']}</code>\n"
        f"• 1win Сайт: <code>{links['ref_url']}</code>\n"
        f"• 1winToken: <code>{links['onewin_tok_url']}</code>",
        reply_markup=_links_menu_kb().as_markup(),
    )
