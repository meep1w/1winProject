# app/utils/i18n.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from app.config import get_config, SUPPORTED_LANGS, DEFAULT_LANG

_LOCALES: dict[str, dict[str, str]] = {}
_LOADED = False


def _load_locales() -> None:
    """Ленивая загрузка JSON-локалей из app/locales/*.json"""
    global _LOADED, _LOCALES
    if _LOADED:
        return

    base = Path(__file__).resolve().parent.parent / "locales"
    if not base.exists():
        _LOCALES = {}
        _LOADED = True
        return

    for p in base.glob("*.json"):
        lang = p.stem  # ru.json -> ru
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # ключи в строку, значения в строку
                    _LOCALES[lang] = {str(k): str(v) for k, v in data.items()}
        except Exception:
            # не валим процесс: просто пропустим битую локаль
            continue

    _LOADED = True


def langs() -> tuple[str, ...]:
    """Список поддерживаемых языков из конфига."""
    return SUPPORTED_LANGS


def _pick_lang(lang: str | None) -> str:
    """Нормализуем язык: если не поддерживается — дефолт."""
    if not lang:
        return DEFAULT_LANG
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def t(key: str, *, lang: str | None = None, **params: Any) -> str:
    """
    Перевод по ключу:
      - сначала язык пользователя
      - потом дефолтный язык
      - потом сам ключ (как fallback для отладки)
    Подстановки — через .format(**params)
    """
    _load_locales()
    l = _pick_lang(lang)

    # 1) точное совпадение языка
    text = _LOCALES.get(l, {}).get(key)
    # 2) fallback на дефолт
    if text is None and l != DEFAULT_LANG:
        text = _LOCALES.get(DEFAULT_LANG, {}).get(key)
    # 3) крайний случай — вернуть ключ
    if text is None:
        text = key

    try:
        if params:
            text = text.format(**params)
    except Exception:
        # при ошибке форматирования вернём как есть
        pass
    return text


def has_key(key: str, *, lang: str | None = None) -> bool:
    """Проверка наличия ключа в указанной локали (или в дефолтной)."""
    _load_locales()
    l = _pick_lang(lang)
    if key in _LOCALES.get(l, {}):
        return True
    if l != DEFAULT_LANG and key in _LOCALES.get(DEFAULT_LANG, {}):
        return True
    return False


def reload_locales() -> None:
    """Горячая перезагрузка словарей (на будущее из админки)."""
    global _LOADED, _LOCALES
    _LOADED = False
    _LOCALES = {}
    _load_locales()


def example_bootstrap() -> None:
    """
    Небольшой self-check во время разработки:
    запускаем из main.py один раз, чтобы убедиться, что локали читаются.
    Не критично в проде.
    """
    cfg = get_config()
    # просто вызовем t(), чтобы инициировать загрузку
    _ = t("app.started", lang=cfg.default_lang)
