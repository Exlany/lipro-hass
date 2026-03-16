"""MQTT payload log sanitization helpers and boundary-family shim."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
import json
import re
from typing import TYPE_CHECKING, Any, Final, Protocol, cast

if TYPE_CHECKING:
    from custom_components.lipro.core.protocol.boundary import BoundaryDecodeResult


class _BoundaryDecoderModule(Protocol):
    """Typed view of the lazily imported boundary module."""

    def decode_mqtt_message_envelope_payload(
        self,
        payload: Any,
    ) -> BoundaryDecodeResult[dict[str, Any]]: ...

    def decode_mqtt_properties_payload(
        self,
        payload: Any,
    ) -> BoundaryDecodeResult[dict[str, Any]]: ...


@lru_cache(maxsize=1)
def _boundary_decoder_module() -> _BoundaryDecoderModule:
    """Resolve the protocol-boundary module lazily to avoid import cycles."""
    return cast(
        _BoundaryDecoderModule,
        import_module("custom_components.lipro.core.protocol.boundary"),
    )


# Hard limit for incoming MQTT payloads to avoid excessive memory/log churn.
_MAX_MQTT_PAYLOAD_BYTES: Final[int] = 64 * 1024
# Max payload preview length in debug logs.
_MAX_MQTT_LOG_CHARS: Final[int] = 200

# Keys frequently carrying credentials/identifiers in MQTT payloads.
_MQTT_LOG_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "authorization",
        "accesstoken",
        "refreshtoken",
        "apikey",
        "accesskey",
        "secretkey",
        "secret",
        "password",
        "wifissid",
        "mac",
        "macaddress",
        "blemac",
        "ip",
        "ipaddress",
        "deviceid",
        "iotdeviceid",
        "gatewaydeviceid",
        "serial",
    }
)

_MQTT_LOG_STRING_PATTERNS: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;\"']+"),
        r"\1***",
    ),
    (
        re.compile(
            r"(?i)\b(access[_-]?token|refresh[_-]?token|api[_-]?key|secret|password)\b(\s*[:=]\s*)([^\s,;\"']+)"
        ),
        r"\1\2***",
    ),
    (
        re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}"),
        "***",
    ),
    (
        re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
        "***",
    ),
    (
        re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9._~+/=-]{32,}(?![A-Za-z0-9])"),
        "***",
    ),
)


def parse_mqtt_payload(payload: Any) -> dict[str, Any]:
    """Decode MQTT payloads via the formal protocol boundary family."""
    module = _boundary_decoder_module()
    envelope = module.decode_mqtt_message_envelope_payload(payload).canonical
    return module.decode_mqtt_properties_payload(envelope).canonical


def _sanitize_mqtt_log_value(value: Any, key: str | None = None) -> Any:
    """Sanitize MQTT payload values before debug logging."""
    if key is not None:
        normalized_key = key.strip().lower().replace("_", "").replace("-", "")
        if normalized_key in _MQTT_LOG_SENSITIVE_KEYS:
            return "***"

    if isinstance(value, dict):
        return {str(k): _sanitize_mqtt_log_value(v, str(k)) for k, v in value.items()}

    if isinstance(value, list):
        return [_sanitize_mqtt_log_value(item) for item in value]

    if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped[0] in "{[":
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError):
                pass
            else:
                redacted = _sanitize_mqtt_log_value(parsed)
                if isinstance(redacted, (dict, list)):
                    return json.dumps(
                        redacted,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )

        sanitized = value
        for pattern, replacement in _MQTT_LOG_STRING_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    return value


def _format_mqtt_payload_for_log(payload: dict[str, Any]) -> str:
    """Return a redacted string representation suitable for debug logs."""
    sanitized = _sanitize_mqtt_log_value(payload)
    return json.dumps(
        sanitized,
        ensure_ascii=False,
        separators=(",", ":"),
    )


__all__ = [
    "_MAX_MQTT_LOG_CHARS",
    "_MAX_MQTT_PAYLOAD_BYTES",
    "_format_mqtt_payload_for_log",
    "_sanitize_mqtt_log_value",
    "parse_mqtt_payload",
]
