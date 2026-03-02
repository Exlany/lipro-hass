"""System health support for the Lipro integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, VERSION


async def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


def _iter_runtime_coordinators(hass: HomeAssistant) -> list[Any]:
    """Collect active runtime coordinators from Lipro config entries."""
    coordinators: list[Any] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is None:
            continue
        coordinators.append(coordinator)
    return coordinators


def _count_total_devices(coordinators: list[Any]) -> int:
    """Count total devices across all active coordinators."""
    total_devices = 0
    for coordinator in coordinators:
        devices = getattr(coordinator, "devices", None)
        if devices is None:
            continue
        try:
            total_devices += len(devices)
        except TypeError:
            continue
    return total_devices


@callback
def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Return system health information for the Lipro integration."""
    entries = hass.config_entries.async_entries(DOMAIN)
    coordinators = _iter_runtime_coordinators(hass)

    info: dict[str, Any] = {
        "component_version": VERSION,
        "can_reach_server": any(
            bool(getattr(coordinator, "last_update_success", False))
            for coordinator in coordinators
        ),
        "logged_accounts": len(entries),
        "total_devices": _count_total_devices(coordinators),
    }

    mqtt_connected_entries = 0
    has_mqtt_field = False
    for coordinator in coordinators:
        mqtt_connected = getattr(coordinator, "mqtt_connected", None)
        if not isinstance(mqtt_connected, bool):
            continue
        has_mqtt_field = True
        if mqtt_connected:
            mqtt_connected_entries += 1

    if has_mqtt_field:
        info["mqtt_connected_entries"] = mqtt_connected_entries

    return info
