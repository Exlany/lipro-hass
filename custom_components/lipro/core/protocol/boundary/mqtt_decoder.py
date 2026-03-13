"""MQTT-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from ...utils.property_normalization import normalize_properties
from .result import BoundaryDecodeResult, BoundaryDecoderKey

CanonicalT = TypeVar("CanonicalT")
_MQTT_PROPERTIES_FAMILY = "mqtt.properties"
_MQTT_PROPERTIES_VERSION = "v1"
_MQTT_PROPERTIES_AUTHORITY = "tests/core/mqtt/test_mqtt.py"
_MQTT_PROPERTY_GROUPS = (
    "common",
    "light",
    "fanLight",
    "switchs",
    "outlet",
    "curtain",
    "gateway",
)
_NOISE_VALUES = frozenset({"-1", ""})


def _select_property_source(payload: dict[str, Any]) -> dict[str, Any]:
    """Select the mapping that actually contains device property groups."""
    current = payload
    for _ in range(3):
        if any(
            isinstance(current.get(group_name), dict)
            for group_name in _MQTT_PROPERTY_GROUPS
        ):
            return current
        next_payload = None
        for wrapper_key in ("data", "payload"):
            candidate = current.get(wrapper_key)
            if isinstance(candidate, dict):
                next_payload = candidate
                break
        if next_payload is None:
            return current
        current = next_payload
    return current


def _build_property_fingerprint(payload: object) -> str:
    """Return a safe shape fingerprint for MQTT property payloads."""
    if not isinstance(payload, dict):
        return type(payload).__name__
    source = _select_property_source(payload)
    groups = [
        group_name
        for group_name in _MQTT_PROPERTY_GROUPS
        if isinstance(source.get(group_name), dict)
    ]
    if not groups:
        return "no-groups"
    return "|".join(groups)


@dataclass(frozen=True, slots=True)
class MqttDecodeContext:
    """Describe one MQTT decoder family's topic-scoped authority."""

    family: str
    topic_family: str
    authority: str
    version: str = "v1"

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable family/version identity for registry use."""
        return BoundaryDecoderKey(family=self.family, version=self.version)


class MqttBoundaryDecoder(Protocol[CanonicalT]):
    """Protocol for one MQTT payload decoder family."""

    @property
    def context(self) -> MqttDecodeContext:
        """Return topic-bound decoder metadata."""
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
        """Decode one MQTT payload to a canonical protocol contract."""
        ...


class MqttPropertiesDecoder:
    """Decode MQTT device-property frames into canonical property mappings."""

    def __init__(self) -> None:
        """Initialize the metadata describing the first MQTT boundary family."""
        self._context = MqttDecodeContext(
            family=_MQTT_PROPERTIES_FAMILY,
            topic_family="Topic_Device_State/*",
            authority=_MQTT_PROPERTIES_AUTHORITY,
            version=_MQTT_PROPERTIES_VERSION,
        )

    @property
    def context(self) -> MqttDecodeContext:
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
        """Decode one MQTT property payload into canonical device properties."""
        if not isinstance(payload, dict):
            return BoundaryDecodeResult(
                key=self.key,
                canonical={},
                authority=self.authority,
                fingerprint=type(payload).__name__,
            )

        properties: dict[str, Any] = {}
        source = _select_property_source(payload)
        for group_name in _MQTT_PROPERTY_GROUPS:
            group_data = source.get(group_name)
            if not isinstance(group_data, dict):
                continue
            for mqtt_key, value in group_data.items():
                if isinstance(value, str) and value.strip() in _NOISE_VALUES:
                    continue
                if isinstance(value, (int, float)) and value == -1:
                    continue
                properties[str(mqtt_key)] = value

        return BoundaryDecodeResult(
            key=self.key,
            canonical=normalize_properties(properties),
            authority=self.authority,
            fingerprint=_build_property_fingerprint(payload),
        )


def decode_mqtt_properties_payload(
    payload: object,
) -> BoundaryDecodeResult[dict[str, Any]]:
    """Decode one MQTT property payload through the formal boundary family."""
    return MqttPropertiesDecoder().decode(payload)
