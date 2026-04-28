"""Formal system-health surface for control-plane adapters."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypedDict, cast

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant

from ..const.base import VERSION
from .models import RuntimeCoordinatorSnapshot
from .runtime_access import build_runtime_snapshots, iter_runtime_entries


class FailureEntry(TypedDict):
    """Stable per-entry failure projection for system health."""

    entry_ref: str
    failure_category: str | None
    failure_origin: str | None
    handling_policy: str | None
    error_type: str | None


class SystemHealthPayload(TypedDict, total=False):
    """Stable system-health payload shape exposed by the thin adapter."""

    component_version: str
    can_reach_server: bool
    logged_accounts: int
    total_devices: int
    mqtt_connected_entries: int
    failure_entries: list[FailureEntry]


def _build_failure_entries(
    snapshots: list[RuntimeCoordinatorSnapshot],
) -> list[FailureEntry]:
    """Project failure summaries into the stable system-health payload shape."""
    return [
        {
            "entry_ref": snapshot.entry_ref or snapshot.entry_id,
            "failure_category": snapshot.failure_summary["failure_category"],
            "failure_origin": snapshot.failure_summary["failure_origin"],
            "handling_policy": snapshot.failure_summary["handling_policy"],
            "error_type": snapshot.failure_summary["error_type"],
        }
        for snapshot in snapshots
        if snapshot.failure_summary["error_type"] is not None
    ]


def _count_mqtt_connected_entries(
    snapshots: list[RuntimeCoordinatorSnapshot],
) -> int | None:
    """Count entries with an explicit MQTT connected signal."""
    mqtt_connected_values = [
        snapshot.mqtt_connected
        for snapshot in snapshots
        if isinstance(snapshot.mqtt_connected, bool)
    ]
    if not mqtt_connected_values:
        return None
    return sum(mqtt_connected_values)


def _build_system_health_payload(
    *,
    version: str,
    logged_accounts: int,
    snapshots: list[RuntimeCoordinatorSnapshot],
) -> SystemHealthPayload:
    """Build the stable system-health payload from runtime snapshots."""
    health_info: SystemHealthPayload = {
        "component_version": version,
        "can_reach_server": any(snapshot.last_update_success for snapshot in snapshots),
        "logged_accounts": logged_accounts,
        "total_devices": sum(snapshot.device_count for snapshot in snapshots),
    }

    mqtt_connected_entries = _count_mqtt_connected_entries(snapshots)
    if mqtt_connected_entries is not None:
        health_info["mqtt_connected_entries"] = mqtt_connected_entries

    failure_entries = _build_failure_entries(snapshots)
    if failure_entries:
        health_info["failure_entries"] = failure_entries

    return health_info


async def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    del hass
    register.async_register_info(
        cast(
            Callable[[HomeAssistant], Awaitable[dict[object, object]]],
            system_health_info,
        )
    )


async def system_health_info(
    hass: HomeAssistant,
    version: str = VERSION,
) -> SystemHealthPayload:
    """Return system health information for the Lipro integration."""
    entries = iter_runtime_entries(hass)
    snapshots = build_runtime_snapshots(hass)

    return _build_system_health_payload(
        version=version,
        logged_accounts=len(entries),
        snapshots=snapshots,
    )
