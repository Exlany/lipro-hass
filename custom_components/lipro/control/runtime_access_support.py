"""Internal helpers backing the formal runtime_access import home."""

from __future__ import annotations

from collections.abc import Mapping
from inspect import getattr_static
from typing import TYPE_CHECKING, cast

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..core.telemetry import RuntimeTelemetryExporter
from ..core.telemetry.models import TelemetryJsonValue, TelemetrySourcePayload
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


def _get_explicit_bool_member(obj: object | None, name: str) -> bool | None:
    """Return one explicit bool member when present and correctly typed."""
    value = _get_explicit_member(obj, name)
    return value if isinstance(value, bool) else None


def _get_explicit_mapping_member(
    obj: object | None,
    name: str,
) -> Mapping[str, object] | None:
    """Return one explicit mapping member when present and correctly typed."""
    value = _get_explicit_member(obj, name)
    return value if isinstance(value, Mapping) else None


def _coerce_telemetry_json_value(value: object) -> TelemetryJsonValue | None:
    """Return one telemetry-safe JSON value when the object already matches the exporter contract."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        result: list[TelemetryJsonValue] = []
        for item in value:
            normalized = _coerce_telemetry_json_value(item)
            if normalized is None and item is not None:
                return None
            result.append(normalized)
        return result
    if isinstance(value, Mapping):
        return _coerce_telemetry_source_payload(value)
    return None


def _coerce_telemetry_source_payload(
    payload: Mapping[str, object],
) -> TelemetrySourcePayload:
    """Return a telemetry-source payload narrowed to JSON-safe exporter values."""
    normalized: TelemetrySourcePayload = {}
    for key, value in payload.items():
        normalized_value = _coerce_telemetry_json_value(value)
        if normalized_value is not None or value is None:
            normalized[str(key)] = normalized_value
    return normalized


class _ProtocolFacadeTelemetrySource(ProtocolTelemetrySource):
    """Adapter exposing protocol-root telemetry through an explicit source port."""

    def __init__(self, protocol: ProtocolTelemetryFacadeLike) -> None:
        self._protocol = protocol

    def get_protocol_telemetry_snapshot(self) -> TelemetrySourcePayload:
        snapshot = _get_explicit_member(self._protocol, "protocol_diagnostics_snapshot")
        if callable(snapshot):
            result = snapshot()
            if isinstance(result, Mapping):
                return _coerce_telemetry_source_payload(result)
        diagnostics_context = _get_explicit_member(self._protocol, "diagnostics_context")
        context_snapshot = _get_explicit_member(diagnostics_context, "snapshot")
        if callable(context_snapshot):
            result = context_snapshot()
            if isinstance(result, Mapping):
                return _coerce_telemetry_source_payload(result)
        return {}


class _CoordinatorTelemetrySource(RuntimeTelemetrySource):
    """Adapter exposing runtime telemetry through an explicit source port."""

    def __init__(self, coordinator: RuntimeCoordinatorView, *, entry_id: str | None) -> None:
        self._coordinator = coordinator
        self._entry_id = entry_id

    def get_runtime_telemetry_snapshot(self) -> TelemetrySourcePayload:
        payload = _coerce_telemetry_source_payload(
            self._coordinator.runtime_telemetry_snapshot
        )
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
    last_update_success = _get_explicit_bool_member(coordinator, "last_update_success")
    mqtt_service = _get_explicit_member(coordinator, "mqtt_service")
    mqtt_connected = _get_explicit_bool_member(mqtt_service, "connected")
    protocol = _get_explicit_member(coordinator, "protocol")
    devices = _get_explicit_mapping_member(coordinator, "devices")

    return RuntimeCoordinatorView(
        coordinator=coordinator,
        update_interval=None if update_interval is None else str(update_interval),
        last_update_success=last_update_success or False,
        mqtt_connected=mqtt_connected,
        protocol=(
            cast(ProtocolTelemetryFacadeLike, protocol) if protocol is not None else None
        ),
        runtime_telemetry_snapshot=_build_runtime_telemetry_snapshot(coordinator),
        devices=cast("Mapping[str, LiproDevice] | None", devices),
    )


def _build_runtime_entry_coordinator(
    runtime_entry: RuntimeEntryPort,
) -> RuntimeCoordinatorView | None:
    """Build the coordinator projection owned by one runtime entry."""
    coordinator = runtime_entry.runtime_data
    if coordinator is None:
        return None
    return _build_runtime_coordinator_view(coordinator)



def _coerce_runtime_entry_port(entry: object) -> RuntimeEntryPort | None:
    """Return the live config entry when it exposes the runtime-entry port."""
    if not _has_explicit_runtime_member(entry, "runtime_data"):
        return None

    entry_id = _get_explicit_member(entry, "entry_id")
    options = _get_explicit_member(entry, "options")
    if not isinstance(entry_id, str) or not isinstance(options, Mapping):
        return None

    return cast(RuntimeEntryPort, entry)



def _build_runtime_entry_view_support(
    entry: RuntimeEntryPort | object,
) -> RuntimeEntryView | None:
    """Build the typed runtime-entry read-model for control-plane consumers."""
    runtime_entry = _coerce_runtime_entry_port(entry)
    if runtime_entry is None:
        return None

    return RuntimeEntryView(
        entry=runtime_entry,
        entry_id=runtime_entry.entry_id,
        options=runtime_entry.options,
        coordinator=_build_runtime_entry_coordinator(runtime_entry),
    )



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



def _get_entry_runtime_coordinator_support(
    entry: RuntimeEntryPort | object,
) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    runtime_entry = _build_runtime_entry_view_support(entry)
    if runtime_entry is None or runtime_entry.coordinator is None:
        return None
    return runtime_entry.coordinator.coordinator



def _iter_runtime_entries_support(
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



def _iter_runtime_entry_views_support(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryView]:
    """Return typed runtime-entry read-models for active Lipro entries."""
    views: list[RuntimeEntryView] = []
    for entry in _iter_runtime_entries_support(hass, entry_id=entry_id):
        view = _build_runtime_entry_view_support(entry)
        if view is not None:
            views.append(view)
    return views



def _iter_runtime_coordinators_support(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[LiproCoordinator]:
    """Return loaded runtime coordinators for the Lipro domain."""
    return [
        view.coordinator.coordinator
        for view in _iter_runtime_entry_views_support(hass, entry_id=entry_id)
        if view.coordinator is not None
    ]


def _build_runtime_entry_coordinator_pair(
    view: RuntimeEntryView,
) -> RuntimeEntryCoordinator | None:
    """Return the live entry/coordinator pair for one runtime view."""
    if view.coordinator is None:
        return None
    return view.entry, view.coordinator.coordinator



def _iter_runtime_entry_coordinators_support(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryCoordinator]:
    """Return loaded runtime entry/coordinator pairs for the Lipro domain."""
    pairs: list[RuntimeEntryCoordinator] = []
    for view in _iter_runtime_entry_views_support(hass, entry_id=entry_id):
        pair = _build_runtime_entry_coordinator_pair(view)
        if pair is not None:
            pairs.append(pair)
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


def _find_runtime_device_in_mapping(
    coordinator: LiproCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device from the explicit coordinator mapping."""
    return _get_runtime_device_mapping_support(coordinator).get(device_id)


