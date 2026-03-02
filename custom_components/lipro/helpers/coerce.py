"""Coercion helpers for tolerant option/config parsing."""

from __future__ import annotations

import logging
from typing import Any


def coerce_int_option(
    value: Any,
    *,
    option_name: str,
    default: int,
    min_value: int | None = None,
    max_value: int | None = None,
    logger: logging.Logger | None = None,
) -> int:
    """Coerce an option value to int with safe fallback and optional clamp."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        if logger is not None:
            logger.warning(
                "Invalid option %s=%r, using default %d",
                option_name,
                value,
                default,
            )
        parsed = default

    if min_value is not None:
        parsed = max(min_value, parsed)
    if max_value is not None:
        parsed = min(max_value, parsed)
    return parsed


def coerce_bool_option(
    value: Any,
    *,
    option_name: str,
    default: bool,
    logger: logging.Logger | None = None,
) -> bool:
    """Coerce an option value to bool with safe fallback."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False

    if logger is not None:
        logger.warning(
            "Invalid option %s=%r, using default %s",
            option_name,
            value,
            default,
        )
    return default
