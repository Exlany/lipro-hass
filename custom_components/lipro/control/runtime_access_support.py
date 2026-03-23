"""Internal helpers backing the formal runtime_access import home."""

from __future__ import annotations

from collections.abc import Mapping
from inspect import getattr_static
from typing import TYPE_CHECKING, cast

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..core.telemetry import RuntimeTelemetryExporter
from ..core.telemetry.ports import ProtocolTelemetrySource, RuntimeTelemetrySource
from ..runtime_types import LiproCoordinator, ProtocolTelemetryFacadeLike
from .runtime_access_types import (
    RuntimeCoordinatorView,
    RuntimeEntryPort,
    RuntimeEntryView,
)

if TYPE_CHECKING:
    from ..core.device import LiproDevice


_MISSING = object()

type RuntimeEntryCoordinator = tuple[RuntimeEntryPort, LiproCoordinator]


def _get_static_member(obj: object | None, name: str) -> object:
    """Return one statically declared member without triggering dynamic fallback."""
    if obj is None:
        return _MISSING
    try:
        return getattr_static(obj, name)
    except AttributeError:
        return _MISSING


def _get_explicit_member(obj: object | None, name: str) -> object | None:
    """Return one explicitly declared instance/class member without mock-ghost probing."""
    if _get_static_member(obj, name) is _MISSING:
        return None
    try:
        return cast(object | None, getattr(obj, name))
    except AttributeError:
        return None


def _has_explicit_runtime_member(obj: object | None, name: str) -> bool:
    """Return whether a runtime-facing attribute is explicitly bound on the object."""
    return _get_static_member(obj, name) is not _MISSING


class _ProtocolFacadeTelemetrySource(ProtocolTelemetrySource):
    """Adapter exposing protocol-root telemetry through an explicit source port."""

    def __init__(self, protocol: ProtocolTelemetryFacadeLike) -> None:
        self._protocol = protocol

    def get_protocol_telemetry_snapshot(self) -> Mapping[str, object]:
        snapshot = _get_explicit_member(self._protocol, "protocol_diagnostics_snapshot")
        if callable(snapshot):
            result = snapshot()
            if isinstance(result, Mapping):
                return dict(result)
        diagnostics_context = _get_explicit_member(self._protocol, "diagnostics_context")
        context_snapshot = _get_explicit_member(diagnostics_context, "snapshot")
        if callable(context_snapshot):
            result = context_snapshot()
            if isinstance(result, Mapping):
                return dict(result)
        return {}


class _CoordinatorTelemetrySource(RuntimeTelemetrySource):
    """Adapter exposing runtime telemetry through an explicit source port."""

    def __init__(self, coordinator: RuntimeCoordinatorView, *, entry_id: str | None) -> None:
        self._coordinator = coordinator
        self._entry_id = entry_id

    def get_runtime_telemetry_snapshot(self) -> Mapping[str, object]:
        payload = dict(self._coordinator.runtime_telemetry_snapshot)
        if self._entry_id:
            return {"entry_id": self._entry_id, **payload}
        return payload



def _build_runtime_telemetry_snapshot(coordinator: LiproCoordinator) -> Mapping[str, object]:
    """Return a normalized runtime telemetry snapshot for one coordinator."""
    telemetry_service = _get_explicit_member(coordinator, "telemetry_service")
    build_snapshot = _get_explicit_member(telemetry_service, "build_snapshot")
    if callable(build_snapshot):
        snapshot = build_snapshot()
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
    return {}



def _build_runtime_coordinator_view(
    coordinator: LiproCoordinator,
) -> RuntimeCoordinatorView:
    """Build the explicit runtime read-model for one coordinator."""
    update_interval = _get_explicit_member(coordinator, "update_interval")
    last_update_success = _get_explicit_member(coordinator, "last_update_success")
    mqtt_service = _get_explicit_member(coordinator, "mqtt_service")
    mqtt_connected = _get_explicit_member(mqtt_service, "connected")
    protocol = _get_explicit_member(coordinator, "protocol")
    devices = _get_explicit_member(coordinator, "devices")

    return RuntimeCoordinatorView(
        coordinator=coordinator,
        update_interval=None if update_interval is None else str(update_interval),
        last_update_success=(
            last_update_success if isinstance(last_update_success, bool) else False
        ),
        mqtt_connected=mqtt_connected if isinstance(mqtt_connected, bool) else None,
        protocol=(
            cast(ProtocolTelemetryFacadeLike, protocol) if protocol is not None else None
        ),
        runtime_telemetry_snapshot=_build_runtime_telemetry_snapshot(coordinator),
        devices=devices if isinstance(devices, Mapping) else None,
    )



def _coerce_runtime_entry_port(entry: object) -> RuntimeEntryPort | None:
    """Return the live config entry when it exposes the runtime-entry port."""
    if not _has_explicit_runtime_member(entry, "runtime_data"):
        return None

    entry_id = _get_explicit_member(entry, "entry_id")
    options = _get_explicit_member(entry, "options")
    if not isinstance(entry_id, str) or not isinstance(options, Mapping):
        return None

    return cast(RuntimeEntryPort, entry)



def build_runtime_entry_view(
    entry: RuntimeEntryPort | object,
) -> RuntimeEntryView | None:
    """Build the typed runtime-entry read-model for control-plane consumers."""
    runtime_entry = _coerce_runtime_entry_port(entry)
    if runtime_entry is None:
        return None

    coordinator = runtime_entry.runtime_data
    return RuntimeEntryView(
        entry=runtime_entry,
        entry_id=runtime_entry.entry_id,
        options=runtime_entry.options,
        coordinator=(
            _build_runtime_coordinator_view(coordinator)
            if coordinator is not None
            else None
        ),
    )



