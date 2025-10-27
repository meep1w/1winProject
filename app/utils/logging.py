# app/utils/logging.py
from __future__ import annotations

import logging
import sys
from pathlib import Path

from loguru import logger

from app.config import get_config


class InterceptHandler(logging.Handler):
    """Перекидываем стандартный logging в loguru, чтобы все логи были едиными."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        # идём вверх по стеку, чтобы source в логах указывал на реальный вызов, а не на этот хендлер
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _std_to_loguru(level: str) -> int:
    """Преобразуем строковый уровень в int для std logging."""
    return getattr(logging, level.upper(), logging.INFO)


def setup_logging() -> None:
    """Единая настройка логов: stdout + файл с ротацией. Уровень берём из ENV."""
    cfg = get_config()

    # 1) Глушим стандартные хендлеры
    logging.root.handlers = []
    logging.root.setLevel(_std_to_loguru(cfg.log_level))

    # 2) Перехват стандартного logging в loguru
    intercept = InterceptHandler()
    for name in ("aiogram", "aiohttp", "asyncio"):
        logging.getLogger(name).handlers = [intercept]
        logging.getLogger(name).propagate = False
        logging.getLogger(name).setLevel(_std_to_loguru(cfg.log_level))

    logging.getLogger().handlers = [intercept]

    # 3) Настройка loguru
    logger.remove()  # убираем дефолтный sink
    logger.add(
        sys.stdout,
        level=cfg.log_level,
        backtrace=False,
        diagnose=False,
        enqueue=True,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "{message}",
    )

    # 4) Файловый лог с ротацией (ежедневно) и хранением 14 дней
    logs_dir = Path(cfg.db_path).parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        logs_dir / "bot_{time:YYYYMMDD}.log",
        level=cfg.log_level,
        rotation="00:00",
        retention="14 days",
        compression="zip",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    )

    logger.debug("Логирование инициализировано. Уровень: {}", cfg.log_level)
