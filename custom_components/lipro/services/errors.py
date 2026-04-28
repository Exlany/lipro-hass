"""Service-layer error mapping helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import NoReturn

from homeassistant.exceptions import HomeAssistantError

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
from ..const.base import DOMAIN

type CommandFailureContext = Mapping[str, object]


def raise_service_error(
    translation_key: str,
    *,
    err: Exception | None = None,
    translation_placeholders: Mapping[str, str] | None = None,
) -> NoReturn:
    """Raise a translated HomeAssistantError, preserving original cause."""
    service_error = HomeAssistantError(
        translation_domain=DOMAIN,
        translation_key=translation_key,
        translation_placeholders=(
            dict(translation_placeholders) if translation_placeholders else None
        ),
    )
    if err is not None:
        raise service_error from err
    raise service_error


def _normalize_response_code(value: object) -> int | str | None:
    """Return one supported response code value from arbitrary input."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, str)):
        return value
    return None


def _extract_error_code(err: object | None) -> int | str | None:
    """Extract a supported error code from one exception-like object."""
    if err is None:
        return None
    return _normalize_response_code(getattr(err, "code", None))


def _extract_failure_code(failure: CommandFailureContext | None) -> int | str | None:
    """Extract a supported error code from one command failure payload."""
    if failure is None:
        return None
    return _normalize_response_code(failure.get("code"))


def resolve_command_failure_translation_key(
    *,
    failure: CommandFailureContext | None = None,
    err: object | None = None,
) -> str:
    """Map command failure context to user-facing translation key."""
    if failure is not None and failure.get("reason") == "push_failed":
        return "command_push_failed"

    code = _extract_error_code(err)
    if code is None:
        code = _extract_failure_code(failure)

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
