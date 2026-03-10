"""Attribute delegation for the thin device facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .state import DEVICE_STATE_EXPORTED_ATTRIBUTES

if TYPE_CHECKING:
    from .device import LiproDevice

_CAPABILITY_ATTRS = (
    "is_light",
    "is_fan_light",
    "is_curtain",
    "is_switch",
    "is_outlet",
    "is_heater",
    "is_sensor",
    "is_body_sensor",
    "is_door_sensor",
    "is_gateway",
    "supports_color_temp",
)
_STATE_METHOD_ATTRS = (
    "get_property",
    "get_bool_property",
    "get_int_property",
    "get_float_property",
    "get_optional_int_property",
    "get_str_property",
    "percent_to_kelvin_for_device",
    "kelvin_to_percent_for_device",
)
_NETWORK_ATTRS = (
    "ip_address",
    "wifi_ssid",
    "wifi_rssi",
    "net_type",
    "mac_address",
    "firmware_version",
    "latest_sync_timestamp",
    "mesh_address",
    "mesh_type",
    "is_mesh_gateway",
    "ble_mac",
    "connection_quality",
)
_EXTRA_ATTRS = (
    "gear_list",
    "last_gear_index",
    "has_gear_presets",
    "has_sleep_wake_features",
    "has_floor_lamp_features",
    "panel_info",
    "panel_type",
    "is_ir_remote_device",
    "ir_remote_gateway_device_id",
    "rc_list",
    "supports_ir_switch",
)

DEVICE_DELEGATED_ATTRIBUTES: dict[str, str] = {
    **dict.fromkeys(_CAPABILITY_ATTRS, "capabilities"),
    **dict.fromkeys(DEVICE_STATE_EXPORTED_ATTRIBUTES, "state"),
    **dict.fromkeys(_STATE_METHOD_ATTRS, "state"),
    **dict.fromkeys(_NETWORK_ATTRS, "network_info"),
    **dict.fromkeys(_EXTRA_ATTRS, "extras"),
}


def resolve_device_attribute(device: LiproDevice, name: str) -> object:
    """Delegate device attributes to focused helper objects."""
    if name in DEVICE_DELEGATED_ATTRIBUTES:
        return getattr(getattr(device, DEVICE_DELEGATED_ATTRIBUTES[name]), name)
    msg = f"{type(device).__name__!s} has no attribute {name!r}"
    raise AttributeError(msg)


__all__ = ["DEVICE_DELEGATED_ATTRIBUTES", "resolve_device_attribute"]
