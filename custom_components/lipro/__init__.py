"""The Lipro Smart Home integration."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .core import LiproAuthManager, LiproClient, LiproDataUpdateCoordinator
from .entry_auth import (
    async_authenticate_entry as _async_authenticate_entry,
    build_entry_auth_context as _build_entry_auth_context_helper,
    clear_entry_runtime_data as _clear_entry_runtime_data,
    get_entry_int_option as _get_entry_int_option,
    persist_entry_tokens_if_changed as _persist_entry_tokens_if_changed_helper,
)
from .entry_options import (
    async_reload_entry_if_options_changed as _async_reload_entry_if_options_changed_helper,
    remove_entry_options_snapshot as _remove_entry_options_snapshot_helper,
    store_entry_options_snapshot as _store_entry_options_snapshot_helper,
)
from .runtime_infra import (
    async_ensure_runtime_infra as _async_ensure_runtime_infra_helper,
    get_runtime_infra_lock as _get_runtime_infra_lock,
    has_other_runtime_entries as _has_other_runtime_entries,
    remove_device_registry_listener as _remove_device_registry_listener_helper,
    setup_device_registry_listener as _setup_device_registry_listener_helper,
)
from .services.entrypoints import (
    async_setup_services as _async_setup_services,
    remove_services as _remove_services,
)

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

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

type LiproConfigEntry = ConfigEntry[LiproDataUpdateCoordinator]

FIRMWARE_SUPPORT_MANIFEST: Final = "firmware_support_manifest.json"
_DATA_OPTIONS_SNAPSHOTS: Final = "options_snapshots"


def _async_setup_device_registry_listener(hass: HomeAssistant) -> None:
    """Set up one shared device-registry listener for Lipro entries."""
    _setup_device_registry_listener_helper(hass, logger=_LOGGER)


def _remove_device_registry_listener(hass: HomeAssistant) -> None:
    """Remove the shared device-registry listener if present."""
    _remove_device_registry_listener_helper(hass)


async def _async_ensure_runtime_infra(hass: HomeAssistant) -> None:
    """Ensure shared runtime infra (services/listener) is ready."""
    await _async_ensure_runtime_infra_helper(
        hass,
        setup_services=_async_setup_services,
        setup_device_registry_listener=_async_setup_device_registry_listener,
    )


def _store_entry_options_snapshot(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Store a snapshot of config-entry options for update-listener diffing."""
    _store_entry_options_snapshot_helper(hass, entry)


def _remove_entry_options_snapshot(hass: HomeAssistant, entry_id: str) -> None:
    """Drop stored option snapshot for an entry, if present."""
    _remove_entry_options_snapshot_helper(hass, entry_id)


async def _async_reload_entry_if_options_changed(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload the config entry only when options changed."""
    await _async_reload_entry_if_options_changed_helper(hass, entry)


def _persist_entry_tokens_if_changed(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    auth_manager: LiproAuthManager,
) -> None:
    """Persist refreshed access/refresh tokens when they changed."""
    _persist_entry_tokens_if_changed_helper(hass, entry, auth_manager)


def _build_entry_auth_context(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> tuple[LiproClient, LiproAuthManager]:
    """Build API client and auth manager from config entry data."""
    return _build_entry_auth_context_helper(
        hass,
        entry,
        get_client_session=async_get_clientsession,
        client_factory=LiproClient,
        auth_manager_factory=LiproAuthManager,
        logger=_LOGGER,
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    await _async_ensure_runtime_infra(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    await _async_ensure_runtime_infra(hass)

    client, auth_manager = _build_entry_auth_context(hass, entry)
    await _async_authenticate_entry(auth_manager)

    scan_interval = _get_entry_int_option(
        entry,
        option_name=CONF_SCAN_INTERVAL,
        default=DEFAULT_SCAN_INTERVAL,
        min_value=MIN_SCAN_INTERVAL,
        max_value=MAX_SCAN_INTERVAL,
        logger=_LOGGER,
    )
    coordinator = LiproDataUpdateCoordinator(
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
        _clear_entry_runtime_data(entry)
        raise

    entry.runtime_data = coordinator

    try:
        _persist_entry_tokens_if_changed(hass, entry, auth_manager)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await coordinator.async_shutdown()
        _clear_entry_runtime_data(entry)
        raise

    _store_entry_options_snapshot(hass, entry)
    entry.async_on_unload(
        entry.add_update_listener(_async_reload_entry_if_options_changed)
    )
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
        _clear_entry_runtime_data(entry)
        _remove_entry_options_snapshot(hass, entry.entry_id)

    if result:
        lock = _get_runtime_infra_lock(hass)
        if lock is None:
            if not _has_other_runtime_entries(hass, exclude_entry_id=entry.entry_id):
                _remove_services(hass)
                _remove_device_registry_listener(hass)
        else:
            async with lock:
                if not _has_other_runtime_entries(
                    hass,
                    exclude_entry_id=entry.entry_id,
                ):
                    _remove_services(hass)
                    _remove_device_registry_listener(hass)

    return result


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
