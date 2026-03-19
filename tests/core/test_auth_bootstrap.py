"""Focused tests for host-neutral auth bootstrap helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.auth import (
    AuthBootstrapSeed,
    async_login_with_password_hash,
    build_protocol_auth_context,
    hash_password_for_auth,
)

_DEFAULT_HASH = "hashed-value"


def _seed(
    *,
    password_hash: str | None = _DEFAULT_HASH,
    remember_password_hash: bool = False,
    request_timeout: int | None = None,
    entry_id: str | None = None,
    access_token: str | None = None,
    refresh_token: str | None = None,
    user_id: int | None = None,
    expires_at: float | None = None,
    biz_id: str | None = None,
) -> AuthBootstrapSeed:
    return AuthBootstrapSeed(
        phone="13800000000",
        phone_id="phone-id",
        password_hash=password_hash,
        remember_password_hash=remember_password_hash,
        request_timeout=request_timeout,
        entry_id=entry_id,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        expires_at=expires_at,
        biz_id=biz_id,
    )


def test_hash_password_for_auth_uses_vendor_md5_contract() -> None:
    assert hash_password_for_auth("demo-value") == "6d038b053fcd9e764a147d766df9021f"


def test_build_protocol_auth_context_passes_explicit_timeout_and_entry_id() -> None:
    session = MagicMock(name="session")
    client = MagicMock(name="protocol")
    auth_manager = MagicMock(name="auth_manager")
    protocol_factory = MagicMock(return_value=client)
    auth_manager_factory = MagicMock(return_value=auth_manager)

    result_client, result_auth_manager = build_protocol_auth_context(
        _seed(request_timeout=15, entry_id="entry-1"),
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )

    protocol_factory.assert_called_once_with(
        "phone-id",
        session,
        request_timeout=15,
        entry_id="entry-1",
    )
    auth_manager_factory.assert_called_once_with(client)
    assert result_client is client
    assert result_auth_manager is auth_manager


def test_build_protocol_auth_context_seeds_tokens_and_remembered_hash() -> None:
    session = MagicMock(name="session")
    client = MagicMock(name="protocol")
    auth_manager = MagicMock(name="auth_manager")
    protocol_factory = MagicMock(return_value=client)
    auth_manager_factory = MagicMock(return_value=auth_manager)

    build_protocol_auth_context(
        _seed(
            remember_password_hash=True,
            access_token="access",
            refresh_token="refresh",
            user_id=10001,
            expires_at=123.0,
            biz_id="biz-id",
        ),
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )

    auth_manager.set_tokens.assert_called_once_with(
        "access",
        "refresh",
        10001,
        123.0,
        "biz-id",
    )
    auth_manager.set_credentials.assert_called_once_with(
        "13800000000",
        _DEFAULT_HASH,
        password_is_hashed=True,
    )


@pytest.mark.asyncio
async def test_async_login_with_password_hash_requires_hash() -> None:
    with pytest.raises(ValueError, match="password_hash is required"):
        await async_login_with_password_hash(
            _seed(password_hash=None),
            MagicMock(name="session"),
            protocol_factory=MagicMock(),
            auth_manager_factory=MagicMock(),
        )


@pytest.mark.asyncio
async def test_async_login_with_password_hash_uses_auth_manager_login() -> None:
    session = MagicMock(name="session")
    client = MagicMock(name="protocol")
    auth_manager = MagicMock(name="auth_manager")
    auth_manager.login = AsyncMock(return_value=MagicMock(name="auth_session"))
    protocol_factory = MagicMock(return_value=client)
    auth_manager_factory = MagicMock(return_value=auth_manager)

    result = await async_login_with_password_hash(
        _seed(password_hash="abc123"),
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )

    auth_manager.login.assert_awaited_once_with(
        "13800000000",
        "abc123",
        password_is_hashed=True,
    )
    assert result is auth_manager.login.return_value
