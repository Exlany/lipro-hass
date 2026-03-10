"""Small pure helpers shared by ``DeviceState``."""

from __future__ import annotations

from ...const.properties import (
    DIRECTION_CLOSING,
    DIRECTION_OPENING,
    kelvin_to_percent,
    percent_to_kelvin,
)


def percent_to_kelvin_for_bounds(
    percent: int,
    *,
    min_color_temp_kelvin: int,
    max_color_temp_kelvin: int,
) -> int:
    """Convert API percentage to Kelvin using device-specific bounds."""
    bounded_percent = max(0, min(100, percent))
    if max_color_temp_kelvin > 0 and min_color_temp_kelvin > 0:
        temp_range = max_color_temp_kelvin - min_color_temp_kelvin
        if temp_range <= 0:
            return min_color_temp_kelvin
        return min_color_temp_kelvin + int(bounded_percent * temp_range / 100)
    return percent_to_kelvin(bounded_percent)


def kelvin_to_percent_for_bounds(
    kelvin: int,
    *,
    min_color_temp_kelvin: int,
    max_color_temp_kelvin: int,
) -> int:
    """Convert Kelvin back to API percentage using device-specific bounds."""
    if max_color_temp_kelvin > 0 and min_color_temp_kelvin > 0:
        temp_range = max_color_temp_kelvin - min_color_temp_kelvin
        if temp_range <= 0:
            return 50
        bounded_kelvin = max(min_color_temp_kelvin, min(max_color_temp_kelvin, kelvin))
        return max(
            0,
            min(
                100,
                round((bounded_kelvin - min_color_temp_kelvin) * 100 / temp_range),
            ),
        )
    return kelvin_to_percent(kelvin)


def direction_to_ha(value: object) -> str | None:
    """Normalize Lipro curtain direction into HA-friendly strings."""
    if value == DIRECTION_OPENING:
        return "opening"
    if value == DIRECTION_CLOSING:
        return "closing"
    return None


__all__ = [
    "direction_to_ha",
    "kelvin_to_percent_for_bounds",
    "percent_to_kelvin_for_bounds",
]
