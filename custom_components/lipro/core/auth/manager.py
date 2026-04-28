"""Authentication manager for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import logging
import time
from typing import TYPE_CHECKING

from ...const.api import ERROR_REFRESH_TOKEN_EXPIRED
from ...const.config import CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, CONF_USER_ID
from ..api import LiproAuthError, LiproRefreshTokenExpiredError
from ..protocol import LiproProtocolFacade
from ..utils.log_safety import safe_error_placeholder
from .manager_support import (
    StoredCredentials,
    TokenLeaseState,
    optional_int,
    optional_text,
    require_text,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    import asyncio
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class AuthSessionSnapshot:
    """Formal auth/session contract consumed by HA adapters and control code."""

    access_token: str | None
    refresh_token: str | None
    user_id: int | None
    expires_at: float | None
    phone_id: str | None
    biz_id: str | None = None

    @property
    def has_tokens(self) -> bool:
        """Return whether both access and refresh tokens are present."""
        return bool(self.access_token and self.refresh_token)


class LiproAuthManager:
    """Manage auth/login/refresh orchestration above the protocol client."""

    def __init__(self, client: LiproProtocolFacade) -> None:
        """Bind one protocol facade and initialize manager-owned auth state."""
        self._client = client
        self._credentials = StoredCredentials()
        self._lease = TokenLeaseState()
        self._session = AuthSessionSnapshot(
            access_token=self._client_text_or_cached("access_token", None),
            refresh_token=self._client_text_or_cached("refresh_token", None),
            user_id=self._client_int_or_cached("user_id", None),
            expires_at=None,
            phone_id=self._client_text_or_cached("phone_id", None),
            biz_id=self._client_text_or_cached("biz_id", None),
        )
        self._on_tokens_updated: Callable[[], None] | None = None
        self._client.set_token_refresh_callback(self._do_token_refresh)

    @property
    def _phone(self) -> str | None:
        return self._credentials.phone

    @_phone.setter
    def _phone(self, value: str | None) -> None:
        self._credentials.phone = value

    @property
    def _password(self) -> str | None:
        return self._credentials.password

    @_password.setter
    def _password(self, value: str | None) -> None:
        self._credentials.password = value

    @property
    def _password_is_hashed(self) -> bool:
        return self._credentials.password_is_hashed

    @_password_is_hashed.setter
    def _password_is_hashed(self, value: bool) -> None:
        self._credentials.password_is_hashed = value

    @property
    def _token_expires_at(self) -> float:
        return self._lease.expires_at

    @_token_expires_at.setter
    def _token_expires_at(self, value: float) -> None:
        self._lease.expires_at = value

    @property
    def _current_expiry_seconds(self) -> int:
        return self._lease.current_expiry_seconds

    @_current_expiry_seconds.setter
    def _current_expiry_seconds(self, value: int) -> None:
        self._lease.current_expiry_seconds = value

    @property
    def _last_refresh_time(self) -> float:
        return self._lease.last_refresh_time

    @_last_refresh_time.setter
    def _last_refresh_time(self, value: float) -> None:
        self._lease.last_refresh_time = value

    @property
    def _refresh_lock(self) -> asyncio.Lock:
        return self._lease.refresh_lock

    def set_tokens_updated_callback(self, callback: Callable[[], None] | None) -> None:
        """Set a callback invoked after tokens are refreshed/login succeeds."""
        self._on_tokens_updated = callback

    def _notify_tokens_updated(self) -> None:
        """Invoke token-updated callback when set."""
        if self._on_tokens_updated is None:
            return
        try:
            self._on_tokens_updated()
        except (
            AttributeError,
            LookupError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as err:
            _LOGGER.debug(
                "Token-updated callback failed (%s)",
                safe_error_placeholder(err),
            )

    def _client_text_or_cached(self, attr_name: str, cached: str | None) -> str | None:
        """Read one client text attribute, falling back when mocks return sentinels."""
        value = getattr(self._client, attr_name, None)
        return value if value is None or isinstance(value, str) else cached

    def _client_int_or_cached(self, attr_name: str, cached: int | None) -> int | None:
        """Read one client integer attribute, preserving explicit `None` clears."""
        value = getattr(self._client, attr_name, None)
        if value is None:
            return None
        normalized = optional_int(value)
        return normalized if normalized is not None else cached

    def _remember_session(
        self,
        *,
        access_token: str | None,
        refresh_token: str | None,
        user_id: int | None,
        expires_at: float | None,
        biz_id: str | None,
    ) -> None:
        """Persist the canonical auth/session snapshot owned by the manager."""
        self._session = AuthSessionSnapshot(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            expires_at=expires_at,
            phone_id=self._client_text_or_cached("phone_id", self._session.phone_id),
            biz_id=biz_id,
        )

    @property
    def is_authenticated(self) -> bool:
        """Check if we have valid tokens."""
        return self.get_auth_session().access_token is not None

    @property
    def token_expires_at(self) -> float:
        """Return token expiry timestamp."""
        return self._lease.expires_at

    @property
    def current_expiry_seconds(self) -> int:
        """Return current adaptive expiry time in seconds."""
        return self._lease.current_expiry_seconds

    def set_credentials(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> None:
        """Store credentials for re-authentication."""
        self._credentials.set(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        expires_at: float | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Set authentication tokens."""
        self._client.set_tokens(access_token, refresh_token, user_id, biz_id)
        self._lease.record_restored_tokens(now=time.time(), expires_at=expires_at)
        self._remember_session(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            expires_at=self._lease.expires_at,
            biz_id=biz_id,
        )

    def _sync_client_tokens_from_result(
        self,
        result: Mapping[str, object],
        *,
        expires_at: float | None,
    ) -> None:
        """Apply one formal login/refresh result to the protocol client state."""
        access_token = require_text(
            result.get(CONF_ACCESS_TOKEN),
            field_name=CONF_ACCESS_TOKEN,
        )
        refresh_token = require_text(
            result.get(CONF_REFRESH_TOKEN),
            field_name=CONF_REFRESH_TOKEN,
        )
        user_id = optional_int(result.get(CONF_USER_ID))
        biz_id = optional_text(result.get("biz_id"))
        self._client.set_tokens(access_token, refresh_token, user_id, biz_id)
        self._remember_session(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            expires_at=expires_at,
            biz_id=biz_id,
        )

    def get_auth_session(self) -> AuthSessionSnapshot:
        """Return the current formal auth/session snapshot."""
        return AuthSessionSnapshot(
            access_token=self._client_text_or_cached(
                "access_token",
                self._session.access_token,
            ),
            refresh_token=self._client_text_or_cached(
                "refresh_token",
                self._session.refresh_token,
            ),
            user_id=self._client_int_or_cached("user_id", self._session.user_id),
            expires_at=self._lease.expires_at or self._session.expires_at,
            phone_id=self._client_text_or_cached("phone_id", self._session.phone_id),
            biz_id=self._client_text_or_cached("biz_id", self._session.biz_id),
        )

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> AuthSessionSnapshot:
        """Login with credentials."""
        self.set_credentials(phone, password, password_is_hashed=password_is_hashed)
        result = await self._client.login(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )
        self._lease.record_login(now=time.time())
        self._sync_client_tokens_from_result(result, expires_at=self._lease.expires_at)
        _LOGGER.debug(
            "Login successful, token expires in %d seconds",
            self._lease.current_expiry_seconds,
        )
        self._notify_tokens_updated()
        return self.get_auth_session()

    def _has_stored_credentials(self) -> bool:
        return self._credentials.is_available

    async def _login_with_stored_credentials(self) -> AuthSessionSnapshot:
        if not self._has_stored_credentials():
            msg = "Not authenticated and no credentials available"
            raise LiproAuthError(msg)
        phone = self._credentials.phone
        password = self._credentials.password
        if phone is None or password is None:
            msg = "Stored credentials became unavailable during re-login"
            raise LiproAuthError(msg)
        return await self.login(
            phone,
            password,
            password_is_hashed=self._credentials.password_is_hashed,
        )

    async def refresh_token(self) -> AuthSessionSnapshot:
        """Refresh the access token."""
        try:
            result = await self._client.refresh_access_token()
            self._lease.record_refresh(now=time.time())
            self._sync_client_tokens_from_result(
                result,
                expires_at=self._lease.expires_at,
            )
            _LOGGER.debug(
                "Token refreshed, expires in %d seconds",
                self._lease.current_expiry_seconds,
            )
            self._notify_tokens_updated()
            return self.get_auth_session()
        except LiproAuthError as err:
            if err.code in ERROR_REFRESH_TOKEN_EXPIRED:
                _LOGGER.warning(
                    "Refresh token expired (code: %s), re-login required",
                    err.code,
                )
                if self._has_stored_credentials():
                    _LOGGER.info("Attempting re-login with stored credentials")
                    return await self._login_with_stored_credentials()
                msg = "Refresh token expired"
                raise LiproRefreshTokenExpiredError(msg, err.code) from err
            if self._has_stored_credentials():
                _LOGGER.warning("Token refresh failed, attempting re-login")
                return await self._login_with_stored_credentials()
            raise

    def _adjust_expiry_on_401(self) -> None:
        """Adjust token expiry when 401 is received before expected expiry."""
        updated = self._lease.adjust_expiry_on_401(now=time.time())
        if updated is None:
            return
        previous, new = updated
        _LOGGER.info(
            "Adaptive expiry: reducing from %d to %d seconds (401 before expected expiry)",
            previous,
            new,
        )

    async def _do_token_refresh(self) -> None:
        """Internal callback for automatic 401 handling."""
        async with self._refresh_lock:
            now = time.time()
            if self._lease.recently_refreshed(now=now):
                _LOGGER.debug(
                    "Token was refreshed %d seconds ago, skipping",
                    int(now - self._lease.last_refresh_time),
                )
                return
            _LOGGER.debug("Automatic token refresh triggered by 401")
            self._adjust_expiry_on_401()
            await self.refresh_token()

    async def async_ensure_authenticated(self) -> None:
        """Compatibility wrapper used by coordinator update flows."""
        await self.ensure_valid_token()

    async def ensure_valid_token(self) -> None:
        """Ensure we have a valid token, refreshing if needed."""
        if not self.is_authenticated:
            async with self._refresh_lock:
                if not self.is_authenticated:
                    await self._login_with_stored_credentials()
                    return
        if not self._lease.needs_refresh(now=time.time()):
            return
        async with self._refresh_lock:
            remaining = int(self._lease.expires_at - time.time())
            if not self.is_authenticated:
                await self._login_with_stored_credentials()
                return
            if self._lease.needs_refresh(now=time.time()):
                _LOGGER.debug(
                    "Token expiring in %d seconds, refreshing proactively",
                    remaining,
                )
                await self.refresh_token()
