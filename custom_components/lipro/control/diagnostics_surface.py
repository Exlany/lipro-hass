"""Formal diagnostics surface for control-plane adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .runtime_access import (
    build_runtime_snapshot,
    get_entry_runtime_coordinator,
    get_runtime_device_mapping,
)
from .telemetry_surface import build_entry_diagnostics_view

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from .. import LiproConfigEntry
    from ..core.device import LiproDevice


def build_device_diagnostics(
    device: LiproDevice,
    *,
    redact_device_properties: Any,
) -> dict[str, Any]:
    """Build redacted diagnostics payload for a single device."""
    device_info: dict[str, Any] = {
        "name": "**REDACTED**",
        "device_type": device.device_type,
        "device_type_hex": device.device_type_hex,
        "category": device.category.value,
        "physical_model": device.physical_model,
        "is_group": device.is_group,
        "room_name": "**REDACTED**",
        "available": device.available,
        "is_connected": device.state.is_connected,
        "properties": redact_device_properties(device.properties),
    }
    if device.network_info.firmware_version:
        device_info["firmware_version"] = device.network_info.firmware_version
    if device.network_info.wifi_rssi is not None:
        device_info["wifi_rssi"] = device.network_info.wifi_rssi
    if device.network_info.net_type:
        device_info["net_type"] = device.network_info.net_type
    if device.network_info.mesh_address is not None:
        device_info["mesh_address"] = device.network_info.mesh_address
    if device.network_info.mesh_type is not None:
        device_info["mesh_type"] = device.network_info.mesh_type
    if device.network_info.is_mesh_gateway:
        device_info["is_mesh_gateway"] = True

    outlet_power_info = device.outlet_power_info
    if outlet_power_info is not None:
        device_info["outlet_power_info"] = dict(outlet_power_info)

    if device.extra_data and "gateway_device_id" in device.extra_data:
        device_info["extra_data"] = {"gateway_device_id": "**REDACTED**"}

    return device_info


def extract_device_serial(device: DeviceEntry, *, domain: str) -> str | None:
    """Extract the Lipro serial from a HA device entry."""
    for candidate_domain, identifier in device.identifiers:
        if candidate_domain == domain:
            return identifier
    return None


def _build_coordinator_view(
    entry: Any, coordinator: Any
) -> tuple[dict[str, Any], list[str]]:
    snapshot = build_runtime_snapshot(entry)
    degraded: list[str] = []
    if not isinstance(getattr(coordinator, "devices", None), Mapping):
        degraded.append("devices")

    view = {
        "last_update_success": bool(
            snapshot.last_update_success if snapshot is not None else False
        ),
        "update_interval": str(getattr(coordinator, "update_interval", "")),
        "device_count": snapshot.device_count if snapshot is not None else 0,
        "mqtt_connected": snapshot.mqtt_connected if snapshot is not None else None,
    }
    return view, degraded


def _build_anonymous_share_view(share_manager: Any) -> tuple[dict[str, Any], bool]:
    enabled = bool(getattr(share_manager, "is_enabled", False))
    pending_count = getattr(share_manager, "pending_count", None)
    degraded = False
    pending_devices = 0
    pending_errors = 0
    if (
        isinstance(pending_count, tuple)
        and len(pending_count) == 2
        and all(isinstance(item, int) for item in pending_count)
    ):
        pending_devices, pending_errors = pending_count
    else:
        degraded = True

    payload = {
        "enabled": enabled,
        "pending_devices": pending_devices,
        "pending_errors": pending_errors,
    }
    if degraded:
        payload["degraded"] = True
    return payload, degraded


def _get_device_from_runtime(coordinator: Any, serial: str) -> Any | None:
    getter = getattr(coordinator, "get_device", None)
    if callable(getter):
        return getter(serial)
    return get_runtime_device_mapping(coordinator).get(serial)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    *,
    get_anonymous_share_manager: Any,
    async_redact_data: Any,
    redact_entry_title: Any,
    build_device_diagnostics_fn: Any,
    to_redact: set[str],
    options_to_redact: set[str],
) -> dict[str, Any]:
    """Return diagnostics payload for one config entry."""
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return {"error": "entry_not_loaded"}

    devices_info = [
        build_device_diagnostics_fn(device)
        for device in get_runtime_device_mapping(coordinator).values()
    ]
    share_manager = get_anonymous_share_manager(hass, entry_id=entry.entry_id)
    coordinator_view, degraded_runtime = _build_coordinator_view(entry, coordinator)
    anonymous_share_view, degraded_share = _build_anonymous_share_view(share_manager)
    telemetry_view = build_entry_diagnostics_view(entry)

    payload: dict[str, Any] = {
        "entry": {
            "title": redact_entry_title(entry.title),
            "data": async_redact_data(entry.data, to_redact),
            "options": async_redact_data(entry.options, options_to_redact),
        },
        "coordinator": coordinator_view,
        "anonymous_share": anonymous_share_view,
        "devices": devices_info,
    }
    if degraded_runtime:
        payload["coordinator"]["degraded_fields"] = degraded_runtime
    if telemetry_view is not None:
        payload["telemetry"] = telemetry_view
    if degraded_share:
        payload["anonymous_share"]["source"] = "degraded_runtime_access"
    return payload


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    device: DeviceEntry,
    *,
    domain: str,
    async_redact_data: Any,
    redact_entry_title: Any,
    build_device_diagnostics_fn: Any,
    extract_device_serial_fn: Any,
    to_redact: set[str],
    options_to_redact: set[str],
) -> dict[str, Any]:
    """Return diagnostics payload for one device entry."""
    del hass
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return {"error": "entry_not_loaded"}
    serial = extract_device_serial_fn(device, domain=domain)
    if serial is None:
        return {"error": "device_not_in_lipro_domain"}

    lipro_device = _get_device_from_runtime(coordinator, serial)
    if lipro_device is None:
        if not isinstance(getattr(coordinator, "devices", None), Mapping):
            return {"error": "device_cache_unavailable"}
        return {"error": "device_not_found"}

    coordinator_view, degraded_runtime = _build_coordinator_view(entry, coordinator)
    payload: dict[str, Any] = {
        "entry": {
            "title": redact_entry_title(entry.title),
            "data": async_redact_data(entry.data, to_redact),
            "options": async_redact_data(entry.options, options_to_redact),
        },
        "coordinator": coordinator_view,
        "device": build_device_diagnostics_fn(lipro_device),
    }
    if degraded_runtime:
        payload["coordinator"]["degraded_fields"] = degraded_runtime
    return payload
