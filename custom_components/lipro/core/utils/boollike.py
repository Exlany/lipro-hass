"""Shared bool-like parsing helpers.

This module is dependency-light so it can be reused across core modules without
creating import cycles.
"""

from __future__ import annotations

_TRUE_STRINGS = frozenset({"1", "true", "yes", "on"})
_FALSE_STRINGS = frozenset({"0", "false", "no", "off", ""})


def parse_boollike(value: object) -> bool | None:
    """Parse a bool-like value into ``bool``.

    Returns ``None`` when the value cannot be interpreted.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE_STRINGS:
            return True
        if normalized in _FALSE_STRINGS:
            return False
    return None


__all__ = ["parse_boollike"]
