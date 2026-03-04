"""The Lipro Smart Home integration."""

from __future__ import annotations

from contextlib import suppress
import logging
from typing import TYPE_CHECKING, Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
)
from .core import (
    LiproAuthError,
    LiproAuthManager,
    LiproClient,
    LiproConnectionError,
    LiproDataUpdateCoordinator,
)
from .helpers.options import coerce_int_option
from .services.entrypoints import (
    async_setup_services as _async_setup_services,
    remove_services as _remove_services,
)
from .services.maintenance import (
    async_setup_device_registry_listener as _async_setup_device_registry_listener_service,
)

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

# Supported platforms (using Platform enum per HA best practices)
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

type LiproConfigEntry = ConfigEntry[LiproDataUpdateCoordinator]

FIRMWARE_SUPPORT_MANIFEST: Final = "firmware_support_manifest.json"
_DATA_DEVICE_REGISTRY_LISTENER_UNSUB: Final = "device_registry_listener_unsub"


def _get_entry_int_option(
    entry: LiproConfigEntry,
    *,
    option_name: str,
    default: int,
    min_value: int,
    max_value: int,
) -> int:
    """Read and coerce an integer option from a config entry."""
    return coerce_int_option(
        entry.options.get(option_name, default),
        option_name=option_name,
        default=default,
        min_value=min_value,
        max_value=max_value,
        logger=_LOGGER,
    )


def _async_setup_device_registry_listener(hass: HomeAssistant) -> None:
    """Set up one shared device-registry listener for Lipro entries."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not isinstance(domain_data, dict):
        return
    if _DATA_DEVICE_REGISTRY_LISTENER_UNSUB in domain_data:
        return

    domain_data[_DATA_DEVICE_REGISTRY_LISTENER_UNSUB] = (
        _async_setup_device_registry_listener_service(
            hass,
            domain=DOMAIN,
            logger=_LOGGER,
            reload_entry=hass.config_entries.async_reload,
        )
    )


def _async_remove_device_registry_listener(hass: HomeAssistant) -> None:
    """Remove the shared device-registry listener if present."""
    domain_data = hass.data.get(DOMAIN)
    if not isinstance(domain_data, dict):
        return

    unsubscribe = domain_data.pop(_DATA_DEVICE_REGISTRY_LISTENER_UNSUB, None)
    if callable(unsubscribe):
        unsubscribe()


async def _async_ensure_runtime_infra(hass: HomeAssistant) -> None:
    """Ensure shared runtime infra (services/listener) is ready."""
    await _async_setup_services(hass)
    _async_setup_device_registry_listener(hass)


def _clear_entry_runtime_data(entry: ConfigEntry) -> None:
    """Clear runtime_data field defensively after failed setup/unload."""
    # Keep the attribute present so callers can safely read `entry.runtime_data`
    # and treat None as "not loaded", without risking AttributeError.
    with suppress(Exception):
        entry.runtime_data = None


def _has_other_runtime_entries(
    hass: HomeAssistant,
    *,
    exclude_entry_id: str,
) -> bool:
    """Return whether another loaded Lipro entry still has runtime data."""
    return any(
        config_entry.entry_id != exclude_entry_id
        and getattr(config_entry, "runtime_data", None) is not None
        for config_entry in hass.config_entries.async_entries(DOMAIN)
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Lipro component."""
    await _async_ensure_runtime_infra(hass)
    return True


