"""Command trace helpers for coordinator command pipeline."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
import re
from typing import TYPE_CHECKING

from ..api import LiproApiError
from ..utils.log_safety import mask_ip_addresses, safe_error_placeholder
from ..utils.redaction import redact_identifier
from .result_policy import TracePayload

if TYPE_CHECKING:
    from ..device import LiproDevice

_TRACE_MESSAGE_MAX_CHARS = 200
_TRACE_TOKEN_LIKE = re.compile(r"\b[a-zA-Z0-9_-]{32,}\b")
_TRACE_IOT_DEVICE_ID = re.compile(r"\b03ab[0-9a-f]{12}\b", re.IGNORECASE)
_TRACE_MESH_GROUP_ID = re.compile(r"\bmesh_group_\d+\b", re.IGNORECASE)


def _sanitize_trace_message(value: object) -> str | None:
    """Return a log-safe, bounded trace message string."""
    if not isinstance(value, str):
        return None

    message = value.replace("\n", " ").replace("\r", " ").strip()
    if not message:
        return None

    message = _TRACE_TOKEN_LIKE.sub("[TOKEN]", message)
    message = mask_ip_addresses(message, placeholder="[IP]")
    message = _TRACE_IOT_DEVICE_ID.sub(
        lambda match: redact_identifier(match.group(0)) or "***",
        message,
    )
    message = _TRACE_MESH_GROUP_ID.sub("mesh_group_***", message)

    if len(message) > _TRACE_MESSAGE_MAX_CHARS:
        message = f"{message[:_TRACE_MESSAGE_MAX_CHARS]}…"
    return message


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
) -> TracePayload:
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
    trace: TracePayload,
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


def update_trace_with_response(trace: TracePayload, result: object) -> None:
    """Attach API response metadata to command trace."""
    if not isinstance(result, dict):
        return

    trace["push_success"] = result.get("pushSuccess")
    trace["response_code"] = result.get("code") or result.get("errorCode")
    trace["response_message"] = _sanitize_trace_message(result.get("message"))
    trace["response_msg_sn"] = result.get("msgSn")
    trace["response_push_timestamp"] = result.get("pushTimestamp")


def update_trace_with_exception(
    trace: TracePayload,
    *,
    route: str,
    err: LiproApiError,
) -> None:
    """Attach API exception metadata to command trace."""
    trace["route"] = route
    trace["success"] = False
    trace["error"] = type(err).__name__
    trace["error_message"] = safe_error_placeholder(err)
    trace["error_detail"] = _sanitize_trace_message(str(err))
    trace["error_code"] = err.code
