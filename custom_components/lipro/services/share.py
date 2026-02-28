"""Anonymous-share related service handlers for Lipro integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError


async def async_handle_submit_anonymous_share(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: Any,
    get_client_session: Any,
    raise_service_error: Any,
    domain: str,
) -> dict[str, Any]:
    """Handle submit_anonymous_share service."""
    del call
    share_manager = get_anonymous_share_manager(hass)
    if not share_manager.is_enabled:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="anonymous_share_not_enabled",
        )

    device_count, error_count = share_manager.pending_count
    if device_count == 0 and error_count == 0:
        return {
            "success": True,
            "message": "No data to submit",
            "devices": 0,
            "errors": 0,
        }

    session = get_client_session(hass)
    success = await share_manager.submit_report(session, force=True)
    if not success:
        raise_service_error("anonymous_share_submit_failed")

    return {
        "success": True,
        "devices": device_count,
        "errors": error_count,
    }


async def async_handle_get_anonymous_share_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_anonymous_share_manager: Any,
) -> dict[str, Any]:
    """Handle get_anonymous_share_report service."""
    del call
    share_manager = get_anonymous_share_manager(hass)
    report = share_manager.get_pending_report()
    if report is None:
        return {
            "has_data": False,
            "devices": [],
            "errors": [],
        }

    return {
        "has_data": True,
        "device_count": report.get("device_count", 0),
        "error_count": report.get("error_count", 0),
        "devices": report.get("devices", []),
        "errors": report.get("errors", []),
    }
