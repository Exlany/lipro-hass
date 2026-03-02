"""Command service handlers for Lipro integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ..core import LiproApiError
from ..core.utils.redaction import redact_identifier as _redact_identifier


async def async_send_command_with_service_errors(
    coordinator: Any,
    device: Any,
    *,
    command: str,
    properties: list[dict[str, str]] | None,
    requested_device_id: str | None,
    failure_log: str,
    api_error_log: str,
    resolve_command_failure_translation_key: Any,
    raise_service_error: Any,
    logger: Any,
) -> None:
    """Send one command and map API/push failures to translated service errors."""
    try:
        success = await coordinator.async_send_command(
            device,
            command,
            properties,
            fallback_device_id=requested_device_id,
        )
        if success:
            return

        failure_context = getattr(coordinator, "last_command_failure", None)
        logger.warning(
            failure_log,
            command,
            _redact_identifier(requested_device_id) or "***",
            _redact_identifier(getattr(device, "serial", None)) or "***",
            failure_context,
        )
        raise_service_error(
            resolve_command_failure_translation_key(
                failure=failure_context,
            )
        )
    except HomeAssistantError:
        raise
    except LiproApiError as err:
        logger.warning(api_error_log, err)
        raise_service_error(
            resolve_command_failure_translation_key(err=err),
            err=err,
        )


def build_send_command_result(
    resolved_serial: str,
    *,
    requested_device_id: str | None,
    is_alias_resolution: bool,
) -> dict[str, Any]:
    """Build send_command response payload with alias metadata."""
    result: dict[str, Any] = {
        "success": True,
        "serial": resolved_serial,
    }
    if is_alias_resolution and requested_device_id:
        result["requested_device_id"] = requested_device_id
        result["resolved_device_id"] = resolved_serial
    return result


async def async_handle_send_command(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    summarize_service_properties: Any,
    log_send_command_call: Any,
    resolve_command_failure_translation_key: Any,
    raise_service_error: Any,
    logger: Any,
    attr_command: str,
    attr_properties: str,
    attr_device_id: str,
) -> dict[str, Any]:
    """Handle the send_command service call."""
    command = call.data[attr_command]
    properties = call.data.get(attr_properties)
    properties_summary = summarize_service_properties(properties)
    requested_device_id = call.data.get(attr_device_id)

    device, coordinator = await get_device_and_coordinator(hass, call)
    is_alias_resolution = log_send_command_call(
        requested_device_id,
        device.serial,
        command,
        properties_summary,
    )

    await async_send_command_with_service_errors(
        coordinator,
        device,
        command=command,
        properties=properties,
        requested_device_id=requested_device_id,
        failure_log=(
            "send_command failed (command=%s, device_id=%s, "
            "resolved_serial=%s, failure=%s)"
        ),
        api_error_log="API error sending command: %s",
        resolve_command_failure_translation_key=resolve_command_failure_translation_key,
        raise_service_error=raise_service_error,
        logger=logger,
    )
    return build_send_command_result(
        device.serial,
        requested_device_id=requested_device_id,
        is_alias_resolution=is_alias_resolution,
    )
