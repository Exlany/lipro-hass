"""Tests for services.diagnostics coordinator fault-tolerance behavior."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core import LiproApiError
from custom_components.lipro.services.diagnostics import (
    async_call_optional_capability,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_query_user_cloud,
    async_handle_submit_developer_feedback,
    collect_developer_reports,
)
from custom_components.lipro.services.diagnostics.handlers import (
    _build_last_error_payload,
)
from custom_components.lipro.services.diagnostics.helpers import (
    _async_get_first_coordinator_capability_result,
    _coerce_service_float,
    _coerce_service_int,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
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
        attr_entry_id="entry_id",
        raise_service_error=raise_service_error,
    )

    assert result == {
        "success": False,
        "message": "No active Lipro config entries",
        "submitted_entries": 0,
    }
    collect_reports.assert_called_once_with(hass, requested_entry_id=None)
    get_anonymous_share_manager.assert_not_called()
    get_client_session.assert_not_called()
    raise_service_error.assert_not_called()


@pytest.mark.asyncio
async def test_async_handle_get_developer_report_forwards_entry_id() -> None:
    """get_developer_report should scope collection when entry_id is provided."""
    hass = cast(HomeAssistant, MagicMock())
    call = service_call(hass, {"entry_id": "entry-2"})
    collect_reports = MagicMock(return_value=[{"runtime": {"ok": True}}])

    result = await async_handle_get_developer_report(
        hass,
        call,
        collect_reports=collect_reports,
        attr_entry_id="entry_id",
    )

    assert result == {
        "entry_count": 1,
        "reports": [{"runtime": {"ok": True}}],
        "requested_entry_id": "entry-2",
    }
    collect_reports.assert_called_once_with(hass, requested_entry_id="entry-2")


@pytest.mark.asyncio
async def test_async_handle_submit_developer_feedback_forwards_entry_id() -> None:
    """submit_developer_feedback should forward scoped entry_id to report collection and share manager."""
    hass = cast(HomeAssistant, MagicMock())
    call = service_call(hass, {"entry_id": "entry-2", "note": "manual run"})
    collect_reports = MagicMock(return_value=[{"runtime": {"ok": True}}])
    share_manager = MagicMock()
    share_manager.submit_developer_feedback = AsyncMock(return_value=True)
    get_anonymous_share_manager = MagicMock(return_value=share_manager)
    session = MagicMock()
    get_client_session = MagicMock(return_value=session)
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
        attr_entry_id="entry_id",
        raise_service_error=raise_service_error,
    )

    assert result == {
        "success": True,
        "submitted_entries": 1,
        "requested_entry_id": "entry-2",
    }
    collect_reports.assert_called_once_with(hass, requested_entry_id="entry-2")
    get_anonymous_share_manager.assert_called_once_with(hass, entry_id="entry-2")
    share_manager.submit_developer_feedback.assert_awaited_once()
    payload = share_manager.submit_developer_feedback.await_args.args[1]
    assert payload["requested_entry_id"] == "entry-2"


@pytest.mark.asyncio
async def test_async_handle_get_developer_report_propagates_entry_validation() -> None:
    """get_developer_report should surface entry validation errors from the collector."""
    hass = cast(HomeAssistant, MagicMock())
    collect_reports = MagicMock(
        side_effect=ServiceValidationError(
            translation_domain="lipro", translation_key="entry_not_found"
        )
    )

    with pytest.raises(ServiceValidationError):
        await async_handle_get_developer_report(
            hass,
            service_call(hass, {"entry_id": "missing-entry"}),
            collect_reports=collect_reports,
            attr_entry_id="entry_id",
        )


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


def test_service_number_coercion_handles_bool_and_default() -> None:
    """Numeric coercion should preserve schema-friendly bool and fallback behavior."""
    hass = cast(HomeAssistant, MagicMock())
    call = service_call(hass, {"int_value": True, "float_value": False, "bad": object()})

    assert _coerce_service_int(call, "int_value", 7) == 1
    assert _coerce_service_int(call, "bad", 7) == 7
    assert _coerce_service_float(call, "float_value", 1.5) == 0.0
    assert _coerce_service_float(call, "missing", 1.5) == 1.5


@pytest.mark.asyncio
async def test_async_get_first_coordinator_capability_result_raises_homeassistant_error() -> (
    None
):
    coordinator = MagicMock()
    coordinator.client.get_city = AsyncMock(side_effect=HomeAssistantError("stop"))

    with pytest.raises(HomeAssistantError, match="stop"):
        await _async_get_first_coordinator_capability_result(
            iter([coordinator]),
            capability="get_city",
            collector=lambda item: item.client.get_city(),
        )


@pytest.mark.asyncio
async def test_async_get_first_coordinator_capability_result_keeps_last_api_error() -> (
    None
):
    first = MagicMock()
    first.client.get_city = AsyncMock(side_effect=RuntimeError("boom"))
    second = MagicMock()
    second.client.get_city = AsyncMock(side_effect=LiproApiError("api down", code=503))

    has_result, result, last_error = await _async_get_first_coordinator_capability_result(
        iter([first, second]),
        capability="get_city",
        collector=lambda item: item.client.get_city(),
    )

    assert has_result is False
    assert result is None
    assert isinstance(last_error, LiproApiError)
    assert last_error.code == 503


def test_build_last_error_payload_omits_empty_message_and_none_code() -> None:
    """Serializable last-error payload should only include meaningful fields."""
    assert _build_last_error_payload(None) is None
    assert _build_last_error_payload(LiproApiError("   ", code=None)) is None
    assert _build_last_error_payload(LiproApiError("bad gateway", code=502)) == {
        "code": 502,
        "message": "bad gateway",
    }


@pytest.mark.asyncio
async def test_async_handle_query_user_cloud_raises_last_api_error() -> None:
    """query_user_cloud should surface the last API error when all entries fail."""
    coordinator = MagicMock()
    coordinator.client.query_user_cloud = AsyncMock(
        side_effect=LiproApiError("cloud unavailable", code=504)
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
