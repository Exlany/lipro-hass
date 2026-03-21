"""Support-only wiring helpers for the HA root adapter.

`custom_components.lipro.__init__` remains the only HA root adapter home; this
module only carries mechanical controller/service-registry assembly.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
import logging
from typing import Protocol

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .service_registry import ServiceRegistry


class ServiceRegistrationsLike(Protocol):
    """Service-registration table surface consumed by the root wiring helper."""

    PUBLIC_SERVICE_REGISTRATIONS: Sequence[object]
    DEVELOPER_SERVICE_REGISTRATIONS: Sequence[object]
    SERVICE_REGISTRATIONS: Sequence[object]

    def has_debug_mode_runtime_entry(self, hass: HomeAssistant) -> bool:
        """Return whether at least one runtime entry is in debug mode."""


def build_service_registry(
    *,
    domain: str,
    registrations: ServiceRegistrationsLike,
    async_setup_services: Callable[..., object],
    remove_services: Callable[..., object],
    get_runtime_infra_lock: Callable[[HomeAssistant], object],
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


__all__ = [
    "ServiceRegistrationsLike",
    "build_entry_lifecycle_controller_kwargs",
    "build_service_registry",
]
