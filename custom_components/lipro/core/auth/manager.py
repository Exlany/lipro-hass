"""Authentication manager for Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import logging
import time
from typing import TYPE_CHECKING

from ...const.api import (
    ACCESS_TOKEN_EXPIRY_SECONDS,
    ERROR_REFRESH_TOKEN_EXPIRED,
    TOKEN_EXPIRY_MIN,
    TOKEN_EXPIRY_REDUCTION_FACTOR,
    TOKEN_REFRESH_BUFFER,
    TOKEN_REFRESH_DEDUP_WINDOW,
)
from ...const.config import CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, CONF_USER_ID
from ..api import LiproAuthError, LiproRefreshTokenExpiredError
from ..protocol import LiproProtocolFacade
from ..utils.log_safety import safe_error_placeholder

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
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




def _require_text(value: object, *, field_name: str) -> str:
    """Return one required text field from a protocol result mapping."""
    if isinstance(value, str):
        return value
    msg = f"Missing or invalid {field_name} in auth result"
    raise TypeError(msg)


def _optional_text(value: object) -> str | None:
    """Return one optional text field when present."""
    return value if isinstance(value, str) else None


def _optional_int(value: object) -> int | None:
    """Return one optional integer field when present."""
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


class LiproAuthManager:
    """Manages authentication and token refresh for Lipro API.

    Implements:
    - Thread-safe token refresh with asyncio.Lock
    - Adaptive token expiry based on 401 frequency
    - Automatic re-login when refresh token expires
    """

    def __init__(self, client: LiproProtocolFacade) -> None:
        """Initialize the auth manager.

        Args:
            client: The Lipro API client.

        """
        self._client = client
        self._token_expires_at: float = 0
        self._phone: str | None = None
        self._password: str | None = None
        self._password_is_hashed: bool = False
        # Adaptive expiry: start with default, reduce on 401
        self._current_expiry_seconds: int = ACCESS_TOKEN_EXPIRY_SECONDS
        # Last refresh timestamp (for deduplication)
        self._last_refresh_time: float = 0
        # Lock to prevent concurrent token refreshes
        self._refresh_lock: asyncio.Lock = asyncio.Lock()
        # Optional callback invoked after successful token refresh/login.
        self._on_tokens_updated: Callable[[], None] | None = None

        # Register this manager's refresh method as the client's callback
        self._client.set_token_refresh_callback(self._do_token_refresh)

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

    @property
    def is_authenticated(self) -> bool:
        """Check if we have valid tokens."""
        return self._client.access_token is not None

    @property
    def token_expires_at(self) -> float:
        """Return token expiry timestamp."""
        return self._token_expires_at

    @property
    def current_expiry_seconds(self) -> int:
        """Return current adaptive expiry time in seconds."""
        return self._current_expiry_seconds

    def set_credentials(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> None:
        """Store credentials for re-authentication.

        Always stores the MD5 hash, never plaintext password.

        Args:
            phone: Phone number.
            password: Password (plain text or MD5 hash).
            password_is_hashed: If True, password is already MD5 hashed.

        """
        self._phone = phone
        if password_is_hashed:
            self._password = password
        else:
            self._password = hashlib.md5(
                password.encode("utf-8"), usedforsecurity=False
            ).hexdigest()
        self._password_is_hashed = True

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        expires_at: float | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Set authentication tokens.

        Args:
            access_token: The access token.
            refresh_token: The refresh token.
            user_id: Optional user ID.
            expires_at: Optional expiry timestamp.

        """
        self._client.set_tokens(access_token, refresh_token, user_id, biz_id)
        # Use expires_at if provided and valid (not None and not 0)
        if expires_at is not None and expires_at > 0:
            self._token_expires_at = expires_at
        else:
            self._token_expires_at = time.time() + self._current_expiry_seconds
        # Persisted tokens may be stale; do not mark as "just refreshed".
        # This keeps the first runtime 401 eligible for an immediate refresh.
        self._last_refresh_time = 0.0

    def _sync_client_tokens_from_result(self, result: Mapping[str, object]) -> None:
        """Apply one formal login/refresh result to the protocol client state."""
        access_token = _require_text(
            result.get(CONF_ACCESS_TOKEN),
            field_name=CONF_ACCESS_TOKEN,
        )
        refresh_token = _require_text(
            result.get(CONF_REFRESH_TOKEN),
            field_name=CONF_REFRESH_TOKEN,
        )
        user_id = _optional_int(result.get(CONF_USER_ID))
        biz_id = _optional_text(result.get("biz_id"))
        self._client.set_tokens(access_token, refresh_token, user_id, biz_id)
        self._client.access_token = access_token
        self._client.refresh_token = refresh_token
        self._client.user_id = user_id
        if hasattr(self._client, "biz_id"):
            self._client.biz_id = biz_id

    def get_auth_session(self) -> AuthSessionSnapshot:
        """Return the current formal auth/session snapshot."""
        return AuthSessionSnapshot(
            access_token=self._client.access_token,
            refresh_token=self._client.refresh_token,
            user_id=self._client.user_id,
            expires_at=self._token_expires_at,
            phone_id=self._client.phone_id,
            biz_id=self._client.biz_id,
        )

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> AuthSessionSnapshot:
        """Login with credentials.

        Args:
            phone: Phone number.
            password: Password (plain text or MD5 hash).
            password_is_hashed: If True, password is already MD5 hashed.

        Returns:
            Login result with tokens.

        """
        self.set_credentials(phone, password, password_is_hashed=password_is_hashed)

        result = await self._client.login(
            phone, password, password_is_hashed=password_is_hashed
        )
        self._sync_client_tokens_from_result(result)
        # Reset adaptive expiry on successful login
        self._current_expiry_seconds = ACCESS_TOKEN_EXPIRY_SECONDS
        self._token_expires_at = time.time() + self._current_expiry_seconds
        self._last_refresh_time = time.time()

        _LOGGER.debug(
            "Login successful, token expires in %d seconds",
            self._current_expiry_seconds,
        )
        self._notify_tokens_updated()

        return self.get_auth_session()

    async def refresh_token(self) -> AuthSessionSnapshot:
        """Refresh the access token.

        Returns:
            New tokens.

        Raises:
            LiproRefreshTokenExpiredError: If refresh token is expired (20002, 1202).
            LiproAuthError: If refresh fails for other reasons.

        """
        try:
            result = await self._client.refresh_access_token()
            self._sync_client_tokens_from_result(result)
            self._token_expires_at = time.time() + self._current_expiry_seconds
            self._last_refresh_time = time.time()

            _LOGGER.debug(
                "Token refreshed, expires in %d seconds",
                self._current_expiry_seconds,
            )
            self._notify_tokens_updated()

            return self.get_auth_session()
        except LiproAuthError as err:
            # Check for refresh token expired error codes
            if err.code in ERROR_REFRESH_TOKEN_EXPIRED:
                _LOGGER.warning(
                    "Refresh token expired (code: %s), re-login required",
                    err.code,
                )
                # Try re-login if we have credentials
                if self._phone and self._password:
                    _LOGGER.info("Attempting re-login with stored credentials")
                    return await self.login(
                        self._phone,
                        self._password,
                        password_is_hashed=self._password_is_hashed,
                    )
                msg = "Refresh token expired"
                raise LiproRefreshTokenExpiredError(msg, err.code) from err

            # For other auth errors, try re-login as fallback
            if self._phone and self._password:
                _LOGGER.warning("Token refresh failed, attempting re-login")
                return await self.login(
                    self._phone,
                    self._password,
                    password_is_hashed=self._password_is_hashed,
                )
            raise

    def _adjust_expiry_on_401(self) -> None:
        """Adjust token expiry time when 401 is received (adaptive strategy).

        If we receive a 401 before the expected expiry, reduce the estimated
        expiry time to prevent future 401s.
        """
        now = time.time()
        time_since_refresh = now - self._last_refresh_time

        # Only adjust if 401 came before expected expiry
        if time_since_refresh < self._current_expiry_seconds:
            # Calculate new expiry based on when 401 actually occurred
            # Use the smaller of: actual time * reduction factor, or current * reduction
            new_expiry = int(
                min(
                    time_since_refresh * TOKEN_EXPIRY_REDUCTION_FACTOR,
                    self._current_expiry_seconds * TOKEN_EXPIRY_REDUCTION_FACTOR,
                ),
            )
            # Ensure minimum expiry time
            new_expiry = max(new_expiry, TOKEN_EXPIRY_MIN)

            if new_expiry < self._current_expiry_seconds:
                _LOGGER.info(
                    "Adaptive expiry: reducing from %d to %d seconds "
                    "(401 after %d seconds)",
                    self._current_expiry_seconds,
                    new_expiry,
                    int(time_since_refresh),
                )
                self._current_expiry_seconds = new_expiry

    async def _do_token_refresh(self) -> None:
        """Internal callback for automatic 401 handling.

        This is called by the API client when a 401 is detected.
        Uses asyncio.Lock to prevent concurrent refreshes.

        Raises:
            LiproRefreshTokenExpiredError: If refresh token is expired.
            LiproAuthError: If refresh fails.

        """
        async with self._refresh_lock:
            # Check if token was already refreshed recently (within last 5 seconds)
            # This prevents multiple concurrent 401s from triggering duplicate refreshes
            if time.time() - self._last_refresh_time < TOKEN_REFRESH_DEDUP_WINDOW:
                _LOGGER.debug(
                    "Token was refreshed %d seconds ago, skipping",
                    int(time.time() - self._last_refresh_time),
                )
                return

            _LOGGER.debug("Automatic token refresh triggered by 401")

            # Adjust expiry time based on when 401 occurred (adaptive strategy)
            self._adjust_expiry_on_401()

            await self.refresh_token()

    async def async_ensure_authenticated(self) -> None:
        """Compatibility wrapper used by coordinator update flows."""
        await self.ensure_valid_token()

    async def ensure_valid_token(self) -> None:
        """Ensure we have a valid token, refreshing if needed.

        Uses TOKEN_REFRESH_BUFFER to refresh before actual expiry.

        Raises:
            LiproAuthError: If unable to get valid token.

        """
        if not self.is_authenticated:
            if self._phone and self._password:
                await self.login(
                    self._phone,
                    self._password,
                    password_is_hashed=self._password_is_hashed,
                )
                return
            msg = "Not authenticated and no credentials available"
            raise LiproAuthError(msg)

        # Refresh if token expires within buffer time
        if time.time() >= self._token_expires_at - TOKEN_REFRESH_BUFFER:
            async with self._refresh_lock:
                # Double-check after acquiring lock (another coroutine may have refreshed)
                if time.time() >= self._token_expires_at - TOKEN_REFRESH_BUFFER:
                    _LOGGER.debug(
                        "Token expiring in %d seconds, refreshing proactively",
                        int(self._token_expires_at - time.time()),
                    )
                    await self.refresh_token()

