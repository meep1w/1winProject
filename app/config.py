# app/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # подхват .env из корня


SUPPORTED_LANGS = ("ru", "en", "hi", "pt", "es", "ui", "tr", "in", "fr", "ozbek", "de")
DEFAULT_LANG = "ru"


@dataclass(frozen=True)
class Config:
    # core
    bot_token: str
    admin_id: int

    # postbacks
    postback_channel_id: int
    postback_secret: str

    # links
    support_url: str
    ref_url: str
    onewin_tok_url: str

    # runtime
    db_path: Path
    app_env: str
    log_level: str

    # domain (на будущее под мини-апп)
    domain: str
    domain_ip: str

    # i18n
    languages: tuple[str, ...] = SUPPORTED_LANGS
    default_lang: str = DEFAULT_LANG


def _req(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing env var: {name}")
    return val


def _build_config() -> Config:
    cfg = Config(
        bot_token=_req("BOT_TOKEN"),
        admin_id=int(_req("ADMIN_ID")),
        postback_channel_id=int(_req("POSTBACK_CHANNEL_ID")),
        postback_secret=_req("POSTBACK_SECRET"),
        support_url=_req("SUPPORT_URL"),
        ref_url=_req("REF_URL"),
        onewin_tok_url=_req("ONEWIN_TOK_URL"),
        db_path=Path(os.getenv("DB_PATH", "./data/bot.db")).resolve(),
        app_env=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        domain=os.getenv("DOMAIN", ""),
        domain_ip=os.getenv("DOMAIN_IP", ""),
    )
    # гарантируем, что папка для БД существует
    cfg.db_path.parent.mkdir(parents=True, exist_ok=True)
    return cfg


_config: Config | None = None


def get_config() -> Config:
    """Ленивая загрузка конфигурации (один раз на процесс)."""
    global _config
    if _config is None:
        _config = _build_config()
    return _config
