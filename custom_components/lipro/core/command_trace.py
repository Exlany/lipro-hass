"""Command trace helpers for coordinator command pipeline."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .api import LiproApiError

if TYPE_CHECKING:
    from .device import LiproDevice


def extract_command_property_keys(
    properties: list[dict[str, str]] | None,
) -> list[str]:
    """Extract command property keys for trace logging."""
    keys: list[str] = []
    for item in properties or []:
        key = item.get("key")
        if isinstance(key, str):
            keys.append(key)
    return keys


def build_command_trace(
    *,
    device: LiproDevice,
    command: str,
    properties: list[dict[str, str]] | None,
    fallback_device_id: str | None,
    redact_identifier: Callable[[str | None], str | None],
) -> dict[str, Any]:
    """Build initial command trace payload."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "device_id": redact_identifier(device.serial),
        "is_group": device.is_group,
        "iot_name": device.iot_name,
        "device_type": device.device_type,
        "physical_model": device.physical_model,
        "requested_command": command,
        "requested_property_count": len(properties or []),
        "requested_property_keys": extract_command_property_keys(properties),
        "requested_fallback_device_id": redact_identifier(fallback_device_id),
    }


def update_trace_with_resolved_request(
    trace: dict[str, Any],
    *,
    command: str,
    properties: list[dict[str, str]] | None,
    fallback_device_id: str | None,
    redact_identifier: Callable[[str | None], str | None],
) -> None:
    """Attach resolved command/fallback fields to trace payload."""
    trace["effective_fallback_device_id"] = redact_identifier(fallback_device_id)
    trace["resolved_command"] = command
    trace["resolved_property_count"] = len(properties or [])
    trace["resolved_property_keys"] = extract_command_property_keys(properties)


def update_trace_with_response(trace: dict[str, Any], result: Any) -> None:
    """Attach API response metadata to command trace."""
    if not isinstance(result, dict):
        return

    trace["push_success"] = result.get("pushSuccess")
    trace["response_code"] = result.get("code") or result.get("errorCode")
    trace["response_message"] = result.get("message")
    trace["response_msg_sn"] = result.get("msgSn")
    trace["response_push_timestamp"] = result.get("pushTimestamp")


def update_trace_with_exception(
    trace: dict[str, Any],
    *,
    route: str,
    err: LiproApiError,
) -> None:
    """Attach API exception metadata to command trace."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = type(err).__name__
    trace["error_message"] = str(err)
    trace["error_code"] = err.code
