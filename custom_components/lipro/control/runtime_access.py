"""Control-owned runtime access helpers."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from .models import RuntimeCoordinatorSnapshot


def get_entry_runtime_coordinator(entry: Any) -> Any | None:
    """Return the coordinator attached to a config entry, if loaded."""
    return getattr(entry, "runtime_data", None)


def iter_runtime_entries(hass: HomeAssistant) -> list[Any]:
    """Return all Lipro config entries known to Home Assistant."""
    return list(hass.config_entries.async_entries(DOMAIN))


def iter_runtime_coordinators(hass: HomeAssistant) -> list[Any]:
    """Return loaded runtime coordinators for the Lipro domain."""
    coordinators: list[Any] = []
    for entry in iter_runtime_entries(hass):
        coordinator = get_entry_runtime_coordinator(entry)
        if coordinator is not None:
            coordinators.append(coordinator)
    return coordinators


def build_runtime_snapshot(entry: Any) -> RuntimeCoordinatorSnapshot | None:
    """Build one control-plane runtime snapshot from a config entry."""
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return None

    devices = getattr(coordinator, "devices", None)
    try:
        device_count = len(devices) if devices is not None else 0
    except TypeError:
        device_count = 0

    mqtt_connected: bool | None = None
    mqtt_service = getattr(coordinator, "mqtt_service", None)
    connected = getattr(mqtt_service, "connected", None)
    if isinstance(connected, bool):
        mqtt_connected = connected

    return RuntimeCoordinatorSnapshot(
        entry_id=str(getattr(entry, "entry_id", "")),
        coordinator=coordinator,
        device_count=device_count,
        last_update_success=bool(getattr(coordinator, "last_update_success", False)),
        mqtt_connected=mqtt_connected,
    )


def build_runtime_snapshots(hass: HomeAssistant) -> list[RuntimeCoordinatorSnapshot]:
    """Build runtime snapshots for all loaded Lipro entries."""
    snapshots: list[RuntimeCoordinatorSnapshot] = []
    for entry in iter_runtime_entries(hass):
        snapshot = build_runtime_snapshot(entry)
        if snapshot is not None:
            snapshots.append(snapshot)
    return snapshots
