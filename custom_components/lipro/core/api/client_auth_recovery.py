"""Authentication recovery and response finalization for Lipro REST protocol."""

from __future__ import annotations

import logging
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
        self._state = state

    @property
    def access_token(self) -> str | None:
        return self._state.access_token

    @property
    def refresh_token(self) -> str | None:
        return self._state.refresh_token

    @property
    def user_id(self) -> int | None:
        return self._state.user_id

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        self._state.set_tokens(
            access_token,
            refresh_token,
            user_id=user_id,
            biz_id=biz_id,
        )

    def set_token_refresh_callback(self, callback) -> None:
        self._state.on_token_refresh = callback

    @staticmethod
    def is_auth_error_code(code: Any) -> bool:
        normalized = _response_safety.normalize_response_code(code)
        if isinstance(normalized, str) and normalized.lower() == "token_expired":
            return True
        return (
            normalized in ERROR_AUTH_CODES or normalized in ERROR_REFRESH_TOKEN_EXPIRED
        )

    @staticmethod
    def is_success_code(code: Any) -> bool:
        normalized = _response_safety.normalize_response_code(code)
        return normalized in RESPONSE_SUCCESS_CODES

    @classmethod
    def resolve_auth_error_code(
        cls,
        code: Any,
        error_code: Any,
    ) -> int | str | None:
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
        normalized_error_code = _response_safety.normalize_response_code(error_code)
        if normalized_error_code not in (None, "", 0):
            return normalized_error_code
        normalized_code = _response_safety.normalize_response_code(code)
        if normalized_code not in (None, "", 0):
            return normalized_code
        return None

    async def handle_auth_error_and_retry(
        self,
        path: str,
        request_token: str | None,
        is_retry: bool,
    ) -> bool:
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
        normalized = _response_safety.normalize_response_code(code)
        return normalized in (ERROR_INVALID_PARAM, ERROR_INVALID_PARAM_STR)

    @staticmethod
    def unwrap_iot_success_payload(result: dict[str, Any]) -> Any:
        if "data" in result:
            data = result["data"]
            return {} if data is None else data
        return result

    async def handle_401_with_refresh(self, request_token: str | None) -> bool:
        if not self._state.on_token_refresh:
            return False

        if self._state.access_token != request_token and self._state.access_token is not None:
            _LOGGER.debug(
                "Token already refreshed by another request, using new token",
            )
            return True

        async with self._state.refresh_lock:
            if self._state.access_token != request_token and self._state.access_token is not None:
                _LOGGER.debug(
                    "Token already refreshed by another request (verified in lock), using new token",
                )
                return True

            try:
                _LOGGER.debug("Executing token refresh")
                await self._state.on_token_refresh()
                refreshed_token = self._state.access_token
                if refreshed_token is None or refreshed_token == request_token:
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
                _LOGGER.warning(
                    "Token refresh failed (%s)", safe_error_placeholder(err)
                )
                return False
            except LiproConnectionError as err:
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
