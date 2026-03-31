"""Focused developer-report and feedback handlers for diagnostics services."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, ServiceCall

from ..execution import ServiceErrorRaiser
from .helper_support import (
    build_developer_feedback_payload as _support_build_developer_feedback_payload,
)
from .types import (
    DeveloperFeedbackResponse,
    DeveloperReportCollector,
    DeveloperReportResponse,
)

if TYPE_CHECKING:
    from .types import (
        AnonymousShareManagerFactory,
        ClientSessionGetter,
        DeveloperReport,
    )

OptionalServiceStringGetter = Callable[[ServiceCall, str], str | None]
OptionalNoteGetter = Callable[[ServiceCall, str], str]


@dataclass(slots=True, frozen=True)
class _DeveloperFeedbackRequest:
    requested_entry_id: str | None
    note: str


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


def _build_feedback_request(
    call: ServiceCall,
    *,
    get_optional_service_string: OptionalServiceStringGetter,
    get_optional_note: OptionalNoteGetter,
    attr_entry_id: str,
    attr_note: str,
) -> _DeveloperFeedbackRequest:
    return _DeveloperFeedbackRequest(
        requested_entry_id=get_optional_service_string(call, attr_entry_id),
        note=get_optional_note(call, attr_note),
    )


def _build_feedback_result(
    *,
    success: bool,
    submitted_entries: int,
    requested_entry_id: str | None,
    message: str | None = None,
) -> DeveloperFeedbackResponse:
    result: DeveloperFeedbackResponse = {
        "success": success,
        "submitted_entries": submitted_entries,
    }
    if message is not None:
        result["message"] = message
    if requested_entry_id is not None:
        result["requested_entry_id"] = requested_entry_id
    return result


def _build_no_active_entries_feedback_result(
    requested_entry_id: str | None,
) -> DeveloperFeedbackResponse:
    """Build the canonical failure payload when no Lipro entries are active."""
    return _build_feedback_result(
        success=False,
        submitted_entries=0,
        requested_entry_id=requested_entry_id,
        message="No active Lipro config entries",
    )


def _build_feedback_submission_payload(
    *,
    reports: list[DeveloperReport],
    request: _DeveloperFeedbackRequest,
    domain: str,
    service_name: str,
) -> dict[str, object]:
    """Build the developer-feedback payload for one service request."""
    return build_developer_feedback_payload(
        reports=reports,
        note=request.note,
        domain=domain,
        service_name=service_name,
        requested_entry_id=request.requested_entry_id,
    )


async def _submit_feedback_payload(
    hass: HomeAssistant,
    *,
    request: _DeveloperFeedbackRequest,
    feedback_payload: dict[str, object],
    get_anonymous_share_manager: AnonymousShareManagerFactory,
    get_client_session: ClientSessionGetter,
) -> bool:
    """Submit one developer-feedback payload through the scoped share manager."""
    share_manager = get_anonymous_share_manager(
        hass,
        entry_id=request.requested_entry_id,
    )
    return await share_manager.submit_developer_feedback(
        get_client_session(hass),
        feedback_payload,
    )


async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: DeveloperReportCollector,
    get_optional_service_string: OptionalServiceStringGetter,
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
    get_optional_service_string: OptionalServiceStringGetter,
    get_optional_note: OptionalNoteGetter,
    domain: str,
    service_submit_developer_feedback: str,
    attr_note: str,
    attr_entry_id: str,
    raise_service_error: ServiceErrorRaiser,
) -> DeveloperFeedbackResponse:
    """Handle the submit_developer_feedback service."""
    request = _build_feedback_request(
        call,
        get_optional_service_string=get_optional_service_string,
        get_optional_note=get_optional_note,
        attr_entry_id=attr_entry_id,
        attr_note=attr_note,
    )
    reports = collect_reports(hass, requested_entry_id=request.requested_entry_id)
    if not reports:
        return _build_no_active_entries_feedback_result(request.requested_entry_id)

    feedback_payload = _build_feedback_submission_payload(
        reports=reports,
        request=request,
        domain=domain,
        service_name=service_submit_developer_feedback,
    )
    success = await _submit_feedback_payload(
        hass,
        request=request,
        feedback_payload=feedback_payload,
        get_anonymous_share_manager=get_anonymous_share_manager,
        get_client_session=get_client_session,
    )
    if not success:
        raise_service_error("developer_feedback_submit_failed")
    return _build_feedback_result(
        success=True,
        submitted_entries=len(reports),
        requested_entry_id=request.requested_entry_id,
    )
