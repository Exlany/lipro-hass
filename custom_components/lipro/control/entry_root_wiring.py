# ruff: noqa: D102
"""Support-only wiring helpers for the HA root adapter.

`custom_components.lipro.__init__` remains the only HA root adapter home; this
module only carries mechanical controller/service-registry assembly.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Protocol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .service_registry import (
    GetRuntimeInfraLockFn,
    RemoveServicesFn,
    ServiceRegistry,
    SetupServicesFn,
)

if TYPE_CHECKING:
    from .entry_lifecycle_support import (
        AuthenticateEntry,
        AuthManagerFactory,
        BuildEntryAuthContext,
        ClearEntryRuntimeData,
        CoordinatorFactory,
        EnsureRuntimeInfra,
        GetClientSession,
        GetEntryIntOption,
        HasOtherRuntimeEntries,
        PersistEntryTokens,
        ProtocolFactory,
        ReloadEntryIfOptionsChanged,
        RemoveDeviceRegistryListener,
        RemoveEntryOptionsSnapshot,
        SetupDeviceRegistryListener,
        StoreEntryOptionsSnapshot,
    )


class ServiceRegistrationsLike(Protocol):
    """Service-registration table surface consumed by the root wiring helper."""

    PUBLIC_SERVICE_REGISTRATIONS: Sequence[object]
    DEVELOPER_SERVICE_REGISTRATIONS: Sequence[object]
    SERVICE_REGISTRATIONS: Sequence[object]

    def has_debug_mode_runtime_entry(self, hass: HomeAssistant) -> bool:
        """Return whether at least one runtime entry is in debug mode."""


@dataclass(frozen=True, slots=True)
class EntryLifecycleControllerDependencies:
    """Typed collaborator bundle consumed by the runtime lifecycle owner."""

    logger: logging.Logger
    platforms: tuple[Platform, ...]
    protocol_factory: ProtocolFactory
    auth_manager_factory: AuthManagerFactory
    coordinator_factory: CoordinatorFactory
    get_client_session: GetClientSession
    build_entry_auth_context: BuildEntryAuthContext
    async_authenticate_entry: AuthenticateEntry
    clear_entry_runtime_data: ClearEntryRuntimeData
    get_entry_int_option: GetEntryIntOption
    persist_entry_tokens_if_changed: PersistEntryTokens
    store_entry_options_snapshot: StoreEntryOptionsSnapshot
    remove_entry_options_snapshot: RemoveEntryOptionsSnapshot
    async_reload_entry_if_options_changed: ReloadEntryIfOptionsChanged
    async_ensure_runtime_infra: EnsureRuntimeInfra
    setup_device_registry_listener: SetupDeviceRegistryListener
    remove_device_registry_listener: RemoveDeviceRegistryListener
    has_other_runtime_entries: HasOtherRuntimeEntries
    service_registry: ServiceRegistry


class EntryLifecycleControllerLike(Protocol):
    """Minimal lifecycle-controller surface consumed by HA root adapters."""

    async def async_setup_component(
        self, hass: HomeAssistant, config: object
    ) -> bool: ...

    async def async_setup_entry(self, hass: HomeAssistant, entry: object) -> bool: ...

    async def async_unload_entry(self, hass: HomeAssistant, entry: object) -> bool: ...

    async def async_reload_entry(self, hass: HomeAssistant, entry: object) -> None: ...


class EntryLifecycleControllerFactory(Protocol):
    """Runtime-loaded controller constructor surface."""

    def __call__(
        self,
        *,
        dependencies: EntryLifecycleControllerDependencies,
    ) -> EntryLifecycleControllerLike: ...


def build_service_registry(
    *,
    domain: str,
    registrations: ServiceRegistrationsLike,
    async_setup_services: SetupServicesFn,
    remove_services: RemoveServicesFn,
    get_runtime_infra_lock: GetRuntimeInfraLockFn,
) -> ServiceRegistry:
    """Build the service-registry collaborator consumed by the lifecycle owner."""
    return ServiceRegistry(
        domain=domain,
        public_registrations=registrations.PUBLIC_SERVICE_REGISTRATIONS,
        developer_registrations=registrations.DEVELOPER_SERVICE_REGISTRATIONS,
        service_registrations=registrations.SERVICE_REGISTRATIONS,
        async_setup_services=async_setup_services,
        remove_services=remove_services,
        has_debug_mode_runtime_entry=registrations.has_debug_mode_runtime_entry,
        get_runtime_infra_lock=get_runtime_infra_lock,
    )


def build_entry_lifecycle_controller_dependencies(
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
) -> EntryLifecycleControllerDependencies:
    """Build the stable typed collaborator bundle for one lifecycle owner."""
    return EntryLifecycleControllerDependencies(
        logger=logger,
        platforms=tuple(platforms),
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
        coordinator_factory=coordinator_factory,
        get_client_session=get_client_session,
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
        service_registry=service_registry,
    )


def build_entry_lifecycle_controller(
    *,
    controller_factory: EntryLifecycleControllerFactory,
    controller_dependencies: EntryLifecycleControllerDependencies,
) -> EntryLifecycleControllerLike:
    """Build the runtime lifecycle controller outside the HA root adapter."""
    return controller_factory(dependencies=controller_dependencies)


__all__ = [
    "EntryLifecycleControllerDependencies",
    "EntryLifecycleControllerLike",
    "ServiceRegistrationsLike",
    "build_entry_lifecycle_controller",
    "build_entry_lifecycle_controller_dependencies",
    "build_service_registry",
]
