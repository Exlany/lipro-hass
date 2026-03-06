"""Shared runtime infrastructure helpers for the Lipro integration."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Final

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .const.base import DOMAIN
from .services.maintenance import (
    async_setup_device_registry_listener as _async_setup_device_registry_listener_service,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    import logging

_DATA_DEVICE_REGISTRY_LISTENER_UNSUB: Final = "device_registry_listener_unsub"
_DATA_RUNTIME_INFRA_LOCK: Final = "runtime_infra_lock"


def setup_device_registry_listener(
    hass: HomeAssistant,
    *,
    logger: logging.Logger,
) -> None:
    """Set up one shared device-registry listener for Lipro entries."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not isinstance(domain_data, dict):
        return
    if _DATA_DEVICE_REGISTRY_LISTENER_UNSUB in domain_data:
        return

    domain_data[_DATA_DEVICE_REGISTRY_LISTENER_UNSUB] = (
        _async_setup_device_registry_listener_service(
            hass,
            domain=DOMAIN,
            logger=logger,
            reload_entry=hass.config_entries.async_reload,
        )
    )


def remove_device_registry_listener(hass: HomeAssistant) -> None:
    """Remove the shared device-registry listener if present."""
    domain_data = hass.data.get(DOMAIN)
    if not isinstance(domain_data, dict):
        return

    unsubscribe = domain_data.pop(_DATA_DEVICE_REGISTRY_LISTENER_UNSUB, None)
    if callable(unsubscribe):
        unsubscribe()


def get_runtime_infra_lock(hass: HomeAssistant) -> asyncio.Lock | None:
    """Return per-domain lock for shared runtime infra setup/teardown."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not isinstance(domain_data, dict):
        return None

    lock = domain_data.get(_DATA_RUNTIME_INFRA_LOCK)
    if isinstance(lock, asyncio.Lock):
        return lock

    lock = asyncio.Lock()
    domain_data[_DATA_RUNTIME_INFRA_LOCK] = lock
    return lock


async def async_ensure_runtime_infra(
    hass: HomeAssistant,
    *,
    setup_services: Callable[[HomeAssistant], Awaitable[None]],
    setup_device_registry_listener: Callable[[HomeAssistant], None],
) -> None:
    """Ensure shared runtime infra (services/listener) is ready."""
    lock = get_runtime_infra_lock(hass)
    if lock is None:
        await setup_services(hass)
        setup_device_registry_listener(hass)
        return

    async with lock:
        await setup_services(hass)
        setup_device_registry_listener(hass)


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
