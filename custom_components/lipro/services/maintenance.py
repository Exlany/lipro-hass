"""Maintenance service handlers and registry listeners for Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import functools
from typing import Any

from homeassistant.core import (
    CALLBACK_TYPE,
    Event,
    HomeAssistant,
    ServiceCall,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr

from ..core.utils.redaction import redact_identifier as _redact_identifier


def _iter_runtime_entry_coordinators(
    hass: HomeAssistant,
    *,
    domain: str,
    requested_entry_id: str | None,
) -> list[tuple[str, Any]]:
    """Collect runtime coordinators for one entry or all entries."""
    targets: list[tuple[str, Any]] = []
    for entry in hass.config_entries.async_entries(domain):
        if requested_entry_id and entry.entry_id != requested_entry_id:
            continue
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is None:
            continue
        targets.append((entry.entry_id, coordinator))
    return targets


async def async_handle_refresh_devices(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    domain: str,
    attr_entry_id: str,
) -> dict[str, Any]:
    """Handle refresh_devices service call."""
    requested_entry_id = call.data.get(attr_entry_id)
    targets = _iter_runtime_entry_coordinators(
        hass,
        domain=domain,
        requested_entry_id=requested_entry_id,
    )

    if requested_entry_id and not targets:
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="entry_not_found",
            translation_placeholders={"entry_id": requested_entry_id},
        )

    refreshed_entries = 0
    for _entry_id, coordinator in targets:
        await coordinator.device_refresh_service.async_refresh_devices()
        refreshed_entries += 1

    result: dict[str, Any] = {"success": True, "refreshed_entries": refreshed_entries}
    if requested_entry_id:
        result["requested_entry_id"] = requested_entry_id
    return result


def _is_lipro_device_entry(device_entry: Any, *, domain: str) -> bool:
    """Return True when a device-registry entry belongs to Lipro integration."""
    for identifier in getattr(device_entry, "identifiers", set()):
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
    device_entry: Any,
) -> list[str]:
    """List Lipro config entries linked to one device-registry entry."""
    matched_entry_ids: list[str] = []
    for entry_id in getattr(device_entry, "config_entries", set()):
        if not isinstance(entry_id, str) or not entry_id:
            continue
        config_entry = hass.config_entries.async_get_entry(entry_id)
        if config_entry is None or config_entry.domain != domain:
            continue
        matched_entry_ids.append(entry_id)
    return matched_entry_ids


def async_setup_device_registry_listener(
    hass: HomeAssistant,
    *,
    domain: str,
    logger: Any,
    reload_entry: Callable[[str], Awaitable[Any]],
) -> CALLBACK_TYPE:
    """Listen for Lipro device registry disable/enable changes and reload entries."""
    pending_reload_tasks: dict[str, asyncio.Task[Any]] = {}

    async def _async_reload_entry(entry_id: str) -> None:
        """Reload one config entry."""
        await reload_entry(entry_id)

    def _handle_reload_task_done(entry_id: str, task: asyncio.Task[Any]) -> None:
        """Clear bookkeeping and surface task failures without leaking tasks."""
        pending_reload_tasks.pop(entry_id, None)
        if task.cancelled():
            return

        try:
            task.result()
        except Exception as err:  # noqa: BLE001
            logger.warning(
                "Config entry reload failed after device registry update (%s, %s)",
                entry_id,
                type(err).__name__,
            )

    @callback
    def _async_handle_device_registry_updated(
        event: Event[dr.EventDeviceRegistryUpdatedData],
    ) -> None:
        """Handle device_registry_updated events with minimal reload strategy."""
        event_data = event.data
        if event_data.get("action") != "update":
            return

        changes = event_data.get("changes")
        if not isinstance(changes, dict) or "disabled_by" not in changes:
            return

        device_id = event_data.get("device_id")
        if not isinstance(device_id, str) or not device_id:
            return

        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(device_id)
        if device_entry is None or not _is_lipro_device_entry(
            device_entry,
            domain=domain,
        ):
            return

        old_disabled_by = changes.get("disabled_by")
        new_disabled_by = device_entry.disabled_by
        if (old_disabled_by is None) == (new_disabled_by is None):
            return

        for entry_id in _iter_lipro_config_entry_ids_for_device(
            hass,
            domain=domain,
            device_entry=device_entry,
        ):
            current_task = pending_reload_tasks.get(entry_id)
            if current_task is not None and not current_task.done():
                continue

            logger.info(
                "Device registry disabled state changed for %s, scheduling entry reload (%s)",
                _redact_identifier(device_id),
                entry_id,
            )
            task = hass.async_create_task(_async_reload_entry(entry_id))
            pending_reload_tasks[entry_id] = task

            task.add_done_callback(
                functools.partial(_handle_reload_task_done, entry_id)
            )

    unsubscribe = hass.bus.async_listen(
        dr.EVENT_DEVICE_REGISTRY_UPDATED,
        _async_handle_device_registry_updated,
    )

    @callback
    def _unsubscribe_listener() -> None:
        """Stop listening and cancel pending reload tasks."""
        unsubscribe()
        for task in tuple(pending_reload_tasks.values()):
            if not task.done():
                task.cancel()
        pending_reload_tasks.clear()

    return _unsubscribe_listener
