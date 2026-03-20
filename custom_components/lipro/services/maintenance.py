"""Maintenance service handlers for the Lipro integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..control.runtime_access import iter_runtime_entry_coordinators
from .contracts import RefreshDevicesResult


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    attr_entry_id: str,
) -> RefreshDevicesResult:
    """Handle refresh_devices service call."""
    raw_entry_id = call.data.get(attr_entry_id)
    requested_entry_id = raw_entry_id if isinstance(raw_entry_id, str) else None
    targets = iter_runtime_entry_coordinators(hass, entry_id=requested_entry_id)

    if requested_entry_id and not targets:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="entry_not_found",
            translation_placeholders={"entry_id": requested_entry_id},
        )

    refreshed_entries = 0
    for _entry, coordinator in targets:
        await coordinator.device_refresh_service.async_refresh_devices()
        refreshed_entries += 1

    result: RefreshDevicesResult = {
        "success": True,
        "refreshed_entries": refreshed_entries,
    }
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result
