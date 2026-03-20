"""REST-side decoder contracts and concrete family implementations."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, TypeVar, cast

from ...api.schedule_codec import parse_mesh_schedule_json
from .rest_decoder_support import (
    _build_payload_fingerprint,
    _decode_device_list_canonical,
    _decode_device_status_canonical,
    _decode_list_envelope_canonical,
    _decode_mesh_group_status_canonical,
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

CanonicalT = TypeVar("CanonicalT")
_REST_MQTT_CONFIG_FAMILY = "rest.mqtt-config"
_REST_MQTT_CONFIG_VERSION = "v1"
_REST_MQTT_CONFIG_AUTHORITY = "tests/fixtures/api_contracts/get_mqtt_config.*.json"
_REST_DEVICE_LIST_FAMILY = "rest.device-list"
_REST_DEVICE_LIST_VERSION = "v1"
_REST_DEVICE_LIST_AUTHORITY = "tests/fixtures/api_contracts/get_device_list.*.json"
_REST_DEVICE_STATUS_FAMILY = "rest.device-status"
_REST_DEVICE_STATUS_VERSION = "v1"
_REST_DEVICE_STATUS_AUTHORITY = "tests/fixtures/api_contracts/query_device_status.*.json"
_REST_MESH_GROUP_STATUS_FAMILY = "rest.mesh-group-status"
_REST_MESH_GROUP_STATUS_VERSION = "v1"
_REST_MESH_GROUP_STATUS_AUTHORITY = (
    "tests/fixtures/api_contracts/query_mesh_group_status.*.json"
)
_REST_LIST_ENVELOPE_FAMILY = "rest.list-envelope"
_REST_LIST_ENVELOPE_VERSION = "v1"
_REST_LIST_ENVELOPE_AUTHORITY = "tests/fixtures/api_contracts/get_device_list.*.json"
_REST_SCHEDULE_JSON_FAMILY = "rest.schedule-json"
_REST_SCHEDULE_JSON_VERSION = "v1"
_REST_SCHEDULE_JSON_AUTHORITY = "tests/fixtures/api_contracts/query_mesh_schedule_json.v1.json"


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


def _build_schedule_json_fingerprint(payload: object) -> str:
    canonical = _decode_schedule_json_canonical(payload)
    return (
        f"days:{len(canonical['days'])}|"
        f"time:{len(canonical['time'])}|"
        f"evt:{len(canonical['evt'])}"
    )


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

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalMqttConfig]:
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
            fingerprint=_build_payload_fingerprint(payload),
        )


class ListEnvelopeRestDecoder:
    """Decode generic REST list envelopes into a canonical transport shape."""

    def __init__(self, *, offset: int = 0) -> None:
        """Bind the decoder to one pagination offset for `has_more` calculation."""
        self._offset = offset
        self._context = RestDecodeContext(
            family=_REST_LIST_ENVELOPE_FAMILY,
            endpoint="generic_list",
            authority=_REST_LIST_ENVELOPE_AUTHORITY,
            version=_REST_LIST_ENVELOPE_VERSION,
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

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalListEnvelope]:
        """Decode one REST list envelope into canonical rows/metadata."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_list_envelope_canonical(payload, offset=self._offset),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class ScheduleJsonRestDecoder:
    """Decode scheduleJson payloads into canonical schedule triples."""

    def __init__(self) -> None:
        """Initialize one decoder bound to the schedule-json authority family."""
        self._context = RestDecodeContext(
            family=_REST_SCHEDULE_JSON_FAMILY,
            endpoint="schedule_json",
            authority=_REST_SCHEDULE_JSON_AUTHORITY,
            version=_REST_SCHEDULE_JSON_VERSION,
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

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalScheduleJson]:
        """Decode one scheduleJson payload into the canonical triple contract."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_schedule_json_canonical(payload),
            authority=self.authority,
            fingerprint=_build_schedule_json_fingerprint(payload),
        )


class DeviceListRestDecoder:
    """Decode device-list payloads into a canonical catalog page contract."""

    def __init__(self, *, offset: int = 0) -> None:
        """Bind the decoder to one pagination offset for `has_more` calculation."""
        self._offset = max(0, offset)
        self._context = RestDecodeContext(
            family=_REST_DEVICE_LIST_FAMILY,
            endpoint="get_device_list",
            authority=_REST_DEVICE_LIST_AUTHORITY,
            version=_REST_DEVICE_LIST_VERSION,
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
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalDeviceListPage]:
        """Decode one device-list payload into the canonical catalog page."""
        canonical = _decode_device_list_canonical(payload, offset=self._offset)
        return BoundaryDecodeResult(
            key=self.key,
            canonical=canonical,
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class DeviceStatusRestDecoder:
    """Decode device-status payloads into canonical status rows."""

    def __init__(self) -> None:
        """Initialize one device-status decoder bound to its authority family."""
        self._context = RestDecodeContext(
            family=_REST_DEVICE_STATUS_FAMILY,
            endpoint="query_device_status",
            authority=_REST_DEVICE_STATUS_AUTHORITY,
            version=_REST_DEVICE_STATUS_VERSION,
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
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(
        self,
        payload: object,
    ) -> BoundaryDecodeResult[list[CanonicalDeviceStatusRow]]:
        """Decode one device-status payload into canonical rows."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_device_status_canonical(payload),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
        )


class MeshGroupStatusRestDecoder:
    """Decode mesh-group-status payloads into canonical topology rows."""

    def __init__(self) -> None:
        """Initialize one device-status decoder bound to its authority family."""
        self._context = RestDecodeContext(
            family=_REST_MESH_GROUP_STATUS_FAMILY,
            endpoint="query_mesh_group_status",
            authority=_REST_MESH_GROUP_STATUS_AUTHORITY,
            version=_REST_MESH_GROUP_STATUS_VERSION,
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
        """Return the authoritative fixture source backing this family."""
        return self._context.authority

    def decode(
        self,
        payload: object,
    ) -> BoundaryDecodeResult[list[CanonicalMeshGroupStatusRow]]:
        """Decode one mesh-group-status payload into canonical topology rows."""
        return BoundaryDecodeResult(
            key=self.key,
            canonical=_decode_mesh_group_status_canonical(payload),
            authority=self.authority,
            fingerprint=_build_payload_fingerprint(payload),
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
