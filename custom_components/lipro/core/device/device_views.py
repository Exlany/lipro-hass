"""Read-only view helpers exposed by the thin device facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...const.categories import DeviceCategory, get_device_category
from .device_factory import has_valid_iot_id
from .device_snapshots import (
    build_capabilities_snapshot,
    build_identity_snapshot,
    build_network_info,
)
from .profile import resolve_device_type_hex, resolve_platforms

if TYPE_CHECKING:
    from .capabilities import DeviceCapabilities
    from .device import LiproDevice
    from .identity import DeviceIdentity
    from .network_info import DeviceNetworkInfo


def identity(device: LiproDevice) -> DeviceIdentity:
    """Return immutable identity metadata for the device."""
    return build_identity_snapshot(device)


def capabilities(device: LiproDevice) -> DeviceCapabilities:
    """Return immutable capability metadata for the device."""
    return build_capabilities_snapshot(device)


def network_info(device: LiproDevice) -> DeviceNetworkInfo:
    """Return structured network and diagnostics metadata."""
    return build_network_info(device.properties)


def device_type_hex(device: LiproDevice) -> str:
    """Return resolved Lipro device type hex."""
    return resolve_device_type_hex(
        device_type=device.device_type,
        iot_name=device.iot_name,
        physical_model=device.physical_model,
    )


def category(device: LiproDevice) -> DeviceCategory:
    """Return the Home Assistant category for this device."""
    return get_device_category(device_type_hex(device))


def platforms(device: LiproDevice) -> list[str]:
    """Return Home Assistant platforms for this device."""
    return resolve_platforms(category(device))


def unique_id(device: LiproDevice) -> str:
    """Return the stable entity unique-id prefix for this device."""
    return f"lipro_{device.serial}"


def iot_device_id(device: LiproDevice) -> str:
    """Return the normalized IoT device id."""
    return device.serial


def has_valid_iot_id_property(device: LiproDevice) -> bool:
    """Return whether the serial matches the expected ID format."""
    return has_valid_iot_id(device.serial, is_group=device.is_group)


def panel_type(device: LiproDevice) -> int:
    """Return panel type discriminator used by panel state commands."""
    return int(device.extras.panel_type)


def fan_speed_range(device: LiproDevice) -> tuple[int, int]:
    """Return the supported fan-speed range for fan entities."""
    return (1, device.max_fan_gear)


__all__ = [
    "capabilities",
    "category",
    "device_type_hex",
    "fan_speed_range",
    "has_valid_iot_id_property",
    "identity",
    "iot_device_id",
    "network_info",
    "panel_type",
    "platforms",
    "unique_id",
]
