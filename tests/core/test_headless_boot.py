"""Focused regression tests for the local headless boot seam."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro import headless
from custom_components.lipro.core.auth import AuthBootstrapSeed, AuthSessionSnapshot
from custom_components.lipro.headless.boot import (
    HeadlessBootContext,
    build_headless_boot_context,
    build_password_boot_seed,
)

_HASHED_VALUE = 'hashed-value'
_UNSET = object()


def _seed(*, password_hash: str | None | object = _UNSET) -> AuthBootstrapSeed:
    effective_password_hash: str | None
    if password_hash is _UNSET:
        effective_password_hash = _HASHED_VALUE
    else:
        effective_password_hash = cast(str | None, password_hash)
    return AuthBootstrapSeed(
        phone='13800000000',
        phone_id='phone-id',
        password_hash=effective_password_hash,
    )


def test_headless_package_exports_no_public_surface() -> None:
    assert headless.__all__ == []


def test_headless_boot_module_stays_host_neutral() -> None:
    module_text = (
        Path(__file__).resolve().parents[2]
        / 'custom_components'
        / 'lipro'
        / 'headless'
        / 'boot.py'
    ).read_text(encoding='utf-8')

    assert 'homeassistant' not in module_text


def test_build_password_boot_seed_returns_hashed_seed() -> None:
    seed = build_password_boot_seed(
        '13800000000',
        _HASHED_VALUE,
        'phone-id',
    )

    assert seed.phone == '13800000000'
    assert seed.phone_id == 'phone-id'
    assert seed.password_hash == _HASHED_VALUE


def test_build_headless_boot_context_reuses_bootstrap_context() -> None:
    session = MagicMock(name='session')
    protocol = MagicMock(name='protocol')
    auth_manager = MagicMock(name='auth_manager')
    protocol_factory = MagicMock(name='protocol_factory')
    auth_manager_factory = MagicMock(name='auth_manager_factory')
    seed = _seed()

    with patch(
        'custom_components.lipro.headless.boot.build_protocol_auth_context',
        return_value=(protocol, auth_manager),
    ) as mock_build:
        context = build_headless_boot_context(
            seed,
            session,
            protocol_factory=protocol_factory,
            auth_manager_factory=auth_manager_factory,
        )

    assert context.seed == seed
    assert context.session is session
    assert context.protocol is protocol
    assert context.auth_manager is auth_manager
    mock_build.assert_called_once_with(
        seed,
        session,
        protocol_factory=protocol_factory,
        auth_manager_factory=auth_manager_factory,
    )


@pytest.mark.asyncio
async def test_headless_boot_login_uses_hashed_password() -> None:
    auth_session = AuthSessionSnapshot(
        access_token='access',
        refresh_token='refresh',
        user_id=10001,
        expires_at=123.0,
        phone_id='phone-id',
        biz_id='biz-id',
    )
    auth_manager = MagicMock(name='auth_manager')
    auth_manager.login = AsyncMock(return_value=auth_session)
    context = HeadlessBootContext(
        seed=_seed(),
        session=MagicMock(name='session'),
        protocol=MagicMock(name='protocol'),
        auth_manager=auth_manager,
    )

    result = await context.async_login_with_password_hash()

    assert result == auth_session
    auth_manager.login.assert_awaited_once_with(
        '13800000000',
        _HASHED_VALUE,
        password_is_hashed=True,
    )


@pytest.mark.asyncio
async def test_headless_boot_requires_password_hash_for_login() -> None:
    context = HeadlessBootContext(
        seed=_seed(password_hash=None),
        session=MagicMock(name='session'),
        protocol=MagicMock(name='protocol'),
        auth_manager=MagicMock(name='auth_manager'),
    )

    with pytest.raises(ValueError, match='password_hash is required'):
        await context.async_login_with_password_hash()


@pytest.mark.asyncio
async def test_headless_boot_exposes_snapshot_boundary() -> None:
    auth_session = AuthSessionSnapshot(
        access_token='access',
        refresh_token='refresh',
        user_id=10001,
        expires_at=123.0,
        phone_id='phone-id',
        biz_id='biz-id',
    )
    auth_manager = MagicMock(name='auth_manager')
    auth_manager.ensure_valid_token = AsyncMock()
    auth_manager.get_auth_session.return_value = auth_session
    context = HeadlessBootContext(
        seed=_seed(),
        session=MagicMock(name='session'),
        protocol=MagicMock(name='protocol'),
        auth_manager=auth_manager,
    )

    assert context.auth_session_snapshot() == auth_session
    ensured = await context.async_ensure_authenticated()

    assert ensured == auth_session
    auth_manager.ensure_valid_token.assert_awaited_once_with()
