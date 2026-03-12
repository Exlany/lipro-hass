"""Login helpers for the Lipro config flow."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

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
from ..core.utils.log_safety import safe_error_placeholder
from ..core.utils.vendor_crypto import md5_compat_hexdigest

_LOGGER = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using the vendor-mandated MD5 compatibility digest."""
    return md5_compat_hexdigest(password)


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


@dataclass
class LoginResult:
    """Result of a successful login."""

    access_token: str
    refresh_token: str
    user_id: int
    biz_id: str | None

    def to_entry_data(
        self,
        phone: str,
        password_hash: str,
        phone_id: str,
        *,
        remember_password_hash: bool,
    ) -> dict[str, Any]:
        """Convert to config entry data dict."""
        entry_data: dict[str, Any] = {
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
