"""
Application logging configuration.

This module configures Loguru for both console and file logging.
"""

from pathlib import Path

from loguru import logger

from src.config import settings
from src.constants import LOG_FILE_NAME, LOG_FORMAT

from functools import wraps
from time import perf_counter
from typing import Any, Callable

# ------------------------------------------------------------------
# Create logs directory if it doesn't exist
# ------------------------------------------------------------------

log_path = Path(LOG_FILE_NAME)
log_path.parent.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Remove default logger
# ------------------------------------------------------------------

logger.remove()

# ------------------------------------------------------------------
# Console Logger
# ------------------------------------------------------------------

logger.add(
    sink=lambda message: print(message, end=""),
    level=settings.log_level.upper(),
    format=LOG_FORMAT,
    colorize=True,
    backtrace=True,
    diagnose=False,
)

# ------------------------------------------------------------------
# File Logger
# ------------------------------------------------------------------

logger.add(
    LOG_FILE_NAME,
    level=settings.log_level.upper(),
    format=LOG_FORMAT,
    rotation="5 MB",
    retention="10 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=False,
)

def log_execution_time(operation: str | None = None):
    """
    Decorator to log the execution time of a function.

    Args:
        operation: Optional human-readable operation name.
                   Defaults to the function name.
    """

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            operation_name = operation or func.__name__

            logger.info(f"Starting: {operation_name}")

            start = perf_counter()

            try:
                result = func(*args, **kwargs)

                elapsed = perf_counter() - start

                logger.success(
                    f"Completed: {operation_name} "
                    f"({elapsed:.2f}s)"
                )

                return result

            except Exception:
                elapsed = perf_counter() - start

                logger.exception(
                    f"Failed: {operation_name} "
                    f"({elapsed:.2f}s)"
                )

                raise

        return wrapper

    return decorator

# ------------------------------------------------------------------
# Export logger
# ------------------------------------------------------------------

__all__ = [
    "logger",
    "log_execution_time",
]