"""Login helpers for the Lipro config flow."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Protocol

from homeassistant.data_entry_flow import AbortFlow

from ..const.config import (
    CONF_ACCESS_TOKEN,
    CONF_BIZ_ID,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REMEMBER_PASSWORD_HASH,
    CONF_USER_ID,
)
from ..core.api import LiproApiError, LiproAuthError, LiproConnectionError
from ..core.auth import hash_password_for_auth
from ..core.utils.log_safety import safe_error_placeholder

if TYPE_CHECKING:
    import aiohttp

    from homeassistant.core import HomeAssistant

    from ..core.auth import AuthBootstrapSeed, AuthSessionSnapshot, LiproAuthManager
    from ..core.protocol import LiproProtocolFacade

_LOGGER = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using the host-neutral auth helper."""
    return hash_password_for_auth(password)


def map_login_error(err: LiproApiError) -> str:
    """Map login exception to error key for UI display."""
    if isinstance(err, LiproAuthError):
        _LOGGER.warning("Authentication failed (%s)", safe_error_placeholder(err))
        return "invalid_auth"
    if isinstance(err, LiproConnectionError):
        _LOGGER.warning("Connection failed (%s)", safe_error_placeholder(err))
        return "cannot_connect"
    _LOGGER.warning("API error (%s)", safe_error_placeholder(err))
    return "unknown"


class PasswordHashLoginBootContext(Protocol):
    """Minimal boot-context contract needed by the config flow."""

    async def async_login_with_password_hash(self) -> AuthSessionSnapshot:
        """Authenticate using the already-hashed password."""


class BuildHeadlessBootContext(Protocol):
    """Factory contract for the shared headless boot context."""

    def __call__(
        self,
        seed: AuthBootstrapSeed,
        session: aiohttp.ClientSession,
        *,
        protocol_factory: type[LiproProtocolFacade],
        auth_manager_factory: type[LiproAuthManager],
    ) -> PasswordHashLoginBootContext:
        """Build one password-hash login boot context."""


type SessionGetter = Callable[[HomeAssistant], aiohttp.ClientSession]
type BuildPasswordBootSeed = Callable[[str, str, str], AuthBootstrapSeed]
type DoLogin = Callable[[str, str, str], Awaitable[AuthSessionSnapshot]]


async def async_do_hashed_login(
    *,
    hass: HomeAssistant,
    phone: str,
    password_hash: str,
    phone_id: str,
    get_client_session: SessionGetter,
    build_boot_context: BuildHeadlessBootContext,
    build_password_boot_seed: BuildPasswordBootSeed,
    protocol_factory: type[LiproProtocolFacade],
    auth_manager_factory: type[LiproAuthManager],
) -> AuthSessionSnapshot:
    """Perform one hashed-password login through the shared boot contract."""
    session = get_client_session(hass)
    boot_context = build_boot_context(
        build_password_boot_seed(phone, password_hash, phone_id),
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )
    return await boot_context.async_login_with_password_hash()


async def async_try_hashed_login(
    *,
    phone: str,
    password_hash: str,
    phone_id: str,
    errors: dict[str, str],
    context_name: str,
    do_login: DoLogin,
    logger: logging.Logger,
) -> AuthSessionSnapshot | None:
    """Attempt one hashed-password login and fill flow errors on failure."""
    try:
        return await do_login(phone, password_hash, phone_id)
    except LiproApiError as err:
        errors["base"] = map_login_error(err)
    except asyncio.CancelledError:
        raise
    except AbortFlow:
        raise
    except (KeyError, TypeError, ValueError) as err:
        logger.error(
            "Malformed login response during %s (%s)",
            context_name,
            safe_error_placeholder(err),
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )
        errors["base"] = "unknown"
    except (AttributeError, RuntimeError) as err:
        logger.error(
            "Unexpected login failure during %s (%s)",
            context_name,
            safe_error_placeholder(err),
            exc_info=logger.isEnabledFor(logging.DEBUG),
        )
        errors["base"] = "unknown"
    return None


@dataclass(frozen=True, slots=True)
class ConfigEntryLoginProjection:
    """HA config-entry projection derived from the formal auth session."""

    access_token: str
    refresh_token: str
    user_id: int
    biz_id: str | None

    @classmethod
    def from_auth_session(
        cls,
        auth_session: AuthSessionSnapshot,
    ) -> ConfigEntryLoginProjection:
        """Project one formal auth/session snapshot to config-entry payload fields."""
        return cls(
            access_token=auth_session.access_token or "",
            refresh_token=auth_session.refresh_token or "",
            user_id=auth_session.user_id or 0,
            biz_id=auth_session.biz_id,
        )

    def to_entry_data(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        *,
        remember_password_hash: bool,
    ) -> dict[str, object]:
        """Convert the HA projection to config-entry data."""
        entry_data: dict[str, object] = {
            CONF_PHONE: phone,
            CONF_PHONE_ID: phone_id,
            CONF_ACCESS_TOKEN: self.access_token,
            CONF_REFRESH_TOKEN: self.refresh_token,
            CONF_USER_ID: self.user_id,
            CONF_BIZ_ID: self.biz_id,
            CONF_REMEMBER_PASSWORD_HASH: remember_password_hash,
        }
        if remember_password_hash:
            entry_data[CONF_PASSWORD_HASH] = password_hash
        return entry_data
