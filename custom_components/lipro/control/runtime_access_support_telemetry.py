"""Support-only telemetry helpers for runtime access."""

from __future__ import annotations

from collections.abc import Mapping

from ..core.telemetry.models import TelemetryJsonValue, TelemetrySourcePayload
from ..core.telemetry.ports import ProtocolTelemetrySource, RuntimeTelemetrySource
from ..runtime_types import LiproCoordinator, ProtocolTelemetryFacadeLike
from .runtime_access_support_members import _get_explicit_member
from .runtime_access_types import RuntimeCoordinatorView


def _coerce_telemetry_json_value(value: object) -> TelemetryJsonValue | None:
    """Return one telemetry-safe JSON value when the object already matches the exporter contract."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        result: list[TelemetryJsonValue] = []
        for item in value:
            normalized = _coerce_telemetry_json_value(item)
            if normalized is None and item is not None:
                return None
            result.append(normalized)
        return result
    if isinstance(value, Mapping):
        return _coerce_telemetry_source_payload(value)
    return None


def _coerce_telemetry_source_payload(
    payload: Mapping[str, object],
) -> TelemetrySourcePayload:
    """Return a telemetry-source payload narrowed to JSON-safe exporter values."""
    normalized: TelemetrySourcePayload = {}
    for key, value in payload.items():
        normalized_value = _coerce_telemetry_json_value(value)
        if normalized_value is not None or value is None:
            normalized[str(key)] = normalized_value
    return normalized


class _ProtocolFacadeTelemetrySource(ProtocolTelemetrySource):
    """Adapter exposing protocol-root telemetry through an explicit source port."""

    def __init__(self, protocol: ProtocolTelemetryFacadeLike) -> None:
        self._protocol = protocol

    def get_protocol_telemetry_snapshot(self) -> TelemetrySourcePayload:
        snapshot = _get_explicit_member(self._protocol, "protocol_diagnostics_snapshot")
        if callable(snapshot):
            result = snapshot()
            if isinstance(result, Mapping):
                return _coerce_telemetry_source_payload(result)
        diagnostics_context = _get_explicit_member(self._protocol, "diagnostics_context")
        context_snapshot = _get_explicit_member(diagnostics_context, "snapshot")
        if callable(context_snapshot):
            result = context_snapshot()
            if isinstance(result, Mapping):
                return _coerce_telemetry_source_payload(result)
        return {}


class _CoordinatorTelemetrySource(RuntimeTelemetrySource):
    """Adapter exposing runtime telemetry through an explicit source port."""

    def __init__(self, coordinator: RuntimeCoordinatorView, *, entry_id: str | None) -> None:
        self._coordinator = coordinator
        self._entry_id = entry_id

    def get_runtime_telemetry_snapshot(self) -> TelemetrySourcePayload:
        payload = _coerce_telemetry_source_payload(
            self._coordinator.runtime_telemetry_snapshot
        )
        if self._entry_id:
            return {"entry_id": self._entry_id, **payload}
        return payload


def _build_runtime_telemetry_snapshot(coordinator: LiproCoordinator) -> Mapping[str, object]:
    """Return a normalized runtime telemetry snapshot for one coordinator."""
    telemetry_service = _get_explicit_member(coordinator, "telemetry_service")
    build_snapshot = _get_explicit_member(telemetry_service, "build_snapshot")
    if callable(build_snapshot):
        snapshot = build_snapshot()
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
    return {}