def _build_entry_auth_context(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> tuple[LiproClient, LiproAuthManager]:
    """Build API client and auth manager from config entry data."""
    phone_id = entry.data[CONF_PHONE_ID]
    phone = entry.data[CONF_PHONE]
    password_hash = entry.data.get(CONF_PASSWORD_HASH)
    remember_password_hash = entry.data.get(CONF_REMEMBER_PASSWORD_HASH)
    if remember_password_hash is None:
        remember_password_hash = bool(password_hash)

    request_timeout = _get_entry_int_option(
        entry,
        option_name=CONF_REQUEST_TIMEOUT,
        default=DEFAULT_REQUEST_TIMEOUT,
        min_value=MIN_REQUEST_TIMEOUT,
        max_value=MAX_REQUEST_TIMEOUT,
    )

    session = async_get_clientsession(hass)
    client = LiproClient(phone_id, session, request_timeout=request_timeout)
    auth_manager = LiproAuthManager(client)

    if CONF_ACCESS_TOKEN in entry.data and CONF_REFRESH_TOKEN in entry.data:
        auth_manager.set_tokens(
            entry.data[CONF_ACCESS_TOKEN],
            entry.data[CONF_REFRESH_TOKEN],
            entry.data.get(CONF_USER_ID),
            entry.data.get(CONF_EXPIRES_AT),
        )

    if remember_password_hash and isinstance(password_hash, str) and password_hash:
        auth_manager.set_credentials(phone, password_hash, password_is_hashed=True)
    auth_manager.set_tokens_updated_callback(
        lambda: _persist_entry_tokens_if_changed(hass, entry, auth_manager)
    )
    return client, auth_manager


async def _async_authenticate_entry(auth_manager: LiproAuthManager) -> None:
    """Authenticate one config entry and map failures to HA setup exceptions."""
    try:
        await auth_manager.ensure_valid_token()
    except LiproAuthError as err:
        msg = f"Authentication failed: {err}"
        raise ConfigEntryAuthFailed(msg) from err
    except LiproConnectionError as err:
        msg = f"Connection failed: {err}"
        raise ConfigEntryNotReady(msg) from err


def _persist_entry_tokens_if_changed(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    auth_manager: LiproAuthManager,
) -> None:
    """Persist refreshed access/refresh tokens when they changed."""
    auth_data = auth_manager.get_auth_data()
    if not auth_data.get(CONF_ACCESS_TOKEN) or not auth_data.get(CONF_REFRESH_TOKEN):
        return
    if auth_data[CONF_ACCESS_TOKEN] == entry.data.get(CONF_ACCESS_TOKEN) and auth_data[
        CONF_REFRESH_TOKEN
    ] == entry.data.get(CONF_REFRESH_TOKEN):
        return

    hass.config_entries.async_update_entry(
        entry,
        data={
            **entry.data,
            CONF_ACCESS_TOKEN: auth_data[CONF_ACCESS_TOKEN],
            CONF_REFRESH_TOKEN: auth_data[CONF_REFRESH_TOKEN],
            CONF_EXPIRES_AT: auth_data[CONF_EXPIRES_AT],
        },
    )


async def async_setup_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Set up Lipro from a config entry."""
    await _async_ensure_runtime_infra(hass)

    client, auth_manager = _build_entry_auth_context(hass, entry)
    await _async_authenticate_entry(auth_manager)

    # Get scan interval from options (or use default)
    scan_interval = _get_entry_int_option(
        entry,
        option_name=CONF_SCAN_INTERVAL,
        default=DEFAULT_SCAN_INTERVAL,
        min_value=MIN_SCAN_INTERVAL,
        max_value=MAX_SCAN_INTERVAL,
    )

    # Create coordinator with configurable scan interval
    coordinator = LiproDataUpdateCoordinator(
        hass,
        client,
        auth_manager,
        entry,
        update_interval=scan_interval,
    )

    # Fetch initial data and ensure resources are cleaned up on failure.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await coordinator.async_shutdown()
        _clear_entry_runtime_data(entry)
        raise

    # Store coordinator in runtime data
    entry.runtime_data = coordinator

    try:
        # Update stored tokens if they changed
        _persist_entry_tokens_if_changed(hass, entry, auth_manager)
        # Set up platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await coordinator.async_shutdown()
        _clear_entry_runtime_data(entry)
        raise

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> bool:
    """Unload a config entry."""
    result = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Ensure coordinator resources are released on unload.
    if result:
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            await coordinator.async_shutdown()
        _clear_entry_runtime_data(entry)

    # Unregister shared infra when no loaded runtime entry remains.
    if result and not _has_other_runtime_entries(
        hass,
        exclude_entry_id=entry.entry_id,
    ):
        _remove_services(hass)
        _async_remove_device_registry_listener(hass)

    return result


async def async_reload_entry(hass: HomeAssistant, entry: LiproConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
