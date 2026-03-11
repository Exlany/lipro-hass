"""Auth endpoints for LiproClient."""

from __future__ import annotations

from ..client_base import _ClientBase
from ..types import LoginResponse


class _ClientAuthEndpointsMixin(_ClientBase):
    """Endpoints: authentication."""

    async def login(
        self,
        phone: str,
        password: str,
        *,
        password_is_hashed: bool = False,
    ) -> LoginResponse:
        """Login with phone number and password."""
        return await self._auth_api.login(
            phone,
            password,
            password_is_hashed=password_is_hashed,
        )

    async def refresh_access_token(self) -> LoginResponse:
        """Refresh the access token."""
        return await self._auth_api.refresh_access_token()


__all__ = ["_ClientAuthEndpointsMixin"]
