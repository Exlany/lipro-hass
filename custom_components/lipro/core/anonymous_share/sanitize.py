"""Sanitization helpers for anonymous share payloads."""

from __future__ import annotations

import ipaddress
import json
import re
from typing import Any, Final

from ..utils.log_safety import mask_ip_addresses

# Pre-compiled patterns for sensitive data detection and sanitization
_RE_MAC_ADDRESS = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
_RE_MAC_EXACT = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
# Compact MAC-like identifiers seen in payloads (e.g., rcList.address).
_RE_MAC_COMPACT = re.compile(r"\b[0-9A-Fa-f]{12}\b")
_RE_MAC_COMPACT_EXACT = re.compile(r"^[0-9A-Fa-f]{12}$")
_RE_IP_ADDRESS = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
_RE_IP_EXACT = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
_RE_DEVICE_ID = re.compile(r"03ab[0-9a-f]{12}", re.IGNORECASE)
_RE_DEVICE_ID_EXACT = re.compile(r"^03ab[0-9a-f]{12}$", re.IGNORECASE)
_RE_TOKEN_LIKE = re.compile(r"^[a-zA-Z0-9_-]{32,}$")
_RE_TOKEN_EMBEDDED = re.compile(r"\b[a-zA-Z0-9_-]{32,}\b")
_RE_AUTH_BEARER = re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;\"']+")
_RE_SECRET_KV = re.compile(
    r"(?i)\b("
    r"access[_-]?token|refresh[_-]?token|install[_-]?token|"
    r"api[_-]?key|access[_-]?key|secret(?:[_-]?key)?|password|phone[_-]?id"
    r")\b"
    r"(\s*[:=]\s*)([^\s,;\"']+)"
)

# Keys to always redact from reports
REDACT_KEYS: Final = frozenset(
    {
        "accessKey",
        "access_token",
        "accessToken",
        "apiKey",
        "biz_id",
        "bizId",
        "bleMac",
        "deviceId",
        "deviceName",
        "device_id",
        "gatewayDeviceId",
        "gateway_device_id",
        "groupId",
        "installToken",
        "install_token",
        "iotDeviceId",
        "iot_device_id",
        "ip",
        "ipAddress",
        "mac",
        "macAddress",
        "password",
        "phone",
        "phoneId",
        "phone_id",
        "refresh_token",
        "refreshToken",
        "roomId",
        "roomName",
        "secretKey",
        "serial",
        "ssid",
        "userId",
        "user_id",
        "wifiSsid",
        "wifi_ssid",
    }
)

_REDACT_KEYS_LOWER: Final[frozenset[str]] = frozenset(k.lower() for k in REDACT_KEYS)
_SENSITIVE_KEY_RULES: Final[tuple[frozenset[str], ...]] = (_REDACT_KEYS_LOWER,)

_SANITIZE_STRING_RULES: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (_RE_AUTH_BEARER, r"\1[TOKEN]"),
    (_RE_SECRET_KV, r"\1\2[REDACTED]"),
    (_RE_TOKEN_EMBEDDED, "[TOKEN]"),
    (_RE_MAC_ADDRESS, "[MAC]"),
    (_RE_MAC_COMPACT, "[MAC]"),
    (_RE_IP_ADDRESS, "[IP]"),
    (_RE_DEVICE_ID, "[DEVICE_ID]"),
)

_SENSITIVE_VALUE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    _RE_MAC_EXACT,
    _RE_MAC_COMPACT_EXACT,
    _RE_IP_EXACT,
    _RE_DEVICE_ID_EXACT,
    _RE_TOKEN_LIKE,
)

# Sanitization limits for privacy-preserving data truncation
_MAX_LIST_ITEMS: Final = 50  # Max items when sanitizing lists
_MAX_DICT_ITEMS: Final = 100  # Max key/value pairs when sanitizing mappings
_MAX_NESTED_DEPTH: Final = 8  # Max recursive depth when preserving structure
_MAX_STRING_LENGTH: Final = 500  # Strings longer than this are truncated
_TRUNCATED_STRING_PREFIX_LENGTH: Final = 200  # Keep this many chars when truncating


