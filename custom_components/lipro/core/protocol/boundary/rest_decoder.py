"""REST-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from .result import BoundaryDecodeResult, BoundaryDecoderKey

CanonicalT = TypeVar("CanonicalT")
_REST_MQTT_CONFIG_FAMILY = "rest.mqtt-config"
_REST_MQTT_CONFIG_VERSION = "v1"
_REST_MQTT_CONFIG_AUTHORITY = "tests/fixtures/api_contracts/get_mqtt_config.*.json"


def _build_mapping_fingerprint(payload: object) -> str:
    """Return a shape-only fingerprint safe for telemetry and replay tags."""
    if not isinstance(payload, dict):
        return type(payload).__name__
    top_keys = ",".join(sorted(str(key) for key in payload))
    nested = payload.get("data")
    if isinstance(nested, dict):
        nested_keys = ",".join(sorted(str(key) for key in nested))
        return f"dict[{top_keys}]::data[{nested_keys}]"
    return f"dict[{top_keys}]"


def _extract_mqtt_config_mapping(
    result: object,
    *,
    is_success_code: Callable[[object], bool],
) -> dict[str, Any] | None:
    """Extract the canonical MQTT-config mapping from known REST envelopes."""
    if not isinstance(result, dict):
        return None

    if "accessKey" in result and "secretKey" in result:
        return dict(result)

    payload = result.get("data")
    if not isinstance(payload, dict):
        return None
    if "accessKey" not in payload or "secretKey" not in payload:
        return None
    if "code" not in result or is_success_code(result.get("code")):
        return dict(payload)
    return None


@dataclass(frozen=True, slots=True)
class RestDecodeContext:
    """Describe one REST decoder family's endpoint-scoped authority."""

    family: str
    endpoint: str
    authority: str
    version: str = "v1"

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable family/version identity for registry use."""
        return BoundaryDecoderKey(family=self.family, version=self.version)


class RestBoundaryDecoder(Protocol[CanonicalT]):
    """Protocol for one REST payload decoder family."""

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        ...

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the registry key for this family implementation."""
        ...

    @property
    def authority(self) -> str:
        """Return the authoritative source backing this decoder family."""
        ...

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalT]:
        """Decode one REST payload to a canonical protocol contract."""
        ...


class MqttConfigRestDecoder:
    """Decode the MQTT-config REST family into the canonical contract shape."""

    def __init__(self, *, is_success_code: Callable[[object], bool]) -> None:
        """Store the success-code predicate used by the vendor REST envelope."""
        self._is_success_code = is_success_code
        self._context = RestDecodeContext(
            family=_REST_MQTT_CONFIG_FAMILY,
            endpoint="get_mqtt_config",
            authority=_REST_MQTT_CONFIG_AUTHORITY,
            version=_REST_MQTT_CONFIG_VERSION,
        )

    @property
    def context(self) -> RestDecodeContext:
        """Return the metadata describing this decoder family."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the family/version identity used by the registry."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[dict[str, Any]]:
        """Decode the MQTT-config response into a canonical mapping."""
        canonical = _extract_mqtt_config_mapping(
            payload,
            is_success_code=self._is_success_code,
        )
        if canonical is None:
            message = "MQTT config response missing accessKey/secretKey"
            raise ValueError(message)
        return BoundaryDecodeResult(
            key=self.key,
            canonical=canonical,
            authority=self.authority,
            fingerprint=_build_mapping_fingerprint(payload),
        )


def decode_mqtt_config_payload(
    payload: object,
    *,
    is_success_code: Callable[[object], bool],
) -> BoundaryDecodeResult[dict[str, Any]]:
    """Decode one MQTT-config REST payload through the formal boundary family."""
    return MqttConfigRestDecoder(is_success_code=is_success_code).decode(payload)
