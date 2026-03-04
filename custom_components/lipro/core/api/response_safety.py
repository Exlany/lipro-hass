"""Response safety helpers for API logging and code normalization."""

from __future__ import annotations

import re
from typing import Any, Final

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


_SENSITIVE_PATTERNS = (
    (re.compile(r'"access_token"\s*:\s*"[^"]*"'), '"access_token": "***"'),
    (re.compile(r'"refresh_token"\s*:\s*"[^"]*"'), '"refresh_token": "***"'),
    (re.compile(r'"accessToken"\s*:\s*"[^"]*"'), '"accessToken": "***"'),
    (re.compile(r'"refreshToken"\s*:\s*"[^"]*"'), '"refreshToken": "***"'),
    (re.compile(r'"accessKey"\s*:\s*"[^"]*"'), '"accessKey": "***"'),
    (re.compile(r'"secretKey"\s*:\s*"[^"]*"'), '"secretKey": "***"'),
    (re.compile(r'"password"\s*:\s*"[^"]*"'), '"password": "***"'),
    (
        re.compile(r'"phone"\s*:\s*"(?P<prefix>\+?)(?P<digits>\d{6,20})"'),
        _mask_phone_field,
    ),
    (re.compile(r'"user_id"\s*:\s*"[^"]*"'), '"user_id": "***"'),
    (re.compile(r'"userId"\s*:\s*"[^"]*"'), '"userId": "***"'),
    (re.compile(r'"biz_id"\s*:\s*"[^"]*"'), '"biz_id": "***"'),
    (re.compile(r'"bizId"\s*:\s*"[^"]*"'), '"bizId": "***"'),
    (re.compile(r'"user_id"\s*:\s*-?\d+'), '"user_id": "***"'),
    (re.compile(r'"userId"\s*:\s*-?\d+'), '"userId": "***"'),
    (re.compile(r'"biz_id"\s*:\s*-?\d+'), '"biz_id": "***"'),
    (re.compile(r'"bizId"\s*:\s*-?\d+'), '"bizId": "***"'),
    (re.compile(r'"deviceName"\s*:\s*"[^"]*"'), '"deviceName": "***"'),
    (re.compile(r'"roomName"\s*:\s*"[^"]*"'), '"roomName": "***"'),
    (re.compile(r'"userName"\s*:\s*"[^"]*"'), '"userName": "***"'),
    (re.compile(r'"roomId"\s*:\s*"[^"]*"'), '"roomId": "***"'),
    (re.compile(r'"wifi_ssid"\s*:\s*"[^"]*"'), '"wifi_ssid": "***"'),
    (re.compile(r'"wifiSsid"\s*:\s*"[^"]*"'), '"wifiSsid": "***"'),
    (re.compile(r'"mac"\s*:\s*"[^"]*"'), '"mac": "***"'),
    (re.compile(r'"macAddress"\s*:\s*"[^"]*"'), '"macAddress": "***"'),
    (re.compile(r'"bleMac"\s*:\s*"[^"]*"'), '"bleMac": "***"'),
    (re.compile(r'"ip"\s*:\s*"[^"]*"'), '"ip": "***"'),
    (re.compile(r'"ipAddress"\s*:\s*"[^"]*"'), '"ipAddress": "***"'),
    (re.compile(r'"serial"\s*:\s*"[^"]*"'), '"serial": "***"'),
    (re.compile(r'"iot_device_id"\s*:\s*"[^"]*"'), '"iot_device_id": "***"'),
    (re.compile(r'"iotDeviceId"\s*:\s*"[^"]*"'), '"iotDeviceId": "***"'),
    (re.compile(r'"deviceId"\s*:\s*"[^"]*"'), '"deviceId": "***"'),
    (re.compile(r'"groupId"\s*:\s*"[^"]*"'), '"groupId": "***"'),
    (re.compile(r'"gatewayDeviceId"\s*:\s*"[^"]*"'), '"gatewayDeviceId": "***"'),
)


def mask_sensitive_data(data: str) -> str:
    """Mask sensitive data in logs."""
    result = data
    for pattern, replacement in _SENSITIVE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


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
