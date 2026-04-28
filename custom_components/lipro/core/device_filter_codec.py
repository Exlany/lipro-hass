"""Shared device-filter option codecs for UI and runtime consumers."""

from __future__ import annotations

from collections.abc import Iterable
import re

from ..const.config import (
    DEFAULT_DEVICE_FILTER_MODE,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
    DEVICE_FILTER_MODE_OFF,
    MAX_DEVICE_FILTER_LIST_CHARS,
    MAX_DEVICE_FILTER_LIST_ITEMS,
)

_DEVICE_FILTER_MODE_VALUES: frozenset[str] = frozenset(
    {
        DEVICE_FILTER_MODE_OFF,
        DEVICE_FILTER_MODE_INCLUDE,
        DEVICE_FILTER_MODE_EXCLUDE,
    }
)
_DEVICE_FILTER_LIST_SPLIT_RE = re.compile(r"[\r\n,;]+")


def normalize_device_filter_mode(value: object) -> str:
    """Normalize raw mode option to one canonical device filter mode."""
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in _DEVICE_FILTER_MODE_VALUES:
            return normalized
    return DEFAULT_DEVICE_FILTER_MODE


def split_device_filter_text(value: str) -> list[str]:
    """Split one raw device-filter string into canonical tokens."""
    normalized = (
        value[:MAX_DEVICE_FILTER_LIST_CHARS].replace("\r\n", "\n").replace("\r", "\n")
    )
    if MAX_DEVICE_FILTER_LIST_ITEMS <= 0:
        return []

    tokens: list[str] = []
    for token in _DEVICE_FILTER_LIST_SPLIT_RE.split(normalized):
        stripped = token.strip()
        if not stripped:
            continue
        tokens.append(stripped)
        if len(tokens) >= MAX_DEVICE_FILTER_LIST_ITEMS:
            break
    return tokens


def coerce_device_filter_list_text(value: object) -> str:
    """Coerce one stored filter-list option to canonical form-friendly text."""
    if isinstance(value, str):
        separator = ", "
        if "," in value and not any(marker in value for marker in ("\r", "\n", ";")):
            separator = ","
        return separator.join(split_device_filter_text(value))[
            :MAX_DEVICE_FILTER_LIST_CHARS
        ]
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, str)):
        parts: list[str] = []
        for item in value:
            for token in split_device_filter_text(str(item)):
                parts.append(token)
                if len(parts) >= MAX_DEVICE_FILTER_LIST_ITEMS:
                    break
            if len(parts) >= MAX_DEVICE_FILTER_LIST_ITEMS:
                break
        return ", ".join(parts)[:MAX_DEVICE_FILTER_LIST_CHARS]
    return ""


def parse_device_filter_values(value: object) -> frozenset[str]:
    """Parse one persisted device-filter value payload into lowercase value set."""
    if isinstance(value, str):
        tokens = split_device_filter_text(value)
    else:
        coerced = coerce_device_filter_list_text(value)
        tokens = split_device_filter_text(coerced)
    return frozenset(token.lower() for token in tokens)


__all__ = [
    "coerce_device_filter_list_text",
    "normalize_device_filter_mode",
    "parse_device_filter_values",
    "split_device_filter_text",
]
