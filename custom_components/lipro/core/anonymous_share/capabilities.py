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


def _append_light_capabilities(
    detected: list[str],
    device: LiproDevice,
    properties: dict[str, Any],
) -> None:
    """Append light-family capabilities in the canonical outward order."""
    detected.append("light")
    _append_capabilities_for_properties(
        detected,
        properties,
        _LIGHT_PRIMARY_PROPERTY_CAPABILITIES,
    )
    if device.extras.has_gear_presets:
        detected.append("gear_presets")
    _append_capabilities_for_properties(
        detected,
        properties,
        _LIGHT_SECONDARY_PROPERTY_CAPABILITIES,
    )


def _append_fan_capabilities(
    detected: list[str],
    properties: dict[str, Any],
) -> None:
    """Append fan-family capabilities in the canonical outward order."""
    detected.append("fan")
    _append_capabilities_for_properties(
        detected,
        properties,
        _FAN_PROPERTY_CAPABILITIES,
    )


def _append_curtain_capabilities(
    detected: list[str],
    properties: dict[str, Any],
) -> None:
    """Append curtain-family capabilities in the canonical outward order."""
    detected.append("cover")
    if PROP_POSITION in properties:
        detected.append("position")


def _append_sensor_capabilities(
    detected: list[str],
    properties: dict[str, Any],
) -> None:
    """Append sensor-family capabilities in the canonical outward order."""
    detected.append("sensor")
    _append_capabilities_for_properties(
        detected,
        properties,
        _SENSOR_PROPERTY_CAPABILITIES,
    )
    if _has_any_property(properties, _MOTION_SENSOR_TRIGGER_PROPERTIES):
        detected.append("motion_sensor")


def _append_heater_capabilities(
    detected: list[str],
    properties: dict[str, Any],
) -> None:
    """Append heater-family capabilities in the canonical outward order."""
    detected.append("heater")
    _append_capabilities_for_properties(
        detected,
        properties,
        _HEATER_PROPERTY_CAPABILITIES,
    )


def detect_device_capabilities(device: LiproDevice) -> list[str]:
    """Detect device capabilities from properties and category."""
    detected: list[str] = []
    properties = device.properties
    capability_snapshot = device.capabilities

    if capability_snapshot.is_light:
        _append_light_capabilities(detected, device, properties)

    if capability_snapshot.is_fan_light:
        _append_fan_capabilities(detected, properties)

    if capability_snapshot.is_curtain:
        _append_curtain_capabilities(detected, properties)

    if capability_snapshot.is_sensor:
        _append_sensor_capabilities(detected, properties)

    if capability_snapshot.is_heater:
        _append_heater_capabilities(detected, properties)

    if capability_snapshot.is_switch or capability_snapshot.is_outlet:
        detected.append("switch")

    return detected


__all__ = ["detect_device_capabilities"]
