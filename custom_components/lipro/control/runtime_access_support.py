"""Internal helpers backing the formal runtime_access import home."""

from __future__ import annotations

from ..core.telemetry import RuntimeTelemetryExporter
from .models import RuntimeCoordinatorSnapshot, RuntimeDiagnosticsProjection
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
    _coerce_device_count,
    _coerce_entry_ref,
    _coerce_failure_summary,
    _coerce_last_update_success,
    _coerce_mqtt_connected,
    _coerce_update_interval,
    build_entry_system_health_view_from_view_support,
    build_entry_telemetry_exporter_from_view_support,
)
from .runtime_access_support_views import (
    _build_runtime_entry_view_support,
    _get_entry_runtime_coordinator_support,
    _iter_runtime_coordinators_support,
    _iter_runtime_entries_support,
    _iter_runtime_entry_coordinators_support,
    _iter_runtime_entry_views_support,
)
from .runtime_access_types import RuntimeEntryPort, RuntimeEntryView


def build_runtime_snapshot_from_view_support(
    runtime_entry: RuntimeEntryView | None,
) -> RuntimeCoordinatorSnapshot | None:
    """Build one runtime snapshot from a typed runtime-entry view."""
    if (
        runtime_entry is None
        or not runtime_entry.entry_id
        or runtime_entry.coordinator is None
    ):
        return None
    coordinator = runtime_entry.coordinator
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
    degraded_fields = ("devices",) if runtime_entry.coordinator.devices is None else ()
    return RuntimeDiagnosticsProjection(
        snapshot=snapshot,
        update_interval=_coerce_update_interval(runtime_entry.coordinator),
        degraded_fields=degraded_fields,
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
