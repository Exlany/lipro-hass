"""Control-owned runtime access helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..runtime_types import LiproCoordinator

if TYPE_CHECKING:
    from ..core.device import LiproDevice
from .models import RuntimeCoordinatorSnapshot

type RuntimeTelemetryView = dict[str, object]


def _as_runtime_entry(entry: object) -> RuntimeEntryLike | None:
    """Return a runtime-entry view when the object exposes the required fields."""
    entry_id = getattr(entry, "entry_id", None)
    if not hasattr(entry, "runtime_data"):
        return None
    if not isinstance(entry_id, str):
        obj_dict = getattr(entry, "__dict__", None)
        if not isinstance(obj_dict, dict):
            return None
        obj_dict["entry_id"] = ""

    options = getattr(entry, "options", None)
    if not isinstance(options, Mapping):
        obj_dict = getattr(entry, "__dict__", None)
        if not isinstance(obj_dict, dict):
            return None
        obj_dict["options"] = {}
        options = getattr(entry, "options", None)
        if not isinstance(options, Mapping):
            return None

    return cast(RuntimeEntryLike, entry)


class RuntimeEntryLike(Protocol):
    """Minimal config-entry surface consumed by control runtime access."""

    entry_id: str
    runtime_data: LiproCoordinator | None
    options: Mapping[str, object]


@runtime_checkable
class _MqttServiceLike(Protocol):
    """Minimal MQTT service surface needed for snapshots."""

    connected: bool


def get_entry_runtime_coordinator(
    entry: RuntimeEntryLike | object,
) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    runtime_entry = _as_runtime_entry(entry)
    if runtime_entry is None:
        return None
    return runtime_entry.runtime_data


def iter_runtime_entries(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryLike]:
    """Return Lipro config entries, optionally scoped to one entry id."""
    entries: list[RuntimeEntryLike] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime_entry = _as_runtime_entry(entry)
        if runtime_entry is None:
            continue
        if entry_id is None or runtime_entry.entry_id == entry_id:
            entries.append(runtime_entry)
    return entries


def iter_runtime_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[LiproCoordinator]:
    """Return loaded runtime coordinators for the Lipro domain."""
    coordinators: list[LiproCoordinator] = []
    for entry in iter_runtime_entries(hass, entry_id=entry_id):
        coordinator = get_entry_runtime_coordinator(entry)
        if coordinator is not None:
            coordinators.append(coordinator)
    return coordinators


def find_runtime_entry_for_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> RuntimeEntryLike | None:
    """Return the config entry that owns one active coordinator."""
    config_entry = coordinator.config_entry
    runtime_entry = _as_runtime_entry(config_entry)
    if runtime_entry is not None:
        if get_entry_runtime_coordinator(runtime_entry) is coordinator:
            return runtime_entry
    for entry in iter_runtime_entries(hass):
        if get_entry_runtime_coordinator(entry) is coordinator:
            return entry
    return None


def is_debug_mode_enabled_for_entry(entry: RuntimeEntryLike | object) -> bool:
    """Return whether one config entry explicitly opts into debug services."""
    runtime_entry = _as_runtime_entry(entry)
    if runtime_entry is None:
        return DEFAULT_DEBUG_MODE
    return bool(runtime_entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE))


def has_debug_mode_runtime_entry(hass: HomeAssistant) -> bool:
    """Return True when any loaded runtime entry opts into debug mode."""
    return any(
        is_debug_mode_enabled_for_entry(entry)
        and get_entry_runtime_coordinator(entry) is not None
        for entry in iter_runtime_entries(hass)
    )


def is_developer_runtime_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the coordinator belongs to a debug-enabled entry."""
    entry = find_runtime_entry_for_coordinator(hass, coordinator)
    return entry is not None and is_debug_mode_enabled_for_entry(entry)


def iter_developer_runtime_coordinators(hass: HomeAssistant) -> list[LiproCoordinator]:
    """Return runtime coordinators that explicitly opted into debug mode."""
    return [
        coordinator
        for coordinator in iter_runtime_coordinators(hass)
        if is_developer_runtime_coordinator(hass, coordinator)
    ]


def build_entry_system_health_view(
    entry: RuntimeEntryLike | object,
) -> RuntimeTelemetryView:
    """Return the control-plane system-health projection for one config entry."""
    runtime_entry = _as_runtime_entry(entry)
    if runtime_entry is None:
        return {}

    from .telemetry_surface import (  # noqa: PLC0415
        build_entry_system_health_view as _build_entry_system_health_view,
    )

    view = _build_entry_system_health_view(runtime_entry)
    return dict(view) if isinstance(view, Mapping) else {}


def get_runtime_device_mapping(coordinator: LiproCoordinator) -> Mapping[str, LiproDevice]:
    """Return a safe device mapping view for one runtime coordinator."""
    devices = coordinator.devices
    return devices if isinstance(devices, Mapping) else {}


def _coerce_device_count(
    telemetry_view: RuntimeTelemetryView,
    coordinator: LiproCoordinator,
) -> int:
    device_count = telemetry_view.get("device_count")
    if isinstance(device_count, int):
        return device_count
    return len(get_runtime_device_mapping(coordinator))


def _coerce_mqtt_connected(
    telemetry_view: RuntimeTelemetryView,
    coordinator: LiproCoordinator,
) -> bool | None:
    mqtt_connected = telemetry_view.get("mqtt_connected")
    if isinstance(mqtt_connected, bool):
        return mqtt_connected
    mqtt_service = getattr(coordinator, "mqtt_service", None)
    if not isinstance(mqtt_service, _MqttServiceLike):
        return None
    connected = mqtt_service.connected
    return connected if isinstance(connected, bool) else None


def _coerce_last_update_success(
    telemetry_view: RuntimeTelemetryView,
    coordinator: LiproCoordinator,
) -> bool:
    last_update_success = telemetry_view.get("last_update_success")
    if isinstance(last_update_success, bool):
        return last_update_success
    return coordinator.last_update_success


def build_runtime_snapshot(
    entry: RuntimeEntryLike | object,
) -> RuntimeCoordinatorSnapshot | None:
    """Build one control-plane runtime snapshot from a config entry."""
    runtime_entry = _as_runtime_entry(entry)
    if runtime_entry is None:
        return None

    coordinator = get_entry_runtime_coordinator(runtime_entry)
    if coordinator is None:
        return None

    telemetry_view = build_entry_system_health_view(runtime_entry)
    if not runtime_entry.entry_id:
        return None

    return RuntimeCoordinatorSnapshot(
        entry_id=runtime_entry.entry_id,
        coordinator=coordinator,
        device_count=_coerce_device_count(telemetry_view, coordinator),
        last_update_success=_coerce_last_update_success(telemetry_view, coordinator),
        mqtt_connected=_coerce_mqtt_connected(telemetry_view, coordinator),
    )


def build_runtime_snapshots(hass: HomeAssistant) -> list[RuntimeCoordinatorSnapshot]:
    """Build runtime snapshots for all active Lipro entries."""
    snapshots: list[RuntimeCoordinatorSnapshot] = []
    for entry in iter_runtime_entries(hass):
        snapshot = build_runtime_snapshot(entry)
        if snapshot is not None:
            snapshots.append(snapshot)
    return snapshots
