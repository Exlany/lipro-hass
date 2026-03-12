"""Formal diagnostics surface for control-plane adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .runtime_access import build_runtime_snapshot, get_entry_runtime_coordinator

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
        "is_connected": device.is_connected,
        "properties": redact_device_properties(device.properties),
    }
    if device.firmware_version:
        device_info["firmware_version"] = device.firmware_version
    if device.wifi_rssi is not None:
        device_info["wifi_rssi"] = device.wifi_rssi
    if device.net_type:
        device_info["net_type"] = device.net_type
    if device.mesh_address is not None:
        device_info["mesh_address"] = device.mesh_address
    if device.mesh_type is not None:
        device_info["mesh_type"] = device.mesh_type
    if device.is_mesh_gateway:
        device_info["is_mesh_gateway"] = True

    if device.extra_data:
        safe_extra: dict[str, Any] = {}
        if "power_info" in device.extra_data:
            safe_extra["power_info"] = device.extra_data["power_info"]
        if "gateway_device_id" in device.extra_data:
            safe_extra["gateway_device_id"] = "**REDACTED**"
        if safe_extra:
            device_info["extra_data"] = safe_extra

    return device_info


def extract_device_serial(device: DeviceEntry, *, domain: str) -> str | None:
    """Extract the Lipro serial from a HA device entry."""
    for candidate_domain, identifier in device.identifiers:
        if candidate_domain == domain:
            return identifier
    return None


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
        build_device_diagnostics_fn(device) for device in coordinator.devices.values()
    ]
    share_manager = get_anonymous_share_manager(hass, entry_id=entry.entry_id)
    device_count, error_count = share_manager.pending_count
    snapshot = build_runtime_snapshot(entry)

    return {
        "entry": {
            "title": redact_entry_title(entry.title),
            "data": async_redact_data(entry.data, to_redact),
            "options": async_redact_data(entry.options, options_to_redact),
        },
        "coordinator": {
            "last_update_success": bool(
                snapshot.last_update_success if snapshot is not None else False
            ),
            "update_interval": str(getattr(coordinator, "update_interval", "")),
            "device_count": snapshot.device_count if snapshot is not None else 0,
            "mqtt_connected": (
                snapshot.mqtt_connected if snapshot is not None else None
            ),
        },
        "anonymous_share": {
            "enabled": share_manager.is_enabled,
            "pending_devices": device_count,
            "pending_errors": error_count,
        },
        "devices": devices_info,
    }


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

    lipro_device = coordinator.get_device(serial)
    if lipro_device is None:
        return {"error": "device_not_found"}

    snapshot = build_runtime_snapshot(entry)
    return {
        "entry": {
            "title": redact_entry_title(entry.title),
            "data": async_redact_data(entry.data, to_redact),
            "options": async_redact_data(entry.options, options_to_redact),
        },
        "coordinator": {
            "last_update_success": bool(
                snapshot.last_update_success if snapshot is not None else False
            ),
            "update_interval": str(getattr(coordinator, "update_interval", "")),
            "device_count": snapshot.device_count if snapshot is not None else 0,
            "mqtt_connected": (
                snapshot.mqtt_connected if snapshot is not None else None
            ),
        },
        "device": build_device_diagnostics_fn(lipro_device),
    }
