"""Focused developer-report and feedback handlers for diagnostics services."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from ...control import telemetry_surface as _telemetry_surface
from ...control.runtime_access import (
    find_runtime_entry_for_coordinator as _find_runtime_entry_for_coordinator,
)
from ...runtime_types import LiproCoordinator
from .helper_support import (
    build_developer_feedback_payload as _support_build_developer_feedback_payload,
)
from .types import (
    DeveloperFeedbackResponse,
    DeveloperReport,
    DeveloperReportCollector,
    DeveloperReportResponse,
    RuntimeCoordinatorIterator,
)

if TYPE_CHECKING:
    from logging import Logger

    from homeassistant.core import ServiceCall

    from .types import AnonymousShareManagerFactory, ClientSessionGetter

_CAPABILITY_PROJECTION_ERRORS = (RuntimeError, ValueError, TypeError, LookupError)


def _collect_exporter_developer_report(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> DeveloperReport | None:
    """Return the exporter-backed developer report for one runtime entry."""
    entry = _find_runtime_entry_for_coordinator(hass, coordinator)
    if entry is None:
        return None
    view = _telemetry_surface.get_entry_telemetry_view(entry, "developer")
    if isinstance(view, dict):
        return view
    return None


def collect_developer_reports(
    hass: HomeAssistant,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
    logger: Logger,
) -> list[DeveloperReport]:
    """Collect exporter-backed developer reports from active config entries."""
    reports: list[DeveloperReport] = []
    for coordinator in iter_runtime_coordinators(hass):
        try:
            exporter_report = _collect_exporter_developer_report(hass, coordinator)
            if exporter_report is not None:
                reports.append(dict(exporter_report))
        except asyncio.CancelledError:
            raise
        except HomeAssistantError:
            raise
        except _CAPABILITY_PROJECTION_ERRORS as err:
            logger.warning(
                "Skip one %s capability due to error (%s)",
                "coordinator developer report",
                type(err).__name__,
            )
    return reports


def build_developer_feedback_payload(
    *,
    reports: list[DeveloperReport],
    note: str,
    domain: str,
    service_name: str,
    requested_entry_id: str | None,
) -> dict[str, object]:
    """Build the canonical developer-feedback service payload."""
    return _support_build_developer_feedback_payload(
        reports=reports,
        note=note,
        domain=domain,
        service_name=service_name,
        requested_entry_id=requested_entry_id,
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: DeveloperReportCollector,
    get_optional_service_string,
    attr_entry_id: str,
) -> DeveloperReportResponse:
    """Handle the get_developer_report service."""
    requested_entry_id = get_optional_service_string(call, attr_entry_id)
    result: DeveloperReportResponse = {
        "entry_count": 0,
        "reports": [],
    }
    reports = collect_reports(hass, requested_entry_id=requested_entry_id)
    result["entry_count"] = len(reports)
    result["reports"] = reports
    if requested_entry_id is not None:
        result["requested_entry_id"] = requested_entry_id
    return result


async def async_handle_submit_developer_feedback(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: DeveloperReportCollector,
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    get_client_session: ClientSessionGetter,
    get_optional_service_string,
    get_optional_note,
    domain: str,
    service_submit_developer_feedback: str,
    attr_note: str,
    attr_entry_id: str,
    raise_service_error,
) -> DeveloperFeedbackResponse:
    """Handle the submit_developer_feedback service."""
    requested_entry_id = get_optional_service_string(call, attr_entry_id)
    reports = collect_reports(hass, requested_entry_id=requested_entry_id)
    if not reports:
        result: DeveloperFeedbackResponse = {
            "success": False,
            "message": "No active Lipro config entries",
            "submitted_entries": 0,
        }
        if requested_entry_id is not None:
            result["requested_entry_id"] = requested_entry_id
        return result

    feedback_payload = build_developer_feedback_payload(
        reports=reports,
        note=get_optional_note(call, attr_note),
        domain=domain,
        service_name=service_submit_developer_feedback,
        requested_entry_id=requested_entry_id,
    )

    share_manager = get_anonymous_share_manager(hass, entry_id=requested_entry_id)
    success = await share_manager.submit_developer_feedback(
        get_client_session(hass),
        feedback_payload,
    )
    if not success:
        raise_service_error("developer_feedback_submit_failed")

    success_result: DeveloperFeedbackResponse = {
        "success": True,
        "submitted_entries": len(reports),
    }
    if requested_entry_id is not None:
        success_result["requested_entry_id"] = requested_entry_id
    return success_result
