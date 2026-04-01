"""Diagnostics redaction policy owned by the control plane."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
import re
from typing import Any, Final

from ..const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_SSID_LIST,
)
from ..core.utils.redaction import (
    DIAGNOSTICS_REDACTION_MARKERS,
    EXPLICIT_SENSITIVE_KEY_VARIANTS,
    PROPERTY_REDACTION_KEY_VARIANTS,
    PROPERTY_SENSITIVE_KEY_NAMES,
    is_sensitive_key_name,
    normalize_redaction_key,
    redact_sensitive_literal,
    redact_sensitive_text,
)

TO_REDACT: Final = set(EXPLICIT_SENSITIVE_KEY_VARIANTS)

OPTIONS_TO_REDACT: Final = TO_REDACT | {
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_DID_LIST,
}

PROPERTY_KEYS_TO_REDACT: Final = set(PROPERTY_REDACTION_KEY_VARIANTS)

_NESTED_KEYS_TO_REDACT: Final[frozenset[str]] = frozenset(
    {
        *PROPERTY_SENSITIVE_KEY_NAMES,
        "deviceid",
        "serial",
        "iotdeviceid",
        "iot_device_id",
        "groupid",
        "gatewaydeviceid",
    }
)

_PHONE_EMBEDDED_RE: Final = re.compile(r"(\d{3})\d{4}(\d{4})")
_JSON_CONTAINER_PREFIXES: Final[frozenset[str]] = frozenset({'{', '['})


def redact_entry_title(title: object) -> str:
    """Redact sensitive identifiers from config-entry title."""
    if not isinstance(title, str):
        return ""
    redacted = _PHONE_EMBEDDED_RE.sub(r"\1****\2", title)
    return redact_sensitive_text(
        redacted,
        markers=DIAGNOSTICS_REDACTION_MARKERS,
    )


def _should_redact_nested_key(key: str | None) -> bool:
    if key is None:
        return False
    return is_sensitive_key_name(
        key,
        extra_keys=_NESTED_KEYS_TO_REDACT,
    )


def _redact_mapping_value(mapping: Mapping[object, object]) -> dict[str, object]:
    return {
        str(key): redact_property_value(value, str(key))
        for key, value in mapping.items()
    }


def _redact_sequence_value(items: Sequence[object]) -> list[object]:
    return [redact_property_value(item) for item in items]


def _redact_json_container_string(value: str) -> str | None:
    stripped = value.strip()
    if not stripped or stripped[0] not in _JSON_CONTAINER_PREFIXES:
        return None
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return None
    redacted = redact_property_value(parsed)
    if isinstance(redacted, (dict, list)):
        return json.dumps(
            redacted,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    return None


def _redact_scalar_string(value: str) -> str:
    literal = redact_sensitive_literal(
        value,
        markers=DIAGNOSTICS_REDACTION_MARKERS,
    )
    if literal is not None:
        return literal

    sanitized = redact_sensitive_text(
        value,
        markers=DIAGNOSTICS_REDACTION_MARKERS,
    )
    if sanitized != value:
        return sanitized
    return value


def redact_property_value(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive values in diagnostics payloads."""
    if _should_redact_nested_key(key):
        return DIAGNOSTICS_REDACTION_MARKERS.secret

    if isinstance(value, Mapping):
        return _redact_mapping_value(value)

    if isinstance(value, list):
        return _redact_sequence_value(value)

    if isinstance(value, tuple):
        return _redact_sequence_value(value)

    if isinstance(value, str):
        json_container = _redact_json_container_string(value)
        if json_container is not None:
            return json_container
        return _redact_scalar_string(value)

    return value


def redact_device_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from one device-properties mapping."""
    return {
        key: redact_property_value(value, normalize_redaction_key(key))
        for key, value in properties.items()
    }
