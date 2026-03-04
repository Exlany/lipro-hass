"""Coercion helpers for tolerant option/config parsing."""

from __future__ import annotations

import logging
from typing import Any

from ..core.utils.boollike import parse_boollike


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
    parsed = parse_boollike(value)
    if parsed is not None:
        return parsed

    if logger is not None:
        logger.warning(
            "Invalid option %s=%r, using default %s",
            option_name,
            value,
            default,
        )
    return default
