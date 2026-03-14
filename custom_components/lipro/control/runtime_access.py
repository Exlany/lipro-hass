"""Control-owned runtime access helpers."""

from __future__ import annotations

from collections.abc import Mapping
from importlib import import_module
from typing import Any

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..runtime_types import LiproCoordinator
from .models import RuntimeCoordinatorSnapshot


def get_entry_runtime_coordinator(entry: Any) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    coordinator = getattr(entry, "runtime_data", None)
    return coordinator if coordinator is not None else None


def iter_runtime_entries(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[Any]:
    """Return Lipro config entries, optionally scoped to one entry id."""
    return [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry_id is None or getattr(entry, "entry_id", None) == entry_id
    ]


def iter_runtime_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[LiproCoordinator]:
    """Return loaded runtime coordinators for the Lipro domain."""
    coordinators: list[LiproCoordinator] = []
    for entry in iter_runtime_entries(hass, entry_id=entry_id):
        coordinator = get_entry_runtime_coordinator(entry)
        if coordinator is not None:
            coordinators.append(coordinator)
    return coordinators


def find_runtime_entry_for_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> Any | None:
    """Return the config entry that owns one active coordinator."""
    config_entry = getattr(coordinator, "config_entry", None)
    if get_entry_runtime_coordinator(config_entry) is coordinator:
        return config_entry
    for entry in iter_runtime_entries(hass):
        if get_entry_runtime_coordinator(entry) is coordinator:
            return entry
    return None


def is_debug_mode_enabled_for_entry(entry: Any) -> bool:
    """Return whether one config entry explicitly opts into debug services."""
    options = getattr(entry, "options", None)
    if not isinstance(options, Mapping):
        return DEFAULT_DEBUG_MODE
    return bool(options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE))


def has_debug_mode_runtime_entry(hass: HomeAssistant) -> bool:
    """Return True when any loaded runtime entry opts into debug mode."""
    return any(
        is_debug_mode_enabled_for_entry(entry)
        and get_entry_runtime_coordinator(entry) is not None
        for entry in iter_runtime_entries(hass)
    )


def is_developer_runtime_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the coordinator belongs to a debug-enabled entry."""
    entry = find_runtime_entry_for_coordinator(hass, coordinator)
    return entry is not None and is_debug_mode_enabled_for_entry(entry)


def iter_developer_runtime_coordinators(hass: HomeAssistant) -> list[LiproCoordinator]:
    """Return runtime coordinators that explicitly opted into debug mode."""
    return [
        coordinator
        for coordinator in iter_runtime_coordinators(hass)
        if is_developer_runtime_coordinator(hass, coordinator)
    ]


def build_entry_system_health_view(entry: Any) -> dict[str, Any]:
    """Return the control-plane system-health projection for one config entry."""
    telemetry_surface = import_module("custom_components.lipro.control.telemetry_surface")
    view = telemetry_surface.build_entry_system_health_view(entry)
    return view if isinstance(view, dict) else {}


def get_runtime_device_mapping(coordinator: Any) -> Mapping[str, Any]:
    """Return a safe device mapping view for one runtime coordinator."""
    devices = getattr(coordinator, "devices", None)
    return devices if isinstance(devices, Mapping) else {}


def _coerce_device_count(telemetry_view: dict[str, Any], coordinator: Any) -> int:
    device_count = telemetry_view.get("device_count")
    if isinstance(device_count, int):
        return device_count
    devices = get_runtime_device_mapping(coordinator)
    return len(devices)


def _coerce_mqtt_connected(telemetry_view: dict[str, Any], coordinator: Any) -> bool | None:
    mqtt_connected = telemetry_view.get("mqtt_connected")
    if isinstance(mqtt_connected, bool):
        return mqtt_connected
    mqtt_service = getattr(coordinator, "mqtt_service", None)
    connected = getattr(mqtt_service, "connected", None)
    return connected if isinstance(connected, bool) else None


def _coerce_last_update_success(telemetry_view: dict[str, Any], coordinator: Any) -> bool:
    last_update_success = telemetry_view.get("last_update_success")
    if isinstance(last_update_success, bool):
        return last_update_success
    return bool(getattr(coordinator, "last_update_success", False))


def build_runtime_snapshot(entry: Any) -> RuntimeCoordinatorSnapshot | None:
    """Build one control-plane runtime snapshot from a config entry."""
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return None

    telemetry_view = build_entry_system_health_view(entry)
    return RuntimeCoordinatorSnapshot(
        entry_id=str(getattr(entry, "entry_id", "")),
        coordinator=coordinator,
        device_count=_coerce_device_count(telemetry_view, coordinator),
        last_update_success=_coerce_last_update_success(telemetry_view, coordinator),
        mqtt_connected=_coerce_mqtt_connected(telemetry_view, coordinator),
    )


def build_runtime_snapshots(hass: HomeAssistant) -> list[RuntimeCoordinatorSnapshot]:
    """Build runtime snapshots for all loaded Lipro entries."""
    snapshots: list[RuntimeCoordinatorSnapshot] = []
    for entry in iter_runtime_entries(hass):
        snapshot = build_runtime_snapshot(entry)
        if snapshot is not None:
            snapshots.append(snapshot)
    return snapshots
