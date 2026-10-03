"""Response safety helpers for API logging and code normalization."""

from __future__ import annotations

import re
from typing import Any, Final

from ..utils.redaction import (
    JSON_LOG_FIELD_PATTERN,
    JSON_LOG_SENSITIVE_KEYS,
    is_sensitive_key_name,
)

INVALID_JSON_MASK_INPUT_MAX_CHARS: Final = 2048
INVALID_JSON_LOG_PREVIEW_MAX_CHARS: Final = 200
INVALID_JSON_BODY_READ_MAX_BYTES: Final = 8192

DEVICE_TYPE_HEX_PATTERN = re.compile(r"^[0-9a-f]{8}$", re.IGNORECASE)


def _mask_phone_digits(phone_digits: str) -> str:
    """Mask phone digits while preserving recognizable prefix/suffix."""
    if len(phone_digits) <= 4:
        return "***"
    if len(phone_digits) <= 8:
        return f"{phone_digits[:2]}***{phone_digits[-2:]}"
    return f"{phone_digits[:3]}****{phone_digits[-4:]}"


def _mask_phone_field(match: re.Match[str]) -> str:
    """Mask one phone field match from serialized JSON-like logs."""
    prefix = match.group("prefix")
    digits = match.group("digits")
    return f'"phone": "{prefix}{_mask_phone_digits(digits)}"'


_PHONE_VALUE = re.compile(r'"(?P<prefix>\+?)(?P<digits>\d{6,20})"')


def _mask_json_field(match: re.Match[str]) -> str:
    key = match.group("key")
    if not is_sensitive_key_name(key, extra_keys=JSON_LOG_SENSITIVE_KEYS):
        return match.group(0)
    value = match.group("value")
    if key == "phone" and (phone := _PHONE_VALUE.fullmatch(value)):
        return _mask_phone_field(phone)
    return f'"{key}": "***"'


def mask_sensitive_data(data: str) -> str:
    """Mask JSON fields using the shared policy, including incomplete values."""
    return JSON_LOG_FIELD_PATTERN.sub(_mask_json_field, data)


def normalize_response_code(code: Any) -> int | str | None:
    """Normalize API response codes for robust comparisons."""
    if code is None:
        return None
    if isinstance(code, bool):
        return int(code)
    if isinstance(code, int):
        return code
    if isinstance(code, float):
        if code.is_integer():
            return int(code)
        return str(code).strip()
    if isinstance(code, str):
        normalized = code.strip()
        if not normalized:
            return None
        if normalized.lstrip("+-").isdigit():
            try:
                return int(normalized, 10)
            except ValueError:
                return normalized
        return normalized
    return str(code).strip()
