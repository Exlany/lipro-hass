"""The Lipro Smart Home integration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
import logging
from typing import TYPE_CHECKING, Protocol, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const.base import DOMAIN
from .control.service_registry import ServiceRegistry
from .entry_options import (
    async_reload_entry_if_options_changed as _async_reload_entry_if_options_changed_impl,
    remove_entry_options_snapshot,
    store_entry_options_snapshot as _store_entry_options_snapshot_impl,
)
from .runtime_infra import (
    async_ensure_runtime_infra,
    get_runtime_infra_lock,
    has_other_runtime_entries,
    remove_device_registry_listener,
    setup_device_registry_listener,
)
from .runtime_types import LiproRuntimeCoordinator
from .services.registry import async_setup_services, remove_services

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType



class _CoreModule(Protocol):
    """Runtime-loaded core module surface used by this adapter."""

    LiproAuthManager: Callable[..., object]
    LiproProtocolFacade: Callable[..., object]


class _CoordinatorModule(Protocol):
    """Runtime-loaded coordinator module surface used by this adapter."""

    Coordinator: Callable[..., object]


class _EntryAuthModule(Protocol):
    """Runtime-loaded config-entry auth helpers used by this adapter."""

    async def async_authenticate_entry(self, auth_manager: object) -> None: ...

    def build_entry_auth_context(
        self,
        hass: HomeAssistant,
        entry: LiproConfigEntry,
        *,
        get_client_session: Callable[[HomeAssistant], object],
        client_factory: object,
        auth_manager_factory: object,
        logger: logging.Logger,
    ) -> tuple[object, object]: ...

    def clear_entry_runtime_data(self, entry: LiproConfigEntry) -> None: ...

    def get_entry_int_option(
        self,
        entry: LiproConfigEntry,
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
        entry: LiproConfigEntry,
        auth_manager: object,
    ) -> None: ...


class _ServiceRegistrationsModule(Protocol):
    """Runtime-loaded service registration table surface."""

    PUBLIC_SERVICE_REGISTRATIONS: Sequence[object]
    DEVELOPER_SERVICE_REGISTRATIONS: Sequence[object]
    SERVICE_REGISTRATIONS: Sequence[object]

    def has_debug_mode_runtime_entry(self, hass: HomeAssistant) -> bool: ...


class _EntryLifecycleControllerLike(Protocol):
    """Minimal lifecycle-controller surface consumed by HA root adapters."""

    async def async_setup_component(self, hass: HomeAssistant, config: object) -> bool: ...

    async def async_setup_entry(
        self,
        hass: HomeAssistant,
        entry: LiproConfigEntry,
    ) -> bool: ...

    async def async_unload_entry(
        self,
        hass: HomeAssistant,
        entry: LiproConfigEntry,
    ) -> bool: ...

    async def async_reload_entry(
        self,
        hass: HomeAssistant,
        entry: LiproConfigEntry,
    ) -> None: ...


class _EntryLifecycleControllerFactory(Protocol):
    """Runtime-loaded controller constructor surface."""

    def __call__(self, **kwargs: object) -> _EntryLifecycleControllerLike: ...


class _EntryLifecycleControllerModule(Protocol):
    """Runtime-loaded lifecycle-controller module surface."""

    EntryLifecycleController: _EntryLifecycleControllerFactory


LiproProtocolFacade: Callable[..., object]
LiproAuthManager: Callable[..., object]
Coordinator: Callable[..., object]


_LOGGER = logging.getLogger(__name__)
if not TYPE_CHECKING:
    _CORE_MODULE_NAME = "custom_components.lipro.core"
    _COORDINATOR_MODULE_NAME = "custom_components.lipro.coordinator_entry"

    def _load_module(module_name: str) -> object:
        """Load one module via runtime import only."""
        return __import__(module_name, fromlist=["_"])

    def _load_core_callable(name: str) -> Callable[..., object]:
        """Resolve one core-plane constructor lazily."""
        core_module = cast(_CoreModule, _load_module(_CORE_MODULE_NAME))
        return cast(Callable[..., object], getattr(core_module, name))

    def _build_lipro_protocol_facade(*args: object, **kwargs: object) -> object:
        """Lazy protocol-facade constructor exposed for runtime wiring/tests."""
        return _load_core_callable("LiproProtocolFacade")(*args, **kwargs)

    def _build_lipro_auth_manager(*args: object, **kwargs: object) -> object:
        """Lazy auth-manager constructor exposed for runtime wiring/tests."""
        return _load_core_callable("LiproAuthManager")(*args, **kwargs)

    def _build_coordinator(*args: object, **kwargs: object) -> object:
        """Lazy runtime-coordinator constructor exposed for runtime wiring/tests."""
        coordinator_module = cast(_CoordinatorModule, _load_module(_COORDINATOR_MODULE_NAME))
        return coordinator_module.Coordinator(*args, **kwargs)

    LiproProtocolFacade = _build_lipro_protocol_facade
    LiproAuthManager = _build_lipro_auth_manager
    Coordinator = _build_coordinator
else:

    def _load_module(module_name: str) -> object:
        """Type-checking placeholder for runtime-only module loading."""
        del module_name
        raise NotImplementedError

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

type LiproRuntimeData = LiproRuntimeCoordinator | None
type LiproConfigEntry = ConfigEntry[LiproRuntimeData]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _entry_auth_module() -> _EntryAuthModule:
    """Load entry-auth helpers lazily to keep adapter typing local."""
    return cast(_EntryAuthModule, _load_module("custom_components.lipro.entry_auth"))


def _service_registrations_module() -> _ServiceRegistrationsModule:
    """Load service registration tables lazily for the control-plane adapter."""
    return cast(
        _ServiceRegistrationsModule,
        _load_module("custom_components.lipro.services.registrations"),
    )


def _build_entry_auth_context(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    *,
    get_client_session: Callable[[HomeAssistant], object],
    client_factory: object,
    auth_manager_factory: object,
    logger: logging.Logger,
) -> tuple[object, object]:
    """Adapter wrapper for entry-auth collaborator wiring."""
    return _entry_auth_module().build_entry_auth_context(
        hass,
        entry,
        get_client_session=get_client_session,
        client_factory=client_factory,
        auth_manager_factory=auth_manager_factory,
        logger=logger,
    )


async def _async_authenticate_entry(auth_manager: object) -> None:
    """Adapter wrapper for entry authentication."""
    await _entry_auth_module().async_authenticate_entry(auth_manager)


def _clear_entry_runtime_data(entry: LiproConfigEntry) -> None:
    """Adapter wrapper for runtime-data cleanup."""
    _entry_auth_module().clear_entry_runtime_data(entry)


def _get_entry_int_option(
    entry: LiproConfigEntry,
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


def _persist_entry_tokens_if_changed(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    auth_manager: object,
) -> None:
    """Adapter wrapper for token persistence."""
    _entry_auth_module().persist_entry_tokens_if_changed(hass, entry, auth_manager)


def _store_entry_options_snapshot(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> None:
    """Adapter wrapper for options snapshot storage."""
    _store_entry_options_snapshot_impl(hass, entry)


async def _async_reload_entry_if_options_changed(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> None:
    """Adapter wrapper for option-diff reloads."""
    await _async_reload_entry_if_options_changed_impl(hass, entry)


def _build_service_registry() -> ServiceRegistry:
    registrations = _service_registrations_module()
    return ServiceRegistry(
        domain=DOMAIN,
        public_registrations=registrations.PUBLIC_SERVICE_REGISTRATIONS,
        developer_registrations=registrations.DEVELOPER_SERVICE_REGISTRATIONS,
        service_registrations=registrations.SERVICE_REGISTRATIONS,
        async_setup_services=async_setup_services,
        remove_services=remove_services,
        has_debug_mode_runtime_entry=registrations.has_debug_mode_runtime_entry,
        get_runtime_infra_lock=get_runtime_infra_lock,
    )


def _build_entry_lifecycle_controller() -> _EntryLifecycleControllerLike:
    controller_module = cast(
        _EntryLifecycleControllerModule,
        _load_module("custom_components.lipro.control.entry_lifecycle_controller"),
    )
    controller_factory = controller_module.EntryLifecycleController
    return controller_factory(
        logger=_LOGGER,
        domain=DOMAIN,
        platforms=PLATFORMS,
        client_factory=LiproProtocolFacade,
        auth_manager_factory=LiproAuthManager,
        coordinator_factory=Coordinator,
        get_client_session=async_get_clientsession,
        build_entry_auth_context=_build_entry_auth_context,
        async_authenticate_entry=_async_authenticate_entry,
        clear_entry_runtime_data=_clear_entry_runtime_data,
        get_entry_int_option=_get_entry_int_option,
        persist_entry_tokens_if_changed=_persist_entry_tokens_if_changed,
        store_entry_options_snapshot=_store_entry_options_snapshot,
        remove_entry_options_snapshot=remove_entry_options_snapshot,
        async_reload_entry_if_options_changed=_async_reload_entry_if_options_changed,
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
