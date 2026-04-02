"""Control-owned runtime access helpers."""

from __future__ import annotations

from collections.abc import Mapping

from homeassistant.core import HomeAssistant

from ..core.device import LiproDevice
from ..core.telemetry import RuntimeTelemetryExporter
from ..core.telemetry.models import SystemHealthTelemetryView
from ..runtime_types import LiproCoordinator
from . import runtime_access_support as _support
from .models import RuntimeCoordinatorSnapshot, RuntimeDiagnosticsProjection
from .runtime_access_support import (
    _build_runtime_entry_view_support,
    _find_runtime_device_and_coordinator_support,
    _find_runtime_device_for_entry_support,
    _find_runtime_device_support,
    _find_runtime_entry_for_coordinator_support,
    _get_entry_runtime_coordinator_support,
    _get_runtime_device_mapping_support,
    _has_debug_mode_runtime_entry_support,
    _is_debug_mode_enabled_for_entry_support,
    _is_developer_runtime_coordinator_support,
    _is_runtime_device_mapping_degraded_support,
    _iter_developer_runtime_coordinators_support,
    _iter_runtime_coordinators_support,
    _iter_runtime_devices_for_entry_support,
    _iter_runtime_entries_support,
    _iter_runtime_entry_coordinators_support,
    _iter_runtime_entry_views_support,
)
from .runtime_access_types import RuntimeEntryPort, RuntimeEntryView

type RuntimeEntryLike = RuntimeEntryView | RuntimeEntryPort | object
type RuntimeEntryCoordinator = tuple[RuntimeEntryPort, LiproCoordinator]
type RuntimeDeviceAndCoordinator = tuple[LiproDevice, LiproCoordinator]


def _build_entry_telemetry_exporter_from_view(
    runtime_entry: RuntimeEntryView | None,
) -> RuntimeTelemetryExporter | None:
    return _support.build_entry_telemetry_exporter_from_view_support(runtime_entry)


def build_entry_telemetry_exporter(
    entry: RuntimeEntryLike,
) -> RuntimeTelemetryExporter | None:
    """Return the formal runtime telemetry exporter for one config entry."""
    runtime_entry = entry if isinstance(entry, RuntimeEntryView) else build_runtime_entry_view(entry)
    return _build_entry_telemetry_exporter_from_view(runtime_entry)


def build_runtime_entry_view(
    entry: RuntimeEntryLike,
) -> RuntimeEntryView | None:
    """Return the formal runtime-entry view for one config entry."""
    return _build_runtime_entry_view_support(entry)


def get_entry_runtime_coordinator(
    entry: RuntimeEntryLike,
) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    return _get_entry_runtime_coordinator_support(entry)


def iter_runtime_entries(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryPort]:
    """Return live Lipro runtime entries, optionally scoped to one entry id."""
    return _iter_runtime_entries_support(hass, entry_id=entry_id)


def iter_runtime_entry_views(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryView]:
    """Return runtime-entry read-models for active Lipro entries."""
    return _iter_runtime_entry_views_support(hass, entry_id=entry_id)


def iter_runtime_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[LiproCoordinator]:
    """Return loaded runtime coordinators for the Lipro domain."""
    return _iter_runtime_coordinators_support(hass, entry_id=entry_id)


def iter_runtime_entry_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryCoordinator]:
    """Return loaded runtime entry/coordinator pairs for the Lipro domain."""
    return _iter_runtime_entry_coordinators_support(hass, entry_id=entry_id)


def get_runtime_device_mapping(
    coordinator: LiproCoordinator,
) -> Mapping[str, LiproDevice]:
    """Return a safe device mapping view for one runtime coordinator."""
    return _get_runtime_device_mapping_support(coordinator)


def find_runtime_device(
    coordinator: LiproCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device via the formal runtime-access surface."""
    return _find_runtime_device_support(coordinator, device_id)


def find_runtime_device_and_coordinator(
    hass: HomeAssistant,
    *,
    device_id: str,
    entry_id: str | None = None,
) -> RuntimeDeviceAndCoordinator | None:
    """Return the runtime device plus owning coordinator when available."""
    return _find_runtime_device_and_coordinator_support(
        hass,
        device_id=device_id,
        entry_id=entry_id,
    )


def find_runtime_entry_for_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> RuntimeEntryPort | None:
    """Return the owning config entry for one runtime coordinator."""
    return _find_runtime_entry_for_coordinator_support(hass, coordinator)


def find_runtime_device_for_entry(
    entry: RuntimeEntryLike,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device for one config entry when available."""
    return _find_runtime_device_for_entry_support(entry, device_id)


def iter_runtime_devices_for_entry(entry: RuntimeEntryLike) -> list[LiproDevice]:
    """Return runtime devices for one config entry when loaded."""
    return _iter_runtime_devices_for_entry_support(entry)


def iter_developer_runtime_coordinators(hass: HomeAssistant) -> list[LiproCoordinator]:
    """Return runtime coordinators for entries flagged as developer/debug."""
    return _iter_developer_runtime_coordinators_support(hass)


def has_debug_mode_runtime_entry(hass: HomeAssistant) -> bool:
    """Return whether any loaded runtime entry explicitly enables debug mode."""
    return _has_debug_mode_runtime_entry_support(hass)


def is_debug_mode_enabled_for_entry(entry: RuntimeEntryLike) -> bool:
    """Return whether debug mode is enabled for one runtime entry."""
    return _is_debug_mode_enabled_for_entry_support(entry)


def is_developer_runtime_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether one runtime coordinator belongs to a developer/debug entry."""
    return _is_developer_runtime_coordinator_support(hass, coordinator)


def is_runtime_device_mapping_degraded(
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the runtime device projection is degraded."""
    return _is_runtime_device_mapping_degraded_support(coordinator)


def build_entry_system_health_view(
    entry: RuntimeEntryLike,
) -> SystemHealthTelemetryView | None:
    """Return the control-plane system-health projection for one config entry."""
    runtime_entry = entry if isinstance(entry, RuntimeEntryView) else build_runtime_entry_view(entry)
    return _support.build_entry_system_health_view_from_view_support(runtime_entry)


def build_runtime_snapshot(
    entry: RuntimeEntryLike,
) -> RuntimeCoordinatorSnapshot | None:
    """Build one control-plane runtime snapshot from a config entry."""
    runtime_entry = entry if isinstance(entry, RuntimeEntryView) else build_runtime_entry_view(entry)
    return _support.build_runtime_snapshot_from_view_support(runtime_entry)


def build_runtime_diagnostics_projection(
    entry: RuntimeEntryLike,
) -> RuntimeDiagnosticsProjection | None:
    """Build the typed diagnostics-facing runtime projection for one config entry."""
    runtime_entry = entry if isinstance(entry, RuntimeEntryView) else build_runtime_entry_view(entry)
    return _support.build_runtime_diagnostics_projection_from_view_support(runtime_entry)


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
