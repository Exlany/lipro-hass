"""Sanitization helpers for anonymous share payloads."""

from __future__ import annotations

import json
from typing import Any, Final

from ..utils.redaction import (
    EXPLICIT_SENSITIVE_KEY_VARIANTS,
    SHARE_REDACTION_MARKERS,
    is_sensitive_key_name,
    looks_sensitive_value,
    normalize_redaction_key,
    redact_sensitive_text,
)

REDACT_KEYS: Final = EXPLICIT_SENSITIVE_KEY_VARIANTS

_REDACT_KEYS_NORMALIZED: Final[frozenset[str]] = frozenset(
    normalize_redaction_key(key) for key in REDACT_KEYS
)

_PRESERVED_UPLOAD_KEYS: Final[frozenset[str]] = frozenset({"iotname", "iot_name"})

_MAX_LIST_ITEMS: Final = 50
_MAX_DICT_ITEMS: Final = 100
_MAX_NESTED_DEPTH: Final = 8
_MAX_STRING_LENGTH: Final = 500
_TRUNCATED_STRING_PREFIX_LENGTH: Final = 200


def is_sensitive_key(key: Any) -> bool:
    """Return True when a key should be dropped from anonymized payloads."""
    if not isinstance(key, str):
        return False
    normalized = normalize_redaction_key(key)
    if normalized in _PRESERVED_UPLOAD_KEYS:
        return False
    return is_sensitive_key_name(key, extra_keys=_REDACT_KEYS_NORMALIZED)


def sanitize_string(value: str) -> str:
    """Sanitize a string by redacting known sensitive patterns."""
    return redact_sensitive_text(value, markers=SHARE_REDACTION_MARKERS)


def _sanitize_container_string(value: str, *, depth: int) -> str | None:
    """Sanitize one JSON-string container recursively when parseable."""
    stripped = value.strip()
    if not stripped or stripped[0] not in "[{":
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


def _sanitize_scalar_value(value: Any) -> Any:
    """Sanitize one scalar value without traversing nested containers."""
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


def looks_sensitive(value: str) -> bool:
    """Return True when a value looks like sensitive data."""
    return looks_sensitive_value(value)


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
        sanitized_json = _sanitize_container_string(value, depth=_depth)
        if sanitized_json is not None:
            return sanitized_json

    return _sanitize_scalar_value(value)


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
