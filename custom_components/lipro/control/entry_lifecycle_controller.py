"""Formal control-plane lifecycle owner for Lipro config entries."""

from __future__ import annotations

import asyncio
from functools import partial
import logging
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from ..const.config import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .service_registry import ServiceRegistry


class EntryLifecycleController:
    """Own integration setup/unload/reload orchestration."""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        domain: str,
        platforms: list[Platform],
        client_factory: Any,
        auth_manager_factory: Any,
        coordinator_factory: Any,
        get_client_session: Any,
        build_entry_auth_context: Any,
        async_authenticate_entry: Any,
        clear_entry_runtime_data: Any,
        get_entry_int_option: Any,
        persist_entry_tokens_if_changed: Any,
        store_entry_options_snapshot: Any,
        remove_entry_options_snapshot: Any,
        async_reload_entry_if_options_changed: Any,
        async_ensure_runtime_infra: Any,
        setup_device_registry_listener: Any,
        remove_device_registry_listener: Any,
        has_other_runtime_entries: Any,
        service_registry: ServiceRegistry,
    ) -> None:
        """Initialize the control-plane owner with explicit collaborators."""
        self._logger = logger
        self._domain = domain
        self._platforms = platforms
        self._client_factory = client_factory
        self._auth_manager_factory = auth_manager_factory
        self._coordinator_factory = coordinator_factory
        self._get_client_session = get_client_session
        self._build_entry_auth_context = build_entry_auth_context
        self._async_authenticate_entry = async_authenticate_entry
        self._clear_entry_runtime_data = clear_entry_runtime_data
        self._get_entry_int_option = get_entry_int_option
        self._persist_entry_tokens_if_changed = persist_entry_tokens_if_changed
        self._store_entry_options_snapshot = store_entry_options_snapshot
        self._remove_entry_options_snapshot = remove_entry_options_snapshot
        self._async_reload_entry_if_options_changed = (
            async_reload_entry_if_options_changed
        )
        self._async_ensure_runtime_infra = async_ensure_runtime_infra
        self._setup_device_registry_listener = setup_device_registry_listener
        self._remove_device_registry_listener = remove_device_registry_listener
        self._has_other_runtime_entries = has_other_runtime_entries
        self._service_registry = service_registry

    async def async_setup_component(self, hass: HomeAssistant, config: Any) -> bool:
        """Set up shared runtime infrastructure for the integration."""
        del config
        setup_listener = partial(
            self._setup_device_registry_listener,
            logger=self._logger,
        )
        await self._async_ensure_runtime_infra(
            hass,
            setup_services=self._service_registry.async_sync,
            setup_device_registry_listener=setup_listener,
        )
        return True

    async def async_setup_entry(self, hass: HomeAssistant, entry: Any) -> bool:
        """Set up one Lipro config entry."""
        setup_listener = partial(
            self._setup_device_registry_listener,
            logger=self._logger,
        )
        await self._async_ensure_runtime_infra(
            hass,
            setup_services=self._service_registry.async_sync,
            setup_device_registry_listener=setup_listener,
        )

        client, auth_manager = self._build_entry_auth_context(
            hass,
            entry,
            get_client_session=self._get_client_session,
            client_factory=self._client_factory,
            auth_manager_factory=self._auth_manager_factory,
            logger=self._logger,
        )
        await self._async_authenticate_entry(auth_manager)

        scan_interval = self._get_entry_int_option(
            entry,
            option_name=CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
            min_value=MIN_SCAN_INTERVAL,
            max_value=MAX_SCAN_INTERVAL,
            logger=self._logger,
        )
        coordinator = self._coordinator_factory(
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
            self._clear_entry_runtime_data(entry)
            raise

        entry.runtime_data = coordinator

        try:
            self._persist_entry_tokens_if_changed(hass, entry, auth_manager)
            await hass.config_entries.async_forward_entry_setups(entry, self._platforms)
        except Exception:
            await coordinator.async_shutdown()
            self._clear_entry_runtime_data(entry)
            raise

        self._store_entry_options_snapshot(hass, entry)
        entry.async_on_unload(
            entry.add_update_listener(self._async_reload_entry_if_options_changed)
        )
        await self._service_registry.async_sync_with_lock(hass)
        return True

    async def async_unload_entry(self, hass: HomeAssistant, entry: Any) -> bool:
        """Unload one Lipro config entry."""
        result = await hass.config_entries.async_unload_platforms(
            entry, self._platforms
        )
        if result:
            coordinator = getattr(entry, "runtime_data", None)
            if coordinator is not None:
                try:
                    await coordinator.async_shutdown()
                except asyncio.CancelledError:
                    raise
                except Exception as err:  # noqa: BLE001
                    self._logger.warning(
                        "Coordinator shutdown failed during unload (%s)",
                        type(err).__name__,
                    )
            self._clear_entry_runtime_data(entry)
            self._remove_entry_options_snapshot(hass, entry.entry_id)

        if result:
            if not self._has_other_runtime_entries(
                hass, exclude_entry_id=entry.entry_id
            ):
                self._service_registry.remove_all(hass)
                self._remove_device_registry_listener(hass)
            else:
                await self._service_registry.async_sync_with_lock(hass)

        return result

    async def async_reload_entry(self, hass: HomeAssistant, entry: Any) -> None:
        """Reload one config entry."""
        await hass.config_entries.async_reload(entry.entry_id)
