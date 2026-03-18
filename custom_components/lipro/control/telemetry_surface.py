"""Control-plane bridge for runtime telemetry exporting."""

from __future__ import annotations

from ..core.telemetry import RuntimeTelemetryExporter, TelemetrySnapshot, TelemetryViews
from .runtime_access import _build_entry_telemetry_exporter

type TelemetryPayload = dict[str, object]


def get_entry_telemetry_exporter(entry: object) -> RuntimeTelemetryExporter | None:
    """Return a telemetry exporter for one config entry, when available."""
    return _build_entry_telemetry_exporter(entry)


def build_entry_telemetry_snapshot(entry: object) -> TelemetrySnapshot | None:
    """Build one exporter snapshot for a config entry."""
    exporter = get_entry_telemetry_exporter(entry)
    if exporter is None:
        return None
    return exporter.export_snapshot()


def build_entry_telemetry_views(entry: object) -> TelemetryViews | None:
    """Build all exporter views for a config entry."""
    exporter = get_entry_telemetry_exporter(entry)
    if exporter is None:
        return None
    return exporter.export_views()


def get_entry_telemetry_view(
    entry: object,
    sink_name: str,
) -> TelemetryPayload | None:
    """Return one named telemetry sink view for a config entry."""
    views = build_entry_telemetry_views(entry)
    if views is None:
        return None
    return {
        "diagnostics": views.diagnostics,
        "system_health": views.system_health,
        "developer": views.developer,
        "ci": views.ci,
    }.get(sink_name)


def build_entry_system_health_view(entry: object) -> TelemetryPayload | None:
    """Return the system-health telemetry projection for one entry."""
    return get_entry_telemetry_view(entry, "system_health")


def build_entry_diagnostics_view(entry: object) -> TelemetryPayload | None:
    """Return the diagnostics telemetry projection for one entry."""
    return get_entry_telemetry_view(entry, "diagnostics")


__all__ = [
    "build_entry_diagnostics_view",
    "build_entry_system_health_view",
    "build_entry_telemetry_snapshot",
    "build_entry_telemetry_views",
    "get_entry_telemetry_exporter",
    "get_entry_telemetry_view",
]
