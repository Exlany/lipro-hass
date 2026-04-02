"""Internal helpers backing the formal runtime_access import home."""

from __future__ import annotations

from ..core.telemetry import RuntimeTelemetryExporter
from ..core.telemetry.models import FailureSummary, SystemHealthTelemetryView
from .models import (
    RuntimeCoordinatorSnapshot,
    RuntimeDiagnosticsProjection,
    empty_failure_summary,
)
from .runtime_access_support_devices import (
    _find_runtime_device_and_coordinator_support,
    _find_runtime_device_for_entry_support,
    _find_runtime_device_support,
    _find_runtime_entry_for_coordinator_support,
    _get_runtime_device_mapping_support,
    _has_debug_mode_runtime_entry_support,
    _is_debug_mode_enabled_for_entry_support,
    _is_developer_runtime_coordinator_support,
    _is_runtime_device_mapping_degraded_support,
    _iter_developer_runtime_coordinators_support,
    _iter_runtime_devices_for_entry_support,
)
from .runtime_access_support_telemetry import (
    _CoordinatorTelemetrySource,
    _ProtocolFacadeTelemetrySource,
)
from .runtime_access_support_views import (
    _build_runtime_entry_view_support,
    _get_entry_runtime_coordinator_support,
    _iter_runtime_coordinators_support,
    _iter_runtime_entries_support,
    _iter_runtime_entry_coordinators_support,
    _iter_runtime_entry_views_support,
)
from .runtime_access_types import (
    RuntimeCoordinatorView,
    RuntimeEntryPort,
    RuntimeEntryView,
)


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


def _coerce_entry_ref(
    telemetry_view: SystemHealthTelemetryView | None,
) -> str | None:
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


def build_entry_telemetry_exporter_support(
    entry: RuntimeEntryPort | object,
) -> RuntimeTelemetryExporter | None:
    """Build one explicit telemetry exporter for a runtime entry when available."""
    runtime_entry = _build_runtime_entry_view_support(entry)
    return build_entry_telemetry_exporter_from_view_support(runtime_entry)


__all__ = [
    "_build_runtime_entry_view_support",
    "_find_runtime_device_and_coordinator_support",
    "_find_runtime_device_for_entry_support",
    "_find_runtime_device_support",
    "_find_runtime_entry_for_coordinator_support",
    "_get_entry_runtime_coordinator_support",
    "_get_runtime_device_mapping_support",
    "_has_debug_mode_runtime_entry_support",
    "_is_debug_mode_enabled_for_entry_support",
    "_is_developer_runtime_coordinator_support",
    "_is_runtime_device_mapping_degraded_support",
    "_iter_developer_runtime_coordinators_support",
    "_iter_runtime_coordinators_support",
    "_iter_runtime_devices_for_entry_support",
    "_iter_runtime_entries_support",
    "_iter_runtime_entry_coordinators_support",
    "_iter_runtime_entry_views_support",
    "build_entry_system_health_view_from_view_support",
    "build_entry_telemetry_exporter_from_view_support",
    "build_entry_telemetry_exporter_support",
    "build_runtime_diagnostics_projection_from_view_support",
    "build_runtime_snapshot_from_view_support",
]
