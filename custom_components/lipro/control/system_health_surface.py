"""Formal system-health surface for control-plane adapters."""

from __future__ import annotations

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant

from ..const.base import VERSION
from .models import RuntimeCoordinatorSnapshot
from .runtime_access import build_runtime_snapshots, iter_runtime_entries

type FailureEntry = dict[str, str | None]
type SystemHealthValue = str | int | bool | list[FailureEntry]
type SystemHealthPayload = dict[str, SystemHealthValue]


def _build_failure_entries(
    snapshots: list[RuntimeCoordinatorSnapshot],
) -> list[FailureEntry]:
    """Project failure summaries into the stable system-health payload shape."""
    return [
        {
            "entry_ref": snapshot.entry_ref or snapshot.entry_id,
            **snapshot.failure_summary,
        }
        for snapshot in snapshots
        if snapshot.failure_summary["error_type"] is not None
    ]


async def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    del hass
    register.async_register_info(system_health_info)


async def system_health_info(
    hass: HomeAssistant,
    version: str = VERSION,
) -> SystemHealthPayload:
    """Return system health information for the Lipro integration."""
    entries = iter_runtime_entries(hass)
    snapshots = build_runtime_snapshots(hass)

    health_info: SystemHealthPayload = {
        "component_version": version,
        "can_reach_server": any(snapshot.last_update_success for snapshot in snapshots),
        "logged_accounts": len(entries),
        "total_devices": sum(snapshot.device_count for snapshot in snapshots),
    }

    mqtt_connected_values = [
        snapshot.mqtt_connected
        for snapshot in snapshots
        if isinstance(snapshot.mqtt_connected, bool)
    ]
    if mqtt_connected_values:
        health_info["mqtt_connected_entries"] = sum(mqtt_connected_values)

    failure_entries = _build_failure_entries(snapshots)
    if failure_entries:
        health_info["failure_entries"] = failure_entries

    return health_info
