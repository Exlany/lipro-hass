"""Formal control-plane lifecycle owner for Lipro config entries."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from functools import partial
import logging
from typing import Any, Protocol

from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from ..const.config import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from ..coordinator_entry import Coordinator
from ..core import LiproAuthManager, LiproProtocolFacade
from .service_registry import ServiceRegistry

type EntryLike = ConfigEntry[Any]
type ClientFactory = Callable[..., LiproProtocolFacade]
type AuthManagerFactory = Callable[[LiproProtocolFacade], LiproAuthManager]
type GetClientSession = Callable[[HomeAssistant], ClientSession]
type BuildEntryAuthContext = Callable[..., tuple[LiproProtocolFacade, LiproAuthManager]]
type AuthenticateEntry = Callable[[LiproAuthManager], Awaitable[None]]
type ClearEntryRuntimeData = Callable[[EntryLike], None]
type GetEntryIntOption = Callable[..., int]
type PersistEntryTokens = Callable[[HomeAssistant, EntryLike, LiproAuthManager], None]
type StoreEntryOptionsSnapshot = Callable[[HomeAssistant, EntryLike], None]
type RemoveEntryOptionsSnapshot = Callable[[HomeAssistant, str], None]
type ReloadEntryIfOptionsChanged = Callable[[HomeAssistant, EntryLike], Coroutine[Any, Any, None]]
type EnsureRuntimeInfra = Callable[..., Awaitable[None]]
type RemoveDeviceRegistryListener = Callable[[HomeAssistant], None]


class SetupDeviceRegistryListener(Protocol):
    """Attach the shared device-registry listener using one logger."""

    def __call__(self, hass: HomeAssistant, *, logger: logging.Logger) -> None:
        """Register the shared listener with the provided logger."""


class HasOtherRuntimeEntries(Protocol):
    """Return whether another runtime entry is still active."""

    def __call__(self, hass: HomeAssistant, *, exclude_entry_id: str) -> bool:
        """Return whether another runtime entry remains active."""


class CoordinatorRuntimeLike(Protocol):
    """Minimal coordinator lifecycle surface owned by the control plane."""

    async def async_config_entry_first_refresh(self) -> None:
        """Perform the first runtime refresh for one config entry."""

    async def async_shutdown(self) -> None:
        """Release runtime resources held by one coordinator."""


class CoordinatorFactory(Protocol):
    """Construct the runtime coordinator for one config entry."""

    def __call__(
        self,
        hass: HomeAssistant,
        protocol: LiproProtocolFacade,
        auth_manager: LiproAuthManager,
        config_entry: EntryLike,
        *,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> Coordinator:
        """Return one configured runtime coordinator."""


class EntryLifecycleController:
    """Own integration setup/unload/reload orchestration."""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        domain: str,
        platforms: list[Platform],
        client_factory: ClientFactory,
        auth_manager_factory: AuthManagerFactory,
        coordinator_factory: CoordinatorFactory,
        get_client_session: GetClientSession,
        build_entry_auth_context: BuildEntryAuthContext,
        async_authenticate_entry: AuthenticateEntry,
        clear_entry_runtime_data: ClearEntryRuntimeData,
        get_entry_int_option: GetEntryIntOption,
        persist_entry_tokens_if_changed: PersistEntryTokens,
        store_entry_options_snapshot: StoreEntryOptionsSnapshot,
        remove_entry_options_snapshot: RemoveEntryOptionsSnapshot,
        async_reload_entry_if_options_changed: ReloadEntryIfOptionsChanged,
        async_ensure_runtime_infra: EnsureRuntimeInfra,
        setup_device_registry_listener: SetupDeviceRegistryListener,
        remove_device_registry_listener: RemoveDeviceRegistryListener,
        has_other_runtime_entries: HasOtherRuntimeEntries,
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

    def _build_setup_listener(self) -> Callable[[HomeAssistant], None]:
        """Bind the shared device-registry listener to the controller logger."""
        return partial(
            self._setup_device_registry_listener,
            logger=self._logger,
        )

    async def _async_ensure_runtime_infra_ready(self, hass: HomeAssistant) -> None:
        """Ensure shared runtime services and listeners are ready before entry work."""
        await self._async_ensure_runtime_infra(
            hass,
            setup_services=self._service_registry.async_sync,
            setup_device_registry_listener=self._build_setup_listener(),
        )

    async def _async_abort_setup(
        self,
        *,
        entry: EntryLike,
        coordinator: CoordinatorRuntimeLike,
    ) -> None:
        """Shut down partially started runtime state before re-raising setup errors."""
        await coordinator.async_shutdown()
        self._clear_entry_runtime_data(entry)

    async def async_setup_component(self, hass: HomeAssistant, config: object) -> bool:
        """Set up shared runtime infrastructure for the integration."""
        del config
        await self._async_ensure_runtime_infra_ready(hass)
        return True

    async def async_setup_entry(self, hass: HomeAssistant, entry: EntryLike) -> bool:
        """Set up one Lipro config entry."""
        await self._async_ensure_runtime_infra_ready(hass)

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
        except asyncio.CancelledError:
            await self._async_abort_setup(entry=entry, coordinator=coordinator)
            raise
        except Exception:
            await self._async_abort_setup(entry=entry, coordinator=coordinator)
            raise

        entry.runtime_data = coordinator

        try:
            self._persist_entry_tokens_if_changed(hass, entry, auth_manager)
            await hass.config_entries.async_forward_entry_setups(entry, self._platforms)
        except asyncio.CancelledError:
            await self._async_abort_setup(entry=entry, coordinator=coordinator)
            raise
        except Exception:
            await self._async_abort_setup(entry=entry, coordinator=coordinator)
            raise

        self._store_entry_options_snapshot(hass, entry)
        entry.async_on_unload(
            entry.add_update_listener(self._async_reload_entry_if_options_changed)
        )
        await self._service_registry.async_sync_with_lock(hass)
        return True

    async def async_unload_entry(self, hass: HomeAssistant, entry: EntryLike) -> bool:
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

    async def async_reload_entry(self, hass: HomeAssistant, entry: EntryLike) -> None:
        """Reload one config entry."""
        await hass.config_entries.async_reload(entry.entry_id)
