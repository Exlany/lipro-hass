"""REST-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, cast

from ...api.schedule_codec import parse_mesh_schedule_json
from .rest_decoder_family import (
    DeviceListRestDecoder,
    DeviceStatusRestDecoder,
    ListEnvelopeRestDecoder,
    MeshGroupStatusRestDecoder,
)
from .rest_decoder_registry import (
    RestBoundaryDecoder,
    RestDecodeContext,
    _REST_MQTT_CONFIG_CONTEXT,
    _REST_SCHEDULE_JSON_CONTEXT,
)
from .rest_decoder_utility import _build_payload_fingerprint
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


def _extract_schedule_json_source(payload: object) -> object:
    if not isinstance(payload, Mapping):
        return payload
    if "scheduleJson" in payload:
        return payload.get("scheduleJson")
    if "payload" in payload:
        return payload.get("payload")
    return payload


def _decode_schedule_json_canonical(payload: object) -> CanonicalScheduleJson:
    parsed = parse_mesh_schedule_json(
        _extract_schedule_json_source(payload),
        mask_sensitive_data=lambda value: value,
    )
    return {
        "days": parsed["days"],
        "time": parsed["time"],
        "evt": parsed["evt"],
    }


def _build_schedule_json_fingerprint(canonical: CanonicalScheduleJson) -> str:
    return (
        f"days:{len(canonical['days'])}|"
        f"time:{len(canonical['time'])}|"
        f"evt:{len(canonical['evt'])}"
    )


class MqttConfigRestDecoder:
    """Decode the MQTT-config REST family into the canonical contract shape."""

    def __init__(self, *, is_success_code: Callable[[object], bool]) -> None:
        self._is_success_code = is_success_code
        self._context = _REST_MQTT_CONFIG_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        return self._context.key

    @property
    def authority(self) -> str:
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalMqttConfig]:
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
        self._context = _REST_SCHEDULE_JSON_CONTEXT

    @property
    def context(self) -> RestDecodeContext:
        return self._context

    @property
    def key(self) -> BoundaryDecoderKey:
        return self._context.key

    @property
    def authority(self) -> str:
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalScheduleJson]:
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
