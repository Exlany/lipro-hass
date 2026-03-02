"""Device refresh helpers for coordinator."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from ..const.categories import DeviceCategory
from .device import LiproDevice

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class FetchedDeviceSnapshot:
    """Atomic container for refreshed device indexes."""

    devices: dict[str, LiproDevice]
    device_by_id: dict[str, LiproDevice]
    iot_ids: list[str]
    group_ids: list[str]
    outlet_ids: list[str]


@dataclass(frozen=True)
class StaleDeviceReconcilePlan:
    """Computed stale-device reconciliation result."""

    missing_cycles: dict[str, int]
    removable_serials: set[str]


def register_lookup_id(
    mapping: dict[str, LiproDevice],
    device_id: Any,
    device: LiproDevice,
) -> None:
    """Register a device lookup alias with case-insensitive compatibility."""
    if not isinstance(device_id, str):
        return
    normalized = device_id.strip()
    if not normalized:
        return
    mapping[normalized] = device
    mapping[normalized.lower()] = device


def _safe_device_from_api_data(device_data: dict[str, Any]) -> LiproDevice | None:
    """Build a device from API data, returning None when payload is malformed."""
    try:
        return LiproDevice.from_api_data(device_data)
    except (TypeError, ValueError, AttributeError):
        _LOGGER.debug("Skipping malformed device payload row")
        return None


def _has_valid_device_serial(device: LiproDevice) -> bool:
    """Return True when the device has a valid, non-empty serial."""
    if not isinstance(device.serial, str) or not device.serial.strip():
        _LOGGER.debug("Skipping device with invalid serial type/value")
        return False
    return True


def _safe_is_gateway(device: LiproDevice) -> bool | None:
    """Return gateway status; None when category payload is malformed."""
    try:
        return device.is_gateway
    except (TypeError, ValueError):
        _LOGGER.debug("Skipping device with malformed category payload")
        return None


def _safe_is_outlet(device: LiproDevice) -> bool:
    """Return whether device is an outlet, handling malformed categories."""
    try:
        return device.category == DeviceCategory.OUTLET
    except (TypeError, ValueError):
        _LOGGER.debug("Skipping outlet categorization for malformed device")
        return False


def build_fetched_device_snapshot(
    devices_data: list[dict[str, Any]],
) -> FetchedDeviceSnapshot:
    """Build refreshed device indexes from API payload."""
    new_devices: dict[str, LiproDevice] = {}
    new_device_by_id: dict[str, LiproDevice] = {}
    new_iot_ids: list[str] = []
    new_group_ids: list[str] = []
    new_outlet_ids: list[str] = []

    for device_data in devices_data:
        device = _safe_device_from_api_data(device_data)
        if device is None:
            continue

        if not _has_valid_device_serial(device):
            continue

        is_gateway = _safe_is_gateway(device)
        if is_gateway is None:
            continue

        if is_gateway:
            _LOGGER.debug("Skipping gateway device: %s", device.name)
            continue

        new_devices[device.serial] = device
        register_lookup_id(new_device_by_id, device.serial, device)

        if device.is_group:
            new_group_ids.append(device.serial)
            continue

        if not device.has_valid_iot_id:
            _LOGGER.debug(
                "Device %s has unexpected IoT ID format: %s",
                device.name,
                device.serial,
            )
            continue
        new_iot_ids.append(device.iot_device_id)

        if _safe_is_outlet(device):
            new_outlet_ids.append(device.iot_device_id)

    return FetchedDeviceSnapshot(
        devices=new_devices,
        device_by_id=new_device_by_id,
        iot_ids=new_iot_ids,
        group_ids=new_group_ids,
        outlet_ids=new_outlet_ids,
    )


def plan_stale_device_reconciliation(
    *,
    previous_serials: set[str],
    current_serials: set[str],
    missing_cycles: dict[str, int],
    remove_threshold: int,
) -> StaleDeviceReconcilePlan:
    """Compute stale-device cycle counters and removable serials."""
    updated_missing_cycles = {
        serial: count
        for serial, count in missing_cycles.items()
        if serial not in current_serials
    }
    stale_serials = (previous_serials | set(updated_missing_cycles)) - current_serials

    removable: set[str] = set()
    for serial in stale_serials:
        miss_count = updated_missing_cycles.get(serial, 0) + 1
        updated_missing_cycles[serial] = miss_count
        if miss_count >= remove_threshold:
            removable.add(serial)

    return StaleDeviceReconcilePlan(
        missing_cycles=updated_missing_cycles,
        removable_serials=removable,
    )
