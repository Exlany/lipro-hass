"""Host-neutral auth bootstrap helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..protocol import LiproProtocolFacade
from ..utils.vendor_crypto import md5_compat_hexdigest
from .manager import AuthSessionSnapshot, LiproAuthManager

if TYPE_CHECKING:
    import aiohttp


@dataclass(frozen=True, slots=True)
class AuthBootstrapSeed:
    """Host-neutral seed used to bootstrap protocol/auth collaborators."""

    phone: str
    phone_id: str
    password_hash: str | None = None
    remember_password_hash: bool = False
    request_timeout: int | None = None
    entry_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    user_id: int | None = None
    expires_at: float | None = None
    biz_id: str | None = None

    @property
    def has_token_pair(self) -> bool:
        """Return whether both access and refresh tokens are available."""
        return bool(self.access_token and self.refresh_token)


def hash_password_for_auth(password: str) -> str:
    """Hash one password using the vendor-mandated MD5 compatibility digest."""
    return md5_compat_hexdigest(password)


def build_protocol_auth_context(
    seed: AuthBootstrapSeed,
    session: aiohttp.ClientSession,
    *,
    client_factory: type[LiproProtocolFacade],
    auth_manager_factory: type[LiproAuthManager],
) -> tuple[LiproProtocolFacade, LiproAuthManager]:
    """Build one protocol/auth pair from the host-neutral bootstrap seed."""
    if seed.request_timeout is not None and seed.entry_id is not None:
        client = client_factory(
            seed.phone_id,
            session,
            request_timeout=seed.request_timeout,
            entry_id=seed.entry_id,
        )
    elif seed.request_timeout is not None:
        client = client_factory(
            seed.phone_id,
            session,
            request_timeout=seed.request_timeout,
        )
    elif seed.entry_id is not None:
        client = client_factory(
            seed.phone_id,
            session,
            entry_id=seed.entry_id,
        )
    else:
        client = client_factory(seed.phone_id, session)
    auth_manager = auth_manager_factory(client)

    if seed.has_token_pair:
        auth_manager.set_tokens(
            seed.access_token or '',
            seed.refresh_token or '',
            seed.user_id,
            seed.expires_at,
            seed.biz_id,
        )

    if seed.remember_password_hash and seed.password_hash:
        auth_manager.set_credentials(
            seed.phone,
            seed.password_hash,
            password_is_hashed=True,
        )

    return client, auth_manager


async def async_login_with_password_hash(
    seed: AuthBootstrapSeed,
    session: aiohttp.ClientSession,
    *,
    client_factory: type[LiproProtocolFacade],
    auth_manager_factory: type[LiproAuthManager],
) -> AuthSessionSnapshot:
    """Authenticate using the host-neutral seed and return the formal session."""
    if not seed.password_hash:
        msg = 'password_hash is required for hashed login'
        raise ValueError(msg)

    _, auth_manager = build_protocol_auth_context(
        seed,
        session,
        client_factory=client_factory,
        auth_manager_factory=auth_manager_factory,
    )
    return await auth_manager.login(
        seed.phone,
        seed.password_hash,
        password_is_hashed=True,
    )
