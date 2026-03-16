"""Login helpers for the Lipro config flow."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

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
    from ..core.auth import AuthSessionSnapshot

_LOGGER = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using the host-neutral auth helper."""
    return hash_password_for_auth(password)


def map_login_error(err: LiproApiError) -> str:
    """Map login exception to error key for UI display."""
    if isinstance(err, LiproAuthError):
        _LOGGER.warning('Authentication failed (%s)', safe_error_placeholder(err))
        return 'invalid_auth'
    if isinstance(err, LiproConnectionError):
        _LOGGER.warning('Connection failed (%s)', safe_error_placeholder(err))
        return 'cannot_connect'
    _LOGGER.warning('API error (%s)', safe_error_placeholder(err))
    return 'unknown'


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
            access_token=auth_session.access_token or '',
            refresh_token=auth_session.refresh_token or '',
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
