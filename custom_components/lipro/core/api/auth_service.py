"""Auth endpoint service for Lipro API client."""
# ruff: noqa: SLF001

from __future__ import annotations

import hashlib
from typing import Any

from ...const.api import PATH_LOGIN, PATH_REFRESH_TOKEN
from ...const.config import (
    CONF_ACCESS_TOKEN,
    CONF_BIZ_ID,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
)
from .types import ApiResponse, LoginResponse


class AuthApiService:
    """Auth endpoints extracted from LiproClient."""

    def __init__(
        self, client: Any, auth_error_cls: type[Exception], logger: Any
    ) -> None:
        """Initialize auth endpoint service."""
        self._client = client
        self._auth_error_cls = auth_error_cls
        self._logger = logger

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse:
        """Login with phone number and password/hash."""
        if password_is_hashed:
            password_hash = password
        else:
            password_hash = hashlib.md5(
                password.encode("utf-8"), usedforsecurity=False
            ).hexdigest()

        result: ApiResponse = await self._client._smart_home_request(
            PATH_LOGIN,
            {
                "phone": phone,
                "password": password_hash,
            },
            require_auth=False,
        )

        access_token: str | None = result.get("access_token")  # type: ignore[assignment]
        refresh_token: str | None = result.get("refresh_token")  # type: ignore[assignment]
        if not access_token or not refresh_token:
            msg = "Login response missing access_token or refresh_token"
            raise self._auth_error_cls(msg)

        self._client._access_token = access_token
        self._client._refresh_token = refresh_token
        self._client._user_id = result.get("userId")
        self._client._biz_id = result.get("bizId")

        self._logger.info("Login successful")
        return {
            "access_token": self._client._access_token,
            "refresh_token": self._client._refresh_token,
            "expires_in": 0,
            "user_id": self._client._user_id or "",
        }

    async def refresh_access_token(self) -> LoginResponse:
        """Refresh access token."""
        if not self._client._refresh_token:
            msg = "No refresh token available"
            raise self._auth_error_cls(msg)

        result: ApiResponse = await self._client._smart_home_request(
            PATH_REFRESH_TOKEN,
            {
                "refreshToken": self._client._refresh_token,
                "model": "HomeAssistant",
            },
            require_auth=False,
        )

        access_token: str | None = result.get("access_token")  # type: ignore[assignment]
        refresh_token: str | None = result.get("refresh_token")  # type: ignore[assignment]
        if not access_token or not refresh_token:
            msg = "Refresh response missing access_token or refresh_token"
            raise self._auth_error_cls(msg)

        self._client._access_token = access_token
        self._client._refresh_token = refresh_token
        self._client._user_id = result.get("userId")

        self._logger.info("Token refreshed successfully")
        return {
            "access_token": self._client._access_token,
            "refresh_token": self._client._refresh_token,
            "expires_in": 0,
            "user_id": self._client._user_id or "",
        }
