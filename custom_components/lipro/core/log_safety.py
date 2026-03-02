"""Log-safety helpers for sanitized diagnostics output."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def summarize_properties_for_log(
    properties: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
) -> dict[str, int | list[str]]:
    """Return a log-safe properties summary containing only keys and count."""
    keys: list[str] = []

    if isinstance(properties, Mapping):
        keys = [str(key) for key in properties]
    elif isinstance(properties, Sequence):
        for item in properties:
            if not isinstance(item, Mapping):
                continue
            key = item.get("key")
            if isinstance(key, str):
                keys.append(key)

    return {
        "count": len(keys),
        "keys": keys,
    }


def safe_error_placeholder(err: BaseException) -> str:
    """Build a safe error marker without exposing original message content."""
    error_name = type(err).__name__
    code = getattr(err, "code", None)
    if isinstance(code, bool):
        return error_name
    if isinstance(code, (int, str)):
        normalized = str(code).strip()
        if normalized:
            return f"{error_name}(code={normalized})"
    return error_name
