"""Shared redaction helpers for diagnostics, anonymous share, telemetry, and traces."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import ipaddress
from math import log2
import re
from typing import Final

from .log_safety import mask_ip_addresses

_MAC_ADDRESS_RE: Final = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
_MAC_ADDRESS_EXACT_RE: Final = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
_MAC_COMPACT_RE: Final = re.compile(r"\b[0-9A-Fa-f]{12}\b")
_MAC_COMPACT_EXACT_RE: Final = re.compile(r"^[0-9A-Fa-f]{12}$")
_DEVICE_ID_RE: Final = re.compile(r"03ab[0-9a-f]{12}", re.IGNORECASE)
_DEVICE_ID_EXACT_RE: Final = re.compile(r"^03ab[0-9a-f]{12}$", re.IGNORECASE)
_TOKEN_EXACT_RE: Final = re.compile(r"^[a-zA-Z0-9_-]{32,}$")
_TOKEN_EMBEDDED_RE: Final = re.compile(r"\b[a-zA-Z0-9_-]{32,}\b")
_AUTH_BEARER_RE: Final = re.compile(r'(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;"\']+')
_SECRET_KV_RE: Final = re.compile(
    r'(?i)\b([a-z0-9_-]*(?:token|secret|password|api[_-]?key|access[_-]?key|private[_-]?key)[a-z0-9_-]*)\b'
    r'(\s*[:=]\s*)([^\s,;"\']+)'
)

SHARED_SENSITIVE_KEY_NAMES: Final[frozenset[str]] = frozenset(
    {
        "access_token",
        "accesstoken",
        "access_key",
        "accesskey",
        "api_key",
        "apikey",
        "biz_id",
        "bizid",
        "ble_mac",
        "blemac",
        "device_id",
        "deviceid",
        "device_name",
        "devicename",
        "entry_id",
        "entryid",
        "gateway_device_id",
        "gatewaydeviceid",
        "group_id",
        "groupid",
        "install_token",
        "installtoken",
        "iot_device_id",
        "iotdeviceid",
        "ip",
        "ipaddress",
        "mac",
        "macaddress",
        "password",
        "password_hash",
        "passwordhash",
        "phone",
        "phone_id",
        "phoneid",
        "refresh_access_key",
        "refresh_token",
        "refreshaccesskey",
        "refreshtoken",
        "room_id",
        "roomid",
        "room_name",
        "roomname",
        "secret",
        "secret_key",
        "secretkey",
        "serial",
        "ssid",
        "user_id",
        "userid",
        "wifi_ssid",
        "wifissid",
    }
)

PROPERTY_SENSITIVE_KEY_NAMES: Final[frozenset[str]] = frozenset(
    {
        "ble_mac",
        "blemac",
        "ip",
        "ipaddress",
        "mac",
        "macaddress",
        "wifi_ssid",
        "wifissid",
    }
)

TELEMETRY_REFERENCE_ALIASES: Final[dict[str, str]] = {
    "device_id": "device_ref",
    "deviceid": "device_ref",
    "device_name": "device_ref",
    "devicename": "device_ref",
    "device_serial": "device_ref",
    "deviceserial": "device_ref",
    "entry_id": "entry_ref",
    "entryid": "entry_ref",
    "gateway_device_id": "device_ref",
    "gatewaydeviceid": "device_ref",
    "group_id": "device_ref",
    "groupid": "device_ref",
    "serial": "device_ref",
}

_SECRET_LIKE_KEY_FRAGMENTS: Final[frozenset[str]] = frozenset(
    {
        "token",
        "secret",
        "password",
        "accesskey",
        "apikey",
        "privatekey",
        "clientsecret",
    }
)

_SAFE_SECRET_METADATA_KEYS: Final[frozenset[str]] = frozenset(
    {
        "access_token_present",
        "refresh_token_present",
    }
)


@dataclass(frozen=True, slots=True)
class RedactionMarkers:
    """Sink-specific marker palette built on one shared classifier."""

    secret: str
    token: str
    mac: str
    ip: str
    device_id: str


DIAGNOSTICS_REDACTION_MARKERS: Final = RedactionMarkers(
    secret="**REDACTED**",
    token="**REDACTED**",
    mac="**REDACTED**",
    ip="**REDACTED**",
    device_id="**REDACTED**",
)

SHARE_REDACTION_MARKERS: Final = RedactionMarkers(
    secret="[REDACTED]",
    token="[TOKEN]",
    mac="[MAC]",
    ip="[IP]",
    device_id="[DEVICE_ID]",
)


def _token_entropy(value: str) -> float:
    """Return the per-character Shannon entropy for one token-like string."""
    length = len(value)
    if length == 0:
        return 0.0
    return -sum(
        (count / length) * log2(count / length)
        for count in Counter(value).values()
    )


def _is_probable_token_literal(value: str) -> bool:
    """Return whether one scalar literal is secret-like enough to redact."""
    if _TOKEN_EXACT_RE.fullmatch(value) is None:
        return False
    has_digit = any(char.isdigit() for char in value)
    has_separator = "-" in value or "_" in value
    has_mixed_case = any(char.islower() for char in value) and any(
        char.isupper() for char in value
    )
    if has_digit or has_separator or has_mixed_case:
        return True
    return _token_entropy(value) >= 4.0


def redact_identifier(identifier: str | None) -> str | None:
    """Redact an identifier for share-friendly diagnostics."""
    if not isinstance(identifier, str):
        return None

    normalized = identifier.strip()
    if not normalized:
        return None

    if len(normalized) <= 8:
        return "***"
    return f"{normalized[:4]}***{normalized[-4:]}"


def normalize_redaction_key(key: str) -> str:
    """Normalize one key for shared redaction-policy lookups."""
    return key.strip().lower().replace("-", "_")


def reference_alias_for(key: str) -> str | None:
    """Return the telemetry reference alias for a field, when configured."""
    return TELEMETRY_REFERENCE_ALIASES.get(normalize_redaction_key(key))


def is_sensitive_key_name(
    key: object,
    *,
    extra_keys: frozenset[str] = frozenset(),
) -> bool:
    """Return whether a key is sensitive under the shared policy."""
    if not isinstance(key, str):
        return False
    normalized = normalize_redaction_key(key)
    if normalized in _SAFE_SECRET_METADATA_KEYS:
        return False
    if normalized in SHARED_SENSITIVE_KEY_NAMES or normalized in extra_keys:
        return True
    collapsed = normalized.replace("_", "")
    return any(fragment in collapsed for fragment in _SECRET_LIKE_KEY_FRAGMENTS)


def looks_sensitive_value(value: str) -> bool:
    """Return whether a scalar string looks like sensitive data."""
    stripped = value.strip()
    if not stripped:
        return False
    try:
        ipaddress.ip_address(stripped)
    except ValueError:
        pass
    else:
        return True
    if any(
        pattern.fullmatch(stripped)
        for pattern in (
            _MAC_ADDRESS_EXACT_RE,
            _MAC_COMPACT_EXACT_RE,
            _DEVICE_ID_EXACT_RE,
        )
    ):
        return True
    return _is_probable_token_literal(stripped)


def redact_sensitive_literal(
    value: str,
    *,
    markers: RedactionMarkers,
) -> str | None:
    """Return one fully redacted literal replacement when the whole value is sensitive."""
    stripped = value.strip()
    if not stripped:
        return None
    if _MAC_ADDRESS_EXACT_RE.fullmatch(stripped) or _MAC_COMPACT_EXACT_RE.fullmatch(stripped):
        return markers.mac
    try:
        ipaddress.ip_address(stripped)
    except ValueError:
        pass
    else:
        return markers.ip
    if _DEVICE_ID_EXACT_RE.fullmatch(stripped):
        return markers.device_id
    if _is_probable_token_literal(stripped):
        return markers.token
    return None


def redact_sensitive_text(
    value: str,
    *,
    markers: RedactionMarkers,
) -> str:
    """Redact embedded sensitive fragments from one arbitrary string."""
    result = _AUTH_BEARER_RE.sub(
        lambda match: f"{match.group(1)}{markers.token}",
        value,
    )
    result = _SECRET_KV_RE.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{markers.secret}",
        result,
    )
    result = _TOKEN_EMBEDDED_RE.sub(
        lambda match: (
            markers.token
            if _is_probable_token_literal(match.group(0))
            else match.group(0)
        ),
        result,
    )
    result = _MAC_ADDRESS_RE.sub(markers.mac, result)
    result = _MAC_COMPACT_RE.sub(markers.mac, result)
    result = _DEVICE_ID_RE.sub(markers.device_id, result)
    return mask_ip_addresses(result, placeholder=markers.ip)


__all__ = [
    "DIAGNOSTICS_REDACTION_MARKERS",
    "PROPERTY_SENSITIVE_KEY_NAMES",
    "SHARED_SENSITIVE_KEY_NAMES",
    "SHARE_REDACTION_MARKERS",
    "TELEMETRY_REFERENCE_ALIASES",
    "RedactionMarkers",
    "is_sensitive_key_name",
    "looks_sensitive_value",
    "normalize_redaction_key",
    "redact_identifier",
    "redact_sensitive_literal",
    "redact_sensitive_text",
    "reference_alias_for",
]
