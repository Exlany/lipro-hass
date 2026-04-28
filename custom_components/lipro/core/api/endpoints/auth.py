"""Auth endpoints and collaborators for the REST facade."""

from __future__ import annotations

from ..types import LoginResponse
from .payloads import _EndpointAdapter


class AuthEndpoints(_EndpointAdapter):
    """Auth endpoint helpers for the formal REST facade."""

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


__all__ = ["AuthEndpoints"]
