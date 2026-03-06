"""Config-entry option snapshot helpers for the Lipro integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_DATA_OPTIONS_SNAPSHOTS = "options_snapshots"


def store_entry_options_snapshot(hass: HomeAssistant, entry: ConfigEntry[Any]) -> None:
    """Store a snapshot of config-entry options for update-listener diffing."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not isinstance(domain_data, dict):
        return

    snapshots = domain_data.setdefault(_DATA_OPTIONS_SNAPSHOTS, {})
    if not isinstance(snapshots, dict):
        return

    snapshots[entry.entry_id] = dict(entry.options)


def remove_entry_options_snapshot(hass: HomeAssistant, entry_id: str) -> None:
    """Drop stored option snapshot for an entry, if present."""
    domain_data = hass.data.get(DOMAIN)
    if not isinstance(domain_data, dict):
        return

    snapshots = domain_data.get(_DATA_OPTIONS_SNAPSHOTS)
    if not isinstance(snapshots, dict):
        return

    snapshots.pop(entry_id, None)


async def async_reload_entry_if_options_changed(
    hass: HomeAssistant,
    entry: ConfigEntry[Any],
) -> None:
    """Reload the config entry only when options changed."""
    domain_data = hass.data.get(DOMAIN)
    if not isinstance(domain_data, dict):
        return

    snapshots = domain_data.get(_DATA_OPTIONS_SNAPSHOTS)
    if not isinstance(snapshots, dict):
        domain_data[_DATA_OPTIONS_SNAPSHOTS] = {entry.entry_id: dict(entry.options)}
        return

    previous = snapshots.get(entry.entry_id)
    current = dict(entry.options)

    if isinstance(previous, dict) and previous == current:
        return
    if previous is None:
        snapshots[entry.entry_id] = current
        return

    snapshots[entry.entry_id] = current
    await hass.config_entries.async_reload(entry.entry_id)
