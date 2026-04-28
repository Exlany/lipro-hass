"""Inward-only helpers for runtime snapshot mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast

from custom_components.lipro.core.coordinator.types import PropertyDict
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.protocol.contracts import CanonicalDeviceListItem

type DeviceRow = PropertyDict


def coerce_total_count(
    *,
    offset: int,
    devices_data: list[CanonicalDeviceListItem],
    total: object,
) -> int:
    """Coerce one device-page total into a non-negative integer boundary."""
    fallback_total = offset + len(devices_data)
    if isinstance(total, bool):
        return fallback_total
    if isinstance(total, int):
        return max(total, 0)
    if isinstance(total, float) and total.is_integer():
        return max(int(total), 0)
    if isinstance(total, str):
        try:
            return max(int(total), 0)
        except ValueError:
            return fallback_total
    return fallback_total


def canonical_page_has_more(
    *,
    offset: int,
    devices_data: list[CanonicalDeviceListItem],
    total: object,
) -> bool:
    """Return whether one canonical device page has more rows to fetch."""
    return offset + len(devices_data) < coerce_total_count(
        offset=offset,
        devices_data=devices_data,
        total=total,
    )


def canonicalize_device_row(device_data: Mapping[str, object]) -> DeviceRow:
    """Return one runtime-ready canonical device row."""
    normalized = dict(device_data)
    identity_aliases = normalized.get("identityAliases")
    if not isinstance(identity_aliases, list):
        derived_aliases = {
            candidate.strip()
            for candidate in (
                normalized.get("serial"),
                normalized.get("iotDeviceId"),
            )
            if isinstance(candidate, str) and candidate.strip()
        }
        if derived_aliases:
            normalized["identityAliases"] = sorted(derived_aliases)
    return cast(DeviceRow, normalized)


def device_ref_from_row(device_data: Mapping[str, object]) -> str | None:
    """Return the best-effort device reference for one row."""
    for key in ("serial", "iotDeviceId", "deviceId"):
        candidate = device_data.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


@dataclass(slots=True)
class SnapshotAssembly:
    """Mutable buckets used while assembling one fetched device snapshot."""

    devices: dict[str, LiproDevice] = field(default_factory=dict)
    device_by_id: dict[str, LiproDevice] = field(default_factory=dict)
    identity_mapping: dict[str, LiproDevice] = field(default_factory=dict)
    identity_aliases_by_serial: dict[str, tuple[str, ...]] = field(default_factory=dict)
    iot_ids: list[str] = field(default_factory=list)
    group_ids: list[str] = field(default_factory=list)
    outlet_ids: list[str] = field(default_factory=list)
    cloud_serials: set[str] = field(default_factory=set)
    diagnostic_gateway_devices: dict[str, LiproDevice] = field(default_factory=dict)


def build_index_identity_aliases(
    normalized_row: DeviceRow,
    device: LiproDevice,
) -> tuple[str, ...]:
    """Build the explicit identity aliases used by runtime lookup indexes."""
    raw_identity_aliases = normalized_row.get("identityAliases")
    identity_aliases = (
        {
            alias.strip()
            for alias in raw_identity_aliases
            if isinstance(alias, str) and alias.strip()
        }
        if isinstance(raw_identity_aliases, list)
        else set()
    )
    identity_aliases.add(device.serial)
    if device.iot_device_id:
        identity_aliases.add(device.iot_device_id)
    return tuple(sorted(identity_aliases))


def record_snapshot_device(
    *,
    normalized_row: DeviceRow,
    device: LiproDevice,
    assembly: SnapshotAssembly,
) -> None:
    """Record one normalized device into runtime snapshot buckets."""
    if device.capabilities.is_gateway:
        assembly.diagnostic_gateway_devices[device.serial] = device
        return

    assembly.devices[device.serial] = device
    identity_aliases = build_index_identity_aliases(normalized_row, device)
    assembly.identity_aliases_by_serial[device.serial] = identity_aliases

    for identity_alias in identity_aliases:
        assembly.device_by_id[identity_alias] = device
        assembly.identity_mapping[identity_alias] = device

    assembly.cloud_serials.add(device.serial)

    if device.is_group:
        if device.iot_device_id:
            assembly.group_ids.append(device.iot_device_id)
    elif device.capabilities.is_outlet:
        if device.iot_device_id:
            assembly.outlet_ids.append(device.iot_device_id)
    elif device.iot_device_id:
        assembly.iot_ids.append(device.iot_device_id)


__all__ = [
    "DeviceRow",
    "SnapshotAssembly",
    "build_index_identity_aliases",
    "canonical_page_has_more",
    "canonicalize_device_row",
    "coerce_total_count",
    "device_ref_from_row",
    "record_snapshot_device",
]
