# app/services/webapp.py
from __future__ import annotations

from pathlib import Path
from aiohttp import web

from app.db import get_links, get_user_profile, upsert_user_profile

# Корень с файлами мини-аппа
MINIAPP_DIR = Path(__file__).resolve().parent.parent / "miniapp"
INDEX_FILE = MINIAPP_DIR / "index.html"


# ---------- helpers ----------

def _get_user_id(request: web.Request) -> int | None:
    """
    Пытаемся извлечь user_id:
      1) из query (?user_id=...)
      2) из заголовка X-TG-User-ID
    В реальном WebApp можно пробрасывать user_id из initData после верификации.
    """
    uid = request.query.get("user_id") or request.headers.get("X-TG-User-ID")
    if not uid:
        return None
    try:
        return int(uid)
    except ValueError:
        return None


# ---------- API ----------

async def api_settings(_: web.Request) -> web.Response:
    """
    GET /api/settings -> {"support_url": "...", "ref_url": "...", "onewin_tok_url": "..."}
    Берём из БД (админка управляет).
    """
    links = await get_links()
    return web.json_response(links)


async def api_get_profile(request: web.Request) -> web.Response:
    """
    GET /api/profile?user_id=...  ->  профиль пользователя или {"ok":true,"profile":null}
    """
    user_id = _get_user_id(request)
    if not user_id:
        return web.json_response({"ok": False, "error": "missing user_id"}, status=400)

    profile = await get_user_profile(user_id)
    return web.json_response({"ok": True, "profile": profile})


async def api_upsert_profile(request: web.Request) -> web.Response:
    """
    POST /api/profile?user_id=...
    JSON: { "full_name": "...", "account_id": "...", "tg_handle": "@name", "geo": "RU" }
    Все поля обязательные.
    """
    user_id = _get_user_id(request)
    if not user_id:
        return web.json_response({"ok": False, "error": "missing user_id"}, status=400)

    if not request.content_type.startswith("application/json"):
        return web.json_response({"ok": False, "error": "content_type must be application/json"}, status=415)

    data = await request.json()
    full_name  = (data.get("full_name") or "").strip()
    account_id = (data.get("account_id") or "").strip()
    tg_handle  = (data.get("tg_handle") or "").strip()
    geo        = (data.get("geo") or "").strip()

    if not (full_name and account_id and tg_handle and geo):
        return web.json_response({"ok": False, "error": "all fields are required"}, status=400)

    # Лёгкая нормализация
    if tg_handle and not tg_handle.startswith("@"):
        tg_handle = "@" + tg_handle

    # Ограничим длину полей, чтобы не словить мусор
    full_name  = full_name[:100]
    account_id = account_id[:80]
    tg_handle  = tg_handle[:64]
    geo        = geo[:12]

    await upsert_user_profile(
        user_id=user_id,
        full_name=full_name,
        account_id=account_id,
        tg_handle=tg_handle,
        geo=geo,
    )
    return web.json_response({"ok": True})


# ---------- MiniApp ----------

async def serve_index(_: web.Request) -> web.StreamResponse:
    """
    GET /app -> index.html мини-аппа (SPA).
    Параметры (?lang=..., ?ref=...) просто пробрасываются на фронт как есть.
    """
    if not INDEX_FILE.exists():
        return web.Response(status=404, text="miniapp/index.html not found")
    return web.FileResponse(INDEX_FILE)


def setup_webapp_routes(app: web.Application) -> None:
    """
    Вешаем маршруты мини-аппа на aiohttp-приложение.
    Раздаём статику по двум префиксам:
      - /static/*      — абсолютные пути
      - /app/static/*  — относительные пути из /app (./static/...)
    """
    # API
    app.router.add_get("/api/settings", api_settings)
    app.router.add_get("/api/profile", api_get_profile)
    app.router.add_post("/api/profile", api_upsert_profile)

    # Статика (CSS/JS/картинки)
    static_dir = MINIAPP_DIR / "static"
    if static_dir.exists():
        # Абсолютные пути
        app.router.add_static(
            "/static/",
            path=str(static_dir),
            name="static_root",
            show_index=False,
        )
        # Относительные пути из /app (./static/...)
        app.router.add_static(
            "/app/static/",
            path=str(static_dir),
            name="static_under_app",
            show_index=False,
        )

    # Страница мини-аппа
    app.router.add_get("/app", serve_index)
