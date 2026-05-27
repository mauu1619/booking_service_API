import os
import sys

from loguru import logger

ENV = os.getenv("ENV", "dev")
LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger.remove()

logger = logger.bind(service="booking_service")

if ENV == "dev":
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level> | <magenta>{extra}</magenta>",
        colorize=True,
        enqueue=True,
    )
else:
    logger.add(sys.stderr, level="INFO", serialize=True, enqueue=True)

    logger.add(
        f"{LOG_DIR}/app.log",
        level="INFO",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        serialize=True,
    )

    logger.add(
        f"{LOG_DIR}/error.log",
        level="ERROR",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        serialize=True,
    )

logger.info("Logger initialized", env=ENV)

__all__ = ["logger"]
