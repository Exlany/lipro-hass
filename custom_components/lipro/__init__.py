"""The Lipro Smart Home integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const.base import DOMAIN
from .control import EntryLifecycleController, ServiceRegistry
from .coordinator_entry import Coordinator
from .core import (
    LiproAuthManager,
    LiproClient as _LiproClientCompat,
    LiproProtocolFacade,
)
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

LiproClient = _LiproClientCompat

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

type LiproRuntimeData = Coordinator
type LiproConfigEntry = ConfigEntry[LiproRuntimeData]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _build_service_registry() -> ServiceRegistry:
    return ServiceRegistry(
        domain=DOMAIN,
        public_registrations=PUBLIC_SERVICE_REGISTRATIONS,
        developer_registrations=DEVELOPER_SERVICE_REGISTRATIONS,
        service_registrations=SERVICE_REGISTRATIONS,
        async_setup_services=async_setup_services,
        remove_services=remove_services,
        has_debug_mode_runtime_entry=has_debug_mode_runtime_entry,
        get_runtime_infra_lock=get_runtime_infra_lock,
    )


def _build_entry_lifecycle_controller() -> EntryLifecycleController:
    return EntryLifecycleController(
        logger=_LOGGER,
        domain=DOMAIN,
        platforms=PLATFORMS,
        client_factory=LiproProtocolFacade,
        auth_manager_factory=LiproAuthManager,
        coordinator_factory=Coordinator,
        get_client_session=async_get_clientsession,
        build_entry_auth_context=build_entry_auth_context,
        async_authenticate_entry=async_authenticate_entry,
        clear_entry_runtime_data=clear_entry_runtime_data,
        get_entry_int_option=get_entry_int_option,
        persist_entry_tokens_if_changed=persist_entry_tokens_if_changed,
        store_entry_options_snapshot=store_entry_options_snapshot,
        remove_entry_options_snapshot=remove_entry_options_snapshot,
        async_reload_entry_if_options_changed=async_reload_entry_if_options_changed,
        async_ensure_runtime_infra=async_ensure_runtime_infra,
        setup_device_registry_listener=setup_device_registry_listener,
        remove_device_registry_listener=remove_device_registry_listener,
        has_other_runtime_entries=has_other_runtime_entries,
        service_registry=_build_service_registry(),
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    return await _build_entry_lifecycle_controller().async_setup_component(hass, config)


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    return await _build_entry_lifecycle_controller().async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Unload a config entry."""
    return await _build_entry_lifecycle_controller().async_unload_entry(hass, entry)


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await _build_entry_lifecycle_controller().async_reload_entry(hass, entry)
