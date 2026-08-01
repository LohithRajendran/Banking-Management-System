"""
Logging Configuration
Sets up structured JSON logging for production and colorful logging for development.
"""

import logging
import sys
from pathlib import Path
from config.settings_fastapi import settings


def setup_logging() -> None:
    """Configures global logging system for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
    ]

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True,
    )


logger = logging.getLogger("banking")
