"""Authentication recovery and response finalization for Lipro REST protocol."""

from __future__ import annotations

import logging
from time import monotonic, time
from typing import Any, TypeVar

from ...const.api import (
    ERROR_AUTH_CODES,
    ERROR_INVALID_PARAM,
    ERROR_INVALID_PARAM_STR,
    ERROR_REFRESH_TOKEN_EXPIRED,
    RESPONSE_SUCCESS_CODES,
)
from ..utils.log_safety import safe_error_placeholder
from . import response_safety as _response_safety
from .client_base import ClientSessionState
from .errors import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .observability import record_api_error as _record_api_error

# Use the same logger instance as custom_components.lipro.core.api.client._LOGGER
# so tests patching client._LOGGER.* still intercept logs here.
_LOGGER = logging.getLogger("custom_components.lipro.core.api.client")

_MappingPayloadT = TypeVar("_MappingPayloadT")


class AuthRecoveryCoordinator:
    """Explicit owner for auth classification, refresh, and replay decisions."""

    def __init__(self, state: ClientSessionState) -> None:
        """Initialize auth-recovery bookkeeping around shared session state."""
        self._state = state
        self._auth_error_count = 0
        self._refresh_attempt_count = 0
        self._refresh_success_count = 0
        self._refresh_failure_count = 0
        self._refresh_expired_count = 0
        self._refresh_reused_count = 0
        self._last_refresh_duration_seconds: float | None = None
        self._last_refresh_finished_at: float | None = None
        self._last_refresh_outcome: str | None = None
        self._last_refresh_error_type: str | None = None

    @property
    def access_token(self) -> str | None:
        """Return the access token currently stored in session state."""
        return self._state.access_token

    @property
    def refresh_token(self) -> str | None:
        """Return the refresh token currently stored in session state."""
        return self._state.refresh_token

    @property
    def user_id(self) -> int | None:
        """Return the authenticated user identifier from session state."""
        return self._state.user_id

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Persist freshly issued tokens into shared session state."""
        self._state.set_tokens(
            access_token,
            refresh_token,
            user_id=user_id,
            biz_id=biz_id,
        )

    def set_token_refresh_callback(self, callback) -> None:
        """Register the async callback used to refresh expired tokens."""
        self._state.on_token_refresh = callback

    @staticmethod
    def is_auth_error_code(code: Any) -> bool:
        """Return whether one response code denotes an auth failure."""
        normalized = _response_safety.normalize_response_code(code)
        if isinstance(normalized, str) and normalized.lower() == "token_expired":
            return True
        return (
            normalized in ERROR_AUTH_CODES or normalized in ERROR_REFRESH_TOKEN_EXPIRED
        )

    @staticmethod
    def is_success_code(code: Any) -> bool:
        """Return whether one response code denotes success."""
        normalized = _response_safety.normalize_response_code(code)
        return normalized in RESPONSE_SUCCESS_CODES

    @classmethod
    def resolve_auth_error_code(
        cls,
        code: Any,
        error_code: Any,
    ) -> int | str | None:
        """Resolve the effective auth error code from response variants."""
        for candidate in (code, error_code):
            if not cls.is_auth_error_code(candidate):
                continue
            normalized = _response_safety.normalize_response_code(candidate)
            if isinstance(normalized, str) and normalized.lower() == "token_expired":
                return "token_expired"
            return normalized
        return None

    @staticmethod
    def resolve_error_code(code: Any, error_code: Any) -> int | str | None:
        """Resolve the effective error code from response variants."""
        normalized_error_code = _response_safety.normalize_response_code(error_code)
        if normalized_error_code not in (None, "", 0):
            return normalized_error_code
        normalized_code = _response_safety.normalize_response_code(code)
        if normalized_code not in (None, "", 0):
            return normalized_code
        return None

    def _record_refresh_outcome(
        self,
        *,
        outcome: str,
        duration_seconds: float | None,
        error_type: str | None = None,
    ) -> None:
        self._last_refresh_outcome = outcome
        self._last_refresh_duration_seconds = duration_seconds
        self._last_refresh_finished_at = time()
        self._last_refresh_error_type = error_type

    def telemetry_snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of auth-recovery telemetry."""
        return {
            "auth_error_count": self._auth_error_count,
            "refresh_attempt_count": self._refresh_attempt_count,
            "refresh_success_count": self._refresh_success_count,
            "refresh_failure_count": self._refresh_failure_count,
            "refresh_expired_count": self._refresh_expired_count,
            "refresh_reused_count": self._refresh_reused_count,
            "last_refresh_duration_seconds": self._last_refresh_duration_seconds,
            "last_refresh_finished_at": self._last_refresh_finished_at,
            "last_refresh_outcome": self._last_refresh_outcome,
            "last_refresh_error_type": self._last_refresh_error_type,
        }

    async def handle_auth_error_and_retry(
        self,
        path: str,
        request_token: str | None,
        is_retry: bool,
    ) -> bool:
        """Handle one auth failure and trigger refresh/replay when allowed."""
        self._auth_error_count += 1
        if is_retry or not self._state.on_token_refresh:
            return False
        _LOGGER.info("Received auth error from %s, attempting token refresh", path)
        return await self.handle_401_with_refresh(request_token)

    async def finalize_mapping_result(
        self,
        *,
        path: str,
        result: dict[str, Any],
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request,
        success_payload,
    ) -> _MappingPayloadT:
        """Finalize one mapping result with auth classification and retries."""
        code = result.get("code")
        if self.is_success_code(code):
            return success_payload(result)

        error_code = result.get("errorCode")
        message_value = result.get("message")
        message = (
            message_value
            if isinstance(message_value, str) and message_value.strip()
            else "Unknown error"
        )

        auth_error_code = self.resolve_auth_error_code(code, error_code)
        if auth_error_code is not None:
            if (
                retry_on_auth_error
                and retry_request is not None
                and await self.handle_auth_error_and_retry(
                    path, request_token, is_retry
                )
            ):
                return await retry_request()
            raise LiproAuthError(message, auth_error_code)

        effective_code = self.resolve_error_code(code, error_code)
        _record_api_error(
            path,
            effective_code or 0,
            message,
            method="POST",
            entry_id=self._state.entry_id,
        )
        raise LiproApiError(message, effective_code)

    @staticmethod
    def is_invalid_param_error_code(code: Any) -> bool:
        """Return whether one code denotes an invalid-parameter response."""
        normalized = _response_safety.normalize_response_code(code)
        return normalized in (ERROR_INVALID_PARAM, ERROR_INVALID_PARAM_STR)

    @staticmethod
    def unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        """Extract the canonical success payload from one IoT response."""
        if "data" in result:
            data = result["data"]
            return {} if data is None else data
        return result

    async def handle_401_with_refresh(self, request_token: str | None) -> bool:
        """Refresh tokens after one HTTP 401 and indicate whether replay is safe."""
        if not self._state.on_token_refresh:
            return False

        if self._state.access_token != request_token and self._state.access_token is not None:
            self._refresh_reused_count += 1
            self._record_refresh_outcome(outcome="reused", duration_seconds=0.0)
            _LOGGER.debug(
                "Token already refreshed by another request, using new token",
            )
            return True

        async with self._state.refresh_lock:
            if self._state.access_token != request_token and self._state.access_token is not None:
                self._refresh_reused_count += 1
                self._record_refresh_outcome(outcome="reused", duration_seconds=0.0)
                _LOGGER.debug(
                    "Token already refreshed by another request (verified in lock), using new token",
                )
                return True

            self._refresh_attempt_count += 1
            started_at = monotonic()
            try:
                _LOGGER.debug("Executing token refresh")
                await self._state.on_token_refresh()
                refreshed_token = self._state.access_token
                duration_seconds = monotonic() - started_at
                if refreshed_token is None or refreshed_token == request_token:
                    self._refresh_failure_count += 1
                    self._record_refresh_outcome(
                        outcome="unchanged",
                        duration_seconds=duration_seconds,
                    )
                    _LOGGER.warning(
                        "Token refresh callback completed but token is unchanged"
                    )
                    return False
                self._refresh_success_count += 1
                self._record_refresh_outcome(
                    outcome="success",
                    duration_seconds=duration_seconds,
                )
                _LOGGER.info("Token refresh successful, retrying request")
                return True
            except LiproRefreshTokenExpiredError:
                duration_seconds = monotonic() - started_at
                self._refresh_failure_count += 1
                self._refresh_expired_count += 1
                self._record_refresh_outcome(
                    outcome="refresh_token_expired",
                    duration_seconds=duration_seconds,
                    error_type="LiproRefreshTokenExpiredError",
                )
                _LOGGER.warning("Refresh token expired, re-authentication required")
                raise
            except LiproAuthError as err:
                duration_seconds = monotonic() - started_at
                self._refresh_failure_count += 1
                self._record_refresh_outcome(
                    outcome="auth_error",
                    duration_seconds=duration_seconds,
                    error_type=type(err).__name__,
                )
                _LOGGER.warning(
                    "Token refresh failed (%s)", safe_error_placeholder(err)
                )
                return False
            except LiproConnectionError as err:
                duration_seconds = monotonic() - started_at
                self._refresh_failure_count += 1
                self._record_refresh_outcome(
                    outcome="connection_error",
                    duration_seconds=duration_seconds,
                    error_type=type(err).__name__,
                )
                _LOGGER.warning(
                    "Connection error during token refresh (%s)",
                    safe_error_placeholder(err),
                )
                raise


