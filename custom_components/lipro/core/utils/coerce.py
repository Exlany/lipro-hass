"""Value coercion helpers shared across core modules."""

from __future__ import annotations

import logging
from typing import Any

from .boollike import parse_boollike


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
    except TypeError, ValueError:
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


def coerce_boollike(
    value: Any,
    *,
    default: bool = False,
    logger: logging.Logger | None = None,
    context: str = "value",
) -> bool:
    """Coerce a backend bool-like value into ``bool``.

    The Lipro cloud and MQTT payloads contain booleans represented as:
    - bool
    - int/float (0/1, but some payloads use any non-zero as true)
    - strings ("true"/"false", "on"/"off", "1"/"0")

    Unknown values fall back to ``default``. When ``logger`` is provided, unexpected
    types/strings are logged at debug level with the given ``context`` label.
    """
    parsed = parse_boollike(value)
    if parsed is not None:
        return parsed
    if isinstance(value, str):
        if logger is not None:
            logger.debug(
                "Unexpected %s bool-like string value (len=%d)",
                context,
                len(value),
            )
        return default
    if value is None:
        return default

    if logger is not None:
        logger.debug(
            "Unexpected %s bool-like value type: %s",
            context,
            type(value).__name__,
        )
    return default
