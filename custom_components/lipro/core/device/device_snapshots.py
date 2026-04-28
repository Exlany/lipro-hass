"""Immutable snapshot builders used by the thin device facade."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from ..capability import CapabilityRegistry, CapabilitySnapshot
from .identity import DeviceIdentity
from .network_info import DeviceNetworkInfo

if TYPE_CHECKING:
    from .device import LiproDevice


def build_identity_snapshot(device: LiproDevice) -> DeviceIdentity:
    """Build one immutable identity snapshot from a live device."""
    mac = device.properties.get("mac")
    firmware = device.properties.get("version")
    return DeviceIdentity(
        device_number=device.device_number,
        serial=device.serial,
        name=device.name,
        device_type=device.device_type,
        iot_name=device.iot_name,
        room_id=device.room_id,
        room_name=device.room_name,
        product_id=device.product_id,
        physical_model=device.physical_model,
        mac=mac if isinstance(mac, str) else None,
        firmware=firmware if isinstance(firmware, str) else None,
    )


def build_capabilities_snapshot(device: LiproDevice) -> CapabilitySnapshot:
    """Build one immutable capability snapshot from a live device."""
    return CapabilityRegistry.from_device(device)


def build_network_info(properties: Mapping[str, object]) -> DeviceNetworkInfo:
    """Build structured network metadata from normalized properties."""
    return DeviceNetworkInfo.from_properties(dict(properties))


__all__ = [
    "build_capabilities_snapshot",
    "build_identity_snapshot",
    "build_network_info",
]