class _ClientAuthRecoveryMixin:
    """Thin compatibility adapter over ``AuthRecoveryCoordinator``."""

    def _init_auth_recovery(self, *, entry_id: str | None = None) -> None:
        self._session_state.entry_id = entry_id
        self._auth_recovery = AuthRecoveryCoordinator(self._session_state)

    @property
    def access_token(self) -> str | None:
        return self._auth_recovery.access_token

    @property
    def refresh_token(self) -> str | None:
        return self._auth_recovery.refresh_token

    @property
    def user_id(self) -> int | None:
        return self._auth_recovery.user_id

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        self._auth_recovery.set_tokens(
            access_token,
            refresh_token,
            user_id=user_id,
            biz_id=biz_id,
        )

    def set_token_refresh_callback(self, callback) -> None:
        self._auth_recovery.set_token_refresh_callback(callback)

    async def _handle_auth_error_and_retry(
        self,
        path: str,
        request_token: str | None,
        is_retry: bool,
    ) -> bool:
        return await self._auth_recovery.handle_auth_error_and_retry(
            path, request_token, is_retry
        )

    @staticmethod
    def _is_auth_error_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_auth_error_code(code)

    @staticmethod
    def _is_success_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_success_code(code)

    @classmethod
    def _resolve_auth_error_code(
        cls,
        code: Any,
        error_code: Any,
    ) -> int | str | None:
        return AuthRecoveryCoordinator.resolve_auth_error_code(code, error_code)

    @staticmethod
    def _resolve_error_code(code: Any, error_code: Any) -> int | str | None:
        return AuthRecoveryCoordinator.resolve_error_code(code, error_code)

    async def _finalize_mapping_result(
        self,
        *,
        path: str,
        result: dict[str, Any],
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request,
        success_payload,
    ) -> _MappingPayloadT:
        return await self._auth_recovery.finalize_mapping_result(
            path=path,
            result=result,
            request_token=request_token,
            is_retry=is_retry,
            retry_on_auth_error=retry_on_auth_error,
            retry_request=retry_request,
            success_payload=success_payload,
        )

    @staticmethod
    def _is_invalid_param_error_code(code: Any) -> bool:
        return AuthRecoveryCoordinator.is_invalid_param_error_code(code)

    @staticmethod
    def _unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        return AuthRecoveryCoordinator.unwrap_iot_success_payload(result)

    async def _handle_401_with_refresh(self, request_token: str | None) -> bool:
        return await self._auth_recovery.handle_401_with_refresh(request_token)


__all__ = ["AuthRecoveryCoordinator", "_ClientAuthRecoveryMixin"]
