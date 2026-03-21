"""Support-only lifecycle mechanics for `EntryLifecycleController`.

This module holds entry setup/unload mechanics so the controller can remain the
sole control-plane owner while delegating mechanical flow steps inward.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine, Sequence
from dataclasses import dataclass
from functools import partial
import logging
from typing import Any, Protocol, cast

from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from ..const.config import DEFAULT_SCAN_INTERVAL
from ..coordinator_entry import Coordinator
from ..core import LiproAuthManager, LiproProtocolFacade
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


class EntryLifecycleSupport:
    """Internal support seam for entry lifecycle mechanics."""

    def __init__(
        self,
        *,
        logger: logging.Logger,
        platforms: Sequence[Platform],
        protocol_factory: ProtocolFactory,
        auth_manager_factory: AuthManagerFactory,
        coordinator_factory: CoordinatorFactory,
        get_client_session: GetClientSession,
        build_entry_auth_context: BuildEntryAuthContext,
        async_authenticate_entry: AuthenticateEntry,
        clear_entry_runtime_data: ClearEntryRuntimeData,
        persist_entry_tokens_if_changed: PersistEntryTokens,
        store_entry_options_snapshot: StoreEntryOptionsSnapshot,
        remove_entry_options_snapshot: RemoveEntryOptionsSnapshot,
        async_ensure_runtime_infra: EnsureRuntimeInfra,
        setup_device_registry_listener: SetupDeviceRegistryListener,
        remove_device_registry_listener: RemoveDeviceRegistryListener,
        has_other_runtime_entries: HasOtherRuntimeEntries,
        service_registry: ServiceRegistry,
    ) -> None:
        """Initialize the support seam with controller-owned collaborators."""
        self._logger = logger
        self._platforms = tuple(platforms)
        self._protocol_factory = protocol_factory
        self._auth_manager_factory = auth_manager_factory
        self._coordinator_factory = coordinator_factory
        self._get_client_session = get_client_session
        self._build_entry_auth_context = build_entry_auth_context
        self._async_authenticate_entry = async_authenticate_entry
        self._clear_entry_runtime_data = clear_entry_runtime_data
        self._persist_entry_tokens_if_changed = persist_entry_tokens_if_changed
        self._store_entry_options_snapshot = store_entry_options_snapshot
        self._remove_entry_options_snapshot = remove_entry_options_snapshot
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

    async def async_ensure_runtime_infra_ready(self, hass: HomeAssistant) -> None:
        """Ensure shared runtime services and listeners are ready before entry work."""
        await self._async_ensure_runtime_infra(
            hass,
            setup_services=self._service_registry.async_sync,
            setup_device_registry_listener=self._build_setup_listener(),
        )

    async def async_prepare_entry_setup(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
        *,
        resolve_scan_interval: Callable[[EntryLike], int],
    ) -> EntrySetupArtifacts:
        """Prepare one entry until a coordinator is ready for activation."""
        await self.async_ensure_runtime_infra_ready(hass)

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
            update_interval=resolve_scan_interval(entry),
        )
        return EntrySetupArtifacts(
            auth_manager=auth_manager,
            coordinator=coordinator,
        )

    async def async_activate_entry_setup(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
        setup_artifacts: EntrySetupArtifacts,
        *,
        reload_listener: Callable[[HomeAssistant, ConfigEntry[Any]], Coroutine[Any, Any, None]],
    ) -> None:
        """Run refresh, platform forwarding, shared-service sync, and hook attachment."""
        await setup_artifacts.coordinator.async_config_entry_first_refresh()
        entry.runtime_data = cast(Coordinator | None, setup_artifacts.coordinator)
        self._persist_entry_tokens_if_changed(hass, entry, setup_artifacts.auth_manager)
        await hass.config_entries.async_forward_entry_setups(entry, self._platforms)
        await self._service_registry.async_sync_with_lock(hass)
        self._store_entry_options_snapshot(hass, entry)
        entry.async_on_unload(entry.add_update_listener(reload_listener))

    def clear_entry_lifecycle_state(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
    ) -> None:
        """Clear runtime data and option snapshots for one entry-owned lifecycle state."""
        self._clear_entry_runtime_data(entry)
        self._remove_entry_options_snapshot(hass, entry.entry_id)

    async def async_abort_setup(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
        coordinator: CoordinatorRuntimeLike,
    ) -> None:
        """Shut down partially started runtime state before re-raising setup errors."""
        await coordinator.async_shutdown()
        self.clear_entry_lifecycle_state(hass, entry)

    async def async_cleanup_unloaded_entry(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
        *,
        shutdown_on_unload: Callable[[CoordinatorRuntimeLike], Awaitable[None]],
    ) -> None:
        """Release one unloaded entry runtime and option snapshot state."""
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            await shutdown_on_unload(coordinator)
        self.clear_entry_lifecycle_state(hass, entry)

    async def async_sync_services_after_unload(
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


__all__ = [
    "AuthManagerFactory",
    "AuthenticateEntry",
    "BuildEntryAuthContext",
    "ClearEntryRuntimeData",
    "CoordinatorFactory",
    "CoordinatorRuntimeLike",
    "EnsureRuntimeInfra",
    "EntryLifecycleSupport",
    "EntryLike",
    "EntrySetupArtifacts",
    "GetClientSession",
    "GetEntryIntOption",
    "HasOtherRuntimeEntries",
    "PersistEntryTokens",
    "ProtocolFactory",
    "ReloadEntryIfOptionsChanged",
    "RemoveDeviceRegistryListener",
    "RemoveEntryOptionsSnapshot",
    "SetupDeviceRegistryListener",
    "StoreEntryOptionsSnapshot",
]
