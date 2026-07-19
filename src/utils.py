"""
Utility functions used throughout the application.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

import orjson


# ==========================================================
# Time Utilities
# ==========================================================


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


def current_timestamp() -> str:
    """Return ISO-8601 timestamp."""
    return utc_now().isoformat()


# ==========================================================
# Performance
# ==========================================================


def elapsed_time(start: float) -> float:
    """Return elapsed time in seconds."""
    return round(perf_counter() - start, 3)


# ==========================================================
# UUID
# ==========================================================


def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid4())


# ==========================================================
# Text Processing
# ==========================================================


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace.
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(text: str, length: int = 120) -> str:
    """Truncate long text."""
    if len(text) <= length:
        return text
    return text[:length].rstrip() + "..."


# ==========================================================
# JSON
# ==========================================================


def to_json(data: Any) -> str:
    """
    Convert Python object to formatted JSON.
    """
    return orjson.dumps(
        data,
        option=orjson.OPT_INDENT_2,
    ).decode()


# ==========================================================
# File Utilities
# ==========================================================


def ensure_directory(path: str | Path) -> Path:
    """
    Create directory if it does not exist.
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_text_file(path: str | Path) -> str:
    """
    Read UTF-8 text file.
    """
    return Path(path).read_text(encoding="utf-8")


def write_text_file(path: str | Path, content: str) -> None:
    """
    Write UTF-8 text file.
    """
    Path(path).write_text(content, encoding="utf-8")



# ==========================================================
# Collections
# ==========================================================


def remove_duplicates(items: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""
    return list(dict.fromkeys(items))


def is_blank(text: str) -> bool:
    """Check if text is empty or whitespace."""
    return not text.strip()