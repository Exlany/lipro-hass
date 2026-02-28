"""Service-layer error mapping helpers."""

from __future__ import annotations

from typing import Any, NoReturn

from homeassistant.exceptions import HomeAssistantError

from ..const import DOMAIN
from ..const.api import (
    ERROR_DEVICE_BUSY,
    ERROR_DEVICE_BUSY_STR,
    ERROR_DEVICE_NOT_CONNECTED,
    ERROR_DEVICE_NOT_CONNECTED_STR,
    ERROR_DEVICE_NOT_FOUND,
    ERROR_DEVICE_NOT_FOUND_STR,
    ERROR_DEVICE_OFFLINE,
    ERROR_DEVICE_OFFLINE_LEGACY,
    ERROR_DEVICE_OFFLINE_LEGACY_STR,
    ERROR_DEVICE_OFFLINE_STR,
)


def raise_service_error(
    translation_key: str,
    *,
    err: Exception | None = None,
) -> NoReturn:
    """Raise a translated HomeAssistantError, preserving original cause."""
    if err is None:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key=translation_key,
        )

    raise HomeAssistantError(
        translation_domain=DOMAIN,
        translation_key=translation_key,
    ) from err


def resolve_command_failure_translation_key(
    *,
    failure: dict[str, Any] | None = None,
    err: Any | None = None,
) -> str:
    """Map command failure context to user-facing translation key."""
    if isinstance(failure, dict) and failure.get("reason") == "push_failed":
        return "command_push_failed"

    code: Any = None
    if err is not None:
        code = getattr(err, "code", None)
    elif isinstance(failure, dict):
        code = failure.get("code")

    if code in (ERROR_DEVICE_NOT_CONNECTED, ERROR_DEVICE_NOT_CONNECTED_STR):
        return "command_device_not_connected"
    if code in (ERROR_DEVICE_BUSY, ERROR_DEVICE_BUSY_STR):
        return "command_device_busy"
    if code in (
        ERROR_DEVICE_OFFLINE,
        ERROR_DEVICE_OFFLINE_STR,
        ERROR_DEVICE_OFFLINE_LEGACY,
        ERROR_DEVICE_OFFLINE_LEGACY_STR,
        ERROR_DEVICE_NOT_FOUND,
        ERROR_DEVICE_NOT_FOUND_STR,
    ):
        return "command_device_offline"
    return "command_failed"
