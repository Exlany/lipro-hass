"""Control-owned runtime access helpers."""

from __future__ import annotations

from collections.abc import Mapping

from homeassistant.core import HomeAssistant

from ..core.device import LiproDevice
from ..core.telemetry import RuntimeTelemetryExporter
from ..runtime_types import LiproCoordinator
from . import runtime_access_support as _support
from .models import (
    FailureSummary,
    RuntimeCoordinatorSnapshot,
    RuntimeDiagnosticsProjection,
    empty_failure_summary,
)
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
from .runtime_access_types import (
    RuntimeCoordinatorView,
    RuntimeEntryPort,
    RuntimeEntryView,
)

type RuntimeTelemetryView = dict[str, object]
type RuntimeEntryCoordinator = tuple[RuntimeEntryPort, LiproCoordinator]
type RuntimeDeviceAndCoordinator = tuple[LiproDevice, LiproCoordinator]


def build_entry_telemetry_exporter(
    entry: RuntimeEntryPort | object,
) -> RuntimeTelemetryExporter | None:
    """Return the formal runtime telemetry exporter for one config entry."""
    return _support.build_entry_telemetry_exporter_support(entry)


def build_runtime_entry_view(
    entry: RuntimeEntryPort | object,
) -> RuntimeEntryView | None:
    """Return the formal runtime-entry view for one config entry."""
    return _build_runtime_entry_view_support(entry)


def get_entry_runtime_coordinator(
    entry: RuntimeEntryPort | object,
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
    """Return the config entry that owns one active coordinator."""
    return _find_runtime_entry_for_coordinator_support(hass, coordinator)


def is_debug_mode_enabled_for_entry(entry: RuntimeEntryPort | object) -> bool:
    """Return whether one config entry explicitly opts into debug services."""
    return _is_debug_mode_enabled_for_entry_support(entry)


def has_debug_mode_runtime_entry(hass: HomeAssistant) -> bool:
    """Return True when any loaded runtime entry opts into debug mode."""
    return _has_debug_mode_runtime_entry_support(hass)


def is_developer_runtime_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the coordinator belongs to a debug-enabled entry."""
    return _is_developer_runtime_coordinator_support(hass, coordinator)


def iter_developer_runtime_coordinators(
    hass: HomeAssistant,
) -> list[LiproCoordinator]:
    """Return runtime coordinators that explicitly opted into debug mode."""
    return _iter_developer_runtime_coordinators_support(hass)


def iter_runtime_devices_for_entry(
    entry: RuntimeEntryPort | object,
) -> list[LiproDevice]:
    """Return all runtime devices for one entry through runtime_access."""
    return _iter_runtime_devices_for_entry_support(entry)


def find_runtime_device_for_entry(
    entry: RuntimeEntryPort | object,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device for an entry through runtime_access."""
    return _find_runtime_device_for_entry_support(entry, device_id)


def is_runtime_device_mapping_degraded(
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the runtime device projection is degraded."""
    return _is_runtime_device_mapping_degraded_support(coordinator)


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
