"""Auth endpoints for LiproClient."""

from __future__ import annotations

from typing import Any

from ..client_base import _ClientBase


class _ClientAuthEndpointsMixin(_ClientBase):
    """Endpoints: authentication."""

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> dict[str, Any]:
        """Login with phone number and password."""
        return await self._auth_api.login(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh the access token."""
        return await self._auth_api.refresh_access_token()


__all__ = ["_ClientAuthEndpointsMixin"]
