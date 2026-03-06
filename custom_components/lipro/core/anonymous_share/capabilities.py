"""Anonymous-share capability detection helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from ...const.properties import (
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BATTERY,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_DARK,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_GEAR,
    PROP_FAN_MODE,
    PROP_FOCUS_MODE,
    PROP_HEATER_MODE,
    PROP_LIGHT_MODE,
    PROP_POSITION,
    PROP_SLEEP_AID_ENABLE,
    PROP_TEMPERATURE,
    PROP_WAKE_UP_ENABLE,
    PROP_WIND_GEAR,
)

if TYPE_CHECKING:
    from ..device.device import LiproDevice

_LIGHT_PRIMARY_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_BRIGHTNESS, "brightness"),
    (PROP_TEMPERATURE, "color_temp"),
)

_LIGHT_SECONDARY_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_FADE_STATE, "fade"),
    (PROP_FOCUS_MODE, "focus_mode"),
    (PROP_SLEEP_AID_ENABLE, "sleep_aid"),
    (PROP_WAKE_UP_ENABLE, "wake_up"),
)

_FAN_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_FAN_GEAR, "fan_speed"),
    (PROP_FAN_MODE, "fan_mode"),
)

_SENSOR_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_BATTERY, "battery"),
    (PROP_DOOR_OPEN, "door_sensor"),
    (PROP_DARK, "light_sensor"),
)

_HEATER_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_HEATER_MODE, "heater_mode"),
    (PROP_WIND_GEAR, "wind_speed"),
    (PROP_AERATION_GEAR, "aeration"),
    (PROP_LIGHT_MODE, "heater_light"),
)

_MOTION_SENSOR_TRIGGER_PROPERTIES: Final[frozenset[str]] = frozenset(
    {PROP_BODY_REACTIVE, PROP_ACTIVATED}
)


def _append_capabilities_for_properties(
    capabilities: list[str],
    properties: dict[str, Any],
    mappings: tuple[tuple[str, str], ...],
) -> None:
    """Append capabilities for present property keys in declared order."""
    for prop_key, capability in mappings:
        if prop_key in properties:
            capabilities.append(capability)


def _has_any_property(properties: dict[str, Any], candidates: frozenset[str]) -> bool:
    """Return True when at least one candidate property is present."""
    return any(prop_key in properties for prop_key in candidates)


def detect_device_capabilities(device: LiproDevice) -> list[str]:
    """Detect device capabilities from properties and category."""
    capabilities: list[str] = []
    properties = device.properties

    if device.is_light:
        capabilities.append("light")
        _append_capabilities_for_properties(
            capabilities,
            properties,
            _LIGHT_PRIMARY_PROPERTY_CAPABILITIES,
        )
        if device.has_gear_presets:
            capabilities.append("gear_presets")
        _append_capabilities_for_properties(
            capabilities,
            properties,
            _LIGHT_SECONDARY_PROPERTY_CAPABILITIES,
        )

    if device.is_fan_light:
        capabilities.append("fan")
        _append_capabilities_for_properties(
            capabilities,
            properties,
            _FAN_PROPERTY_CAPABILITIES,
        )

    if device.is_curtain:
        capabilities.append("cover")
        if PROP_POSITION in properties:
            capabilities.append("position")

    if device.is_sensor:
        capabilities.append("sensor")
        _append_capabilities_for_properties(
            capabilities,
            properties,
            _SENSOR_PROPERTY_CAPABILITIES,
        )
        if _has_any_property(properties, _MOTION_SENSOR_TRIGGER_PROPERTIES):
            capabilities.append("motion_sensor")

    if device.is_heater:
        capabilities.append("heater")
        _append_capabilities_for_properties(
            capabilities,
            properties,
            _HEATER_PROPERTY_CAPABILITIES,
        )

    if device.is_switch or device.is_outlet:
        capabilities.append("switch")

    return capabilities


__all__ = ["detect_device_capabilities"]
