# ruff: noqa: SLF001
"""Runtime helpers bound to the thin ``LiproDevice`` facade."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from ...const.properties import PROP_CONNECT_STATE, PROP_GEAR_LIST
from ..utils.property_normalization import normalize_properties
from .device_factory import has_unknown_physical_model
from .extras import DeviceExtras
from .state import DeviceState

if TYPE_CHECKING:
    from .device import LiproDevice


def get_device_state(device: LiproDevice) -> DeviceState:
    """Return the cached mutable state view for one device."""
    if device._state_cache is None:
        device._state_cache = DeviceState(
            device.properties,
            device.min_color_temp_kelvin,
            device.max_color_temp_kelvin,
            device.max_fan_gear,
            device.capabilities.supports_color_temp,
        )
    return device._state_cache


def build_device_extras(device: LiproDevice) -> DeviceExtras:
    """Build structured extras bound to one device facade."""
    return DeviceExtras(
        device.properties,
        device.extra_data,
        serial=device.serial,
        iot_name=device.iot_name,
        physical_model=device.physical_model,
    )


def get_device_extras(device: LiproDevice) -> DeviceExtras:
    """Return cached structured extras and rebuild when bindings change."""
    if device._extras_cache is None or not device._extras_cache.is_bound_to(
        device.properties,
        device.extra_data,
    ):
        device._extras_cache = build_device_extras(device)
    return device._extras_cache


def initialize_device(device: LiproDevice) -> None:
    """Normalize raw device properties and derive stable flags."""
    device.properties = normalize_properties(device.properties)
    device.has_unknown_physical_model = has_unknown_physical_model(
        device.physical_model
    )
    if PROP_CONNECT_STATE in device.properties:
        device.available = get_device_state(device).is_connected


def update_device_properties(device: LiproDevice, properties: Mapping[str, object]) -> None:
    """Merge normalized properties into the live device facade."""
    normalized = normalize_properties(properties)
    device.properties.update(normalized)
    if PROP_GEAR_LIST in normalized and device._extras_cache is not None:
        device._extras_cache.clear_caches()
    if PROP_CONNECT_STATE in normalized:
        device.available = get_device_state(device).is_connected


__all__ = [
    "build_device_extras",
    "get_device_extras",
    "get_device_state",
    "initialize_device",
    "update_device_properties",
]
