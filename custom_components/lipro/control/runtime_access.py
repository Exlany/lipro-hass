"""Control-owned runtime access helpers."""

from __future__ import annotations

from collections.abc import Mapping

from homeassistant.core import HomeAssistant

from . import runtime_access_support as _support
from .models import (
    FailureSummary,
    RuntimeCoordinatorSnapshot,
    RuntimeDiagnosticsProjection,
    empty_failure_summary,
)
from .runtime_access_types import RuntimeCoordinatorView, RuntimeEntryPort

type RuntimeTelemetryView = dict[str, object]

build_entry_telemetry_exporter = _support.build_entry_telemetry_exporter_support
build_runtime_entry_view = _support.build_runtime_entry_view
find_runtime_device = _support.find_runtime_device
find_runtime_device_and_coordinator = _support.find_runtime_device_and_coordinator
find_runtime_device_for_entry = _support.find_runtime_device_for_entry
find_runtime_entry_for_coordinator = _support.find_runtime_entry_for_coordinator
get_entry_runtime_coordinator = _support.get_entry_runtime_coordinator
get_runtime_device_mapping = _support.get_runtime_device_mapping
has_debug_mode_runtime_entry = _support.has_debug_mode_runtime_entry
is_debug_mode_enabled_for_entry = _support.is_debug_mode_enabled_for_entry
is_developer_runtime_coordinator = _support.is_developer_runtime_coordinator
is_runtime_device_mapping_degraded = _support.is_runtime_device_mapping_degraded
iter_developer_runtime_coordinators = _support.iter_developer_runtime_coordinators
iter_runtime_coordinators = _support.iter_runtime_coordinators
iter_runtime_devices_for_entry = _support.iter_runtime_devices_for_entry
iter_runtime_entries = _support.iter_runtime_entries
iter_runtime_entry_coordinators = _support.iter_runtime_entry_coordinators
iter_runtime_entry_views = _support.iter_runtime_entry_views



def build_entry_system_health_view(
    entry: RuntimeEntryPort | object,
) -> RuntimeTelemetryView:
    """Return the control-plane system-health projection for one config entry."""
    exporter = build_entry_telemetry_exporter(entry)
    if exporter is None:
        return {}

    return dict(exporter.export_views().system_health)



def _coerce_device_count(
    telemetry_view: RuntimeTelemetryView,
    coordinator: RuntimeCoordinatorView,
) -> int:
    device_count = telemetry_view.get("device_count")
    if isinstance(device_count, int):
        return device_count
    return len(coordinator.devices or {})



def _coerce_update_interval(coordinator: RuntimeCoordinatorView) -> str:
    update_interval = coordinator.update_interval
    return "" if update_interval is None else str(update_interval)



def _coerce_mqtt_connected(
    telemetry_view: RuntimeTelemetryView,
    coordinator: RuntimeCoordinatorView,
) -> bool | None:
    mqtt_connected = telemetry_view.get("mqtt_connected")
    if isinstance(mqtt_connected, bool):
        return mqtt_connected
    return coordinator.mqtt_connected



def _coerce_last_update_success(
    telemetry_view: RuntimeTelemetryView,
    coordinator: RuntimeCoordinatorView,
) -> bool:
    last_update_success = telemetry_view.get("last_update_success")
    if isinstance(last_update_success, bool):
        return last_update_success
    return coordinator.last_update_success



def _coerce_entry_ref(telemetry_view: RuntimeTelemetryView) -> str | None:
    entry_ref = telemetry_view.get("entry_ref")
    return entry_ref if isinstance(entry_ref, str) else None



def _coerce_failure_summary(telemetry_view: RuntimeTelemetryView) -> FailureSummary:
    failure_summary = telemetry_view.get("failure_summary")
    normalized = empty_failure_summary()
    if not isinstance(failure_summary, Mapping):
        return normalized
    for key in normalized:
        value = failure_summary.get(key)
        normalized[key] = value if isinstance(value, str) else None
    return normalized



def build_runtime_snapshot(
    entry: RuntimeEntryPort | object,
) -> RuntimeCoordinatorSnapshot | None:
    """Build one control-plane runtime snapshot from a config entry."""
    runtime_entry = build_runtime_entry_view(entry)
    if runtime_entry is None or not runtime_entry.entry_id:
        return None

    coordinator = runtime_entry.coordinator
    if coordinator is None:
        return None

    telemetry_view = build_entry_system_health_view(runtime_entry.entry)
    return RuntimeCoordinatorSnapshot(
        entry_id=runtime_entry.entry_id,
        entry_ref=_coerce_entry_ref(telemetry_view),
        device_count=_coerce_device_count(telemetry_view, coordinator),
        last_update_success=_coerce_last_update_success(telemetry_view, coordinator),
        mqtt_connected=_coerce_mqtt_connected(telemetry_view, coordinator),
        failure_summary=_coerce_failure_summary(telemetry_view),
    )



def build_runtime_diagnostics_projection(
    entry: RuntimeEntryPort | object,
) -> RuntimeDiagnosticsProjection | None:
    """Build the typed diagnostics-facing runtime projection for one config entry."""
    runtime_entry = build_runtime_entry_view(entry)
    if runtime_entry is None or runtime_entry.coordinator is None:
        return None

    snapshot = build_runtime_snapshot(runtime_entry.entry)
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



def build_runtime_snapshots(hass: HomeAssistant) -> list[RuntimeCoordinatorSnapshot]:
    """Build runtime snapshots for all active Lipro entries."""
    snapshots: list[RuntimeCoordinatorSnapshot] = []
    for entry in iter_runtime_entries(hass):
        snapshot = build_runtime_snapshot(entry)
        if snapshot is not None:
            snapshots.append(snapshot)
    return snapshots


__all__ = [
    "build_entry_system_health_view",
    "build_entry_telemetry_exporter",
    "build_runtime_diagnostics_projection",
    "build_runtime_entry_view",
    "build_runtime_snapshot",
    "build_runtime_snapshots",
    "find_runtime_device",
    "find_runtime_device_and_coordinator",
    "find_runtime_device_for_entry",
    "find_runtime_entry_for_coordinator",
    "get_entry_runtime_coordinator",
    "get_runtime_device_mapping",
    "has_debug_mode_runtime_entry",
    "is_debug_mode_enabled_for_entry",
    "is_developer_runtime_coordinator",
    "is_runtime_device_mapping_degraded",
    "iter_developer_runtime_coordinators",
    "iter_runtime_coordinators",
    "iter_runtime_devices_for_entry",
    "iter_runtime_entries",
    "iter_runtime_entry_coordinators",
    "iter_runtime_entry_views",
]
