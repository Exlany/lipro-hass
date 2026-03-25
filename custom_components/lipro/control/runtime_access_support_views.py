"""Support-only runtime entry and coordinator view builders."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

from homeassistant.core import HomeAssistant

from ..const.base import DOMAIN
from ..runtime_types import LiproCoordinator, ProtocolTelemetryFacadeLike
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


def _build_runtime_coordinator_view(
    coordinator: LiproCoordinator,
) -> RuntimeCoordinatorView:
    """Build the explicit runtime read-model for one coordinator."""
    facts = _build_runtime_coordinator_facts(coordinator)

    return RuntimeCoordinatorView(
        coordinator=coordinator,
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
    update_interval = _get_explicit_member(coordinator, "update_interval")
    last_update_success = _get_explicit_bool_member(coordinator, "last_update_success")
    mqtt_service = _get_explicit_member(coordinator, "mqtt_service")
    mqtt_connected = _get_explicit_bool_member(mqtt_service, "connected")
    protocol = _get_explicit_member(coordinator, "protocol")
    devices = _get_explicit_mapping_member(coordinator, "devices")

    return RuntimeCoordinatorFacts(
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
    coordinator: LiproCoordinator | None,
) -> RuntimeCoordinatorView | None:
    """Build the coordinator projection owned by one runtime entry."""
    if coordinator is None:
        return None
    return _build_runtime_coordinator_view(coordinator)


def _coerce_runtime_entry_port(
    entry: object,
) -> tuple[RuntimeEntryPort, RuntimeEntryFacts] | None:
    """Return the narrowed runtime-entry port plus typed facts when explicit."""
    if not _has_explicit_runtime_member(entry, "runtime_data"):
        return None

    entry_id = _get_explicit_member(entry, "entry_id")
    options = _get_explicit_mapping_member(entry, "options")
    if not isinstance(entry_id, str) or options is None:
        return None

    return cast(RuntimeEntryPort, entry), RuntimeEntryFacts(
        entry_id=entry_id,
        options=options,
        runtime_data=cast(LiproCoordinator | None, _get_explicit_member(entry, "runtime_data")),
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
