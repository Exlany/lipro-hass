"""Support-only telemetry helpers for runtime access."""

from __future__ import annotations

from collections.abc import Mapping

from ..core.telemetry import RuntimeTelemetryExporter
from ..core.telemetry.models import (
    FailureSummary,
    SystemHealthTelemetryView,
    TelemetryJsonValue,
    TelemetrySourcePayload,
)
from ..core.telemetry.ports import ProtocolTelemetrySource, RuntimeTelemetrySource
from .models import (
    RuntimeCoordinatorSnapshot,
    RuntimeDiagnosticsProjection,
    empty_failure_summary,
)
from .runtime_access_support_members import _has_explicit_runtime_member
from .runtime_access_types import (
    RuntimeAccessCoordinator,
    RuntimeAccessProtocol,
    RuntimeCoordinatorView,
    RuntimeEntryView,
)


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

    def __init__(self, protocol: RuntimeAccessProtocol) -> None:
        self._protocol = protocol

    def get_protocol_telemetry_snapshot(self) -> TelemetrySourcePayload:
        try:
            snapshot = self._protocol.protocol_diagnostics_snapshot
        except AttributeError:
            snapshot = None
        if callable(snapshot):
            result = snapshot()
            if isinstance(result, Mapping):
                return _coerce_telemetry_source_payload(result)

        try:
            diagnostics_context = self._protocol.diagnostics_context
        except AttributeError:
            diagnostics_context = None
        try:
            context_snapshot = diagnostics_context.snapshot
        except AttributeError:
            context_snapshot = None
        if callable(context_snapshot):
            result = context_snapshot()
            if isinstance(result, Mapping):
                return _coerce_telemetry_source_payload(result)
        return {}


class _CoordinatorTelemetrySource(RuntimeTelemetrySource):
    """Adapter exposing runtime telemetry through an explicit source port."""

    def __init__(
        self, coordinator: RuntimeCoordinatorView, *, entry_id: str | None
    ) -> None:
        self._coordinator = coordinator
        self._entry_id = entry_id

    def get_runtime_telemetry_snapshot(self) -> TelemetrySourcePayload:
        payload = _coerce_telemetry_source_payload(
            self._coordinator.runtime_telemetry_snapshot
        )
        if self._entry_id:
            return {"entry_id": self._entry_id, **payload}
        return payload


def build_entry_telemetry_exporter_from_view_support(
    runtime_entry: RuntimeEntryView | None,
) -> RuntimeTelemetryExporter | None:
    """Build one explicit telemetry exporter from a materialized runtime-entry view."""
    if runtime_entry is None or runtime_entry.coordinator is None:
        return None

    protocol = runtime_entry.coordinator.protocol
    if protocol is None:
        return None

    return RuntimeTelemetryExporter(
        protocol_source=_ProtocolFacadeTelemetrySource(protocol),
        runtime_source=_CoordinatorTelemetrySource(
            runtime_entry.coordinator,
            entry_id=runtime_entry.entry_id or None,
        ),
    )


def build_entry_system_health_view_from_view_support(
    runtime_entry: RuntimeEntryView | None,
) -> SystemHealthTelemetryView | None:
    """Build one system-health telemetry view from a runtime-entry view."""
    exporter = build_entry_telemetry_exporter_from_view_support(runtime_entry)
    if exporter is None:
        return None
    return exporter.export_views().system_health


def _coerce_device_count(
    telemetry_view: SystemHealthTelemetryView | None,
    coordinator: RuntimeCoordinatorView,
) -> int:
    coordinator_count = len(coordinator.devices or {})
    if telemetry_view is None:
        return coordinator_count

    device_count = telemetry_view["device_count"]
    if device_count == 0 and coordinator_count > 0:
        return coordinator_count
    return device_count


def _coerce_update_interval(coordinator: RuntimeCoordinatorView) -> str:
    update_interval = coordinator.update_interval
    return "" if update_interval is None else str(update_interval)


def _coerce_mqtt_connected(
    telemetry_view: SystemHealthTelemetryView | None,
    coordinator: RuntimeCoordinatorView,
) -> bool | None:
    if telemetry_view is None or telemetry_view["mqtt_connected"] is None:
        return coordinator.mqtt_connected
    return telemetry_view["mqtt_connected"]


def _coerce_last_update_success(
    telemetry_view: SystemHealthTelemetryView | None,
    coordinator: RuntimeCoordinatorView,
) -> bool:
    if telemetry_view is None or telemetry_view["last_update_success"] is None:
        return coordinator.last_update_success
    return telemetry_view["last_update_success"]


def _coerce_entry_ref(telemetry_view: SystemHealthTelemetryView | None) -> str | None:
    if telemetry_view is None:
        return None
    return telemetry_view["entry_ref"]


def _coerce_failure_summary(
    telemetry_view: SystemHealthTelemetryView | None,
) -> FailureSummary:
    normalized = empty_failure_summary()
    if telemetry_view is None:
        return normalized

    for key in normalized:
        value = telemetry_view["failure_summary"].get(key)
        normalized[key] = value if isinstance(value, str) or value is None else None
    return normalized


def build_runtime_snapshot_from_view_support(
    runtime_entry: RuntimeEntryView | None,
) -> RuntimeCoordinatorSnapshot | None:
    """Build one runtime snapshot from a typed runtime-entry view."""
    if runtime_entry is None or not runtime_entry.entry_id:
        return None

    coordinator = runtime_entry.coordinator
    if coordinator is None:
        return None

    telemetry_view = build_entry_system_health_view_from_view_support(runtime_entry)
    return RuntimeCoordinatorSnapshot(
        entry_id=runtime_entry.entry_id,
        entry_ref=_coerce_entry_ref(telemetry_view),
        device_count=_coerce_device_count(telemetry_view, coordinator),
        last_update_success=_coerce_last_update_success(telemetry_view, coordinator),
        mqtt_connected=_coerce_mqtt_connected(telemetry_view, coordinator),
        failure_summary=_coerce_failure_summary(telemetry_view),
    )


def build_runtime_diagnostics_projection_from_view_support(
    runtime_entry: RuntimeEntryView | None,
) -> RuntimeDiagnosticsProjection | None:
    """Build one diagnostics projection from a typed runtime-entry view."""
    if runtime_entry is None or runtime_entry.coordinator is None:
        return None

    snapshot = build_runtime_snapshot_from_view_support(runtime_entry)
    if snapshot is None:
        return None

    degraded_fields: list[str] = []
    if runtime_entry.coordinator.devices is None:
        degraded_fields.append("devices")

    return RuntimeDiagnosticsProjection(
        snapshot=snapshot,
        update_interval=_coerce_update_interval(runtime_entry.coordinator),
        degraded_fields=tuple(degraded_fields),
    )


def _build_runtime_telemetry_snapshot(
    coordinator: RuntimeAccessCoordinator,
) -> Mapping[str, object]:
    """Return a normalized runtime telemetry snapshot for one coordinator."""
    if not _has_explicit_runtime_member(coordinator, "telemetry_service"):
        return {}
    try:
        telemetry_service = coordinator.telemetry_service
    except AttributeError:
        return {}

    if not _has_explicit_runtime_member(telemetry_service, "build_snapshot"):
        return {}
    try:
        build_snapshot = telemetry_service.build_snapshot
    except AttributeError:
        return {}
    if callable(build_snapshot):
        snapshot = build_snapshot()
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
    return {}
