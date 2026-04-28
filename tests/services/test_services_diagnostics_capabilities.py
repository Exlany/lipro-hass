"""Capability-routing services.diagnostics assertions."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from custom_components.lipro.services.diagnostics import (
    async_call_optional_capability,
    async_handle_get_city,
    async_handle_query_user_cloud,
)
from custom_components.lipro.services.diagnostics.helpers import (
    _async_get_first_authenticated_coordinator_capability_result,
    _async_get_first_coordinator_capability_result,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from tests.helpers.service_call import service_call

from .test_services_diagnostics_support import (
    _build_city_coordinator,
    _build_query_user_cloud_coordinator,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("coordinator_behaviors", "expected_result", "expected_raise_error_code"),
    [
        (
            [
                LiproApiError("temporary failure", code=500),
                RuntimeError("boom"),
                {"province": "浙江省", "city": "杭州市"},
            ],
            {"result": {"province": "浙江省", "city": "杭州市"}},
            None,
        ),
        (
            [
                RuntimeError("first broken"),
                RuntimeError("second broken"),
            ],
            {"result": {}},
            None,
        ),
        (
            [
                RuntimeError("unexpected"),
                LiproApiError("all failed", code=503),
            ],
            None,
            503,
        ),
    ],
)
async def test_async_handle_get_city_mixed_coordinator_outcomes(
    coordinator_behaviors: list[dict[str, Any] | Exception],
    expected_result: dict[str, Any] | None,
    expected_raise_error_code: int | None,
) -> None:
    """get_city should degrade per coordinator and decide final outcome by capability semantics."""
    coordinators = [
        _build_city_coordinator(behavior) for behavior in coordinator_behaviors
    ]
    raise_optional_error = MagicMock(side_effect=RuntimeError("service error"))
    hass = cast(HomeAssistant, MagicMock())

    if expected_raise_error_code is not None:
        with pytest.raises(RuntimeError, match="service error"):
            await async_handle_get_city(
                hass,
                service_call(hass, {}),
                iter_runtime_coordinators=lambda _: iter(coordinators),
                raise_optional_error=raise_optional_error,
                service_get_city="get_city",
            )
        raise_optional_error.assert_called_once()
        capability, err = raise_optional_error.call_args.args
        assert capability == "get_city"
        assert isinstance(err, LiproApiError)
        assert err.code == expected_raise_error_code
        return

    result = await async_handle_get_city(
        hass,
        service_call(hass, {}),
        iter_runtime_coordinators=lambda _: iter(coordinators),
        raise_optional_error=raise_optional_error,
        service_get_city="get_city",
    )
    assert result == expected_result
    raise_optional_error.assert_not_called()


@pytest.mark.asyncio
async def test_async_get_first_authenticated_coordinator_capability_result_reauths_and_degrades() -> (
    None
):
    """Auth-aware helper should trigger reauth and continue until one coordinator succeeds."""
    first = _build_city_coordinator(LiproAuthError("bad credentials"))
    second = _build_city_coordinator({"province": "广东省", "city": "深圳市"})

    (
        has_result,
        result,
        last_error,
    ) = await _async_get_first_authenticated_coordinator_capability_result(
        iter([first, second]),
        capability="get_city",
        collector=lambda coordinator: coordinator.protocol_service.async_get_city(),
    )

    assert has_result is True
    assert result == {"province": "广东省", "city": "深圳市"}
    assert last_error is None
    first.auth_service.async_ensure_authenticated.assert_awaited_once_with()
    first.auth_service.async_trigger_reauth.assert_awaited_once_with("auth_error")
    second.auth_service.async_ensure_authenticated.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_async_call_optional_capability_maps_api_error() -> None:
    """Optional capability helper should map LiproApiError via callback."""
    method = AsyncMock(side_effect=LiproApiError("upstream failed", code=502))
    raise_optional_error = MagicMock(side_effect=RuntimeError("mapped error"))

    with pytest.raises(RuntimeError, match="mapped error"):
        await async_call_optional_capability(
            "get_city",
            method,
            raise_optional_error=raise_optional_error,
            probe_id="city-1",
        )

    method.assert_awaited_once_with(probe_id="city-1")
    raise_optional_error.assert_called_once()
    capability, err = raise_optional_error.call_args.args
    assert capability == "get_city"
    assert isinstance(err, LiproApiError)
    assert err.code == 502


@pytest.mark.asyncio
async def test_async_get_first_coordinator_capability_result_raises_homeassistant_error() -> (
    None
):
    coordinator = MagicMock()
    coordinator.protocol.get_city = AsyncMock(side_effect=HomeAssistantError("stop"))

    with pytest.raises(HomeAssistantError, match="stop"):
        await _async_get_first_coordinator_capability_result(
            iter([coordinator]),
            capability="get_city",
            collector=lambda item: cast(MagicMock, item).protocol.get_city(),
        )


@pytest.mark.asyncio
async def test_async_get_first_coordinator_capability_result_keeps_last_api_error() -> (
    None
):
    first = MagicMock()
    first.protocol.get_city = AsyncMock(side_effect=RuntimeError("boom"))
    second = MagicMock()
    second.protocol.get_city = AsyncMock(
        side_effect=LiproApiError("api down", code=503)
    )

    (
        has_result,
        result,
        last_error,
    ) = await _async_get_first_coordinator_capability_result(
        iter([first, second]),
        capability="get_city",
        collector=lambda item: cast(MagicMock, item).protocol.get_city(),
    )

    assert has_result is False
    assert result is None
    assert isinstance(last_error, LiproApiError)
    assert last_error.code == 503


@pytest.mark.asyncio
async def test_async_handle_query_user_cloud_raises_last_api_error() -> None:
    """query_user_cloud should surface the last API error when all entries fail."""
    coordinator = _build_query_user_cloud_coordinator(
        LiproApiError("cloud unavailable", code=504)
    )
    raise_optional_error = MagicMock(side_effect=RuntimeError("mapped error"))
    hass = cast(HomeAssistant, MagicMock())

    with pytest.raises(RuntimeError, match="mapped error"):
        await async_handle_query_user_cloud(
            hass,
            service_call(hass, {}),
            iter_runtime_coordinators=lambda _hass: iter([coordinator]),
            raise_optional_error=raise_optional_error,
            service_query_user_cloud="query_user_cloud",
        )

    raise_optional_error.assert_called_once()


@pytest.mark.asyncio
async def test_async_handle_query_user_cloud_reauths_before_mapping_auth_failure() -> (
    None
):
    """query_user_cloud should trigger reauth when auth expires before surfacing error."""
    coordinator = _build_query_user_cloud_coordinator(
        LiproRefreshTokenExpiredError("expired")
    )
    raise_optional_error = MagicMock(side_effect=RuntimeError("mapped error"))
    hass = cast(HomeAssistant, MagicMock())

    with pytest.raises(RuntimeError, match="mapped error"):
        await async_handle_query_user_cloud(
            hass,
            service_call(hass, {}),
            iter_runtime_coordinators=lambda _hass: iter([coordinator]),
            raise_optional_error=raise_optional_error,
            service_query_user_cloud="query_user_cloud",
        )

    coordinator.auth_service.async_trigger_reauth.assert_awaited_once_with(
        "auth_expired"
    )
    capability, err = raise_optional_error.call_args.args
    assert capability == "query_user_cloud"
    assert isinstance(err, LiproRefreshTokenExpiredError)