def is_sensitive_key(key: Any) -> bool:
    """Return True when a key should be dropped from anonymized payloads."""
    if not isinstance(key, str):
        return False
    lowered = key.lower()
    return any(lowered in key_set for key_set in _SENSITIVE_KEY_RULES)


def sanitize_string(value: str) -> str:
    """Sanitize a string by redacting known sensitive patterns."""
    result = value
    for pattern, replacement in _SANITIZE_STRING_RULES:
        result = pattern.sub(replacement, result)
    return mask_ip_addresses(result, placeholder="[IP]")


def looks_sensitive(value: str) -> bool:
    """Return True when a value looks like sensitive data."""
    if "." in value or ":" in value:
        try:
            ipaddress.ip_address(value)
        except ValueError:
            pass
        else:
            return True
    return any(pattern.match(value) for pattern in _SENSITIVE_VALUE_PATTERNS)


def _sanitize_mapping(value: dict[Any, Any], *, depth: int) -> dict[str, Any]:
    """Sanitize mapping values while preserving structure and limits."""
    result: dict[str, Any] = {}
    for key, item in value.items():
        if len(result) >= _MAX_DICT_ITEMS:
            break
        if is_sensitive_key(key):
            continue
        result[str(key)] = sanitize_value(
            item,
            preserve_structure=True,
            _depth=depth + 1,
        )
    return result


def _sanitize_list(value: list[Any], *, depth: int) -> list[Any]:
    """Sanitize list values while preserving order and limits."""
    return [
        sanitize_value(
            item,
            preserve_structure=True,
            _depth=depth + 1,
        )
        for item in value[:_MAX_LIST_ITEMS]
    ]


def _sanitize_json_string(value: str, *, depth: int) -> str | None:
    """Sanitize JSON string payloads recursively when parseable."""
    stripped = value.strip()
    if not stripped or stripped[0] not in "{[":
        return None
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return None
    if not isinstance(parsed, (dict, list)):
        return None
    sanitized = sanitize_value(
        parsed,
        preserve_structure=True,
        _depth=depth + 1,
    )
    return json.dumps(
        sanitized,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def sanitize_value(
    value: Any,
    preserve_structure: bool = False,
    *,
    _depth: int = 0,
) -> Any:
    """Sanitize one value (optionally preserving nested structure)."""
    if value is None:
        return None

    if preserve_structure:
        if _depth >= _MAX_NESTED_DEPTH:
            return {}
        if isinstance(value, dict):
            return _sanitize_mapping(value, depth=_depth)
        if isinstance(value, list):
            return _sanitize_list(value, depth=_depth)

    if isinstance(value, str) and preserve_structure:
        sanitized_json = _sanitize_json_string(value, depth=_depth)
        if sanitized_json is not None:
            return sanitized_json

    str_value = str(value)

    if looks_sensitive(str_value):
        return "[redacted]"

    sanitized_value = sanitize_string(str_value)
    if sanitized_value != str_value:
        return sanitized_value

    if isinstance(value, (bool, int, float)):
        return value

    if len(str_value) > _MAX_STRING_LENGTH:
        return str_value[:_TRUNCATED_STRING_PREFIX_LENGTH] + "...[truncated]"

    return value


def sanitize_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Sanitize device properties for reporting."""
    result: dict[str, Any] = {}
    for key, value in properties.items():
        if is_sensitive_key(key):
            continue
        result[key] = sanitize_value(value, preserve_structure=True)
    return result


__all__ = [
    "REDACT_KEYS",
    "_MAX_DICT_ITEMS",
    "_MAX_NESTED_DEPTH",
    "_MAX_STRING_LENGTH",
    "looks_sensitive",
    "sanitize_properties",
    "sanitize_string",
    "sanitize_value",
]
