import sys

from loguru import logger

from app.core.config import settings


def configure_logger() -> None:
    # Default handler is removed to avoid duplicate outputs when configuring custom sink.
    logger.remove()

    sink = sys.stdout if settings.log_sink == "stdout" else settings.log_sink
    logger.add(
        sink,
        level=settings.log_level.upper(),
        serialize=settings.log_serialize,
        backtrace=True,
        diagnose=False,
    )


configure_logger()
