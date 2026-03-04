"""Authentication recovery and response finalization for LiproClient."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, TypeVar

from ...const.api import (
    ERROR_AUTH_CODES,
    ERROR_INVALID_PARAM,
    ERROR_INVALID_PARAM_STR,
    ERROR_REFRESH_TOKEN_EXPIRED,
    RESPONSE_SUCCESS_CODES,
)
from . import response_safety as _response_safety
from .client_pacing import _ClientPacingMixin
from .errors import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .observability import record_api_error as _record_api_error

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")

_MappingPayloadT = TypeVar("_MappingPayloadT")


class _ClientAuthRecoveryMixin(_ClientPacingMixin):
    """Mixin implementing auth recovery and mapping-response finalization."""

    def _init_auth_recovery(self) -> None:
        """Initialize authentication/token state and refresh coordination."""
        self._access_token = None
        self._refresh_token = None
        self._user_id = None
        self._biz_id = None
        self._on_token_refresh = None
        self._refresh_lock = asyncio.Lock()

    @property
    def access_token(self) -> str | None:
        """Return the access token."""
        return self._access_token

    @property
    def refresh_token(self) -> str | None:
        """Return the refresh token."""
        return self._refresh_token

    @property
    def user_id(self) -> int | None:
        """Return the user ID."""
        return self._user_id

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Set authentication tokens."""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user_id = user_id
        self._biz_id = biz_id

    def set_token_refresh_callback(
        self,
        callback: Callable[[], Awaitable[None]] | None,
    ) -> None:
        """Set callback to be called when token needs refresh."""
        self._on_token_refresh = callback

    async def _handle_auth_error_and_retry(
        self,
        path: str,
        old_token: str | None,
        is_retry: bool,
    ) -> bool:
        """Handle auth error by refreshing token.

        Args:
            path: API path (for logging).
            old_token: Token used in the failed request.
            is_retry: Whether this is already a retry attempt.

        Returns:
            True if token was refreshed and request should be retried.

        """
        if is_retry or not self._on_token_refresh:
            return False
        _LOGGER.info("Received auth error from %s, attempting token refresh", path)
        return await self._handle_401_with_refresh(old_token)

    @staticmethod
    def _is_auth_error_code(code: Any) -> bool:
        """Check whether an API code represents an authentication failure."""
        normalized = _response_safety.normalize_response_code(code)
        if isinstance(normalized, str) and normalized.lower() == "token_expired":
            return True
        return (
            normalized in ERROR_AUTH_CODES or normalized in ERROR_REFRESH_TOKEN_EXPIRED
        )

    @staticmethod
    def _is_success_code(code: Any) -> bool:
        """Check whether an API code represents success."""
        normalized = _response_safety.normalize_response_code(code)
        return normalized in RESPONSE_SUCCESS_CODES

    @classmethod
    def _resolve_auth_error_code(
        cls,
        code: Any,
        error_code: Any,
    ) -> int | str | None:
        """Pick the most relevant auth code from response code/errorCode fields."""
        if cls._is_auth_error_code(code):
            normalized = _response_safety.normalize_response_code(code)
            if isinstance(normalized, str) and normalized.lower() == "token_expired":
                return "token_expired"
            return normalized
        if cls._is_auth_error_code(error_code):
            normalized = _response_safety.normalize_response_code(error_code)
            if isinstance(normalized, str) and normalized.lower() == "token_expired":
                return "token_expired"
            return normalized
        return None

    @staticmethod
    def _resolve_error_code(code: Any, error_code: Any) -> int | str | None:
        """Pick the most specific error code from code/errorCode fields."""
        normalized_error_code = _response_safety.normalize_response_code(error_code)
        if normalized_error_code not in (None, "", 0):
            return normalized_error_code
        normalized_code = _response_safety.normalize_response_code(code)
        if normalized_code not in (None, "", 0):
            return normalized_code
        return None

    async def _finalize_mapping_result(
        self,
        *,
        path: str,
        result: dict[str, Any],
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request: Callable[[], Awaitable[_MappingPayloadT]] | None,
        success_payload: Callable[[dict[str, Any]], _MappingPayloadT],
    ) -> _MappingPayloadT:
        """Finalize shared Smart Home/IoT mapping response handling.

        This keeps success extraction plus auth/API error mapping behavior aligned
        across request pipelines while preserving endpoint-specific retry policy.
        """
        code = result.get("code")
        if self._is_success_code(code):
            return success_payload(result)

        error_code = result.get("errorCode")
        message = result.get("message", "Unknown error")

        auth_error_code = self._resolve_auth_error_code(code, error_code)
        if auth_error_code is not None:
            if (
                retry_on_auth_error
                and retry_request is not None
                and await self._handle_auth_error_and_retry(
                    path, request_token, is_retry
                )
            ):
                return await retry_request()
            raise LiproAuthError(message, auth_error_code)

        effective_code = self._resolve_error_code(code, error_code)
        # Record API error for anonymous share
        _record_api_error(path, effective_code or 0, message, method="POST")
        raise LiproApiError(message, effective_code)

    @staticmethod
    def _is_invalid_param_error_code(code: Any) -> bool:
        """Check whether error code represents invalid request payload/params."""
        normalized = _response_safety.normalize_response_code(code)
        return normalized in (ERROR_INVALID_PARAM, ERROR_INVALID_PARAM_STR)

    @staticmethod
    def _unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        """Unwrap successful IoT API payload.

        Most endpoints use ``{"code":"0000","data":...}``, but a few may return
        direct payload objects. Keep empty ``data`` containers (for example `{}`)
        and only coerce ``None`` to empty dict for call-site compatibility.
        """
        if "data" in result:
            data = result["data"]
            return {} if data is None else data
        return result

    async def _handle_401_with_refresh(self, old_token: str | None) -> bool:
        """Handle 401 error by refreshing token with concurrency control.

        This implements the same pattern as Android's TokenInterceptor:
        - Use lock to prevent multiple concurrent refresh attempts
        - Double-check if token was already refreshed by another request
        - Call refresh callback to get new token

        Args:
            old_token: The token that was used in the failed request.

        Returns:
            True if token was refreshed successfully, False otherwise.

        Raises:
            LiproConnectionError: If refresh fails due to transient network issues.

        """
        if not self._on_token_refresh:
            return False

        async with self._refresh_lock:
            # Double-check: token might have been refreshed by another request
            if self._access_token != old_token and self._access_token is not None:
                _LOGGER.debug(
                    "Token already refreshed by another request, using new token",
                )
                return True

            # Perform the refresh
            try:
                _LOGGER.debug("Executing token refresh")
                await self._on_token_refresh()
                refreshed_token = self._access_token
                if refreshed_token is None or refreshed_token == old_token:
                    _LOGGER.warning(
                        "Token refresh callback completed but token is unchanged"
                    )
                    return False
                _LOGGER.info("Token refresh successful, retrying request")
                return True
            except LiproRefreshTokenExpiredError:
                _LOGGER.warning("Refresh token expired, re-authentication required")
                raise
            except LiproAuthError as err:
                _LOGGER.warning("Token refresh failed: %s", err)
                return False
            except LiproConnectionError as err:
                _LOGGER.warning("Connection error during token refresh: %s", err)
                raise
