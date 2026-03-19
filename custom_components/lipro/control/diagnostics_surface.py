"""Formal diagnostics surface for control-plane adapters."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Protocol

from ..runtime_types import LiproCoordinator
from .models import empty_failure_summary
from .runtime_access import (
    build_runtime_snapshot,
    find_runtime_device,
    get_entry_runtime_coordinator,
    get_runtime_device_mapping,
    is_runtime_device_mapping_degraded,
)
from .telemetry_surface import build_entry_diagnostics_view

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from .. import LiproConfigEntry
    from ..core.device import LiproDevice

type DiagnosticsPayload = dict[str, object]
type RedactDataFn = Callable[[Mapping[str, object], set[str]], object]
type RedactTitleFn = Callable[[str], str]
type RedactDevicePropertiesFn = Callable[[object], object]
type BuildDeviceDiagnosticsFn = Callable[[LiproDevice], DiagnosticsPayload]
type ExtractDeviceSerialFn = Callable[..., str | None]


class _AnonymousShareManagerLike(Protocol):
    """Minimal anonymous-share surface consumed by diagnostics."""

    is_enabled: bool
    pending_count: tuple[int, int]


type AnonymousShareManagerFactory = Callable[..., _AnonymousShareManagerLike]


def build_device_diagnostics(
    device: LiproDevice,
    *,
    redact_device_properties: RedactDevicePropertiesFn,
) -> DiagnosticsPayload:
    """Build redacted diagnostics payload for a single device."""
    device_info: DiagnosticsPayload = {
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
    entry: LiproConfigEntry,
    coordinator: LiproCoordinator,
) -> tuple[DiagnosticsPayload, list[str]]:
    snapshot = build_runtime_snapshot(entry)
    degraded: list[str] = []
    if is_runtime_device_mapping_degraded(coordinator):
        degraded.append("devices")

    failure_summary = (
        dict(snapshot.failure_summary)
        if snapshot is not None
        else empty_failure_summary()
    )
    view: DiagnosticsPayload = {
        "last_update_success": bool(
            snapshot.last_update_success if snapshot is not None else False
        ),
        "update_interval": str(getattr(coordinator, "update_interval", "")),
        "device_count": snapshot.device_count if snapshot is not None else 0,
        "mqtt_connected": snapshot.mqtt_connected if snapshot is not None else None,
        "failure_summary": failure_summary,
    }
    return view, degraded


def _build_anonymous_share_view(
    share_manager: _AnonymousShareManagerLike,
) -> tuple[DiagnosticsPayload, bool]:
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

    payload: DiagnosticsPayload = {
        "enabled": enabled,
        "pending_devices": pending_devices,
        "pending_errors": pending_errors,
    }
    if degraded:
        payload["degraded"] = True
    return payload, degraded


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    *,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    async_redact_data: RedactDataFn,
    redact_entry_title: RedactTitleFn,
    build_device_diagnostics_fn: BuildDeviceDiagnosticsFn,
    to_redact: set[str],
    options_to_redact: set[str],
) -> DiagnosticsPayload:
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

    payload: DiagnosticsPayload = {
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
        coordinator_view["degraded_fields"] = degraded_runtime
    if telemetry_view is not None:
        payload["telemetry"] = telemetry_view
    if degraded_share:
        anonymous_share_view["source"] = "degraded_runtime_access"
    return payload


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    device: DeviceEntry,
    *,
    domain: str,
    async_redact_data: RedactDataFn,
    redact_entry_title: RedactTitleFn,
    build_device_diagnostics_fn: BuildDeviceDiagnosticsFn,
    extract_device_serial_fn: ExtractDeviceSerialFn,
    to_redact: set[str],
    options_to_redact: set[str],
) -> DiagnosticsPayload:
    """Return diagnostics payload for one device entry."""
    del hass
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return {"error": "entry_not_loaded"}
    serial = extract_device_serial_fn(device)
    if serial is None:
        return {"error": "device_not_in_lipro_domain"}

    lipro_device = find_runtime_device(coordinator, serial)
    if lipro_device is None:
        if is_runtime_device_mapping_degraded(coordinator):
            return {"error": "device_cache_unavailable"}
        return {"error": "device_not_found"}

    coordinator_view, degraded_runtime = _build_coordinator_view(entry, coordinator)
    payload: DiagnosticsPayload = {
        "entry": {
            "title": redact_entry_title(entry.title),
            "data": async_redact_data(entry.data, to_redact),
            "options": async_redact_data(entry.options, options_to_redact),
        },
        "coordinator": coordinator_view,
        "device": build_device_diagnostics_fn(lipro_device),
    }
    if degraded_runtime:
        coordinator_view["degraded_fields"] = degraded_runtime
    return payload
