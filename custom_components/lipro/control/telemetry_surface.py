"""Control-plane bridge for runtime telemetry exporting."""

from __future__ import annotations

from ..core.telemetry import RuntimeTelemetryExporter, TelemetrySnapshot, TelemetryViews
from ..core.telemetry.models import (
    DiagnosticsTelemetryView,
    SystemHealthTelemetryView,
    TelemetrySinkPayload,
)
from .runtime_access import build_entry_telemetry_exporter


def get_entry_telemetry_exporter(entry: object) -> RuntimeTelemetryExporter | None:
    """Return a telemetry exporter for one config entry, when available."""
    return build_entry_telemetry_exporter(entry)


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


def _select_telemetry_view(
    views: TelemetryViews,
    sink_name: str,
) -> TelemetrySinkPayload | None:
    """Return one named telemetry sink from an exported view bundle."""
    if sink_name == "diagnostics":
        return views.diagnostics
    if sink_name == "system_health":
        return views.system_health
    if sink_name == "developer":
        return views.developer
    if sink_name == "ci":
        return views.ci
    return None


def get_entry_telemetry_view(
    entry: object,
    sink_name: str,
) -> TelemetrySinkPayload | None:
    """Return one named telemetry sink view for a config entry."""
    views = build_entry_telemetry_views(entry)
    if views is None:
        return None
    return _select_telemetry_view(views, sink_name)


def build_entry_system_health_view(entry: object) -> SystemHealthTelemetryView | None:
    """Return the system-health telemetry projection for one entry."""
    views = build_entry_telemetry_views(entry)
    if views is None:
        return None
    return views.system_health


def build_entry_diagnostics_view(entry: object) -> DiagnosticsTelemetryView | None:
    """Return the diagnostics telemetry projection for one entry."""
    views = build_entry_telemetry_views(entry)
    if views is None:
        return None
    return views.diagnostics


__all__ = [
    "build_entry_diagnostics_view",
    "build_entry_system_health_view",
    "build_entry_telemetry_snapshot",
    "build_entry_telemetry_views",
    "get_entry_telemetry_exporter",
    "get_entry_telemetry_view",
]
