"""Localized lazy-loading and entry-auth helpers for the HA root adapter."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from importlib import import_module
import logging
from typing import TYPE_CHECKING, Protocol, cast

from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from .entry_root_wiring import EntryLifecycleControllerFactory
    from .service_registry import ServiceRegistry


class _CoreModule(Protocol):
    """Runtime-loaded core module surface used by the HA root adapter."""

    LiproAuthManager: Callable[..., object]
    LiproProtocolFacade: Callable[..., object]


class _CoordinatorModule(Protocol):
    """Runtime-loaded coordinator module surface used by the HA root adapter."""

    Coordinator: Callable[..., object]


class _EntryAuthModule(Protocol):
    """Runtime-loaded config-entry auth helpers used by the HA root adapter."""

    async def async_authenticate_entry(self, auth_manager: object) -> None: ...

    def build_entry_auth_context(
        self,
        hass: HomeAssistant,
        entry: object,
        *,
        get_client_session: Callable[[HomeAssistant], object],
        protocol_factory: object,
        auth_manager_factory: object,
        logger: logging.Logger,
    ) -> tuple[object, object]: ...

    def clear_entry_runtime_data(self, entry: object) -> None: ...

    def get_entry_int_option(
        self,
        entry: object,
        *,
        option_name: str,
        default: int,
        min_value: int,
        max_value: int,
        logger: logging.Logger,
    ) -> int: ...

    def persist_entry_tokens_if_changed(
        self,
        hass: HomeAssistant,
        entry: object,
        auth_manager: object,
    ) -> None: ...


class _ServiceRegistrationsModule(Protocol):
    """Runtime-loaded formal control-plane service-registry surface."""

    PUBLIC_SERVICE_REGISTRATIONS: Sequence[object]
    DEVELOPER_SERVICE_REGISTRATIONS: Sequence[object]
    SERVICE_REGISTRATIONS: Sequence[object]

    def build_default_service_registry(
        self,
        *,
        domain: str,
        public_registrations: Sequence[object],
        developer_registrations: Sequence[object],
        service_registrations: Sequence[object],
        get_runtime_infra_lock: Callable[[HomeAssistant], object],
    ) -> ServiceRegistry: ...


class _EntryLifecycleControllerModule(Protocol):
    """Runtime-loaded lifecycle-controller module surface used by the root adapter."""

    EntryLifecycleController: EntryLifecycleControllerFactory


_CORE_MODULE_NAME = "custom_components.lipro.core"
_COORDINATOR_MODULE_NAME = "custom_components.lipro.coordinator_entry"
_ENTRY_AUTH_MODULE_NAME = "custom_components.lipro.entry_auth"
_SERVICE_REGISTRY_MODULE_NAME = "custom_components.lipro.control.service_registry"


def _load_module(module_name: str) -> object:
    """Load one module via runtime import only."""
    return import_module(module_name)


def _core_module() -> _CoreModule:
    """Return the lazily imported core module."""
    return cast(_CoreModule, _load_module(_CORE_MODULE_NAME))


def _coordinator_module() -> _CoordinatorModule:
    """Return the lazily imported coordinator-entry module."""
    return cast(_CoordinatorModule, _load_module(_COORDINATOR_MODULE_NAME))


def _service_registrations_module() -> _ServiceRegistrationsModule:
    """Return the lazily imported service-registry module."""
    return cast(
        _ServiceRegistrationsModule, _load_module(_SERVICE_REGISTRY_MODULE_NAME)
    )


def _entry_lifecycle_controller_module() -> _EntryLifecycleControllerModule:
    """Return the lazily imported lifecycle-controller module."""
    return cast(
        _EntryLifecycleControllerModule,
        _load_module("custom_components.lipro.control.entry_lifecycle_controller"),
    )


def _load_core_callable(name: str) -> Callable[..., object]:
    """Resolve one core-plane constructor lazily."""
    return cast(Callable[..., object], getattr(_core_module(), name))


def build_lipro_protocol_facade(*args: object, **kwargs: object) -> object:
    """Lazy protocol-facade constructor exposed for runtime wiring/tests."""
    return _load_core_callable("LiproProtocolFacade")(*args, **kwargs)


def build_lipro_auth_manager(*args: object, **kwargs: object) -> object:
    """Lazy auth-manager constructor exposed for runtime wiring/tests."""
    return _load_core_callable("LiproAuthManager")(*args, **kwargs)


def build_coordinator(*args: object, **kwargs: object) -> object:
    """Lazy runtime-coordinator constructor exposed for runtime wiring/tests."""
    return _coordinator_module().Coordinator(*args, **kwargs)


def _entry_auth_module() -> _EntryAuthModule:
    """Load entry-auth helpers lazily to keep adapter typing local."""
    return cast(_EntryAuthModule, _load_module(_ENTRY_AUTH_MODULE_NAME))


def build_entry_auth_context(
    hass: HomeAssistant,
    entry: object,
    *,
    get_client_session: Callable[[HomeAssistant], object],
    protocol_factory: object,
    auth_manager_factory: object,
    logger: logging.Logger,
) -> tuple[object, object]:
    """Adapter wrapper for entry-auth collaborator wiring."""
    return _entry_auth_module().build_entry_auth_context(
        hass,
        entry,
        get_client_session=get_client_session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
        logger=logger,
    )


async def async_authenticate_entry(auth_manager: object) -> None:
    """Adapter wrapper for entry authentication."""
    await _entry_auth_module().async_authenticate_entry(auth_manager)


def clear_entry_runtime_data(entry: object) -> None:
    """Adapter wrapper for runtime-data cleanup."""
    _entry_auth_module().clear_entry_runtime_data(entry)


def get_entry_int_option(
    entry: object,
    *,
    option_name: str,
    default: int,
    min_value: int,
    max_value: int,
    logger: logging.Logger,
) -> int:
    """Adapter wrapper for typed option coercion."""
    return _entry_auth_module().get_entry_int_option(
        entry,
        option_name=option_name,
        default=default,
        min_value=min_value,
        max_value=max_value,
        logger=logger,
    )


def persist_entry_tokens_if_changed(
    hass: HomeAssistant,
    entry: object,
    auth_manager: object,
) -> None:
    """Adapter wrapper for token persistence."""
    _entry_auth_module().persist_entry_tokens_if_changed(hass, entry, auth_manager)


def build_service_registry(
    *,
    domain: str,
    get_runtime_infra_lock: Callable[[HomeAssistant], object],
) -> ServiceRegistry:
    """Build the formal service registry for the HA root adapter."""
    registrations = _service_registrations_module()
    return registrations.build_default_service_registry(
        domain=domain,
        public_registrations=registrations.PUBLIC_SERVICE_REGISTRATIONS,
        developer_registrations=registrations.DEVELOPER_SERVICE_REGISTRATIONS,
        service_registrations=registrations.SERVICE_REGISTRATIONS,
        get_runtime_infra_lock=get_runtime_infra_lock,
    )


def load_entry_lifecycle_controller_factory() -> EntryLifecycleControllerFactory:
    """Return the lazy lifecycle-controller factory for the HA root adapter."""
    return _entry_lifecycle_controller_module().EntryLifecycleController


__all__ = [
    "async_authenticate_entry",
    "build_coordinator",
    "build_entry_auth_context",
    "build_lipro_auth_manager",
    "build_lipro_protocol_facade",
    "build_service_registry",
    "clear_entry_runtime_data",
    "get_entry_int_option",
    "load_entry_lifecycle_controller_factory",
    "persist_entry_tokens_if_changed",
]
