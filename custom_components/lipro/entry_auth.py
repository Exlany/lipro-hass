"""Config-entry authentication helpers for the Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
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
from .core.auth import AuthBootstrapSeed
from .core.utils.coerce import coerce_int_option
from .core.utils.log_safety import safe_error_placeholder
from .headless.boot import build_headless_boot_context

if TYPE_CHECKING:
    from collections.abc import Callable

    import aiohttp

    from homeassistant.core import HomeAssistant


ConfigEntryLike = ConfigEntry[object]


@dataclass(frozen=True, slots=True)
class EntryCredentialSeedState:
    """Normalized persisted auth-seed state derived from one config entry."""

    password_hash: str | None
    remember_password_hash: bool


def resolve_entry_credential_seed_state(
    entry_data: Mapping[str, object],
) -> EntryCredentialSeedState:
    """Normalize persisted password-hash/remember state from config-entry data."""
    raw_password_hash = entry_data.get(CONF_PASSWORD_HASH)
    password_hash = raw_password_hash if isinstance(raw_password_hash, str) and raw_password_hash else None
    remember_password_hash = entry_data.get(CONF_REMEMBER_PASSWORD_HASH)
    if remember_password_hash is None:
        remember_password_hash = bool(password_hash)
    return EntryCredentialSeedState(
        password_hash=password_hash,
        remember_password_hash=bool(remember_password_hash),
    )


def apply_entry_credential_seed_state(
    entry_data: Mapping[str, object],
    *,
    password_hash: str,
    remember_password_hash: bool,
) -> dict[str, object]:
    """Project persisted password-hash policy into config-entry data."""
    projected = dict(entry_data)
    projected[CONF_REMEMBER_PASSWORD_HASH] = remember_password_hash
    if remember_password_hash:
        projected[CONF_PASSWORD_HASH] = password_hash
    else:
        projected.pop(CONF_PASSWORD_HASH, None)
    return projected


def _require_entry_string(
    entry: ConfigEntryLike,
    *,
    key: str,
    error_message: str,
) -> str:
    """Return one required string field from config-entry data."""
    value = entry.data.get(key)
    if isinstance(value, str) and value:
        return value
    raise ConfigEntryAuthFailed(error_message)


def _optional_entry_string(entry: ConfigEntryLike, *, key: str) -> str | None:
    """Return one optional string field from config-entry data."""
    value = entry.data.get(key)
    return value if isinstance(value, str) else None


def _resolve_entry_password_seed(
    entry: ConfigEntryLike,
) -> EntryCredentialSeedState:
    """Return normalized persisted auth-seed state for auth bootstrap."""
    return resolve_entry_credential_seed_state(entry.data)


def _build_entry_auth_seed(
    entry: ConfigEntryLike,
    *,
    logger: logging.Logger,
) -> AuthBootstrapSeed:
    """Build one host-neutral auth/bootstrap seed from config-entry state."""
    phone_id = _require_entry_string(
        entry,
        key=CONF_PHONE_ID,
        error_message=(
            "Missing phone_id in config entry data; "
            "please remove and re-add the integration"
        ),
    )
    phone = _require_entry_string(
        entry,
        key=CONF_PHONE,
        error_message=(
            "Missing phone in config entry data; please remove and re-add the integration"
        ),
    )
    credential_seed = _resolve_entry_password_seed(entry)
    request_timeout = get_entry_int_option(
        entry,
        option_name=CONF_REQUEST_TIMEOUT,
        default=DEFAULT_REQUEST_TIMEOUT,
        min_value=MIN_REQUEST_TIMEOUT,
        max_value=MAX_REQUEST_TIMEOUT,
        logger=logger,
    )
    return AuthBootstrapSeed(
        phone=phone,
        phone_id=phone_id,
        password_hash=credential_seed.password_hash,
        remember_password_hash=credential_seed.remember_password_hash,
        request_timeout=request_timeout,
        entry_id=entry.entry_id,
        access_token=_optional_entry_string(entry, key=CONF_ACCESS_TOKEN),
        refresh_token=_optional_entry_string(entry, key=CONF_REFRESH_TOKEN),
        user_id=entry.data.get(CONF_USER_ID),
        expires_at=entry.data.get(CONF_EXPIRES_AT),
        biz_id=_optional_entry_string(entry, key=CONF_BIZ_ID),
    )


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
    protocol_factory: type[LiproProtocolFacade],
    auth_manager_factory: type[LiproAuthManager],
    logger: logging.Logger,
) -> tuple[LiproProtocolFacade, LiproAuthManager]:
    """Build protocol facade and auth manager from config entry data."""
    seed = _build_entry_auth_seed(entry, logger=logger)
    session = get_client_session(hass)
    boot_context = build_headless_boot_context(
        seed,
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )
    boot_context.auth_manager.set_tokens_updated_callback(
        partial(
            persist_entry_tokens_if_changed,
            hass,
            entry,
            boot_context.auth_manager,
        )
    )
    return boot_context.protocol, boot_context.auth_manager


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
    else:
        updated_data.pop(CONF_BIZ_ID, None)

    hass.config_entries.async_update_entry(
        entry,
        data=updated_data,
    )


def clear_entry_runtime_data(entry: ConfigEntryLike) -> None:
    """Clear runtime_data field defensively after failed setup/unload."""
    with suppress(AttributeError):
        entry.runtime_data = None
