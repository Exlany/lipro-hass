"""Tests for shared service execution helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.core.coordinator.services.auth_service import (
    CoordinatorAuthService,
)
from custom_components.lipro.runtime_types import RuntimeReauthReason
from custom_components.lipro.services.execution import (
    _async_ensure_authenticated,
    _async_trigger_reauth,
    async_capture_coordinator_call,
    async_execute_coordinator_call,
)


@pytest.mark.asyncio
async def test_async_ensure_authenticated_and_trigger_reauth_delegate_to_auth_service() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(
        async_ensure_authenticated=AsyncMock(),
        async_trigger_reauth=AsyncMock(),
    )

    await _async_ensure_authenticated(coordinator)
    await _async_trigger_reauth(coordinator, RuntimeReauthReason.AUTH_ERROR)

    coordinator.auth_service.async_ensure_authenticated.assert_awaited_once_with()
    coordinator.auth_service.async_trigger_reauth.assert_awaited_once_with(RuntimeReauthReason.AUTH_ERROR)


@pytest.mark.asyncio
async def test_async_capture_coordinator_call_returns_result_after_auth() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(async_ensure_authenticated=AsyncMock())

    has_result, result, captured_error = await async_capture_coordinator_call(
        coordinator,
        call=AsyncMock(return_value={"ok": True}),
    )

    assert has_result is True
    assert result == {"ok": True}
    assert captured_error is None
    coordinator.auth_service.async_ensure_authenticated.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_capture_coordinator_call_triggers_reauth_and_returns_auth_error() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(
        async_ensure_authenticated=AsyncMock(),
        async_trigger_reauth=AsyncMock(),
    )
    auth_error = LiproAuthError("bad credentials")

    has_result, result, captured_error = await async_capture_coordinator_call(
        coordinator,
        call=AsyncMock(side_effect=auth_error),
    )

    assert has_result is False
    assert result is None
    assert captured_error is auth_error
    coordinator.auth_service.async_trigger_reauth.assert_awaited_once_with(RuntimeReauthReason.AUTH_ERROR)


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_returns_result_after_auth() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(async_ensure_authenticated=AsyncMock())
    call = AsyncMock(return_value={"ok": True})
    raise_service_error = Mock()

    result = await async_execute_coordinator_call(
        coordinator,
        call=call,
        raise_service_error=raise_service_error,
    )

    assert result == {"ok": True}
    coordinator.auth_service.async_ensure_authenticated.assert_awaited_once_with()
    raise_service_error.assert_not_called()


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_triggers_reauth_for_expired_token() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(
        async_ensure_authenticated=AsyncMock(),
        async_trigger_reauth=AsyncMock(),
    )
    raise_service_error = Mock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=LiproRefreshTokenExpiredError("expired")),
            raise_service_error=raise_service_error,
        )

    coordinator.auth_service.async_trigger_reauth.assert_awaited_once_with(RuntimeReauthReason.AUTH_EXPIRED)
    raise_service_error.assert_called_once()


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_maps_auth_error_with_safe_placeholder() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(
        async_ensure_authenticated=AsyncMock(),
        async_trigger_reauth=AsyncMock(),
    )
    raise_service_error = Mock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=LiproAuthError("bad credentials")),
            raise_service_error=raise_service_error,
        )

    coordinator.auth_service.async_trigger_reauth.assert_awaited_once_with(RuntimeReauthReason.AUTH_ERROR)
    assert raise_service_error.call_args.args == ("auth_error",)
    assert "error" in raise_service_error.call_args.kwargs["translation_placeholders"]


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_with_real_auth_service_maps_auth_error(
    hass,
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    coordinator = Mock(
        auth_service=CoordinatorAuthService(
            hass=hass,
            auth_manager=MagicMock(async_ensure_authenticated=AsyncMock()),
            config_entry=entry,
        )
    )
    raise_service_error = Mock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=LiproAuthError("bad credentials")),
            raise_service_error=raise_service_error,
        )

    entry.async_start_reauth.assert_called_once_with(hass)
    assert raise_service_error.call_args.args == ("auth_error",)
    assert "error" in raise_service_error.call_args.kwargs["translation_placeholders"]


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_with_real_auth_service_maps_refresh_expiry(
    hass,
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    entry.async_start_reauth = MagicMock()
    coordinator = Mock(
        auth_service=CoordinatorAuthService(
            hass=hass,
            auth_manager=MagicMock(async_ensure_authenticated=AsyncMock()),
            config_entry=entry,
        )
    )
    raise_service_error = Mock(side_effect=RuntimeError("mapped"))

    with pytest.raises(RuntimeError, match="mapped"):
        await async_execute_coordinator_call(
            coordinator,
            call=AsyncMock(side_effect=LiproRefreshTokenExpiredError("expired")),
            raise_service_error=raise_service_error,
        )

    entry.async_start_reauth.assert_called_once_with(hass)
    assert raise_service_error.call_args.args == ("auth_expired",)
    assert isinstance(
        raise_service_error.call_args.kwargs["err"],
        LiproRefreshTokenExpiredError,
    )


@pytest.mark.asyncio
async def test_async_execute_coordinator_call_passes_api_errors_to_handler() -> None:
    coordinator = Mock()
    coordinator.auth_service = Mock(async_ensure_authenticated=AsyncMock())
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
