"""Support-only runtime device and debug helpers for runtime access."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, cast

from homeassistant.core import HomeAssistant

from ..const.config import CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE
from .runtime_access_support_members import _has_explicit_runtime_member
from .runtime_access_support_views import (
    _build_runtime_coordinator_view,
    _build_runtime_entry_view_support,
    _get_entry_runtime_coordinator_support,
    _iter_runtime_entries_support,
    _iter_runtime_entry_coordinators_support,
    _iter_runtime_entry_views_support,
)
from .runtime_access_types import RuntimeAccessCoordinator, RuntimeEntryPort

if TYPE_CHECKING:
    from ..core.device import LiproDevice


def _call_runtime_device_getter(
    getter: Callable[[str], object] | None,
    *,
    device_id: str,
) -> LiproDevice | None:
    """Call one explicit runtime device getter without MagicMock ghost leakage."""
    if getter is None:
        return None

    device = cast("LiproDevice | None", getter(device_id))
    return device if device is not None else None


def _read_get_device(
    coordinator: RuntimeAccessCoordinator,
) -> Callable[[str], object] | None:
    if not _has_explicit_runtime_member(coordinator, "get_device"):
        return None
    try:
        getter = coordinator.get_device
    except AttributeError:
        return None
    return getter if callable(getter) else None


def _read_get_device_by_id(
    coordinator: RuntimeAccessCoordinator,
) -> Callable[[str], object] | None:
    if not _has_explicit_runtime_member(coordinator, "get_device_by_id"):
        return None
    try:
        getter = coordinator.get_device_by_id
    except AttributeError:
        return None
    return getter if callable(getter) else None


def _find_runtime_device_in_mapping(
    coordinator: RuntimeAccessCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device from the explicit coordinator mapping."""
    return _get_runtime_device_mapping_support(coordinator).get(device_id)


def _find_runtime_device_via_explicit_getters(
    coordinator: RuntimeAccessCoordinator,
    device_id: str,
) -> LiproDevice | None:
    """Return one runtime device via explicit coordinator lookup helpers."""
    for getter in (_read_get_device(coordinator), _read_get_device_by_id(coordinator)):
        device = _call_runtime_device_getter(getter, device_id=device_id)
        if device is not None:
            return device
    return None


def _get_runtime_device_mapping_support(
    coordinator: RuntimeAccessCoordinator,
) -> Mapping[str, LiproDevice]:
    """Return a safe device mapping view for one runtime coordinator."""
    return _build_runtime_coordinator_view(coordinator).devices or {}


def _find_runtime_device_support(
    coordinator: RuntimeAccessCoordinator,
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
) -> tuple[LiproDevice, RuntimeAccessCoordinator] | None:
    """Return the runtime device plus owning coordinator when available."""
    for _entry, coordinator in _iter_runtime_entry_coordinators_support(
        hass, entry_id=entry_id
    ):
        device = _find_runtime_device_support(coordinator, device_id)
        if device is not None:
            return device, coordinator
    return None


def _find_runtime_entry_for_coordinator_support(
    hass: HomeAssistant,
    coordinator: RuntimeAccessCoordinator,
) -> RuntimeEntryPort | None:
    """Return the config entry that owns one active coordinator."""
    try:
        config_entry = coordinator.config_entry
    except AttributeError:
        config_entry = None

    runtime_entry = _build_runtime_entry_view_support(config_entry)
    if runtime_entry is not None:
        if _get_entry_runtime_coordinator_support(runtime_entry.entry) is coordinator:
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
    coordinator: RuntimeAccessCoordinator,
) -> bool:
    """Return whether the coordinator belongs to a debug-enabled entry."""
    entry = _find_runtime_entry_for_coordinator_support(hass, coordinator)
    return entry is not None and _is_debug_mode_enabled_for_entry_support(entry)


def _iter_developer_runtime_coordinators_support(
    hass: HomeAssistant,
) -> list[RuntimeAccessCoordinator]:
    """Return runtime coordinators that explicitly opted into debug mode."""
    coordinators: list[RuntimeAccessCoordinator] = []
    for view in _iter_runtime_entry_views_support(hass):
        if not _is_debug_mode_enabled_for_entry_support(view.entry):
            continue
        coordinator = _get_entry_runtime_coordinator_support(view.entry)
        if coordinator is not None:
            coordinators.append(coordinator)
    return coordinators


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
    coordinator: RuntimeAccessCoordinator,
) -> bool:
    """Return whether the runtime device projection is degraded for one coordinator."""
    return _build_runtime_coordinator_view(coordinator).devices is None
