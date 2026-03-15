"""Control-plane bridge for runtime telemetry exporting."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from ..core.telemetry import RuntimeTelemetryExporter, TelemetrySnapshot, TelemetryViews
from ..core.telemetry.ports import ProtocolTelemetrySource, RuntimeTelemetrySource
from .runtime_access import get_entry_runtime_coordinator

type TelemetryPayload = dict[str, object]


def _get_explicit_attr(obj: object | None, name: str) -> object | None:
    """Return one explicitly bound attribute without triggering MagicMock ghosts."""
    if obj is None:
        return None
    obj_dict = getattr(obj, "__dict__", None)
    if isinstance(obj_dict, dict):
        if name in obj_dict:
            return cast(object, obj_dict[name])
        descriptor = vars(type(obj)).get(name)
        if descriptor is not None:
            return cast(object | None, getattr(obj, name, None))
        return None
    return cast(object | None, getattr(obj, name, None))


class _ProtocolFacadeTelemetrySource(ProtocolTelemetrySource):
    """Adapter exposing protocol-root telemetry as a source port."""

    def __init__(self, protocol: object) -> None:
        self._protocol = protocol

    def get_protocol_telemetry_snapshot(self) -> Mapping[str, object]:
        """Return the current protocol diagnostics snapshot."""
        snapshot = _get_explicit_attr(self._protocol, "protocol_diagnostics_snapshot")
        if callable(snapshot):
            result = snapshot()
            if isinstance(result, Mapping):
                return dict(result)
        diagnostics_context = _get_explicit_attr(self._protocol, "diagnostics_context")
        context_snapshot = _get_explicit_attr(diagnostics_context, "snapshot")
        if callable(context_snapshot):
            result = context_snapshot()
            if isinstance(result, Mapping):
                return dict(result)
        return {}


class _CoordinatorTelemetrySource(RuntimeTelemetrySource):
    """Adapter exposing coordinator runtime telemetry as a source port."""

    def __init__(self, coordinator: object, *, entry_id: str | None) -> None:
        self._coordinator = coordinator
        self._entry_id = entry_id

    def get_runtime_telemetry_snapshot(self) -> Mapping[str, object]:
        """Return the current runtime telemetry snapshot."""
        telemetry_service = _get_explicit_attr(self._coordinator, "telemetry_service")
        build_snapshot = _get_explicit_attr(telemetry_service, "build_snapshot")
        if callable(build_snapshot):
            snapshot = build_snapshot()
            if isinstance(snapshot, Mapping):
                payload = dict(snapshot)
                if self._entry_id:
                    return {"entry_id": self._entry_id, **payload}
                return payload
        return {"entry_id": self._entry_id} if self._entry_id else {}


def get_entry_telemetry_exporter(entry: object) -> RuntimeTelemetryExporter | None:
    """Return a telemetry exporter for one config entry, when available."""
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return None
    protocol = _get_explicit_attr(coordinator, "client")
    if protocol is None:
        return None
    return RuntimeTelemetryExporter(
        protocol_source=_ProtocolFacadeTelemetrySource(protocol),
        runtime_source=_CoordinatorTelemetrySource(
            coordinator,
            entry_id=str(getattr(entry, "entry_id", "")) or None,
        ),
    )


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
