"""Authentication manager for Lipro integration."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from typing import TYPE_CHECKING, Any

from ...const.api import (
    ACCESS_TOKEN_EXPIRY_SECONDS,
    ERROR_REFRESH_TOKEN_EXPIRED,
    TOKEN_EXPIRY_MIN,
    TOKEN_EXPIRY_REDUCTION_FACTOR,
    TOKEN_REFRESH_BUFFER,
    TOKEN_REFRESH_DEDUP_WINDOW,
)
from ...const.config import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
)
from ..api import LiproAuthError, LiproClient, LiproRefreshTokenExpiredError

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable


class LiproAuthManager:
    """Manages authentication and token refresh for Lipro API.

    Implements:
    - Thread-safe token refresh with asyncio.Lock
    - Adaptive token expiry based on 401 frequency
    - Automatic re-login when refresh token expires
    """

    def __init__(self, client: LiproClient) -> None:
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
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Token-updated callback failed: %s", err)

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
    ) -> None:
        """Set authentication tokens.

        Args:
            access_token: The access token.
            refresh_token: The refresh token.
            user_id: Optional user ID.
            expires_at: Optional expiry timestamp.

        """
        self._client.set_tokens(access_token, refresh_token, user_id)
        # Use expires_at if provided and valid (not None and not 0)
        if expires_at is not None and expires_at > 0:
            self._token_expires_at = expires_at
        else:
            self._token_expires_at = time.time() + self._current_expiry_seconds
        # Persisted tokens may be stale; do not mark as "just refreshed".
        # This keeps the first runtime 401 eligible for an immediate refresh.
        self._last_refresh_time = 0.0

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> dict[str, Any]:
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
        # Reset adaptive expiry on successful login
        self._current_expiry_seconds = ACCESS_TOKEN_EXPIRY_SECONDS
        self._token_expires_at = time.time() + self._current_expiry_seconds
        self._last_refresh_time = time.time()

        _LOGGER.debug(
            "Login successful, token expires in %d seconds",
            self._current_expiry_seconds,
        )
        self._notify_tokens_updated()

        return {
            **result,
            "expires_at": self._token_expires_at,
        }

    async def refresh_token(self) -> dict[str, Any]:
        """Refresh the access token.

        Returns:
            New tokens.

        Raises:
            LiproRefreshTokenExpiredError: If refresh token is expired (20002, 1202).
            LiproAuthError: If refresh fails for other reasons.

        """
        try:
            result = await self._client.refresh_access_token()
            self._token_expires_at = time.time() + self._current_expiry_seconds
            self._last_refresh_time = time.time()

            _LOGGER.debug(
                "Token refreshed, expires in %d seconds",
                self._current_expiry_seconds,
            )
            self._notify_tokens_updated()

            return {
                **result,
                "expires_at": self._token_expires_at,
            }
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

    def get_auth_data(self) -> dict[str, Any]:
        """Get authentication data for storage.

        Returns:
            Dictionary with auth data.

        """
        return {
            CONF_ACCESS_TOKEN: self._client.access_token,
            CONF_REFRESH_TOKEN: self._client.refresh_token,
            CONF_USER_ID: self._client.user_id,
            CONF_PHONE_ID: self._client.phone_id,
            CONF_EXPIRES_AT: self._token_expires_at,
        }
