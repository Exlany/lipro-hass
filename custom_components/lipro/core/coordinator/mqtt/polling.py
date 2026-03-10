"""MQTT polling helper functions for coordinator update intervals."""

from __future__ import annotations

from collections.abc import Mapping
import logging

from ...utils.coerce import coerce_int_option
from ..types import PropertyValue
from .policy import compute_relaxed_polling_seconds


def resolve_base_scan_interval_seconds(
    *,
    options: Mapping[str, PropertyValue] | None,
    option_name: str,
    default: int,
    min_value: int,
    max_value: int,
    logger: logging.Logger,
) -> int:
    """Resolve base scan interval from config-entry options with hardening."""
    if options is None:
        return default

    return coerce_int_option(
        options.get(option_name, default),
        option_name=option_name,
        default=default,
        min_value=min_value,
        max_value=max_value,
        logger=logger,
    )


def resolve_polling_interval_seconds_on_mqtt_connect(
    *,
    base_seconds: int,
    multiplier: int,
) -> int:
    """Resolve polling interval when MQTT is connected."""
    return compute_relaxed_polling_seconds(base_seconds, multiplier)


def resolve_polling_interval_seconds_on_mqtt_disconnect(*, base_seconds: int) -> int:
    """Resolve polling interval when MQTT is disconnected."""
    return base_seconds
