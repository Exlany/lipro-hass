"""Tests for shared service execution helpers."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.core import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.services.execution import (
    AuthenticatedCoordinator,
    _async_ensure_authenticated,
    _async_trigger_reauth,
    async_execute_coordinator_call,
)


@pytest.mark.asyncio
async def test_async_ensure_authenticated_and_trigger_reauth_noop_without_methods() -> (
    None
):
    coordinator = cast(AuthenticatedCoordinator, object())

    await _async_ensure_authenticated(coordinator)
    await _async_trigger_reauth(coordinator, "auth_error")


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_returns_result_after_auth() -> None:
    coordinator = Mock()
    coordinator._async_ensure_authenticated = AsyncMock()
    call = AsyncMock(return_value={"ok": True})
    raise_service_error = Mock()

    result = await async_execute_coordinator_call(
        coordinator,
        call=call,
        raise_service_error=raise_service_error,
    )

    assert result == {"ok": True}
    coordinator._async_ensure_authenticated.assert_awaited_once_with()
    raise_service_error.assert_not_called()


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_triggers_reauth_for_expired_token() -> None:
    coordinator = Mock()
    coordinator._async_ensure_authenticated = AsyncMock()
    coordinator._trigger_reauth = AsyncMock()
    raise_service_error = Mock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=LiproRefreshTokenExpiredError("expired")),
            raise_service_error=raise_service_error,
        )

    coordinator._trigger_reauth.assert_awaited_once_with("auth_expired")
    raise_service_error.assert_called_once()


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_maps_auth_error_with_safe_placeholder() -> (
    None
):
    coordinator = Mock()
    coordinator._async_ensure_authenticated = AsyncMock()
    coordinator._trigger_reauth = AsyncMock()
    raise_service_error = Mock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=LiproAuthError("bad credentials")),
            raise_service_error=raise_service_error,
        )

    coordinator._trigger_reauth.assert_awaited_once()
    assert coordinator._trigger_reauth.await_args.args == ("auth_error",)
    assert raise_service_error.call_args.args == ("auth_error",)
    assert "error" in raise_service_error.call_args.kwargs["translation_placeholders"]


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_passes_api_errors_to_handler() -> None:
    coordinator = Mock()
    coordinator._async_ensure_authenticated = AsyncMock()
    raise_service_error = Mock()
    api_error = LiproApiError("upstream", code=502)
    handle_api_error = Mock()

    with pytest.raises(LiproApiError, match="upstream"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=api_error),
            raise_service_error=raise_service_error,
            handle_api_error=handle_api_error,
        )

    handle_api_error.assert_called_once_with(api_error)
    raise_service_error.assert_not_called()
