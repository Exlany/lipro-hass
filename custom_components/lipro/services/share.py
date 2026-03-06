"""Anonymous-share related service handlers for Lipro integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError


def _resolve_share_manager(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: Any,
    attr_entry_id: str,
) -> Any:
    """Resolve aggregate or entry-scoped anonymous-share manager."""
    entry_id = call.data.get(attr_entry_id)
    return get_anonymous_share_manager(hass, entry_id=entry_id)


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: Any,
    get_client_session: Any,
    raise_service_error: Any,
    domain: str,
    attr_entry_id: str,
) -> dict[str, Any]:
    """Handle submit_anonymous_share service."""
    share_manager = _resolve_share_manager(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
        attr_entry_id=attr_entry_id,
    )
    if not share_manager.is_enabled:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="anonymous_share_not_enabled",
        )

    device_count, error_count = share_manager.pending_count
    if device_count == 0 and error_count == 0:
        result = {
            "success": True,
            "message": "No data to submit",
            "devices": 0,
            "errors": 0,
        }
        requested_entry_id = call.data.get(attr_entry_id)
        if requested_entry_id:
            result["requested_entry_id"] = requested_entry_id
        return result

    session = get_client_session(hass)
    success = await share_manager.submit_report(session, force=True)
    if not success:
        raise_service_error("anonymous_share_submit_failed")

    result = {
        "success": True,
        "devices": device_count,
        "errors": error_count,
    }
    requested_entry_id = call.data.get(attr_entry_id)
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: Any,
    attr_entry_id: str,
) -> dict[str, Any]:
    """Handle get_anonymous_share_report service."""
    share_manager = _resolve_share_manager(
        hass,
        call,
        get_anonymous_share_manager=get_anonymous_share_manager,
        attr_entry_id=attr_entry_id,
    )
    report = share_manager.get_pending_report()
    requested_entry_id = call.data.get(attr_entry_id)
    if report is None:
        result = {
            "has_data": False,
            "devices": [],
            "errors": [],
        }
        if requested_entry_id:
            result["requested_entry_id"] = requested_entry_id
        return result

    result = {
        "has_data": True,
        "device_count": report.get("device_count", 0),
        "error_count": report.get("error_count", 0),
        "devices": report.get("devices", []),
        "errors": report.get("errors", []),
    }
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result
