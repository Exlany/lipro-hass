"""Local, proof-only headless boot composition helpers.

This module is a local boot seam for adapter/proof consumers. It is not a
canonical or transitional public surface. The caller owns the lifecycle of the
passed HTTP session.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.auth import (
    AuthBootstrapSeed,
    AuthSessionSnapshot,
    LiproAuthManager,
    build_protocol_auth_context,
)
from ..core.protocol import LiproProtocolFacade

if TYPE_CHECKING:
    import aiohttp


@dataclass(slots=True)
class HeadlessBootContext:
    """One local headless boot context built from the formal auth bootstrap.

    The caller owns the provided session lifecycle. This wrapper only exposes
    the authenticated protocol/auth collaborators plus the formal auth-session
    snapshot boundary needed by proof/adapters.
    """

    seed: AuthBootstrapSeed
    session: aiohttp.ClientSession
    protocol: LiproProtocolFacade
    auth_manager: LiproAuthManager

    async def async_login_with_password_hash(self) -> AuthSessionSnapshot:
        """Authenticate with the hashed password stored on the bootstrap seed."""
        if not self.seed.password_hash:
            msg = 'password_hash is required for hashed login'
            raise ValueError(msg)
        return await self.auth_manager.login(
            self.seed.phone,
            self.seed.password_hash,
            password_is_hashed=True,
        )

    async def async_ensure_authenticated(self) -> AuthSessionSnapshot:
        """Ensure the protocol/auth pair is authenticated and return the snapshot."""
        await self.auth_manager.ensure_valid_token()
        return self.auth_session_snapshot()

    def auth_session_snapshot(self) -> AuthSessionSnapshot:
        """Return the formal auth/session snapshot for this boot context."""
        return self.auth_manager.get_auth_session()


def build_password_boot_seed(
    phone: str,
    password_hash: str,
    phone_id: str,
) -> AuthBootstrapSeed:
    """Build one hashed-password bootstrap seed for local proof/adapters."""
    return AuthBootstrapSeed(
        phone=phone,
        phone_id=phone_id,
        password_hash=password_hash,
    )


def build_headless_boot_context(
    seed: AuthBootstrapSeed,
    session: aiohttp.ClientSession,
    *,
    protocol_factory: type[LiproProtocolFacade],
    auth_manager_factory: type[LiproAuthManager],
) -> HeadlessBootContext:
    """Build one local headless boot context from the host-neutral seed."""
    protocol, auth_manager = build_protocol_auth_context(
        seed,
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )
    return HeadlessBootContext(
        seed=seed,
        session=session,
        protocol=protocol,
        auth_manager=auth_manager,
    )
