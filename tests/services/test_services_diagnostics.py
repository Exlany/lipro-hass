"""Tests for services.diagnostics coordinator fault-tolerance behavior."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core import LiproApiError
from custom_components.lipro.services.diagnostics_service import (
    async_call_optional_capability,
    async_handle_get_city,
    async_handle_submit_developer_feedback,
    collect_developer_reports,
)
from homeassistant.core import HomeAssistant
from tests.helpers.service_call import service_call


def _build_report_coordinator(
    behavior: dict[str, Any] | Exception,
) -> MagicMock:
    """Create a coordinator mock for developer-report collection."""
    coordinator = MagicMock()
    if isinstance(behavior, Exception):
        coordinator.build_developer_report.side_effect = behavior
    else:
        coordinator.build_developer_report.return_value = behavior
    return coordinator


def _build_city_coordinator(
    behavior: dict[str, Any] | Exception,
) -> MagicMock:
    """Create a coordinator mock for get_city capability."""
    coordinator = MagicMock()
    coordinator.client.get_city = AsyncMock()
    if isinstance(behavior, Exception):
        coordinator.client.get_city.side_effect = behavior
    else:
        coordinator.client.get_city.return_value = behavior
    return coordinator


@pytest.mark.parametrize(
    ("coordinator_behaviors", "expected_reports"),
    [
        (
            [
                {"runtime": {"ok": True, "entry": 1}},
                RuntimeError("boom"),
                {"runtime": {"ok": True, "entry": 3}},
            ],
            [
                {"runtime": {"ok": True, "entry": 1}},
                {"runtime": {"ok": True, "entry": 3}},
            ],
        ),
        (
            [
                RuntimeError("first broken"),
                RuntimeError("second broken"),
            ],
            [],
        ),
    ],
)
def test_collect_developer_reports_mixed_coordinator_outcomes(
    coordinator_behaviors: list[dict[str, Any] | Exception],
    expected_reports: list[dict[str, Any]],
) -> None:
    """collect_developer_reports should keep successful entries only."""
    coordinators = [
        _build_report_coordinator(behavior) for behavior in coordinator_behaviors
    ]
    # Should be ignored when capability is unavailable.
    coordinators.insert(1, MagicMock(spec=[]))

    result = collect_developer_reports(
        MagicMock(),
        iter_runtime_coordinators=lambda _: iter(coordinators),
    )

    assert result == expected_reports


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
async def test_async_handle_submit_developer_feedback_no_active_entries() -> None:
    """submit_developer_feedback should return concise failure when no reports."""
    hass = cast(HomeAssistant, MagicMock())
    call = service_call(hass, {})
    collect_reports = MagicMock(return_value=[])
    get_anonymous_share_manager = MagicMock()
    get_client_session = MagicMock()
    raise_service_error = MagicMock()

    result = await async_handle_submit_developer_feedback(
        hass,
        call,
        collect_reports=collect_reports,
        get_anonymous_share_manager=get_anonymous_share_manager,
        get_client_session=get_client_session,
        domain="lipro",
        service_submit_developer_feedback="submit_developer_feedback",
        attr_note="note",
        raise_service_error=raise_service_error,
    )

    assert result == {
        "success": False,
        "message": "No active Lipro config entries",
        "submitted_entries": 0,
    }
    collect_reports.assert_called_once_with(hass)
    get_anonymous_share_manager.assert_not_called()
    get_client_session.assert_not_called()
    raise_service_error.assert_not_called()


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
