"""Shared runtime infrastructure helpers for the Lipro integration.

`runtime_infra.py` remains the outward formal home; device-registry listener
mechanics live in `runtime_infra_device_registry.py` as local support-only helpers.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import CALLBACK_TYPE, HomeAssistant

from .const.base import DOMAIN
from .domain_data import ensure_domain_data, get_domain_data
from .runtime_infra_device_registry import (
    async_setup_device_registry_listener as _async_setup_device_registry_listener,
)

_DATA_DEVICE_REGISTRY_LISTENER_UNSUB: Final = "device_registry_listener_unsub"
_DATA_RUNTIME_INFRA_LOCK: Final = "runtime_infra_lock"


def async_setup_device_registry_listener(
    hass: HomeAssistant,
    *,
    domain: str,
    logger: logging.Logger,
    reload_entry: Callable[[str], Awaitable[object]],
) -> CALLBACK_TYPE:
    """Listen for Lipro device-registry disable/enable changes and reload entries."""
    return _async_setup_device_registry_listener(
        hass,
        domain=domain,
        logger=logger,
        reload_entry=reload_entry,
    )


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
