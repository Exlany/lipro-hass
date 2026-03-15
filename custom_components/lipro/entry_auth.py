"""Config-entry authentication helpers for the Lipro integration."""

from __future__ import annotations

from contextlib import suppress
from functools import partial
import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .const.config import (
    CONF_ACCESS_TOKEN,
    CONF_BIZ_ID,
    CONF_EXPIRES_AT,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_REQUEST_TIMEOUT,
    CONF_USER_ID,
    DEFAULT_REQUEST_TIMEOUT,
    MAX_REQUEST_TIMEOUT,
    MIN_REQUEST_TIMEOUT,
)
from .core import (
    LiproAuthError,
    LiproAuthManager,
    LiproConnectionError,
    LiproProtocolFacade,
)
from .core.utils.coerce import coerce_int_option
from .core.utils.log_safety import safe_error_placeholder

if TYPE_CHECKING:
    from collections.abc import Callable

    import aiohttp

    from homeassistant.core import HomeAssistant


ConfigEntryLike = ConfigEntry[object]


def get_entry_int_option(
    entry: ConfigEntryLike,
    *,
    option_name: str,
    default: int,
    min_value: int,
    max_value: int,
    logger: logging.Logger,
) -> int:
    """Read and coerce an integer option from a config entry."""
    return coerce_int_option(
        entry.options.get(option_name, default),
        option_name=option_name,
        default=default,
        min_value=min_value,
        max_value=max_value,
        logger=logger,
    )


def build_entry_auth_context(
    hass: HomeAssistant,
    entry: ConfigEntryLike,
    *,
    get_client_session: Callable[[HomeAssistant], aiohttp.ClientSession],
    client_factory: type[LiproProtocolFacade],
    auth_manager_factory: type[LiproAuthManager],
    logger: logging.Logger,
) -> tuple[LiproProtocolFacade, LiproAuthManager]:
    """Build API client and auth manager from config entry data."""
    phone_id = entry.data.get(CONF_PHONE_ID)
    phone = entry.data.get(CONF_PHONE)
    if not isinstance(phone_id, str) or not phone_id:
        msg = (
            "Missing phone_id in config entry data; "
            "please remove and re-add the integration"
        )
        raise ConfigEntryAuthFailed(msg)
    if not isinstance(phone, str) or not phone:
        msg = "Missing phone in config entry data; please remove and re-add the integration"
        raise ConfigEntryAuthFailed(msg)

    password_hash = entry.data.get(CONF_PASSWORD_HASH)
    remember_password_hash = entry.data.get(CONF_REMEMBER_PASSWORD_HASH)
    if remember_password_hash is None:
        remember_password_hash = bool(password_hash)

    request_timeout = get_entry_int_option(
        entry,
        option_name=CONF_REQUEST_TIMEOUT,
        default=DEFAULT_REQUEST_TIMEOUT,
        min_value=MIN_REQUEST_TIMEOUT,
        max_value=MAX_REQUEST_TIMEOUT,
        logger=logger,
    )

    session = get_client_session(hass)
    client = client_factory(
        phone_id,
        session,
        request_timeout=request_timeout,
        entry_id=entry.entry_id,
    )
    auth_manager = auth_manager_factory(client)

    if CONF_ACCESS_TOKEN in entry.data and CONF_REFRESH_TOKEN in entry.data:
        auth_manager.set_tokens(
            entry.data[CONF_ACCESS_TOKEN],
            entry.data[CONF_REFRESH_TOKEN],
            entry.data.get(CONF_USER_ID),
            entry.data.get(CONF_EXPIRES_AT),
            entry.data.get(CONF_BIZ_ID),
        )

    if remember_password_hash and isinstance(password_hash, str) and password_hash:
        auth_manager.set_credentials(phone, password_hash, password_is_hashed=True)
    auth_manager.set_tokens_updated_callback(
        partial(persist_entry_tokens_if_changed, hass, entry, auth_manager)
    )
    return client, auth_manager


async def async_authenticate_entry(auth_manager: LiproAuthManager) -> None:
    """Authenticate one config entry and map failures to HA setup exceptions."""
    try:
        await auth_manager.ensure_valid_token()
    except LiproAuthError as err:
        msg = f"Authentication failed ({safe_error_placeholder(err)})"
        raise ConfigEntryAuthFailed(msg) from err
    except LiproConnectionError as err:
        msg = f"Connection failed ({safe_error_placeholder(err)})"
        raise ConfigEntryNotReady(msg) from err


def persist_entry_tokens_if_changed(
    hass: HomeAssistant,
    entry: ConfigEntryLike,
    auth_manager: LiproAuthManager,
) -> None:
    """Persist refreshed access/refresh tokens when they changed."""
    auth_session = auth_manager.get_auth_session()
    access_token = auth_session.access_token
    refresh_token = auth_session.refresh_token
    expires_at = auth_session.expires_at
    biz_id = auth_session.biz_id

    if not isinstance(access_token, str) or not access_token:
        return
    if not isinstance(refresh_token, str) or not refresh_token:
        return
    if (
        access_token == entry.data.get(CONF_ACCESS_TOKEN)
        and refresh_token == entry.data.get(CONF_REFRESH_TOKEN)
        and biz_id == entry.data.get(CONF_BIZ_ID)
    ):
        return

    updated_data = {
        **entry.data,
        CONF_ACCESS_TOKEN: access_token,
        CONF_REFRESH_TOKEN: refresh_token,
        CONF_EXPIRES_AT: expires_at,
    }
    if isinstance(biz_id, str) and biz_id:
        updated_data[CONF_BIZ_ID] = biz_id

    hass.config_entries.async_update_entry(
        entry,
        data=updated_data,
    )


def clear_entry_runtime_data(entry: ConfigEntryLike) -> None:
    """Clear runtime_data field defensively after failed setup/unload."""
    with suppress(AttributeError):
        entry.runtime_data = None
