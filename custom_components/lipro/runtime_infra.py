"""Shared runtime infrastructure helpers for the Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Mapping
import functools
import logging
from typing import Final, Protocol, cast, runtime_checkable

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .const.base import DOMAIN
from .core.utils.redaction import redact_identifier as _redact_identifier
from .domain_data import ensure_domain_data, get_domain_data

_DATA_DEVICE_REGISTRY_LISTENER_UNSUB: Final = "device_registry_listener_unsub"
_DATA_RUNTIME_INFRA_LOCK: Final = "runtime_infra_lock"


@runtime_checkable
class _DeviceRegistryEntryLike(Protocol):
    """Device-registry surface used by reload listeners."""

    identifiers: Iterable[object]
    config_entries: Iterable[object]
    disabled_by: object | None


@runtime_checkable
class _ConfigEntryCarrier(Protocol):
    """Minimal device-like surface that exposes config entries."""

    config_entries: Iterable[object]


type PendingReloadTasks = dict[str, asyncio.Task[None]]


def _is_lipro_device_entry(
    device_entry: _DeviceRegistryEntryLike | object,
    *,
    domain: str,
) -> bool:
    """Return True when a device-registry entry belongs to Lipro integration."""
    if not isinstance(device_entry, _DeviceRegistryEntryLike):
        return False
    for identifier in device_entry.identifiers:
        if (
            isinstance(identifier, tuple)
            and len(identifier) == 2
            and identifier[0] == domain
            and isinstance(identifier[1], str)
            and identifier[1]
        ):
            return True
    return False


def _iter_lipro_config_entry_ids_for_device(
    hass: HomeAssistant,
    *,
    domain: str,
    device_entry: _ConfigEntryCarrier | object,
) -> list[str]:
    """List Lipro config entries linked to one device-registry entry."""
    if not isinstance(device_entry, _ConfigEntryCarrier):
        return []

    config_entries = device_entry.config_entries

    matched_entry_ids: list[str] = []
    for entry_id in config_entries:
        if not isinstance(entry_id, str) or not entry_id:
            continue
        config_entry = hass.config_entries.async_get_entry(entry_id)
        if config_entry is None or config_entry.domain != domain:
            continue
        matched_entry_ids.append(entry_id)
    return matched_entry_ids


def _coerce_device_registry_change_set(
    event_data: Mapping[str, object],
) -> Mapping[str, object] | None:
    """Return the device-registry change-set when the event carries one."""
    changes = event_data.get("changes")
    if not isinstance(changes, dict) or "disabled_by" not in changes:
        return None
    return changes


def _resolve_lipro_device_registry_update(
    hass: HomeAssistant,
    *,
    event_data: Mapping[str, object],
    domain: str,
) -> tuple[str, _DeviceRegistryEntryLike, Mapping[str, object]] | None:
    """Return the updated Lipro device entry when the event is relevant."""
    if event_data.get("action") != "update":
        return None

    changes = _coerce_device_registry_change_set(event_data)
    if changes is None:
        return None

    device_id = event_data.get("device_id")
    if not isinstance(device_id, str) or not device_id:
        return None

    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get(device_id)
    if device_entry is None or not _is_lipro_device_entry(device_entry, domain=domain):
        return None

    return device_id, cast(_DeviceRegistryEntryLike, device_entry), changes


def _did_device_disabled_state_toggle(
    device_entry: _DeviceRegistryEntryLike,
    *,
    changes: Mapping[str, object],
) -> bool:
    """Return True when a device-registry update flips disabled state."""
    old_disabled_by = changes.get("disabled_by")
    new_disabled_by = device_entry.disabled_by
    return (old_disabled_by is None) != (new_disabled_by is None)


def _has_pending_reload_task(task: asyncio.Task[None] | None) -> bool:
    """Return whether one entry already has an unfinished reload task."""
    return task is not None and not task.done()


def _schedule_entry_reload(
    hass: HomeAssistant,
    *,
    pending_reload_tasks: PendingReloadTasks,
    entry_id: str,
    device_id: str,
    logger: logging.Logger,
    reload_entry: Callable[[str], Awaitable[object]],
    on_reload_done: Callable[[str, asyncio.Task[None]], None],
) -> None:
    """Schedule one entry reload when no in-flight task already owns it."""
    if _has_pending_reload_task(pending_reload_tasks.get(entry_id)):
        return

    logger.info(
        "Device registry disabled state changed for %s, scheduling entry reload (%s)",
        _redact_identifier(device_id),
        entry_id,
    )
    task = hass.async_create_task(_async_reload_entry(reload_entry, entry_id))
    pending_reload_tasks[entry_id] = task
    task.add_done_callback(functools.partial(on_reload_done, entry_id))


async def _async_reload_entry(
    reload_entry: Callable[[str], Awaitable[object]],
    entry_id: str,
) -> None:
    """Reload one config entry."""
    await reload_entry(entry_id)


def _cancel_pending_reload_tasks(pending_reload_tasks: PendingReloadTasks) -> None:
    """Cancel all unfinished reload tasks and clear bookkeeping."""
    for task in tuple(pending_reload_tasks.values()):
        if not task.done():
            task.cancel()
    pending_reload_tasks.clear()


def async_setup_device_registry_listener(
    hass: HomeAssistant,
    *,
    domain: str,
    logger: logging.Logger,
    reload_entry: Callable[[str], Awaitable[object]],
) -> CALLBACK_TYPE:
    """Listen for Lipro device-registry disable/enable changes and reload entries."""
    pending_reload_tasks: PendingReloadTasks = {}

    def _handle_reload_task_done(entry_id: str, task: asyncio.Task[None]) -> None:
        """Clear bookkeeping and surface task failures without leaking tasks."""
        pending_reload_tasks.pop(entry_id, None)
        if task.cancelled():
            return

        error = task.exception()
        if error is not None:
            logger.warning(
                "Config entry reload failed after device registry update (%s, %s)",
                entry_id,
                type(error).__name__,
            )

    @callback
    def _async_handle_device_registry_updated(
        event: Event[dr.EventDeviceRegistryUpdatedData],
    ) -> None:
        """Handle device_registry_updated events with minimal reload strategy."""
        resolved_update = _resolve_lipro_device_registry_update(
            hass,
            event_data=event.data,
            domain=domain,
        )
        if resolved_update is None:
            return

        device_id, device_entry, changes = resolved_update
        if not _did_device_disabled_state_toggle(device_entry, changes=changes):
            return

        for entry_id in _iter_lipro_config_entry_ids_for_device(
            hass,
            domain=domain,
            device_entry=device_entry,
        ):
            _schedule_entry_reload(
                hass,
                pending_reload_tasks=pending_reload_tasks,
                entry_id=entry_id,
                device_id=device_id,
                logger=logger,
                reload_entry=reload_entry,
                on_reload_done=_handle_reload_task_done,
            )

    unsubscribe = hass.bus.async_listen(
        dr.EVENT_DEVICE_REGISTRY_UPDATED,
        _async_handle_device_registry_updated,
    )

    @callback
    def _unsubscribe_listener() -> None:
        """Stop listening and cancel pending reload tasks."""
        unsubscribe()
        _cancel_pending_reload_tasks(pending_reload_tasks)

    return _unsubscribe_listener


def setup_device_registry_listener(
    hass: HomeAssistant,
    *,
    logger: logging.Logger,
) -> None:
    """Set up one shared device-registry listener for Lipro entries."""
    domain_data = ensure_domain_data(hass)
    if domain_data is None:
        return
    if _DATA_DEVICE_REGISTRY_LISTENER_UNSUB in domain_data:
        return

    domain_data[_DATA_DEVICE_REGISTRY_LISTENER_UNSUB] = (
        async_setup_device_registry_listener(
            hass,
            domain=DOMAIN,
            logger=logger,
            reload_entry=hass.config_entries.async_reload,
        )
    )


def remove_device_registry_listener(hass: HomeAssistant) -> None:
    """Remove the shared device-registry listener if present."""
    domain_data = get_domain_data(hass)
    if domain_data is None:
        return

    unsubscribe = domain_data.pop(_DATA_DEVICE_REGISTRY_LISTENER_UNSUB, None)
    if callable(unsubscribe):
        unsubscribe()


def get_runtime_infra_lock(hass: HomeAssistant) -> asyncio.Lock | None:
    """Return per-domain lock for shared runtime infra setup/teardown."""
    domain_data = ensure_domain_data(hass)
    if domain_data is None:
        return None

    lock = domain_data.get(_DATA_RUNTIME_INFRA_LOCK)
    if isinstance(lock, asyncio.Lock):
        return lock

    lock = asyncio.Lock()
    domain_data[_DATA_RUNTIME_INFRA_LOCK] = lock
    return lock


async def _async_setup_runtime_infra_unlocked(
    hass: HomeAssistant,
    *,
    setup_services: Callable[[HomeAssistant], Awaitable[None]],
    setup_device_registry_listener: Callable[[HomeAssistant], None],
) -> None:
    """Set up shared services and registry listener without lock orchestration."""
    await setup_services(hass)
    setup_device_registry_listener(hass)


async def async_ensure_runtime_infra(
    hass: HomeAssistant,
    *,
    setup_services: Callable[[HomeAssistant], Awaitable[None]],
    setup_device_registry_listener: Callable[[HomeAssistant], None],
) -> None:
    """Ensure shared runtime infra (services/listener) is ready."""
    lock = get_runtime_infra_lock(hass)
    if lock is None:
        await _async_setup_runtime_infra_unlocked(
            hass,
            setup_services=setup_services,
            setup_device_registry_listener=setup_device_registry_listener,
        )
        return

    async with lock:
        await _async_setup_runtime_infra_unlocked(
            hass,
            setup_services=setup_services,
            setup_device_registry_listener=setup_device_registry_listener,
        )


def has_other_runtime_entries(
    hass: HomeAssistant,
    *,
    exclude_entry_id: str,
) -> bool:
    """Return whether another Lipro entry is loaded or setting up."""
    return any(
        config_entry.entry_id != exclude_entry_id
        and config_entry.state
        in (
            ConfigEntryState.LOADED,
            ConfigEntryState.SETUP_IN_PROGRESS,
        )
        for config_entry in hass.config_entries.async_entries(DOMAIN)
    )
