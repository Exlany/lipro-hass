"""Canonical contracts and protocols owned by the unified protocol root."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, TypedDict, cast

from ..api.client_auth_recovery import AuthRecoveryCoordinator
from ..api.endpoints.payloads import EndpointPayloadNormalizers
from ..api.schedule_codec import (
    coerce_int_list,
    normalize_mesh_timing_rows,
    parse_mesh_schedule_json,
)
from .boundary import (
    BoundaryDecoderDescriptor,
    BoundaryDecoderRegistry,
    build_protocol_boundary_registry,
    decode_device_list_payload,
    decode_device_status_payload,
    decode_mesh_group_status_payload,
)


class CanonicalMqttConfig(TypedDict):
    """Canonical MQTT config contract after protocol-boundary normalization."""

    accessKey: str
    secretKey: str
    endpoint: str
    clientId: str


class CanonicalDeviceListItem(TypedDict, total=False):
    """Canonical device-catalog row consumed by runtime snapshot builders."""

    deviceId: int | str
    serial: str
    deviceName: str
    type: int | str
    iotName: str
    roomId: int | str
    roomName: str
    productId: int | str
    physicalModel: str
    model: str
    isGroup: bool
    online: bool
    category: str
    homeId: str
    homeName: str
    properties: dict[str, Any]
    identityAliases: list[str]


class CanonicalDeviceListPage(TypedDict, total=False):
    """Canonical device-catalog page exposed by the protocol boundary."""

    devices: list[CanonicalDeviceListItem]
    has_more: bool
    total: int


class CanonicalDeviceStatusRow(TypedDict):
    """Canonical device-status row with normalized identity and properties."""

    deviceId: str
    properties: dict[str, Any]


class CanonicalMeshGroupStatusRow(TypedDict, total=False):
    """Canonical mesh-group topology row used by runtime enrichment."""

    groupId: str
    gatewayDeviceId: str | None
    devices: list[dict[str, str]]
    properties: dict[str, Any]


class MqttTransportFacade(Protocol):
    """Stable transport contract consumed by runtime-facing MQTT collaborators."""

    @property
    def is_connected(self) -> bool:
        """Return whether the transport is currently connected."""
        ...

    @property
    def subscribed_devices(self) -> set[str]:
        """Return the active subscribed-device identifiers."""
        ...

    @property
    def subscribed_count(self) -> int:
        """Return the number of tracked subscriptions."""
        ...

    @property
    def last_error(self) -> Exception | None:
        """Return the latest transport error, if any."""
        ...

    async def start(self, device_ids: list[str]) -> None:
        """Start the MQTT transport for the desired device identifiers."""
        ...

    async def stop(self) -> None:
        """Stop the MQTT transport."""
        ...

    async def sync_subscriptions(self, device_ids: set[str]) -> None:
        """Sync subscriptions to the desired identifier set."""
        ...

    async def wait_until_connected(self, timeout: float | None = None) -> bool:
        """Wait until the transport reports a real broker connection."""
        ...


class CanonicalProtocolContracts:
    """Root-owned contract helpers for transport-boundary normalization."""

    extract_list_payload = staticmethod(EndpointPayloadNormalizers.extract_list_payload)
    extract_data_list = staticmethod(EndpointPayloadNormalizers.extract_data_list)
    extract_timings_list = staticmethod(EndpointPayloadNormalizers.extract_timings_list)
    sanitize_iot_device_ids = staticmethod(
        EndpointPayloadNormalizers.sanitize_iot_device_ids
    )
    normalize_power_target_id = staticmethod(
        EndpointPayloadNormalizers.normalize_power_target_id
    )
    coerce_int_list = staticmethod(coerce_int_list)
    parse_mesh_schedule_json = staticmethod(parse_mesh_schedule_json)
    normalize_mesh_timing_rows = staticmethod(normalize_mesh_timing_rows)

    def __init__(
        self,
        *,
        boundary_registry: BoundaryDecoderRegistry | None = None,
    ) -> None:
        """Bind the protocol root to one boundary decoder registry instance."""
        self._boundary_registry = boundary_registry or build_protocol_boundary_registry(
            is_success_code=AuthRecoveryCoordinator.is_success_code,
        )

    def describe_boundary_decoders(self) -> tuple[BoundaryDecoderDescriptor, ...]:
        """Expose stable boundary-family metadata for tests and future telemetry."""
        return self._boundary_registry.describe()

    def normalize_mqtt_config(self, payload: object) -> CanonicalMqttConfig:
        """Normalize one vendor MQTT-config payload through the boundary registry."""
        decoder = self._boundary_registry.resolve("rest.mqtt-config", "v1")
        result = decoder.decode(payload)
        return cast(CanonicalMqttConfig, result.canonical)

    def normalize_device_list_page(
        self,
        payload: object,
        *,
        offset: int = 0,
    ) -> CanonicalDeviceListPage:
        """Normalize one device-list page to the formal catalog-page contract."""
        result = decode_device_list_payload(payload, offset=offset)
        return cast(CanonicalDeviceListPage, result.canonical)

    def normalize_device_status_rows(
        self,
        payload: object,
    ) -> list[CanonicalDeviceStatusRow]:
        """Normalize device-status rows to canonical id/properties contracts."""
        result = decode_device_status_payload(payload)
        return cast(list[CanonicalDeviceStatusRow], result.canonical)

    def build_device_status_map(self, payload: object) -> dict[str, dict[str, Any]]:
        """Build the runtime-ready device-status mapping from raw boundary payloads."""
        return {
            row["deviceId"]: dict(row["properties"])
            for row in self.normalize_device_status_rows(payload)
            if row["deviceId"]
        }

    def normalize_mesh_group_status_rows(
        self,
        payload: object,
    ) -> list[CanonicalMeshGroupStatusRow]:
        """Normalize mesh-group topology rows through the protocol boundary."""
        result = decode_mesh_group_status_payload(payload)
        return cast(list[CanonicalMeshGroupStatusRow], result.canonical)

    @classmethod
    def snapshot_schedule_rows(
        cls,
        rows: Sequence[object],
        *,
        fallback_device_id: str = "",
    ) -> list[dict[str, Any]]:
        """Normalize schedule rows for protocol-level snapshotting."""
        return cls.normalize_mesh_timing_rows(
            rows,
            fallback_device_id=fallback_device_id,
        )


__all__ = [
    "CanonicalDeviceListItem",
    "CanonicalDeviceListPage",
    "CanonicalDeviceStatusRow",
    "CanonicalMeshGroupStatusRow",
    "CanonicalMqttConfig",
    "CanonicalProtocolContracts",
    "MqttTransportFacade",
]