def _build_entry_telemetry_exporter(
    entry: RuntimeEntryPort | object,
) -> RuntimeTelemetryExporter | None:
    """Build one explicit telemetry exporter for a runtime entry when available."""
    runtime_entry = build_runtime_entry_view(entry)
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



def get_entry_runtime_coordinator(
    entry: RuntimeEntryPort | object,
) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    runtime_entry = build_runtime_entry_view(entry)
    if runtime_entry is None or runtime_entry.coordinator is None:
        return None
    return runtime_entry.coordinator.coordinator



def iter_runtime_entries(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryPort]:
    """Return live Lipro config entries, optionally scoped to one entry id."""
    entries: list[RuntimeEntryPort] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime_entry = _coerce_runtime_entry_port(entry)
        if runtime_entry is None:
            continue
        if entry_id is None or runtime_entry.entry_id == entry_id:
            entries.append(runtime_entry)
    return entries



def iter_runtime_entry_views(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryView]:
    """Return typed runtime-entry read-models for active Lipro entries."""
    views: list[RuntimeEntryView] = []
    for entry in iter_runtime_entries(hass, entry_id=entry_id):
        view = build_runtime_entry_view(entry)
        if view is not None:
            views.append(view)
    return views



def iter_runtime_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[LiproCoordinator]:
    """Return loaded runtime coordinators for the Lipro domain."""
    return [
        view.coordinator.coordinator
        for view in iter_runtime_entry_views(hass, entry_id=entry_id)
        if view.coordinator is not None
    ]



def iter_runtime_entry_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryCoordinator]:
    """Return loaded runtime entry/coordinator pairs for the Lipro domain."""
    pairs: list[RuntimeEntryCoordinator] = []
    for view in iter_runtime_entry_views(hass, entry_id=entry_id):
        if view.coordinator is not None:
            pairs.append((view.entry, view.coordinator.coordinator))
    return pairs



def _call_runtime_device_getter(
    coordinator: LiproCoordinator,
    *,
    getter_name: str,
    device_id: str,
) -> LiproDevice | None:
    """Call one explicit runtime device getter without MagicMock ghost leakage."""
    getter = _get_explicit_member(coordinator, getter_name)
    if not callable(getter):
        return None

    device = cast("LiproDevice | None", getter(device_id))
    return device if device is not None else None



def get_runtime_device_mapping(
    coordinator: LiproCoordinator,
) -> Mapping[str, LiproDevice]:
    """Return a safe device mapping view for one runtime coordinator."""
    return _build_runtime_coordinator_view(coordinator).devices or {}



def find_runtime_device(
    coordinator: LiproCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device via mapping first, then explicit lookup helpers."""
    mapped_device = get_runtime_device_mapping(coordinator).get(device_id)
    if mapped_device is not None:
        return mapped_device
    for getter_name in ("get_device", "get_device_by_id"):
        device = _call_runtime_device_getter(
            coordinator,
            getter_name=getter_name,
            device_id=device_id,
        )
        if device is not None:
            return device
    return None



def find_runtime_device_and_coordinator(
    hass: HomeAssistant,
    *,
    device_id: str,
    entry_id: str | None = None,
) -> tuple[LiproDevice, LiproCoordinator] | None:
    """Return the runtime device plus owning coordinator when available."""
    for _entry, coordinator in iter_runtime_entry_coordinators(hass, entry_id=entry_id):
        device = find_runtime_device(coordinator, device_id)
        if device is not None:
            return device, coordinator
    return None



def find_runtime_entry_for_coordinator(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> RuntimeEntryPort | None:
    """Return the config entry that owns one active coordinator."""
    config_entry = _get_explicit_member(coordinator, "config_entry")
    runtime_entry = build_runtime_entry_view(config_entry)
    if runtime_entry is not None and runtime_entry.coordinator is not None:
        if runtime_entry.coordinator.coordinator is coordinator:
            return runtime_entry.entry
    for entry in iter_runtime_entries(hass):
        if get_entry_runtime_coordinator(entry) is coordinator:
            return entry
    return None



def is_debug_mode_enabled_for_entry(entry: RuntimeEntryPort | object) -> bool:
    """Return whether one config entry explicitly opts into debug services."""
    runtime_entry = build_runtime_entry_view(entry)
    if runtime_entry is None:
        return DEFAULT_DEBUG_MODE
    return bool(runtime_entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE))



def has_debug_mode_runtime_entry(hass: HomeAssistant) -> bool:
    """Return True when any loaded runtime entry opts into debug mode."""
    return any(
        is_debug_mode_enabled_for_entry(view.entry)
        and view.coordinator is not None
        for view in iter_runtime_entry_views(hass)
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
        view.coordinator.coordinator
        for view in iter_runtime_entry_views(hass)
        if view.coordinator is not None and is_debug_mode_enabled_for_entry(view.entry)
    ]



def iter_runtime_devices_for_entry(
    entry: RuntimeEntryPort | object,
) -> list[LiproDevice]:
    """Return all runtime devices for one entry through the formal helper surface."""
    runtime_entry = build_runtime_entry_view(entry)
    if runtime_entry is None or runtime_entry.coordinator is None:
        return []
    return list((runtime_entry.coordinator.devices or {}).values())



def find_runtime_device_for_entry(
    entry: RuntimeEntryPort | object,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device for an entry through the formal helper surface."""
    coordinator = get_entry_runtime_coordinator(entry)
    if coordinator is None:
        return None
    return find_runtime_device(coordinator, device_id)



def is_runtime_device_mapping_degraded(
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the runtime device projection is degraded for one coordinator."""
    return _build_runtime_coordinator_view(coordinator).devices is None
