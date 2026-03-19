"""Formal control-plane lifecycle owner for Lipro config entries."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from functools import partial
import logging
from typing import Any, Protocol, cast

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
from .entry_lifecycle_failures import (
    DEGRADABLE_UNLOAD_EXCEPTIONS,
    RELOAD_FAILURE_EXCEPTIONS,
    SETUP_FAILURE_EXCEPTIONS,
    LifecycleFailureContract,
    SetupLifecycleFailure,
    classify_reload_failure,
    classify_setup_failure,
    classify_unload_failure,
)
from .service_registry import ServiceRegistry

type EntryLike = ConfigEntry[Coordinator | None]
type ProtocolFactory = Callable[..., LiproProtocolFacade]
type AuthManagerFactory = Callable[[LiproProtocolFacade], LiproAuthManager]
type GetClientSession = Callable[[HomeAssistant], ClientSession]
type BuildEntryAuthContext = Callable[..., tuple[LiproProtocolFacade, LiproAuthManager]]
type AuthenticateEntry = Callable[[LiproAuthManager], Awaitable[None]]
type ClearEntryRuntimeData = Callable[[EntryLike], None]
type GetEntryIntOption = Callable[..., int]
type PersistEntryTokens = Callable[[HomeAssistant, EntryLike, LiproAuthManager], None]
type StoreEntryOptionsSnapshot = Callable[[HomeAssistant, EntryLike], None]
type RemoveEntryOptionsSnapshot = Callable[[HomeAssistant, str], None]
type ReloadEntryIfOptionsChanged = Callable[[HomeAssistant, EntryLike], Awaitable[None]]
type EnsureRuntimeInfra = Callable[..., Awaitable[None]]
type RemoveDeviceRegistryListener = Callable[[HomeAssistant], None]

@dataclass(frozen=True, slots=True)
class EntrySetupArtifacts:
    """Prepared setup collaborators for one config entry."""

    auth_manager: LiproAuthManager
    coordinator: Coordinator


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
        protocol_factory: ProtocolFactory,
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
        self._protocol_factory = protocol_factory
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

    def _build_reload_options_listener(
        self,
    ) -> Callable[[HomeAssistant, ConfigEntry[Any]], Coroutine[Any, Any, None]]:
        """Build the stable update-listener bridge for options reloads."""

        async def _reload_options_bridge(
            bridge_hass: HomeAssistant,
            bridge_entry: ConfigEntry[Any],
        ) -> None:
            await self._async_reload_entry_if_options_changed(
                bridge_hass,
                cast(EntryLike, bridge_entry),
            )

        return _reload_options_bridge

    async def _async_ensure_runtime_infra_ready(self, hass: HomeAssistant) -> None:
        """Ensure shared runtime services and listeners are ready before entry work."""
        await self._async_ensure_runtime_infra(
            hass,
            setup_services=self._service_registry.async_sync,
            setup_device_registry_listener=self._build_setup_listener(),
        )

    def _resolve_scan_interval(self, entry: EntryLike) -> int:
        """Resolve one entry scan interval through the shared option coercion path."""
        return self._get_entry_int_option(
            entry,
            option_name=CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
            min_value=MIN_SCAN_INTERVAL,
            max_value=MAX_SCAN_INTERVAL,
            logger=self._logger,
        )

    async def _async_prepare_entry_setup(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
    ) -> EntrySetupArtifacts:
        """Prepare one entry until a coordinator is ready for activation."""
        await self._async_ensure_runtime_infra_ready(hass)

        protocol, auth_manager = self._build_entry_auth_context(
            hass,
            entry,
            get_client_session=self._get_client_session,
            protocol_factory=self._protocol_factory,
            auth_manager_factory=self._auth_manager_factory,
            logger=self._logger,
        )
        await self._async_authenticate_entry(auth_manager)

        coordinator = self._coordinator_factory(
            hass,
            protocol,
            auth_manager,
            entry,
            update_interval=self._resolve_scan_interval(entry),
        )
        return EntrySetupArtifacts(
            auth_manager=auth_manager,
            coordinator=coordinator,
        )

    async def _async_complete_setup(
        self,
        *,
        hass: HomeAssistant,
        entry: EntryLike,
        coordinator: CoordinatorRuntimeLike,
        auth_manager: LiproAuthManager,
    ) -> None:
        """Run refresh plus platform forwarding for one prepared entry."""
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = cast(Coordinator | None, coordinator)
        self._persist_entry_tokens_if_changed(hass, entry, auth_manager)
        await hass.config_entries.async_forward_entry_setups(entry, self._platforms)

    def _attach_entry_lifecycle_hooks(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
    ) -> None:
        """Persist entry hooks only after setup activation has fully succeeded."""
        self._store_entry_options_snapshot(hass, entry)
        entry.async_on_unload(
            entry.add_update_listener(self._build_reload_options_listener())
        )

    async def _async_activate_entry_setup(
        self,
        *,
        hass: HomeAssistant,
        entry: EntryLike,
        setup_artifacts: EntrySetupArtifacts,
    ) -> None:
        """Activate one prepared entry and attach shared lifecycle hooks."""
        await self._async_complete_setup(
            hass=hass,
            entry=entry,
            coordinator=setup_artifacts.coordinator,
            auth_manager=setup_artifacts.auth_manager,
        )
        await self._service_registry.async_sync_with_lock(hass)
        self._attach_entry_lifecycle_hooks(hass, entry)

    async def _async_abort_setup(
        self,
        *,
        hass: HomeAssistant,
        entry: EntryLike,
        coordinator: CoordinatorRuntimeLike,
    ) -> None:
        """Shut down partially started runtime state before re-raising setup errors."""
        await coordinator.async_shutdown()
        self._clear_entry_runtime_data(entry)
        self._remove_entry_options_snapshot(hass, entry.entry_id)

    async def _async_run_entry_activation(
        self,
        *,
        hass: HomeAssistant,
        entry: EntryLike,
        setup_artifacts: EntrySetupArtifacts,
    ) -> None:
        """Run prepared setup activation with typed contracts and guaranteed cleanup."""
        activation_completed = False
        lifecycle_failure: SetupLifecycleFailure | None = None

        try:
            await self._async_activate_entry_setup(
                hass=hass,
                entry=entry,
                setup_artifacts=setup_artifacts,
            )
            activation_completed = True
        except asyncio.CancelledError:
            raise
        except SETUP_FAILURE_EXCEPTIONS as err:
            lifecycle_failure = err
            raise
        finally:
            if not activation_completed:
                if lifecycle_failure is not None:
                    self._log_lifecycle_contract(
                        classify_setup_failure(lifecycle_failure)
                    )
                await self._async_abort_setup(
                    hass=hass,
                    entry=entry,
                    coordinator=setup_artifacts.coordinator,
                )

    async def _async_cleanup_unloaded_entry(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
    ) -> None:
        """Release one unloaded entry runtime and option snapshot state."""
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            await self._async_shutdown_on_unload(coordinator)
        self._clear_entry_runtime_data(entry)
        self._remove_entry_options_snapshot(hass, entry.entry_id)

    async def _async_sync_services_after_unload(
        self,
        hass: HomeAssistant,
        entry_id: str,
    ) -> None:
        """Reconcile shared service state after one entry unload."""
        if not self._has_other_runtime_entries(hass, exclude_entry_id=entry_id):
            self._service_registry.remove_all(hass)
            self._remove_device_registry_listener(hass)
            return

        await self._service_registry.async_sync_with_lock(hass)

    def _log_lifecycle_contract(
        self,
        contract: LifecycleFailureContract,
        *,
        warning: bool = False,
    ) -> None:
        """Log one named lifecycle arbitration contract at the intended level."""
        log = self._logger.warning if warning else self._logger.debug
        log(
            "Lifecycle %s contract %s -> %s (%s)",
            contract.stage,
            contract.contract_name,
            contract.handling_policy,
            contract.error_type,
        )


    async def _async_shutdown_on_unload(
        self,
        coordinator: CoordinatorRuntimeLike,
    ) -> None:
        """Shutdown runtime data during unload while preserving cancel semantics."""
        try:
            await coordinator.async_shutdown()
        except asyncio.CancelledError:
            raise
        except DEGRADABLE_UNLOAD_EXCEPTIONS as err:
            self._log_lifecycle_contract(
                classify_unload_failure(err),
                warning=True,
            )

    async def async_setup_component(self, hass: HomeAssistant, config: object) -> bool:
        """Set up shared runtime infrastructure for the integration."""
        del config
        await self._async_ensure_runtime_infra_ready(hass)
        return True

    async def async_setup_entry(self, hass: HomeAssistant, entry: EntryLike) -> bool:
        """Set up one Lipro config entry."""
        try:
            setup_artifacts = await self._async_prepare_entry_setup(hass, entry)
        except asyncio.CancelledError:
            raise
        except SETUP_FAILURE_EXCEPTIONS as err:
            self._log_lifecycle_contract(classify_setup_failure(err))
            raise

        await self._async_run_entry_activation(
            hass=hass,
            entry=entry,
            setup_artifacts=setup_artifacts,
        )
        return True

    async def async_unload_entry(self, hass: HomeAssistant, entry: EntryLike) -> bool:
        """Unload one Lipro config entry."""
        result = await hass.config_entries.async_unload_platforms(
            entry, self._platforms
        )
        if not result:
            return False

        await self._async_cleanup_unloaded_entry(hass, entry)
        await self._async_sync_services_after_unload(hass, entry.entry_id)
        return True

    async def async_reload_entry(self, hass: HomeAssistant, entry: EntryLike) -> None:
        """Reload one config entry."""
        try:
            await hass.config_entries.async_reload(entry.entry_id)
        except asyncio.CancelledError:
            raise
        except RELOAD_FAILURE_EXCEPTIONS as err:
            self._log_lifecycle_contract(classify_reload_failure(err))
            raise
