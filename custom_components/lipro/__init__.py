"""The Lipro Smart Home integration."""

from __future__ import annotations

import asyncio
from functools import partial
import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const.base import DOMAIN
from .const.config import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .coordinator_entry import Coordinator
from .core import LiproAuthManager, LiproClient
from .entry_auth import (
    async_authenticate_entry,
    build_entry_auth_context,
    clear_entry_runtime_data,
    get_entry_int_option,
    persist_entry_tokens_if_changed,
)
from .entry_options import (
    async_reload_entry_if_options_changed,
    remove_entry_options_snapshot,
    store_entry_options_snapshot,
)
from .runtime_infra import (
    async_ensure_runtime_infra,
    get_runtime_infra_lock,
    has_other_runtime_entries,
    remove_device_registry_listener,
    setup_device_registry_listener,
)
from .services.registrations import (
    DEVELOPER_SERVICE_REGISTRATIONS,
    PUBLIC_SERVICE_REGISTRATIONS,
    SERVICE_REGISTRATIONS,
    has_debug_mode_runtime_entry,
)
from .services.registry import async_setup_services, remove_services

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)
_SETUP_DEVICE_REGISTRY_LISTENER = partial(
    setup_device_registry_listener,
    logger=_LOGGER,
)

PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.COVER,
    Platform.SWITCH,
    Platform.FAN,
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.UPDATE,
]

type LiproRuntimeData = Coordinator
type LiproConfigEntry = ConfigEntry[LiproRuntimeData]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def _async_sync_service_registrations(hass: HomeAssistant) -> None:
    """Synchronize shared services with current debug-mode runtime entries."""
    await async_setup_services(
        hass,
        domain=DOMAIN,
        registrations=PUBLIC_SERVICE_REGISTRATIONS,
    )
    if has_debug_mode_runtime_entry(hass):
        await async_setup_services(
            hass,
            domain=DOMAIN,
            registrations=DEVELOPER_SERVICE_REGISTRATIONS,
        )
        return

    remove_services(
        hass,
        domain=DOMAIN,
        registrations=DEVELOPER_SERVICE_REGISTRATIONS,
    )


async def _async_sync_service_registrations_with_lock(hass: HomeAssistant) -> None:
    """Synchronize shared services while holding the runtime infra lock."""
    lock = get_runtime_infra_lock(hass)
    if lock is None:
        await _async_sync_service_registrations(hass)
        return

    async with lock:
        await _async_sync_service_registrations(hass)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    await async_ensure_runtime_infra(
        hass,
        setup_services=_async_sync_service_registrations,
        setup_device_registry_listener=_SETUP_DEVICE_REGISTRY_LISTENER,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    await async_ensure_runtime_infra(
        hass,
        setup_services=_async_sync_service_registrations,
        setup_device_registry_listener=_SETUP_DEVICE_REGISTRY_LISTENER,
    )

    client, auth_manager = build_entry_auth_context(
        hass,
        entry,
        get_client_session=async_get_clientsession,
        client_factory=LiproClient,
        auth_manager_factory=LiproAuthManager,
        logger=_LOGGER,
    )
    await async_authenticate_entry(auth_manager)

    scan_interval = get_entry_int_option(
        entry,
        option_name=CONF_SCAN_INTERVAL,
        default=DEFAULT_SCAN_INTERVAL,
        min_value=MIN_SCAN_INTERVAL,
        max_value=MAX_SCAN_INTERVAL,
        logger=_LOGGER,
    )
    coordinator = Coordinator(
        hass,
        client,
        auth_manager,
        entry,
        update_interval=scan_interval,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await coordinator.async_shutdown()
        clear_entry_runtime_data(entry)
        raise

    entry.runtime_data = coordinator

    try:
        persist_entry_tokens_if_changed(hass, entry, auth_manager)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await coordinator.async_shutdown()
        clear_entry_runtime_data(entry)
        raise

    store_entry_options_snapshot(hass, entry)
    entry.async_on_unload(
        entry.add_update_listener(async_reload_entry_if_options_changed)
    )
    await _async_sync_service_registrations_with_lock(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Unload a config entry."""
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if result:
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            try:
                await coordinator.async_shutdown()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning(
                    "Coordinator shutdown failed during unload (%s)",
                    type(err).__name__,
                )
        clear_entry_runtime_data(entry)
        remove_entry_options_snapshot(hass, entry.entry_id)

    if result:
        lock = get_runtime_infra_lock(hass)
        if lock is None:
            if not has_other_runtime_entries(hass, exclude_entry_id=entry.entry_id):
                remove_services(
                    hass,
                    domain=DOMAIN,
                    registrations=SERVICE_REGISTRATIONS,
                )
                remove_device_registry_listener(hass)
            else:
                await _async_sync_service_registrations(hass)
        else:
            async with lock:
                if not has_other_runtime_entries(
                    hass,
                    exclude_entry_id=entry.entry_id,
                ):
                    remove_services(
                        hass,
                        domain=DOMAIN,
                        registrations=SERVICE_REGISTRATIONS,
                    )
                    remove_device_registry_listener(hass)
                else:
                    await _async_sync_service_registrations(hass)

    return result


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
