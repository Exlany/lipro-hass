# ruff: noqa: D102
"""Support-only wiring helpers for the HA root adapter.

`custom_components.lipro.__init__` remains the only HA root adapter home; this
module only carries mechanical controller/service-registry assembly.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import logging
from typing import Protocol, cast

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .service_registry import (
    GetRuntimeInfraLockFn,
    RemoveServicesFn,
    ServiceRegistry,
    SetupServicesFn,
)


class ServiceRegistrationsLike(Protocol):
    """Service-registration table surface consumed by the root wiring helper."""

    PUBLIC_SERVICE_REGISTRATIONS: Sequence[object]
    DEVELOPER_SERVICE_REGISTRATIONS: Sequence[object]
    SERVICE_REGISTRATIONS: Sequence[object]

    def has_debug_mode_runtime_entry(self, hass: HomeAssistant) -> bool:
        """Return whether at least one runtime entry is in debug mode."""


class EntryLifecycleControllerLike(Protocol):
    """Minimal lifecycle-controller surface consumed by HA root adapters."""

    async def async_setup_component(self, hass: HomeAssistant, config: object) -> bool: ...

    async def async_setup_entry(self, hass: HomeAssistant, entry: object) -> bool: ...

    async def async_unload_entry(self, hass: HomeAssistant, entry: object) -> bool: ...

    async def async_reload_entry(self, hass: HomeAssistant, entry: object) -> None: ...


class EntryLifecycleControllerFactory(Protocol):
    """Runtime-loaded controller constructor surface."""

    def __call__(self, **kwargs: object) -> EntryLifecycleControllerLike: ...


class EntryLifecycleControllerModule(Protocol):
    """Runtime-loaded lifecycle-controller module surface."""

    EntryLifecycleController: EntryLifecycleControllerFactory



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



def build_entry_lifecycle_controller_kwargs(
    *,
    logger: logging.Logger,
    domain: str,
    platforms: list[Platform],
    protocol_factory: object,
    auth_manager_factory: object,
    coordinator_factory: object,
    get_client_session: object,
    build_entry_auth_context: object,
    async_authenticate_entry: object,
    clear_entry_runtime_data: object,
    get_entry_int_option: object,
    persist_entry_tokens_if_changed: object,
    store_entry_options_snapshot: object,
    remove_entry_options_snapshot: object,
    async_reload_entry_if_options_changed: object,
    async_ensure_runtime_infra: object,
    setup_device_registry_listener: object,
    remove_device_registry_listener: object,
    has_other_runtime_entries: object,
    service_registry: ServiceRegistry,
) -> dict[str, object]:
    """Build the stable collaborator bundle for one lifecycle-controller instance."""
    return {
        "logger": logger,
        "domain": domain,
        "platforms": platforms,
        "protocol_factory": protocol_factory,
        "auth_manager_factory": auth_manager_factory,
        "coordinator_factory": coordinator_factory,
        "get_client_session": get_client_session,
        "build_entry_auth_context": build_entry_auth_context,
        "async_authenticate_entry": async_authenticate_entry,
        "clear_entry_runtime_data": clear_entry_runtime_data,
        "get_entry_int_option": get_entry_int_option,
        "persist_entry_tokens_if_changed": persist_entry_tokens_if_changed,
        "store_entry_options_snapshot": store_entry_options_snapshot,
        "remove_entry_options_snapshot": remove_entry_options_snapshot,
        "async_reload_entry_if_options_changed": async_reload_entry_if_options_changed,
        "async_ensure_runtime_infra": async_ensure_runtime_infra,
        "setup_device_registry_listener": setup_device_registry_listener,
        "remove_device_registry_listener": remove_device_registry_listener,
        "has_other_runtime_entries": has_other_runtime_entries,
        "service_registry": service_registry,
    }



def build_entry_lifecycle_controller(
    *,
    load_module: Callable[[str], object],
    controller_module_name: str,
    controller_kwargs: dict[str, object],
) -> EntryLifecycleControllerLike:
    """Build the runtime lifecycle controller outside the HA root adapter."""
    controller_module = cast(
        EntryLifecycleControllerModule,
        load_module(controller_module_name),
    )
    controller_factory = controller_module.EntryLifecycleController
    return controller_factory(**controller_kwargs)


__all__ = [
    "EntryLifecycleControllerLike",
    "ServiceRegistrationsLike",
    "build_entry_lifecycle_controller",
    "build_entry_lifecycle_controller_kwargs",
    "build_service_registry",
]
