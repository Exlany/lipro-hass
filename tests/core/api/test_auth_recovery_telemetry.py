"""Tests for auth-recovery telemetry summaries."""

from __future__ import annotations

from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.lipro.core.api.client_auth_recovery import (
    AuthRecoveryCoordinator,
)
from custom_components.lipro.core.api.client_base import ClientSessionState
from custom_components.lipro.core.api.errors import LiproAuthError


def _state() -> ClientSessionState:
    return ClientSessionState(
        phone_id="13800000000",
        session=MagicMock(spec=aiohttp.ClientSession),
        request_timeout=30,
        entry_id="entry-1",
    )


@pytest.mark.asyncio
async def test_auth_recovery_telemetry_tracks_success_and_reuse() -> None:
    state = _state()
    state.access_token = "old-token"
    coordinator = AuthRecoveryCoordinator(state)

    async def refresh() -> None:
        state.access_token = "new-token"

    coordinator.set_token_refresh_callback(refresh)

    assert await coordinator.handle_401_with_refresh("old-token") is True
    assert await coordinator.handle_401_with_refresh("old-token") is True

    snapshot = coordinator.telemetry_snapshot()

    assert snapshot["refresh_attempt_count"] == 1
    assert snapshot["refresh_success_count"] == 1
    assert snapshot["refresh_reused_count"] == 1
    assert snapshot["last_refresh_outcome"] == "reused"


@pytest.mark.asyncio
async def test_auth_recovery_telemetry_tracks_auth_failure() -> None:
    state = _state()
    state.access_token = "old-token"
    coordinator = AuthRecoveryCoordinator(state)

    async def refresh() -> None:
        raise LiproAuthError("bad token", "token_expired")

    coordinator.set_token_refresh_callback(refresh)

    assert await coordinator.handle_401_with_refresh("old-token") is False

    snapshot = coordinator.telemetry_snapshot()

    assert snapshot["refresh_attempt_count"] == 1
    assert snapshot["refresh_failure_count"] == 1
    assert snapshot["last_refresh_outcome"] == "auth_error"
    assert snapshot["last_refresh_error_type"] == "LiproAuthError"
