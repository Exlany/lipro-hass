"""The Lipro Smart Home integration."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Protocol, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const.base import DOMAIN
from .control.entry_root_support import (
    async_authenticate_entry,
    build_coordinator as _build_coordinator,
    build_entry_auth_context,
    build_lipro_auth_manager as _build_lipro_auth_manager,
    build_lipro_protocol_facade as _build_lipro_protocol_facade,
    build_service_registry as _build_service_registry_impl,
    clear_entry_runtime_data,
    get_entry_int_option,
    load_module as _load_module,
    persist_entry_tokens_if_changed,
)
from .control.entry_root_wiring import (
    EntryLifecycleControllerDependencies as _EntryLifecycleControllerDependencies,
    EntryLifecycleControllerLike as _EntryLifecycleControllerLike,
    build_entry_lifecycle_controller as _build_entry_lifecycle_controller_impl,
    build_entry_lifecycle_controller_dependencies as _build_entry_lifecycle_controller_dependencies_impl,
)
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

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

    from .control.service_registry import ServiceRegistry
    from .coordinator_entry import Coordinator as _CoordinatorType
    from .core import (
        LiproAuthManager as _LiproAuthManagerType,
        LiproProtocolFacade as _LiproProtocolFacadeType,
    )


LiproProtocolFacade: Callable[..., object] = _build_lipro_protocol_facade
LiproAuthManager: Callable[..., object] = _build_lipro_auth_manager
Coordinator: Callable[..., object] = _build_coordinator


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

type LiproRuntimeData = LiproRuntimeCoordinator | None
type LiproConfigEntry = ConfigEntry[LiproRuntimeData]

if TYPE_CHECKING:
    from collections.abc import Awaitable

    type ProtocolFactory = Callable[..., _LiproProtocolFacadeType]
    type AuthManagerFactory = Callable[[_LiproProtocolFacadeType], _LiproAuthManagerType]

    class CoordinatorFactory(Protocol):
        """Typed lazy coordinator constructor used only for local casts."""

        def __call__(
            self,
            hass: HomeAssistant,
            protocol: _LiproProtocolFacadeType,
            auth_manager: _LiproAuthManagerType,
            config_entry: LiproConfigEntry,
            *,
            update_interval: int = ...,
        ) -> _CoordinatorType:
            """Return one configured coordinator instance."""

    type BuildEntryAuthContext = Callable[
        ..., tuple[_LiproProtocolFacadeType, _LiproAuthManagerType]
    ]
    type AuthenticateEntry = Callable[[_LiproAuthManagerType], Awaitable[None]]
    type PersistEntryTokens = Callable[
        [HomeAssistant, LiproConfigEntry, _LiproAuthManagerType],
        None,
    ]
    type StoreEntryOptionsSnapshot = Callable[[HomeAssistant, LiproConfigEntry], None]
    type ReloadEntryIfOptionsChanged = Callable[
        [HomeAssistant, LiproConfigEntry], Awaitable[None]
    ]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


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


store_entry_options_snapshot = _store_entry_options_snapshot
async_reload_entry_if_options_changed = _async_reload_entry_if_options_changed


def _build_service_registry() -> ServiceRegistry:
    return _build_service_registry_impl(
        domain=DOMAIN,
        get_runtime_infra_lock=get_runtime_infra_lock,
    )


def _build_entry_lifecycle_controller_dependencies(
) -> _EntryLifecycleControllerDependencies:
    """Build the stable collaborator bundle for one lifecycle-controller instance."""
    return _build_entry_lifecycle_controller_dependencies_impl(
        logger=_LOGGER,
        platforms=PLATFORMS,
        protocol_factory=cast('ProtocolFactory', LiproProtocolFacade),
        auth_manager_factory=cast('AuthManagerFactory', LiproAuthManager),
        coordinator_factory=cast('CoordinatorFactory', Coordinator),
        get_client_session=async_get_clientsession,
        build_entry_auth_context=cast('BuildEntryAuthContext', build_entry_auth_context),
        async_authenticate_entry=cast('AuthenticateEntry', async_authenticate_entry),
        clear_entry_runtime_data=clear_entry_runtime_data,
        get_entry_int_option=get_entry_int_option,
        persist_entry_tokens_if_changed=cast(
            'PersistEntryTokens', persist_entry_tokens_if_changed
        ),
        store_entry_options_snapshot=cast(
            'StoreEntryOptionsSnapshot', store_entry_options_snapshot
        ),
        remove_entry_options_snapshot=remove_entry_options_snapshot,
        async_reload_entry_if_options_changed=cast(
            'ReloadEntryIfOptionsChanged', async_reload_entry_if_options_changed
        ),
        async_ensure_runtime_infra=async_ensure_runtime_infra,
        setup_device_registry_listener=setup_device_registry_listener,
        remove_device_registry_listener=remove_device_registry_listener,
        has_other_runtime_entries=has_other_runtime_entries,
        service_registry=_build_service_registry(),
    )


def _build_entry_lifecycle_controller() -> _EntryLifecycleControllerLike:
    return _build_entry_lifecycle_controller_impl(
        load_module=_load_module,
        controller_module_name='custom_components.lipro.control.entry_lifecycle_controller',
        controller_dependencies=_build_entry_lifecycle_controller_dependencies(),
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
