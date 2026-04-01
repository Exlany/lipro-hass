"""Support-only runtime entry and coordinator view builders."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..runtime_types import (
    LiproCoordinator,
    LiproRuntimeCoordinator,
    ProtocolTelemetryFacadeLike,
)
from .runtime_access_support_members import (
    _get_explicit_bool_member,
    _get_explicit_mapping_member,
    _get_explicit_member,
    _has_explicit_runtime_member,
)
from .runtime_access_support_telemetry import _build_runtime_telemetry_snapshot
from .runtime_access_types import (
    RuntimeCoordinatorFacts,
    RuntimeCoordinatorView,
    RuntimeEntryFacts,
    RuntimeEntryPort,
    RuntimeEntryView,
)

if TYPE_CHECKING:
    from ..core.device import LiproDevice


type RuntimeEntryCoordinator = tuple[RuntimeEntryPort, LiproCoordinator]


def _read_update_interval(coordinator: LiproCoordinator) -> str | None:
    update_interval = _get_explicit_member(coordinator, "update_interval")
    return None if update_interval is None else str(update_interval)


def _read_last_update_success(coordinator: LiproCoordinator) -> bool:
    last_update_success = _get_explicit_bool_member(
        coordinator,
        "last_update_success",
    )
    return last_update_success if last_update_success is not None else False


def _read_mqtt_connected(coordinator: LiproCoordinator) -> bool | None:
    mqtt_service = _get_explicit_member(coordinator, "mqtt_service")
    if mqtt_service is None:
        return None
    return _get_explicit_bool_member(mqtt_service, "connected")


def _read_protocol(
    coordinator: LiproCoordinator,
) -> ProtocolTelemetryFacadeLike | None:
    protocol = _get_explicit_member(coordinator, "protocol")
    return cast(ProtocolTelemetryFacadeLike, protocol) if protocol is not None else None


def _read_devices(
    coordinator: LiproCoordinator,
) -> Mapping[str, LiproDevice] | None:
    devices = _get_explicit_mapping_member(coordinator, "devices")
    return cast("Mapping[str, LiproDevice] | None", devices)


def _build_runtime_coordinator_view(
    coordinator: LiproCoordinator,
) -> RuntimeCoordinatorView:
    """Build the explicit runtime read-model for one coordinator."""
    facts = _build_runtime_coordinator_facts(coordinator)

    return RuntimeCoordinatorView(
        update_interval=facts.update_interval,
        last_update_success=facts.last_update_success,
        mqtt_connected=facts.mqtt_connected,
        protocol=facts.protocol,
        runtime_telemetry_snapshot=facts.runtime_telemetry_snapshot,
        devices=facts.devices,
    )


def _build_runtime_coordinator_facts(
    coordinator: LiproCoordinator,
) -> RuntimeCoordinatorFacts:
    """Collect the explicit coordinator facts needed by public runtime views."""
    return RuntimeCoordinatorFacts(
        update_interval=_read_update_interval(coordinator),
        last_update_success=_read_last_update_success(coordinator),
        mqtt_connected=_read_mqtt_connected(coordinator),
        protocol=_read_protocol(coordinator),
        runtime_telemetry_snapshot=_build_runtime_telemetry_snapshot(coordinator),
        devices=_read_devices(coordinator),
    )


def _build_runtime_entry_coordinator(
    coordinator: LiproRuntimeCoordinator | None,
) -> RuntimeCoordinatorView | None:
    """Build the coordinator projection owned by one runtime entry."""
    if coordinator is None:
        return None
    return _build_runtime_coordinator_view(cast(LiproCoordinator, coordinator))


def _coerce_runtime_entry_port(
    entry: object,
) -> tuple[RuntimeEntryPort, RuntimeEntryFacts] | None:
    """Return the narrowed runtime-entry port plus typed facts when explicit."""
    if not _has_explicit_runtime_member(entry, "entry_id"):
        return None
    if not _has_explicit_runtime_member(entry, "options"):
        return None
    if not _has_explicit_runtime_member(entry, "runtime_data"):
        return None

    entry_id = _get_explicit_member(entry, "entry_id")
    options = _get_explicit_mapping_member(entry, "options")
    runtime_data = _get_explicit_member(entry, "runtime_data")

    if not isinstance(entry_id, str) or options is None:
        return None

    return cast(RuntimeEntryPort, entry), RuntimeEntryFacts(
        entry_id=entry_id,
        options=options,
        runtime_data=cast(LiproCoordinator | None, runtime_data),
    )


def _build_runtime_entry_view_support(
    entry: RuntimeEntryPort | object,
) -> RuntimeEntryView | None:
    """Build the typed runtime-entry read-model for control-plane consumers."""
    narrowed_entry = _coerce_runtime_entry_port(entry)
    if narrowed_entry is None:
        return None

    runtime_entry, facts = narrowed_entry

    return RuntimeEntryView(
        entry=runtime_entry,
        entry_id=facts.entry_id,
        options=facts.options,
        coordinator=_build_runtime_entry_coordinator(facts.runtime_data),
    )


def _get_entry_runtime_coordinator_support(
    entry: RuntimeEntryPort | object,
) -> LiproCoordinator | None:
    """Return the coordinator attached to a config entry, if loaded."""
    narrowed_entry = _coerce_runtime_entry_port(entry)
    if narrowed_entry is None:
        return None
    _runtime_entry, facts = narrowed_entry
    if facts.runtime_data is None:
        return None
    return cast(LiproCoordinator, facts.runtime_data)


def _iter_runtime_entries_support(
    hass: HomeAssistant,
    *,
    entry_id: str | None = None,
) -> list[RuntimeEntryPort]:
    """Return live Lipro config entries, optionally scoped to one entry id."""
    entries: list[RuntimeEntryPort] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        narrowed_entry = _coerce_runtime_entry_port(entry)
        if narrowed_entry is None:
            continue
        runtime_entry, facts = narrowed_entry
        if entry_id is None or facts.entry_id == entry_id:
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
    coordinators: list[LiproCoordinator] = []
    for entry in _iter_runtime_entries_support(hass, entry_id=entry_id):
        coordinator = _get_entry_runtime_coordinator_support(entry)
        if coordinator is not None:
            coordinators.append(coordinator)
    return coordinators


def _build_runtime_entry_coordinator_pair(
    view: RuntimeEntryView,
) -> RuntimeEntryCoordinator | None:
    """Return the live entry/coordinator pair for one runtime view."""
    coordinator = _get_entry_runtime_coordinator_support(view.entry)
    if coordinator is None:
        return None
    return view.entry, coordinator


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
