"""Feedback/report-focused services.diagnostics assertions."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.services.diagnostics import (
    async_handle_get_developer_report,
    async_handle_submit_developer_feedback,
    collect_developer_reports,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from tests.helpers.service_call import service_call

from .test_services_diagnostics_support import _developer_feedback_report_fixture


@pytest.mark.parametrize(
    ("exporter_results", "expected_reports"),
    [
        (
            [
                {"runtime": {"ok": True, "entry": 1}},
                None,
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
    exporter_results: list[dict[str, Any] | Exception | None],
    expected_reports: list[dict[str, Any]],
) -> None:
    """collect_developer_reports should keep successful exporter reports only."""
    coordinators = [MagicMock() for _ in exporter_results]

    with patch(
        "custom_components.lipro.services.diagnostics.helpers._collect_exporter_developer_report",
        side_effect=exporter_results,
    ):
        result = collect_developer_reports(
            MagicMock(),
            iter_runtime_coordinators=lambda _: iter(coordinators),
            find_runtime_entry_for_coordinator=lambda _hass, _coordinator: MagicMock(),
            get_entry_telemetry_view=lambda _entry, _sink: None,
        )

    assert result == expected_reports


def test_collect_developer_reports_returns_exporter_view_for_bound_entry() -> None:
    """collect_developer_reports should return the exporter-backed developer view."""
    hass = MagicMock()
    entry = MagicMock(entry_id="entry-1", options={})
    coordinator = MagicMock(config_entry=entry)
    entry.runtime_data = coordinator
    hass.config_entries.async_entries.return_value = [entry]

    expected_report = {
        "entry_ref": "entry:1",
        "failure_summary": {
            "failure_category": "network",
            "failure_origin": "protocol.mqtt",
            "handling_policy": "retry",
            "error_type": "TimeoutError",
        },
        "runtime": {"ok": True},
    }

    get_entry_telemetry_view = MagicMock(return_value=expected_report)

    result = collect_developer_reports(
        cast(HomeAssistant, hass),
        iter_runtime_coordinators=lambda _: iter([coordinator]),
        find_runtime_entry_for_coordinator=lambda _hass, _coordinator: entry,
        get_entry_telemetry_view=get_entry_telemetry_view,
    )

    assert result == [expected_report]
    called_entry, called_sink = get_entry_telemetry_view.call_args.args
    assert called_sink == "developer"
    assert getattr(called_entry, "entry_id", None) == entry.entry_id
    assert getattr(called_entry, "runtime_data", None) is coordinator


def test_collect_developer_reports_skips_non_mapping_exporter_view() -> None:
    """Non-dict exporter payloads should be ignored."""
    hass = MagicMock()
    entry = MagicMock(entry_id="entry-1", options={})
    coordinator = SimpleNamespace(config_entry=entry)
    entry.runtime_data = coordinator
    hass.config_entries.async_entries.return_value = [entry]

    result = collect_developer_reports(
        cast(HomeAssistant, hass),
        iter_runtime_coordinators=lambda _: iter([coordinator]),
        find_runtime_entry_for_coordinator=lambda _hass, _coordinator: entry,
        get_entry_telemetry_view=lambda _entry, _sink: None,
    )

    assert result == []


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
    collect_reports = MagicMock(return_value=[_developer_feedback_report_fixture()])

    result = await async_handle_get_developer_report(
        hass,
        call,
        collect_reports=collect_reports,
        attr_entry_id="entry_id",
    )

    assert result == {
        "entry_count": 1,
        "reports": [_developer_feedback_report_fixture()],
        "requested_entry_id": "entry-2",
    }
    collect_reports.assert_called_once_with(hass, requested_entry_id="entry-2")


@pytest.mark.asyncio
async def test_async_handle_submit_developer_feedback_forwards_entry_id() -> None:
    """submit_developer_feedback should forward scoped entry_id to report collection and share manager."""
    hass = cast(HomeAssistant, MagicMock())
    call = service_call(hass, {"entry_id": "entry-2", "note": "manual run"})
    collect_reports = MagicMock(return_value=[_developer_feedback_report_fixture()])
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
    from custom_components.lipro.core.anonymous_share.report_builder import (
        canonicalize_generated_payload,
    )
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    payload = share_manager.submit_developer_feedback.await_args.args[1]
    assert canonicalize_generated_payload(payload) == load_external_boundary_fixture(
        "support_payload",
        "developer_feedback_service.canonical.json",
    )


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
