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
from ..core.utils.log_safety import mask_ip_addresses

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

_PROPERTY_KEYS_LOWER: Final = frozenset(key.lower() for key in PROPERTY_KEYS_TO_REDACT)

_NESTED_KEYS_TO_REDACT_LOWER: Final = _PROPERTY_KEYS_LOWER | frozenset(
    {
        "deviceid",
        "serial",
        "iotdeviceid",
        "iot_device_id",
        "groupid",
        "gatewaydeviceid",
    }
)

_MAC_LITERAL_RE: Final = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
_IPV4_LITERAL_RE: Final = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_DEVICE_ID_LITERAL_RE: Final = re.compile(r"^03ab[0-9a-f]{12}$", re.IGNORECASE)
_MAC_EMBEDDED_RE: Final = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
_IPV4_EMBEDDED_RE: Final = re.compile(r"\d{1,3}(\.\d{1,3}){3}")
_DEVICE_ID_EMBEDDED_RE: Final = re.compile(r"03ab[0-9a-f]{12}", re.IGNORECASE)
_PHONE_EMBEDDED_RE: Final = re.compile(r"(\d{3})\d{4}(\d{4})")


def redact_entry_title(title: Any) -> str:
    """Redact sensitive identifiers from config-entry title."""
    if not isinstance(title, str):
        return ""
    return _PHONE_EMBEDDED_RE.sub(r"\1****\2", title)


def redact_property_value(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive values in diagnostics payloads."""
    if key is not None and key.lower() in _NESTED_KEYS_TO_REDACT_LOWER:
        return "**REDACTED**"

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
                        redacted, ensure_ascii=False, separators=(",", ":")
                    )

        if (
            _MAC_LITERAL_RE.fullmatch(stripped)
            or _IPV4_LITERAL_RE.fullmatch(stripped)
            or _DEVICE_ID_LITERAL_RE.fullmatch(stripped)
        ):
            return "**REDACTED**"

        sanitized = _MAC_EMBEDDED_RE.sub("**REDACTED**", value)
        sanitized = _IPV4_EMBEDDED_RE.sub("**REDACTED**", sanitized)
        sanitized = _DEVICE_ID_EMBEDDED_RE.sub("**REDACTED**", sanitized)
        sanitized = mask_ip_addresses(sanitized, placeholder="**REDACTED**")
        if sanitized != value:
            return sanitized

    return value


def redact_device_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from one device-properties mapping."""
    return {key: redact_property_value(value, key) for key, value in properties.items()}
