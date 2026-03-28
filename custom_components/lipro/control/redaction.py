"""Diagnostics redaction policy owned by the control plane."""

from __future__ import annotations

import json
import re
from typing import Any, Final

from ..const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_PHONE,
    CONF_PHONE_ID,
)
from ..const.properties import PROP_BLE_MAC, PROP_IP, PROP_MAC, PROP_WIFI_SSID
from ..core.utils.redaction import (
    DIAGNOSTICS_REDACTION_MARKERS,
    PROPERTY_SENSITIVE_KEY_NAMES,
    is_sensitive_key_name,
    normalize_redaction_key,
    redact_sensitive_literal,
    redact_sensitive_text,
)

TO_REDACT: Final = {
    CONF_PHONE,
    CONF_PHONE_ID,
    "password",
    "password_hash",
    "access_token",
    "access_key",
    "refresh_token",
    "refresh_access_key",
    "secret",
    "secret_key",
    "user_id",
    "userId",
    "biz_id",
    "bizId",
    "serial",
    "device_id",
    "deviceId",
    "iot_device_id",
    "iotDeviceId",
    "groupId",
    "iotName",
    "gatewayDeviceId",
}

OPTIONS_TO_REDACT: Final = TO_REDACT | {
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_MODEL_LIST,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_DID_LIST,
}

PROPERTY_KEYS_TO_REDACT: Final = {
    PROP_MAC,
    PROP_IP,
    PROP_BLE_MAC,
    PROP_WIFI_SSID,
    "wifiSsid",
    "macAddress",
    "ipAddress",
}

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


def redact_entry_title(title: Any) -> str:
    """Redact sensitive identifiers from config-entry title."""
    if not isinstance(title, str):
        return ""
    redacted = _PHONE_EMBEDDED_RE.sub(r"\1****\2", title)
    return redact_sensitive_text(
        redacted,
        markers=DIAGNOSTICS_REDACTION_MARKERS,
    )


def redact_property_value(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive values in diagnostics payloads."""
    if key is not None and is_sensitive_key_name(
        key,
        extra_keys=_NESTED_KEYS_TO_REDACT,
    ):
        return DIAGNOSTICS_REDACTION_MARKERS.secret

    if isinstance(value, dict):
        return {k: redact_property_value(v, str(k)) for k, v in value.items()}

    if isinstance(value, list):
        return [redact_property_value(item) for item in value]

    if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped[0] in "{[":
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError):
                pass
            else:
                redacted = redact_property_value(parsed)
                if isinstance(redacted, (dict, list)):
                    return json.dumps(
                        redacted,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )

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


def redact_device_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from one device-properties mapping."""
    return {
        key: redact_property_value(value, normalize_redaction_key(key))
        for key, value in properties.items()
    }
