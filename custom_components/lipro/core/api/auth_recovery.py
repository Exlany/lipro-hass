"""Authentication recovery and response finalization for Lipro REST protocol."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from time import monotonic, time
from typing import TypedDict, TypeVar

from ...const.api import (
    ERROR_AUTH_CODES,
    ERROR_INVALID_PARAM,
    ERROR_INVALID_PARAM_STR,
    ERROR_REFRESH_TOKEN_EXPIRED,
    RESPONSE_SUCCESS_CODES,
)
from ..utils.log_safety import safe_error_placeholder
from . import response_safety as _response_safety
from .errors import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .observability import record_api_error as _record_api_error
from .session_state import RestSessionState
from .types import JsonObject, JsonValue

_LOGGER = logging.getLogger("custom_components.lipro.core.api")

_MappingPayloadT = TypeVar("_MappingPayloadT")
TokenRefreshCallback = Callable[[], Awaitable[None]]


class AuthRecoveryTelemetrySnapshot(TypedDict):
    """Serializable auth-recovery telemetry emitted by the REST recovery path."""

    auth_error_count: int
    refresh_attempt_count: int
    refresh_success_count: int
    refresh_failure_count: int
    refresh_expired_count: int
    refresh_reused_count: int
    last_refresh_duration_seconds: float | None
    last_refresh_finished_at: float | None
    last_refresh_outcome: str | None
    last_refresh_error_type: str | None


class RestAuthRecoveryCoordinator:
    """Explicit owner for auth classification, refresh, and replay decisions."""

    def __init__(self, state: RestSessionState) -> None:
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

    def set_token_refresh_callback(self, callback: TokenRefreshCallback) -> None:
        """Register the async callback used to refresh expired tokens."""
        self._state.on_token_refresh = callback

    @staticmethod
    def is_auth_error_code(code: object) -> bool:
        """Return whether one response code denotes an auth failure."""
        normalized = _response_safety.normalize_response_code(code)
        if isinstance(normalized, str) and normalized.lower() == "token_expired":
            return True
        return (
            normalized in ERROR_AUTH_CODES or normalized in ERROR_REFRESH_TOKEN_EXPIRED
        )

    @staticmethod
    def is_success_code(code: object) -> bool:
        """Return whether one response code denotes success."""
        normalized = _response_safety.normalize_response_code(code)
        return normalized in RESPONSE_SUCCESS_CODES

    @classmethod
    def resolve_auth_error_code(
        cls,
        code: object,
        error_code: object,
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
    def resolve_error_code(code: object, error_code: object) -> int | str | None:
        """Resolve the effective error code from response variants."""
        normalized_error_code = _response_safety.normalize_response_code(error_code)
        if normalized_error_code not in (None, "", 0):
            return normalized_error_code
        normalized_code = _response_safety.normalize_response_code(code)
        if normalized_code not in (None, "", 0):
            return normalized_code
        return None

    @staticmethod
    def _resolve_result_message(result: JsonObject) -> str:
        """Resolve one readable message from vendor response payloads."""
        message_value = result.get("message")
        if isinstance(message_value, str) and message_value.strip():
            return message_value
        return "Unknown error"

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

    def _has_reusable_access_token(self, request_token: str | None) -> bool:
        """Return whether another request already refreshed the current access token."""
        access_token = self._state.access_token
        return access_token is not None and access_token != request_token

    def _record_refresh_reuse(self, *, verified_in_lock: bool) -> bool:
        """Record that the in-flight request can reuse a fresher access token."""
        self._refresh_reused_count += 1
        self._record_refresh_outcome(outcome="reused", duration_seconds=0.0)
        if verified_in_lock:
            _LOGGER.debug(
                "Token already refreshed by another request (verified in lock), using new token",
            )
        else:
            _LOGGER.debug(
                "Token already refreshed by another request, using new token",
            )
        return True

    def _record_refresh_failure(
        self,
        *,
        outcome: str,
        duration_seconds: float,
        error_type: str | None = None,
    ) -> None:
        """Record one failed refresh attempt outcome."""
        self._refresh_failure_count += 1
        self._record_refresh_outcome(
            outcome=outcome,
            duration_seconds=duration_seconds,
            error_type=error_type,
        )

    def _complete_refresh_attempt(
        self, *, request_token: str | None, started_at: float
    ) -> bool:
        """Finalize one token-refresh callback and report whether replay is safe."""
        refreshed_token = self._state.access_token
        duration_seconds = monotonic() - started_at
        if refreshed_token is None or refreshed_token == request_token:
            self._record_refresh_failure(
                outcome="unchanged",
                duration_seconds=duration_seconds,
            )
            _LOGGER.warning("Token refresh callback completed but token is unchanged")
            return False

        self._refresh_success_count += 1
        self._record_refresh_outcome(
            outcome="success",
            duration_seconds=duration_seconds,
        )
        _LOGGER.info("Token refresh successful, retrying request")
        return True

    def telemetry_snapshot(self) -> AuthRecoveryTelemetrySnapshot:
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

    async def _retry_mapping_request_if_allowed(
        self,
        *,
        path: str,
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request: Callable[[], Awaitable[_MappingPayloadT]] | None,
    ) -> _MappingPayloadT | None:
        """Retry a mapping request when auth recovery explicitly permits replay."""
        if (
            retry_on_auth_error
            and retry_request is not None
            and await self.handle_auth_error_and_retry(path, request_token, is_retry)
        ):
            return await retry_request()
        return None

    async def finalize_mapping_result(
        self,
        *,
        path: str,
        result: JsonObject,
        request_token: str | None,
        is_retry: bool,
        retry_on_auth_error: bool,
        retry_request: Callable[[], Awaitable[_MappingPayloadT]] | None,
        success_payload: Callable[[JsonObject], _MappingPayloadT],
    ) -> _MappingPayloadT:
        """Finalize one mapping result with auth classification and retries."""
        code = result.get("code")
        if self.is_success_code(code):
            return success_payload(result)

        error_code = result.get("errorCode")
        message = self._resolve_result_message(result)
        auth_error_code = self.resolve_auth_error_code(code, error_code)
        if auth_error_code is not None:
            retried = await self._retry_mapping_request_if_allowed(
                path=path,
                request_token=request_token,
                is_retry=is_retry,
                retry_on_auth_error=retry_on_auth_error,
                retry_request=retry_request,
            )
            if retried is not None:
                return retried
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
    def is_invalid_param_error_code(code: object) -> bool:
        """Return whether one code denotes an invalid-parameter response."""
        normalized = _response_safety.normalize_response_code(code)
        return normalized in (ERROR_INVALID_PARAM, ERROR_INVALID_PARAM_STR)

    @staticmethod
    def unwrap_iot_success_payload(result: JsonObject) -> JsonValue:
        """Extract the canonical success payload from one IoT response."""
        if "data" in result:
            data = result["data"]
            return {} if data is None else data
        return result

    def _start_refresh_attempt(self) -> float:
        """Record one refresh attempt and return its monotonic start time."""
        self._refresh_attempt_count += 1
        return monotonic()

    def _record_refresh_expired(self, *, started_at: float) -> None:
        """Record one refresh-token-expired outcome before re-raising."""
        duration_seconds = monotonic() - started_at
        self._refresh_expired_count += 1
        self._record_refresh_failure(
            outcome="refresh_token_expired",
            duration_seconds=duration_seconds,
            error_type="LiproRefreshTokenExpiredError",
        )
        _LOGGER.warning("Refresh token expired, re-authentication required")

    def _record_refresh_error(
        self,
        *,
        outcome: str,
        started_at: float,
        err: Exception,
        message: str,
    ) -> None:
        """Record one refresh failure that carries a typed exception."""
        self._record_refresh_failure(
            outcome=outcome,
            duration_seconds=monotonic() - started_at,
            error_type=type(err).__name__,
        )
        _LOGGER.warning(message, safe_error_placeholder(err))

    async def _refresh_token_under_lock(self, request_token: str | None) -> bool:
        """Refresh one access token while holding the shared refresh lock."""
        if self._has_reusable_access_token(request_token):
            return self._record_refresh_reuse(verified_in_lock=True)
        refresh_callback = self._state.on_token_refresh
        if refresh_callback is None:
            return False
        started_at = self._start_refresh_attempt()
        try:
            _LOGGER.debug("Executing token refresh")
            await refresh_callback()
            return self._complete_refresh_attempt(
                request_token=request_token,
                started_at=started_at,
            )
        except LiproRefreshTokenExpiredError:
            self._record_refresh_expired(started_at=started_at)
            raise
        except LiproAuthError as err:
            self._record_refresh_error(
                outcome="auth_error",
                started_at=started_at,
                err=err,
                message="Token refresh failed (%s)",
            )
            return False
        except LiproConnectionError as err:
            self._record_refresh_error(
                outcome="connection_error",
                started_at=started_at,
                err=err,
                message="Connection error during token refresh (%s)",
            )
            raise

    async def handle_401_with_refresh(self, request_token: str | None) -> bool:
        """Refresh tokens after one HTTP 401 and indicate whether replay is safe."""
        if not self._state.on_token_refresh:
            return False
        if self._has_reusable_access_token(request_token):
            return self._record_refresh_reuse(verified_in_lock=False)
        async with self._state.refresh_lock:
            return await self._refresh_token_under_lock(request_token)


__all__ = ["AuthRecoveryTelemetrySnapshot", "RestAuthRecoveryCoordinator"]
