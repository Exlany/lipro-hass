"""Auth endpoints and collaborators for the REST facade."""

from __future__ import annotations

from ..client_base import _ClientBase
from ..types import LoginResponse
from .payloads import _EndpointAdapter


class _ClientAuthEndpointsMixin(_ClientBase):
    """Legacy auth endpoint mixin retained for focused helper tests."""

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


class AuthEndpoints(_EndpointAdapter, _ClientAuthEndpointsMixin):
    """Explicit auth endpoint collaborator for ``LiproRestFacade``."""

    EXPORTED_METHODS = (
        "login",
        "refresh_access_token",
    )


__all__ = ["AuthEndpoints", "_ClientAuthEndpointsMixin"]
