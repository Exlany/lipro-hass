"""REST-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, cast

from .rest_decoder_family import (
    DeviceListRestDecoder,
    DeviceStatusRestDecoder,
    ListEnvelopeRestDecoder,
    MeshGroupStatusRestDecoder,
)
from .rest_decoder_registry import (
    _REST_MQTT_CONFIG_CONTEXT,
    _REST_SCHEDULE_JSON_CONTEXT,
    RestBoundaryDecoder,
    RestDecodeContext,
)
from .rest_decoder_utility import (
    _build_payload_fingerprint,
    _build_schedule_json_fingerprint,
    _decode_schedule_json_canonical,
)
from .result import BoundaryDecodeResult, BoundaryDecoderKey

if TYPE_CHECKING:
    from ..contracts import (
        CanonicalDeviceListPage,
        CanonicalDeviceStatusRow,
        CanonicalListEnvelope,
        CanonicalMeshGroupStatusRow,
        CanonicalMqttConfig,
        CanonicalScheduleJson,
    )


def _extract_mqtt_config_mapping(
    payload: object,
    *,
    is_success_code: Callable[[object], bool],
) -> CanonicalMqttConfig | None:
    if not isinstance(payload, dict):
        return None
    if "accessKey" in payload and "secretKey" in payload:
        return cast("CanonicalMqttConfig", dict(payload))

    data = payload.get("data")
    if not isinstance(data, dict):
        return None
    if "accessKey" not in data or "secretKey" not in data:
        return None
    if "code" not in payload or is_success_code(payload.get("code")):
        return cast("CanonicalMqttConfig", dict(data))
    return None


class MqttConfigRestDecoder:
    """Decode the MQTT-config REST family into the canonical contract shape."""

    def __init__(self, *, is_success_code: Callable[[object], bool]) -> None:
        """Initialize the MQTT-config decoder context and status checker."""
        self._is_success_code = is_success_code
        self._context = _REST_MQTT_CONFIG_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable registry key for this decoder family."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source for this decoder family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalMqttConfig]:
        """Decode one MQTT-config payload into the canonical boundary contract."""
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
            fingerprint=_build_payload_fingerprint(payload),
        )


class ScheduleJsonRestDecoder:
    """Decode scheduleJson payloads into canonical schedule triples."""

    def __init__(self) -> None:
        """Initialize the scheduleJson decoder context."""
        self._context = _REST_SCHEDULE_JSON_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        """Return endpoint-bound decoder metadata."""
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        """Return the stable registry key for this decoder family."""
        return self._context.key

    @property
    def authority(self) -> str:
        """Return the authoritative fixture source for this decoder family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalScheduleJson]:
        """Decode one scheduleJson payload into the canonical boundary contract."""
        canonical = _decode_schedule_json_canonical(payload)
        return BoundaryDecodeResult(
            key=self.key,
            canonical=canonical,
            authority=self.authority,
            fingerprint=_build_schedule_json_fingerprint(canonical),
        )


def decode_list_envelope_payload(
    payload: object,
    *,
    offset: int = 0,
) -> BoundaryDecodeResult[CanonicalListEnvelope]:
    """Decode one REST list envelope into canonical rows/metadata."""
    return ListEnvelopeRestDecoder(offset=offset).decode(payload)


def decode_schedule_json_payload(
    payload: object,
) -> BoundaryDecodeResult[CanonicalScheduleJson]:
    """Decode one scheduleJson payload through the formal boundary family."""
    return ScheduleJsonRestDecoder().decode(payload)


def decode_mqtt_config_payload(
    payload: object,
    *,
    is_success_code: Callable[[object], bool],
) -> BoundaryDecodeResult[CanonicalMqttConfig]:
    """Decode one MQTT-config REST payload through the formal boundary family."""
    return MqttConfigRestDecoder(is_success_code=is_success_code).decode(payload)


def decode_device_list_payload(
    payload: object,
    *,
    offset: int = 0,
) -> BoundaryDecodeResult[CanonicalDeviceListPage]:
    """Decode one device-list REST payload into the canonical catalog page."""
    return DeviceListRestDecoder(offset=offset).decode(payload)


def decode_device_status_payload(
    payload: object,
) -> BoundaryDecodeResult[list[CanonicalDeviceStatusRow]]:
    """Decode one device-status REST payload into canonical status rows."""
    return DeviceStatusRestDecoder().decode(payload)


def decode_mesh_group_status_payload(
    payload: object,
) -> BoundaryDecodeResult[list[CanonicalMeshGroupStatusRow]]:
    """Decode one mesh-group-status REST payload into canonical topology rows."""
    return MeshGroupStatusRestDecoder().decode(payload)


__all__ = [
    "DeviceListRestDecoder",
    "DeviceStatusRestDecoder",
    "ListEnvelopeRestDecoder",
    "MeshGroupStatusRestDecoder",
    "MqttConfigRestDecoder",
    "RestBoundaryDecoder",
    "RestDecodeContext",
    "ScheduleJsonRestDecoder",
    "decode_device_list_payload",
    "decode_device_status_payload",
    "decode_list_envelope_payload",
    "decode_mesh_group_status_payload",
    "decode_mqtt_config_payload",
    "decode_schedule_json_payload",
]
