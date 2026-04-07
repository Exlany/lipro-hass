"""Tests for auth-recovery telemetry summaries."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.lipro.core.api import (
    LiproApiError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.api.auth_recovery import RestAuthRecoveryCoordinator
from custom_components.lipro.core.api.errors import LiproAuthError
from custom_components.lipro.core.api.session_state import RestSessionState


def _state() -> RestSessionState:
    return RestSessionState(
        phone_id="13800000000",
        session=MagicMock(spec=aiohttp.ClientSession),
        request_timeout=30,
        entry_id="entry-1",
    )


@pytest.mark.asyncio
async def test_auth_recovery_telemetry_tracks_success_and_reuse() -> None:
    state = _state()
    state.access_token = "old-token"
    coordinator = RestAuthRecoveryCoordinator(state)

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
async def test_finalize_mapping_result_retries_after_successful_auth_refresh() -> None:
    state = _state()
    state.access_token = "old-token"
    coordinator = RestAuthRecoveryCoordinator(state)

    async def refresh() -> None:
        state.access_token = "new-token"

    coordinator.set_token_refresh_callback(refresh)
    retry_request = AsyncMock(return_value={"ok": True})

    result = await coordinator.finalize_mapping_result(
        path="/v2/test",
        result={"code": "token_expired", "message": "expired"},
        request_token="old-token",
        is_retry=False,
        retry_on_auth_error=True,
        retry_request=retry_request,
        success_payload=lambda payload: payload,
    )

    assert result == {"ok": True}
    retry_request.assert_awaited_once()


@pytest.mark.asyncio
async def test_finalize_mapping_result_raises_api_error_for_non_auth_failure() -> None:
    state = _state()
    coordinator = RestAuthRecoveryCoordinator(state)

    with pytest.raises(LiproApiError, match="boom"):
        await coordinator.finalize_mapping_result(
            path="/v2/test",
            result={"code": 500, "errorCode": "bad_request", "message": "boom"},
            request_token=None,
            is_retry=False,
            retry_on_auth_error=True,
            retry_request=AsyncMock(),
            success_payload=lambda payload: payload,
        )


@pytest.mark.asyncio
async def test_auth_recovery_telemetry_tracks_auth_failure() -> None:
    state = _state()
    state.access_token = "old-token"
    coordinator = RestAuthRecoveryCoordinator(state)

    async def refresh() -> None:
        raise LiproAuthError("bad token", "token_expired")

    coordinator.set_token_refresh_callback(refresh)

    assert await coordinator.handle_401_with_refresh("old-token") is False

    snapshot = coordinator.telemetry_snapshot()

    assert snapshot["refresh_attempt_count"] == 1
    assert snapshot["refresh_failure_count"] == 1
    assert snapshot["last_refresh_outcome"] == "auth_error"
    assert snapshot["last_refresh_error_type"] == "LiproAuthError"


@pytest.mark.asyncio
async def test_auth_recovery_without_refresh_callback_returns_false() -> None:
    state = _state()
    state.access_token = "access"
    coordinator = RestAuthRecoveryCoordinator(state)

    assert await coordinator.handle_401_with_refresh("access") is False


@pytest.mark.asyncio
async def test_auth_recovery_without_token_update_returns_false() -> None:
    state = _state()
    state.access_token = "old-token"
    coordinator = RestAuthRecoveryCoordinator(state)
    refresh = AsyncMock()
    coordinator.set_token_refresh_callback(refresh)

    assert await coordinator.handle_401_with_refresh("old-token") is False
    refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_recovery_connection_error_bubbles() -> None:
    state = _state()
    state.access_token = "access"
    coordinator = RestAuthRecoveryCoordinator(state)
    coordinator.set_token_refresh_callback(
        AsyncMock(side_effect=LiproConnectionError("timeout"))
    )

    with pytest.raises(LiproConnectionError, match="timeout"):
        await coordinator.handle_401_with_refresh("access")


@pytest.mark.asyncio
async def test_auth_recovery_refresh_token_expired_bubbles() -> None:
    state = _state()
    state.access_token = "access"
    coordinator = RestAuthRecoveryCoordinator(state)
    coordinator.set_token_refresh_callback(
        AsyncMock(side_effect=LiproRefreshTokenExpiredError("expired"))
    )

    with pytest.raises(LiproRefreshTokenExpiredError, match="expired"):
        await coordinator.handle_401_with_refresh("access")


@pytest.mark.asyncio
async def test_auth_recovery_refresh_auth_error_returns_false() -> None:
    state = _state()
    state.access_token = "access"
    coordinator = RestAuthRecoveryCoordinator(state)
    coordinator.set_token_refresh_callback(
        AsyncMock(side_effect=LiproAuthError("invalid"))
    )

    assert await coordinator.handle_401_with_refresh("access") is False
