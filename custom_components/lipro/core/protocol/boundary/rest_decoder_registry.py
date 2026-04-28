"""Registry metadata for REST boundary decoder families."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from .result import BoundaryDecodeResult, BoundaryDecoderKey

CanonicalT_co = TypeVar("CanonicalT_co", covariant=True)


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


class RestBoundaryDecoder(Protocol[CanonicalT_co]):
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

    def decode(self, payload: object) -> BoundaryDecodeResult[CanonicalT_co]:
        """Decode one REST payload to a canonical protocol contract."""
        ...


_REST_MQTT_CONFIG_CONTEXT = RestDecodeContext(
    family="rest.mqtt-config",
    endpoint="get_mqtt_config",
    authority="tests/fixtures/api_contracts/get_mqtt_config.*.json",
)
_REST_LIST_ENVELOPE_CONTEXT = RestDecodeContext(
    family="rest.list-envelope",
    endpoint="get_device_list",
    authority="tests/fixtures/api_contracts/get_device_list.*.json",
)
_REST_SCHEDULE_JSON_CONTEXT = RestDecodeContext(
    family="rest.schedule-json",
    endpoint="query_mesh_schedule_json",
    authority="tests/fixtures/api_contracts/query_mesh_schedule_json.v1.json",
)
_REST_DEVICE_LIST_CONTEXT = RestDecodeContext(
    family="rest.device-list",
    endpoint="get_device_list",
    authority="tests/fixtures/api_contracts/get_device_list.*.json",
)
_REST_DEVICE_STATUS_CONTEXT = RestDecodeContext(
    family="rest.device-status",
    endpoint="query_device_status",
    authority="tests/fixtures/api_contracts/query_device_status.*.json",
)
_REST_MESH_GROUP_STATUS_CONTEXT = RestDecodeContext(
    family="rest.mesh-group-status",
    endpoint="query_mesh_group_status",
    authority="tests/fixtures/api_contracts/query_mesh_group_status.*.json",
)


__all__ = [
    "_REST_DEVICE_LIST_CONTEXT",
    "_REST_DEVICE_STATUS_CONTEXT",
    "_REST_LIST_ENVELOPE_CONTEXT",
    "_REST_MESH_GROUP_STATUS_CONTEXT",
    "_REST_MQTT_CONFIG_CONTEXT",
    "_REST_SCHEDULE_JSON_CONTEXT",
    "RestBoundaryDecoder",
    "RestDecodeContext",
]
