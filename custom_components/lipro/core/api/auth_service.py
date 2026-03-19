"""Auth endpoint service for Lipro API client."""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Protocol

from ...const.api import PATH_LOGIN, PATH_REFRESH_TOKEN
from .types import ApiResponse, LoginResponse


class AuthClient(Protocol):
    """Minimal client surface consumed by the auth endpoint service."""

    access_token: str | None
    refresh_token: str | None
    user_id: int | None
    biz_id: str | None

    async def smart_home_request(
        self,
        path: str,
        data: dict[str, Any],
        require_auth: bool = True,
        is_retry: bool = False,
        retry_count: int = 0,
    ) -> ApiResponse:
        """Execute one Smart Home request through the formal REST surface."""

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str,
        user_id: int | None = None,
        biz_id: str | None = None,
    ) -> None:
        """Persist freshly issued auth/session fields onto client state."""


class AuthApiService:
    """Auth endpoints extracted from the formal REST facade."""

    def __init__(
        self,
        client: AuthClient,
        auth_error_cls: type[Exception],
        logger: logging.Logger,
    ) -> None:
        """Initialize auth endpoint service."""
        self._client = client
        self._auth_error_cls = auth_error_cls
        self._logger = logger

    @staticmethod
    def _coerce_user_id(raw_user_id: object) -> int:
        """Normalize vendor user id payload to one stable int contract."""
        if isinstance(raw_user_id, int):
            return raw_user_id
        if isinstance(raw_user_id, str):
            normalized = raw_user_id.strip()
            try:
                return int(normalized) if normalized else 0
            except ValueError:
                return 0
        return 0

    def _require_tokens(self, result: ApiResponse, *, context: str) -> tuple[str, str]:
        """Return access/refresh tokens or raise one auth error."""
        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        if isinstance(access_token, str) and isinstance(refresh_token, str):
            if access_token and refresh_token:
                return access_token, refresh_token
        msg = f"{context} response missing access_token or refresh_token"
        raise self._auth_error_cls(msg)

    def _persist_session_state(self, result: ApiResponse, *, context: str) -> None:
        """Persist normalized auth/session fields onto the client."""
        access_token, refresh_token = self._require_tokens(result, context=context)
        raw_biz_id = result.get("bizId")
        self._client.set_tokens(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=self._coerce_user_id(result.get("userId")),
            biz_id=raw_biz_id if isinstance(raw_biz_id, str) else None,
        )

    def _build_login_response(self) -> LoginResponse:
        """Return the normalized auth payload exposed by the REST facade."""
        return {
            "access_token": self._client.access_token or "",
            "refresh_token": self._client.refresh_token or "",
            "expires_in": 0,
            "user_id": 0 if self._client.user_id is None else self._client.user_id,
            "biz_id": self._client.biz_id,
        }

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse:
        """Login with phone number and password/hash."""
        password_hash = (
            password
            if password_is_hashed
            else hashlib.md5(password.encode("utf-8"), usedforsecurity=False).hexdigest()
        )

        result = await self._client.smart_home_request(
            PATH_LOGIN,
            {
                "phone": phone,
                "password": password_hash,
            },
            require_auth=False,
        )

        self._persist_session_state(result, context="Login")
        self._logger.info("Login successful")
        return self._build_login_response()

    async def refresh_access_token(self) -> LoginResponse:
        """Refresh access token."""
        if not self._client.refresh_token:
            msg = "No refresh token available"
            raise self._auth_error_cls(msg)

        result = await self._client.smart_home_request(
            PATH_REFRESH_TOKEN,
            {
                "refreshToken": self._client.refresh_token,
                "model": "HomeAssistant",
            },
            require_auth=False,
        )

        self._persist_session_state(result, context="Refresh")
        self._logger.info("Token refreshed successfully")
        return self._build_login_response()
