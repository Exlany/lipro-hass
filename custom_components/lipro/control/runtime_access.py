"""Control-owned runtime access helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, cast, runtime_checkable

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from ..core.telemetry import RuntimeTelemetryExporter
from ..core.telemetry.ports import ProtocolTelemetrySource, RuntimeTelemetrySource
from ..runtime_types import LiproCoordinator, ProtocolTelemetryFacadeLike

if TYPE_CHECKING:
    from ..core.device import LiproDevice
from .models import FailureSummary, RuntimeCoordinatorSnapshot, empty_failure_summary

type RuntimeTelemetryView = dict[str, object]


def _get_explicit_member(obj: object | None, name: str) -> object | None:
    """Return one explicitly bound member without triggering MagicMock ghosts."""
    if obj is None:
        return None
    obj_dict = getattr(obj, "__dict__", None)
    if isinstance(obj_dict, dict):
        if name in obj_dict:
            return cast(object, obj_dict[name])
        mock_children = obj_dict.get("_mock_children")
        if isinstance(mock_children, dict) and name in mock_children:
            return cast(object, mock_children[name])
        descriptor = vars(type(obj)).get(name)
        if descriptor is not None:
            return cast(object | None, getattr(obj, name, None))
        return None
    return cast(object | None, getattr(obj, name, None))


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

    def __init__(self, coordinator: LiproCoordinator, *, entry_id: str | None) -> None:
        self._coordinator = coordinator
        self._entry_id = entry_id

    def get_runtime_telemetry_snapshot(self) -> Mapping[str, object]:
        telemetry_service = _get_explicit_member(self._coordinator, "telemetry_service")
        build_snapshot = _get_explicit_member(telemetry_service, "build_snapshot")
        if callable(build_snapshot):
            snapshot = build_snapshot()
            if isinstance(snapshot, Mapping):
                payload = dict(snapshot)
                if self._entry_id:
                    return {"entry_id": self._entry_id, **payload}
                return payload
        return {"entry_id": self._entry_id} if self._entry_id else {}


def _build_entry_telemetry_exporter(
    entry: RuntimeEntryLike | object,
) -> RuntimeTelemetryExporter | None:
    """Build one explicit telemetry exporter for a runtime entry when available."""
    runtime_entry = _coerce_runtime_entry_view(entry)
    if runtime_entry is None:
        return None

    coordinator = get_entry_runtime_coordinator(runtime_entry)
    if coordinator is None:
        return None

    protocol = _get_explicit_member(coordinator, "protocol")
    if protocol is None:
        return None

    return RuntimeTelemetryExporter(
        protocol_source=_ProtocolFacadeTelemetrySource(
            cast(ProtocolTelemetryFacadeLike, protocol)
        ),
        runtime_source=_CoordinatorTelemetrySource(
            coordinator,
            entry_id=runtime_entry.entry_id or None,
        ),
    )


def _coerce_runtime_entry_view(entry: object) -> RuntimeEntryLike | None:
    """Return the live config entry when it exposes the formal runtime shape."""
    if not hasattr(entry, "runtime_data"):
        return None

    entry_id = getattr(entry, "entry_id", None)
    options = getattr(entry, "options", None)
    if not isinstance(entry_id, str) or not isinstance(options, Mapping):
        return None

    return cast(RuntimeEntryLike, entry)


class RuntimeEntryLike(Protocol):
    """Minimal config-entry surface consumed by control runtime access."""

    entry_id: str
    runtime_data: LiproCoordinator | None
    options: Mapping[str, object]


type RuntimeEntryCoordinator = tuple[RuntimeEntryLike, LiproCoordinator]


@runtime_checkable
class _MqttServiceLike(Protocol):
    """Minimal MQTT service surface needed for snapshots."""

    connected: bool


def get_entry_runtime_coordinator(
    entry: RuntimeEntryLike | object,
) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    runtime_entry = _coerce_runtime_entry_view(entry)
    if runtime_entry is None:
        return None
    return runtime_entry.runtime_data


def iter_runtime_entries(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryLike]:
    """Return live Lipro config entries, optionally scoped to one entry id."""
    entries: list[RuntimeEntryLike] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime_entry = _coerce_runtime_entry_view(entry)
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


def iter_runtime_entry_coordinators(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryCoordinator]:
    """Return loaded runtime entry/coordinator pairs for the Lipro domain."""
    pairs: list[RuntimeEntryCoordinator] = []
    for entry in iter_runtime_entries(hass, entry_id=entry_id):
        coordinator = get_entry_runtime_coordinator(entry)
        if coordinator is not None:
            pairs.append((entry, coordinator))
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


def find_runtime_device(
    coordinator: LiproCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device via formal lookup helpers or mapping fallback."""
    for getter_name in ("get_device", "get_device_by_id"):
        device = _call_runtime_device_getter(
            coordinator,
            getter_name=getter_name,
            device_id=device_id,
        )
        if device is not None:
            return device
    return get_runtime_device_mapping(coordinator).get(device_id)


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
) -> RuntimeEntryLike | None:
    """Return the config entry that owns one active coordinator."""
    config_entry = coordinator.config_entry
    runtime_entry = _coerce_runtime_entry_view(config_entry)
    if runtime_entry is not None and get_entry_runtime_coordinator(config_entry) is coordinator:
        return runtime_entry
    for entry in iter_runtime_entries(hass):
        if get_entry_runtime_coordinator(entry) is coordinator:
            return entry
    return None


def is_debug_mode_enabled_for_entry(entry: RuntimeEntryLike | object) -> bool:
    """Return whether one config entry explicitly opts into debug services."""
    runtime_entry = _coerce_runtime_entry_view(entry)
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
    exporter = _build_entry_telemetry_exporter(entry)
    if exporter is None:
        return {}

    return dict(exporter.export_views().system_health)


def get_runtime_device_mapping(
    coordinator: LiproCoordinator,
) -> Mapping[str, LiproDevice]:
    """Return a safe device mapping view for one runtime coordinator."""
    devices = coordinator.devices
    return devices if isinstance(devices, Mapping) else {}


def is_runtime_device_mapping_degraded(
    coordinator: LiproCoordinator,
) -> bool:
    """Return whether the runtime device projection is degraded for one coordinator."""
    return not isinstance(_get_explicit_member(coordinator, "devices"), Mapping)


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
    entry: RuntimeEntryLike | object,
) -> RuntimeCoordinatorSnapshot | None:
    """Build one control-plane runtime snapshot from a config entry."""
    runtime_entry = _coerce_runtime_entry_view(entry)
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
        entry_ref=_coerce_entry_ref(telemetry_view),
        device_count=_coerce_device_count(telemetry_view, coordinator),
        last_update_success=_coerce_last_update_success(telemetry_view, coordinator),
        mqtt_connected=_coerce_mqtt_connected(telemetry_view, coordinator),
        failure_summary=_coerce_failure_summary(telemetry_view),
    )


def build_runtime_snapshots(hass: HomeAssistant) -> list[RuntimeCoordinatorSnapshot]:
    """Build runtime snapshots for all active Lipro entries."""
    snapshots: list[RuntimeCoordinatorSnapshot] = []
    for entry in iter_runtime_entries(hass):
        snapshot = build_runtime_snapshot(entry)
        if snapshot is not None:
            snapshots.append(snapshot)
    return snapshots
