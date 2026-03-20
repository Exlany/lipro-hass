"""Tests for anonymous-share service handlers."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.telemetry.models import build_operation_outcome
from custom_components.lipro.services.share import (
    async_handle_get_anonymous_share_report,
    async_handle_submit_anonymous_share,
    build_anonymous_share_preview_response,
    build_submit_anonymous_share_response,
)
from homeassistant.core import HomeAssistant
from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture
from tests.helpers.service_call import service_call


@pytest.mark.asyncio
async def test_async_handle_submit_anonymous_share_success_returns_counts() -> None:
    hass = cast(HomeAssistant, MagicMock())

    share_manager = MagicMock()
    share_manager.is_enabled = True
    share_manager.pending_count = (2, 1)
    share_manager.last_submit_outcome = build_operation_outcome(
        kind="success",
        reason_code="submitted_lite_payload",
    )
    share_manager.submit_report = AsyncMock(return_value=True)

    result = await async_handle_submit_anonymous_share(
        hass,
        service_call(hass, {}),
        get_anonymous_share_manager=MagicMock(return_value=share_manager),
        get_client_session=MagicMock(return_value=object()),
        raise_service_error=MagicMock(),
        domain="lipro",
        attr_entry_id="entry_id",
    )

    assert result == {
        "success": True,
        "devices": 2,
        "errors": 1,
        "outcome_kind": "success",
        "reason_code": "submitted_lite_payload",
    }


@pytest.mark.asyncio
async def test_async_handle_submit_anonymous_share_forwards_entry_id() -> None:
    hass = cast(HomeAssistant, MagicMock())

    share_manager = MagicMock()
    share_manager.is_enabled = True
    share_manager.pending_count = (1, 0)
    share_manager.last_submit_outcome = None
    share_manager.submit_report = AsyncMock(return_value=True)
    get_anonymous_share_manager = MagicMock(return_value=share_manager)

    result = await async_handle_submit_anonymous_share(
        hass,
        service_call(hass, {"entry_id": "entry-2"}),
        get_anonymous_share_manager=get_anonymous_share_manager,
        get_client_session=MagicMock(return_value=object()),
        raise_service_error=MagicMock(),
        domain="lipro",
        attr_entry_id="entry_id",
    )

    get_anonymous_share_manager.assert_called_once_with(hass, entry_id="entry-2")
    assert result == load_external_boundary_fixture(
        "support_payload",
        "submit_anonymous_share_response.json",
    )


@pytest.mark.asyncio
async def test_async_handle_submit_anonymous_share_failure_returns_typed_outcome() -> None:
    hass = cast(HomeAssistant, MagicMock())

    share_manager = MagicMock()
    share_manager.is_enabled = True
    share_manager.pending_count = (1, 1)
    share_manager.last_submit_outcome = build_operation_outcome(
        kind="failed",
        reason_code="rate_limited",
        failure_origin="anonymous_share.submit_share_payload",
        error_type="RateLimitError",
        failure_category="network",
        handling_policy="retry",
        http_status=429,
        retry_after_seconds=30.0,
    )
    share_manager.submit_report = AsyncMock(return_value=False)

    result = await async_handle_submit_anonymous_share(
        hass,
        service_call(hass, {}),
        get_anonymous_share_manager=MagicMock(return_value=share_manager),
        get_client_session=MagicMock(return_value=object()),
        raise_service_error=MagicMock(),
        domain="lipro",
        attr_entry_id="entry_id",
    )

    assert result == {
        "success": False,
        "devices": 1,
        "errors": 1,
        "outcome_kind": "failed",
        "reason_code": "rate_limited",
        "failure_summary": {
            "failure_category": "network",
            "failure_origin": "anonymous_share.submit_share_payload",
            "handling_policy": "retry",
            "error_type": "RateLimitError",
        },
        "http_status": 429,
        "retry_after_seconds": 30.0,
    }


@pytest.mark.asyncio
async def test_async_handle_get_anonymous_share_report_forwards_entry_id() -> None:
    hass = cast(HomeAssistant, MagicMock())

    share_manager = MagicMock()
    share_manager.get_pending_report.return_value = {
        "device_count": 1,
        "error_count": 0,
        "devices": [{"iot_name": "lipro_light"}],
        "errors": [],
    }
    get_anonymous_share_manager = MagicMock(return_value=share_manager)

    result = await async_handle_get_anonymous_share_report(
        hass,
        service_call(hass, {"entry_id": "entry-9"}),
        get_anonymous_share_manager=get_anonymous_share_manager,
        attr_entry_id="entry_id",
    )

    get_anonymous_share_manager.assert_called_once_with(hass, entry_id="entry-9")
    assert result == load_external_boundary_fixture(
        "support_payload",
        "anonymous_share_preview_response.json",
    )


@pytest.mark.asyncio
async def test_async_handle_get_anonymous_share_report_without_data_returns_empty() -> (
    None
):
    hass = cast(HomeAssistant, MagicMock())

    share_manager = MagicMock()
    share_manager.get_pending_report.return_value = None

    result = await async_handle_get_anonymous_share_report(
        hass,
        service_call(hass, {}),
        get_anonymous_share_manager=MagicMock(return_value=share_manager),
        attr_entry_id="entry_id",
    )

    assert result == {
        "has_data": False,
        "devices": [],
        "errors": [],
    }


def test_build_submit_anonymous_share_response_matches_contract_fixture() -> None:
    assert build_submit_anonymous_share_response(
        device_count=1,
        error_count=0,
        requested_entry_id="entry-2",
    ) == load_external_boundary_fixture(
        "support_payload",
        "submit_anonymous_share_response.json",
    )


def test_build_anonymous_share_preview_response_matches_contract_fixture() -> None:
    report = {
        "device_count": 1,
        "error_count": 0,
        "devices": [{"iot_name": "lipro_light"}],
        "errors": [],
    }

    assert build_anonymous_share_preview_response(
        report,
        requested_entry_id="entry-9",
    ) == load_external_boundary_fixture(
        "support_payload",
        "anonymous_share_preview_response.json",
    )
