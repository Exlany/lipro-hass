"""MQTT-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import json
from typing import TYPE_CHECKING, Protocol, TypeVar, cast

from ....const.api import MQTT_TOPIC_PREFIX
from ...api.types import DevicePropertyMap, JsonObject
from ...mqtt.payload import _MAX_MQTT_PAYLOAD_BYTES
from ...mqtt.topics import normalize_mqtt_biz_id
from ...utils.property_normalization import normalize_properties
from .result import BoundaryDecodeResult, BoundaryDecoderKey

if TYPE_CHECKING:
    from ..contracts import (
        CanonicalMqttMessageEnvelope,
        CanonicalMqttProperties,
        CanonicalMqttTopic,
    )

CanonicalT = TypeVar("CanonicalT")
_MQTT_TOPIC_FAMILY = "mqtt.topic"
_MQTT_TOPIC_VERSION = "v1"
_MQTT_TOPIC_AUTHORITY = "tests/fixtures/protocol_boundary/mqtt_topic.device_state.v1.json"
_MQTT_MESSAGE_ENVELOPE_FAMILY = "mqtt.message-envelope"
_MQTT_MESSAGE_ENVELOPE_VERSION = "v1"
_MQTT_MESSAGE_ENVELOPE_AUTHORITY = (
    "tests/fixtures/protocol_boundary/mqtt_message_envelope.device_state.v1.json"
)
_MQTT_PROPERTIES_FAMILY = "mqtt.properties"
_MQTT_PROPERTIES_VERSION = "v1"
_MQTT_PROPERTIES_AUTHORITY = "tests/core/mqtt/test_mqtt.py"
_MQTT_STATE_TOPIC_FAMILY = f"{MQTT_TOPIC_PREFIX}/*"
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


def _normalize_device_id(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized or not all(char.isalnum() or char in "-_" for char in normalized):
        return None
    return normalized


def _select_message_source(payload: JsonObject) -> tuple[JsonObject, str]:
    """Select the mapping containing property groups plus the wrapper path."""
    current = payload
    path = "root"
    for _ in range(3):
        if any(
            isinstance(current.get(group_name), dict)
            for group_name in _MQTT_PROPERTY_GROUPS
        ):
            return current, path
        next_payload = None
        next_key = None
        for wrapper_key in ("data", "payload"):
            candidate = current.get(wrapper_key)
            if isinstance(candidate, dict):
                next_payload = candidate
                next_key = wrapper_key
                break
        if next_payload is None or next_key is None:
            return current, path
        current = next_payload
        path = next_key if path == "root" else f"{path}.{next_key}"
    return current, path


def _select_property_source(payload: JsonObject) -> JsonObject:
    """Select the mapping that actually contains device property groups."""
    source, _ = _select_message_source(payload)
    return source


def _build_topic_fingerprint(topic: object) -> str:
    if not isinstance(topic, str):
        return type(topic).__name__
    parts = topic.split("/")
    prefix = parts[0] if parts else ""
    return f"{prefix}/{len(parts)}"


def _build_message_envelope_fingerprint(payload: object) -> str:
    if not isinstance(payload, dict):
        return type(payload).__name__
    source, path = _select_message_source(cast(JsonObject, payload))
    groups = sorted(str(key) for key, value in source.items() if isinstance(value, Mapping))
    if not groups:
        return path
    return f"{path}:{'|'.join(groups)}"


def _coerce_message_mapping(payload: object) -> JsonObject | None:
    if isinstance(payload, memoryview):
        payload = payload.tobytes()
    if isinstance(payload, (bytes, bytearray)):
        raw_bytes = bytes(payload)
        if len(raw_bytes) > _MAX_MQTT_PAYLOAD_BYTES:
            return None
        try:
            payload = json.loads(raw_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeError):
            return None
    elif isinstance(payload, str):
        if len(payload.encode("utf-8")) > _MAX_MQTT_PAYLOAD_BYTES:
            return None
        try:
            payload = json.loads(payload)
        except (json.JSONDecodeError, UnicodeError):
            return None

    if not isinstance(payload, dict):
        return None
    return cast(JsonObject, dict(payload))


def _build_property_fingerprint(payload: object) -> str:
    """Return a safe shape fingerprint for MQTT property payloads."""
    if not isinstance(payload, dict):
        return type(payload).__name__
    source = _select_property_source(cast(JsonObject, payload))
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


class MqttTopicDecoder:
    """Decode MQTT topic grammar into canonical biz/device identifiers."""

    def __init__(self, *, expected_biz_id: str | None = None) -> None:
        """Bind the decoder to an optional expected biz identifier."""
        self._expected_biz_id = expected_biz_id
        self._context = MqttDecodeContext(
            family=_MQTT_TOPIC_FAMILY,
            topic_family=_MQTT_STATE_TOPIC_FAMILY,
            authority=_MQTT_TOPIC_AUTHORITY,
            version=_MQTT_TOPIC_VERSION,
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
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalMqttTopic]:
        """Decode one MQTT topic into normalized biz/device identifiers."""
        fingerprint = _build_topic_fingerprint(payload)
        if not isinstance(payload, str):
            return BoundaryDecodeResult(
                key=self.key,
                canonical={},
                authority=self.authority,
                fingerprint=fingerprint,
            )

        parts = payload.split("/")
        if len(parts) != 3 or parts[0] != MQTT_TOPIC_PREFIX:
            return BoundaryDecodeResult(
                key=self.key,
                canonical={},
                authority=self.authority,
                fingerprint=fingerprint,
            )

        biz_id = normalize_mqtt_biz_id(parts[1])
        device_id = _normalize_device_id(parts[2])
        if biz_id is None or device_id is None:
            return BoundaryDecodeResult(
                key=self.key,
                canonical={},
                authority=self.authority,
                fingerprint=fingerprint,
            )

        if self._expected_biz_id is not None:
            normalized_expected = normalize_mqtt_biz_id(self._expected_biz_id)
            if normalized_expected is None or normalized_expected != biz_id:
                return BoundaryDecodeResult(
                    key=self.key,
                    canonical={},
                    authority=self.authority,
                    fingerprint=fingerprint,
                )

        canonical: CanonicalMqttTopic = {
            "bizId": biz_id,
            "deviceId": device_id,
            "topicFamily": _MQTT_STATE_TOPIC_FAMILY,
        }
        return BoundaryDecodeResult(
            key=self.key,
            canonical=canonical,
            authority=self.authority,
            fingerprint=fingerprint,
        )


class MqttMessageEnvelopeDecoder:
    """Decode MQTT payload envelopes before property canonicalization."""

    def __init__(self) -> None:
        """Initialize the metadata describing the message-envelope family."""
        self._context = MqttDecodeContext(
            family=_MQTT_MESSAGE_ENVELOPE_FAMILY,
            topic_family=_MQTT_STATE_TOPIC_FAMILY,
            authority=_MQTT_MESSAGE_ENVELOPE_AUTHORITY,
            version=_MQTT_MESSAGE_ENVELOPE_VERSION,
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
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(
        self,
        payload: object,
    ) -> BoundaryDecodeResult[CanonicalMqttMessageEnvelope]:
        """Decode one MQTT payload envelope into the canonical source mapping."""
        mapping = _coerce_message_mapping(payload)
        if mapping is None:
            return BoundaryDecodeResult(
                key=self.key,
                canonical={},
                authority=self.authority,
                fingerprint=type(payload).__name__,
            )

        canonical, _ = _select_message_source(mapping)
        return BoundaryDecodeResult(
            key=self.key,
            canonical=cast("CanonicalMqttMessageEnvelope", dict(canonical)),
            authority=self.authority,
            fingerprint=_build_message_envelope_fingerprint(mapping),
        )


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

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalMqttProperties]:
        """Decode one MQTT property payload into canonical device properties."""
        envelope = decode_mqtt_message_envelope_payload(payload)
        source = envelope.canonical

        properties: DevicePropertyMap = {}
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
            canonical=cast(DevicePropertyMap, normalize_properties(properties)),
            authority=self.authority,
            fingerprint=_build_property_fingerprint(source),
        )


def decode_mqtt_topic_payload(
    payload: object,
    *,
    expected_biz_id: str | None = None,
) -> BoundaryDecodeResult[CanonicalMqttTopic]:
    """Decode one MQTT topic through the formal topic grammar family."""
    return MqttTopicDecoder(expected_biz_id=expected_biz_id).decode(payload)


def decode_mqtt_message_envelope_payload(
    payload: object,
) -> BoundaryDecodeResult[CanonicalMqttMessageEnvelope]:
    """Decode one MQTT payload envelope before property canonicalization."""
    return MqttMessageEnvelopeDecoder().decode(payload)


def decode_mqtt_properties_payload(
    payload: object,
) -> BoundaryDecodeResult[CanonicalMqttProperties]:
    """Decode one MQTT property payload through the formal boundary family."""
    return MqttPropertiesDecoder().decode(payload)
