"""Support-only device-registry listener mechanics backing `runtime_infra.py`."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass
import functools
import logging
from typing import Protocol, cast, runtime_checkable

from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .core.utils.redaction import redact_identifier as _redact_identifier


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


@dataclass(frozen=True, slots=True)
class _DeviceRegistryReloadPlan:
    """Resolved device-registry update plus affected config entries."""

    device_id: str
    entry_ids: tuple[str, ...]


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

    matched_entry_ids: list[str] = []
    for entry_id in device_entry.config_entries:
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


def _build_device_registry_reload_plan(
    hass: HomeAssistant,
    *,
    event_data: Mapping[str, object],
    domain: str,
) -> _DeviceRegistryReloadPlan | None:
    """Return the reload plan for one relevant device-registry update."""
    resolved_update = _resolve_lipro_device_registry_update(
        hass,
        event_data=event_data,
        domain=domain,
    )
    if resolved_update is None:
        return None

    device_id, device_entry, changes = resolved_update
    if not _did_device_disabled_state_toggle(device_entry, changes=changes):
        return None

    entry_ids = tuple(
        _iter_lipro_config_entry_ids_for_device(
            hass,
            domain=domain,
            device_entry=device_entry,
        )
    )
    if not entry_ids:
        return None

    return _DeviceRegistryReloadPlan(device_id=device_id, entry_ids=entry_ids)


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


def _release_pending_reload_task(
    pending_reload_tasks: PendingReloadTasks,
    *,
    entry_id: str,
) -> None:
    """Drop one entry from pending reload bookkeeping."""
    pending_reload_tasks.pop(entry_id, None)


def _log_failed_reload_task(
    logger: logging.Logger,
    *,
    entry_id: str,
    task: asyncio.Task[None],
) -> None:
    """Surface one failed reload task without leaking pending ownership."""
    if task.cancelled():
        return

    error = task.exception()
    if error is not None:
        logger.warning(
            "Config entry reload failed after device registry update (%s, %s)",
            entry_id,
            type(error).__name__,
        )


def _handle_reload_task_done(
    pending_reload_tasks: PendingReloadTasks,
    logger: logging.Logger,
    entry_id: str,
    task: asyncio.Task[None],
) -> None:
    """Finalize one pending reload task and surface any failures."""
    _release_pending_reload_task(pending_reload_tasks, entry_id=entry_id)
    _log_failed_reload_task(logger, entry_id=entry_id, task=task)


def _schedule_reloads_for_device_update(
    hass: HomeAssistant,
    *,
    pending_reload_tasks: PendingReloadTasks,
    event_data: Mapping[str, object],
    domain: str,
    logger: logging.Logger,
    reload_entry: Callable[[str], Awaitable[object]],
    on_reload_done: Callable[[str, asyncio.Task[None]], None],
) -> None:
    """Schedule config-entry reloads for one relevant device-registry update."""
    reload_plan = _build_device_registry_reload_plan(
        hass,
        event_data=event_data,
        domain=domain,
    )
    if reload_plan is None:
        return

    for entry_id in reload_plan.entry_ids:
        _schedule_entry_reload(
            hass,
            pending_reload_tasks=pending_reload_tasks,
            entry_id=entry_id,
            device_id=reload_plan.device_id,
            logger=logger,
            reload_entry=reload_entry,
            on_reload_done=on_reload_done,
        )


def async_setup_device_registry_listener(
    hass: HomeAssistant,
    *,
    domain: str,
    logger: logging.Logger,
    reload_entry: Callable[[str], Awaitable[object]],
) -> CALLBACK_TYPE:
    """Listen for device-registry disable/enable changes and reload entries."""
    pending_reload_tasks: PendingReloadTasks = {}

    def _on_reload_task_done(entry_id: str, task: asyncio.Task[None]) -> None:
        """Finalize reload bookkeeping for one device-registry-triggered task."""
        _handle_reload_task_done(
            pending_reload_tasks,
            logger,
            entry_id,
            task,
        )

    @callback
    def _async_handle_device_registry_updated(
        event: Event[dr.EventDeviceRegistryUpdatedData],
    ) -> None:
        """Handle device_registry_updated events with minimal reload strategy."""
        _schedule_reloads_for_device_update(
            hass,
            event_data=event.data,
            pending_reload_tasks=pending_reload_tasks,
            domain=domain,
            logger=logger,
            reload_entry=reload_entry,
            on_reload_done=_on_reload_task_done,
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
