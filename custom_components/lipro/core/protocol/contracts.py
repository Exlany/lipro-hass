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
)


class CanonicalMqttConfig(TypedDict):
    """Canonical MQTT config contract after protocol-boundary normalization."""

    accessKey: str
    secretKey: str
    endpoint: str
    clientId: str


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
    "CanonicalMqttConfig",
    "CanonicalProtocolContracts",
    "MqttTransportFacade",
]
