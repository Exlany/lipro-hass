"""Auth endpoint service for Lipro API client."""
# ruff: noqa: SLF001

from __future__ import annotations

import hashlib
from typing import Any

from ...const import CONF_ACCESS_TOKEN, CONF_BIZ_ID, CONF_REFRESH_TOKEN, CONF_USER_ID
from ...const.api import PATH_LOGIN, PATH_REFRESH_TOKEN


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
    ) -> dict[str, Any]:
        """Login with phone number and password/hash."""
        if password_is_hashed:
            password_hash = password
        else:
            password_hash = hashlib.md5(
                password.encode("utf-8"), usedforsecurity=False
            ).hexdigest()

        result = await self._client._smart_home_request(
            PATH_LOGIN,
            {
                "phone": phone,
                "password": password_hash,
            },
            require_auth=False,
        )

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        if not access_token or not refresh_token:
            msg = "Login response missing access_token or refresh_token"
            raise self._auth_error_cls(msg)

        self._client._access_token = access_token
        self._client._refresh_token = refresh_token
        self._client._user_id = result.get("userId")
        self._client._biz_id = result.get("bizId")

        self._logger.info("Login successful")
        return {
            CONF_ACCESS_TOKEN: self._client._access_token,
            CONF_REFRESH_TOKEN: self._client._refresh_token,
            CONF_USER_ID: self._client._user_id,
            CONF_BIZ_ID: self._client._biz_id,
            "phone": result.get("phone"),
            "user_name": result.get("userName"),
        }

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh access token."""
        if not self._client._refresh_token:
            msg = "No refresh token available"
            raise self._auth_error_cls(msg)

        result = await self._client._smart_home_request(
            PATH_REFRESH_TOKEN,
            {
                "refreshToken": self._client._refresh_token,
                "model": "HomeAssistant",
            },
            require_auth=False,
        )

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        if not access_token or not refresh_token:
            msg = "Refresh response missing access_token or refresh_token"
            raise self._auth_error_cls(msg)

        self._client._access_token = access_token
        self._client._refresh_token = refresh_token
        self._client._user_id = result.get("userId")

        self._logger.info("Token refreshed successfully")
        return {
            CONF_ACCESS_TOKEN: self._client._access_token,
            CONF_REFRESH_TOKEN: self._client._refresh_token,
            CONF_USER_ID: self._client._user_id,
        }
