"""Internal helpers backing the formal runtime_access import home."""

from __future__ import annotations

from ..core.telemetry import RuntimeTelemetryExporter
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
from .runtime_access_types import RuntimeEntryPort


def build_entry_telemetry_exporter_support(
    entry: RuntimeEntryPort | object,
) -> RuntimeTelemetryExporter | None:
    """Build one explicit telemetry exporter for a runtime entry when available."""
    runtime_entry = _build_runtime_entry_view_support(entry)
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
    "build_entry_telemetry_exporter_support",
]