def _find_runtime_device_via_explicit_getters(
    coordinator: LiproCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device via explicit coordinator lookup helpers."""
    for getter_name in ("get_device", "get_device_by_id"):
        device = _call_runtime_device_getter(
            coordinator,
            getter_name=getter_name,
            device_id=device_id,
        )
        if device is not None:
            return device
    return None



def _get_runtime_device_mapping_support(
    coordinator: LiproCoordinator,
) -> Mapping[str, LiproDevice]:
    """Return a safe device mapping view for one runtime coordinator."""
    return _build_runtime_coordinator_view(coordinator).devices or {}



def _find_runtime_device_support(
    coordinator: LiproCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device via mapping first, then explicit lookup helpers."""
    mapped_device = _find_runtime_device_in_mapping(coordinator, device_id)
    if mapped_device is not None:
        return mapped_device
    return _find_runtime_device_via_explicit_getters(coordinator, device_id)



def _find_runtime_device_and_coordinator_support(
    hass: HomeAssistant,
    *,
    device_id: str,
    entry_id: str | None = None,
) -> tuple[LiproDevice, LiproCoordinator] | None:
    """Return the runtime device plus owning coordinator when available."""
    for _entry, coordinator in _iter_runtime_entry_coordinators_support(hass, entry_id=entry_id):
        device = _find_runtime_device_support(coordinator, device_id)
        if device is not None:
            return device, coordinator
    return None



def _find_runtime_entry_for_coordinator_support(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> RuntimeEntryPort | None:
    """Return the config entry that owns one active coordinator."""
    config_entry = _get_explicit_member(coordinator, "config_entry")
    runtime_entry = _build_runtime_entry_view_support(config_entry)
    if runtime_entry is not None and runtime_entry.coordinator is not None:
        if runtime_entry.coordinator.coordinator is coordinator:
            return runtime_entry.entry
    for entry in _iter_runtime_entries_support(hass):
        if _get_entry_runtime_coordinator_support(entry) is coordinator:
            return entry
    return None



def _is_debug_mode_enabled_for_entry_support(entry: RuntimeEntryPort | object) -> bool:
    """Return whether one config entry explicitly opts into debug services."""
    runtime_entry = _build_runtime_entry_view_support(entry)
    if runtime_entry is None:
        return DEFAULT_DEBUG_MODE
    return bool(runtime_entry.options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE))



def _has_debug_mode_runtime_entry_support(hass: HomeAssistant) -> bool:
    """Return True when any loaded runtime entry opts into debug mode."""
    return any(
        _is_debug_mode_enabled_for_entry_support(view.entry)
        and view.coordinator is not None
        for view in _iter_runtime_entry_views_support(hass)
    )



def _is_developer_runtime_coordinator_support(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the coordinator belongs to a debug-enabled entry."""
    entry = _find_runtime_entry_for_coordinator_support(hass, coordinator)
    return entry is not None and _is_debug_mode_enabled_for_entry_support(entry)



def _iter_developer_runtime_coordinators_support(hass: HomeAssistant) -> list[LiproCoordinator]:
    """Return runtime coordinators that explicitly opted into debug mode."""
    return [
        view.coordinator.coordinator
        for view in _iter_runtime_entry_views_support(hass)
        if view.coordinator is not None and _is_debug_mode_enabled_for_entry_support(view.entry)
    ]



def _iter_runtime_devices_for_entry_support(
    entry: RuntimeEntryPort | object,
) -> list[LiproDevice]:
    """Return all runtime devices for one entry through the formal helper surface."""
    runtime_entry = _build_runtime_entry_view_support(entry)
    if runtime_entry is None or runtime_entry.coordinator is None:
        return []
    return list((runtime_entry.coordinator.devices or {}).values())



def _find_runtime_device_for_entry_support(
    entry: RuntimeEntryPort | object,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device for an entry through the formal helper surface."""
    coordinator = _get_entry_runtime_coordinator_support(entry)
    if coordinator is None:
        return None
    return _find_runtime_device_support(coordinator, device_id)



def _is_runtime_device_mapping_degraded_support(
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the runtime device projection is degraded for one coordinator."""
    return _build_runtime_coordinator_view(coordinator).devices is None
