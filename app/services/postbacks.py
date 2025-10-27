# app/services/postbacks.py
from __future__ import annotations

import json
import time
from typing import Dict, Any, Optional

from aiohttp import web
from aiogram import Bot

from app.config import get_config
from app.db import add_postback


# ======== Маппинг событий 1Win ========
# В ПП у тебя отдельные поля: Регистрация, Доход, Все депозиты, Первый депозит, Повторный депозит, Запуск приложения.
# В каждую ссылку мы добавим фиксированный query-параметр event=...
_EVENT_ALIASES = {
    "register": {"register", "registration", "reg"},
    "income": {"income", "revenue", "profit", "payout"},
    "all_deposits": {"all_deposits", "any_deposit", "deposit"},
    "ftd": {"ftd", "first_deposit", "firstdeposit"},
    "rtd": {"rtd", "repeat_deposit", "redeposit"},
    "app_start": {"app_start", "startapp", "open_app"},
}


def _normalize_event(q: Dict[str, str]) -> str:
    ev = (q.get("event") or q.get("status") or "").lower().strip()
    for norm, aliases in _EVENT_ALIASES.items():
        if ev in aliases or ev == norm:
            return norm
    # эвристика, если ПП не проставила event
    if q.get("transaction_id"):
        # если есть транзакция — это какой-то депозит
        if q.get("amount"):
            return "rtd"
        return "all_deposits"
    if q.get("amount"):
        return "income"
    return "register"


def _extract_user_id(q: Dict[str, str]) -> Optional[int]:
    """
    1Win даёт {user_id}. На всякий случай поддержим sub1/sub2.
    """
    for key in ("user_id", "uid", "tg_id", "sub1", "sub_id", "sub"):
        v = q.get(key)
        if v and v.isdigit():
            return int(v)
    return None


def _format_postback_message(event_type: str, q: Dict[str, str]) -> str:
    parts = [f"📬 <b>Postback</b> — <code>{event_type}</code>"]
    uid = _extract_user_id(q)
    if uid:
        parts.append(f"👤 TG: <code>{uid}</code>")

    amount = q.get("amount")
    if amount:
        parts.append(f"💸 Сумма: <b>{amount}</b>")

    tx = q.get("transaction_id") or q.get("trans_id") or q.get("tid")
    if tx:
        parts.append(f"🧾 Tx: <code>{tx}</code>")

    country = q.get("country")
    if country:
        parts.append(f"🌍 Страна: <code>{country}</code>")

    # субметки
    s1, s2 = q.get("sub1"), q.get("sub2")
    subs_line = " • ".join([f"sub1=<code>{s1}</code>" if s1 else "", f"sub2=<code>{s2}</code>" if s2 else ""]).strip(" •")
    if subs_line:
        parts.append(f"🏷 {subs_line}")

    # полезно видеть всё сырьё (усекаем)
    tail = dict(sorted(q.items()))
    raw = json.dumps(tail, ensure_ascii=False)
    if len(raw) > 1200:
        raw = raw[:1200] + "…"
    parts.append(f"\n<blockquote expandable>{raw}</blockquote>")
    return "\n".join(parts)


async def handle_postback(request: web.Request) -> web.Response:
    """
    GET/POST /postback?... — валидируем секрет, пишем в БД и шлём в канал.
    Параметры от 1Win (по скринам): {event_id}, {date}, {hash_id}, {hash_name}, {source_id}, {source_name},
    {amount}, {transaction_id}, {country}, {user_id}, {sub1}, {sub2}
    """
    cfg = get_config()
    if request.method == "GET":
        params = {k: v for k, v in request.rel_url.query.items()}
    else:
        data = await request.post()
        params = {k: str(v) for k, v in data.items()}

    # секрет
    if (params.get("secret") or "") != cfg.postback_secret:
        return web.Response(status=403, text="forbidden")

    event_type = _normalize_event(params)
    user_id = _extract_user_id(params) or 0

    payload = json.dumps(params, ensure_ascii=False)
    await add_postback(user_id, event_type, payload, int(time.time()))

    text = _format_postback_message(event_type, params)
    bot: Bot = request.app["bot"]

    try:
        await bot.send_message(cfg.postback_channel_id, text)
    except Exception:
        # чтобы ПП не ддосила ретраями, подтверждаем при ошибке доставки в канал
        return web.Response(status=202, text="accepted")

    return web.Response(text="ok")


def build_web_app(bot: Bot) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.add_routes([
        web.get("/postback", handle_postback),
        web.post("/postback", handle_postback),
        web.get("/health", lambda _: web.Response(text="ok")),
    ])
    return app
