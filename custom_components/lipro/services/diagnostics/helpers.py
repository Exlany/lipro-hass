"""Helper utilities for diagnostics services.

This module contains utility functions for parameter extraction,
capability collection, error handling, and result building.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterator
import logging
from typing import NoReturn, TypeVar

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ...const.base import DOMAIN
from ...control import telemetry_surface as _telemetry_surface
from ...control.runtime_access import (
    find_runtime_entry_for_coordinator as _find_runtime_entry_for_coordinator,
)
from ...core import LiproApiError
from ...core.api.types import DiagnosticsApiResponse
from ...core.utils.log_safety import safe_error_placeholder
from ...runtime_types import LiproCoordinator
from ..execution import ServiceErrorRaiser, async_execute_coordinator_call
from .helper_support import (
    _async_get_first_authenticated_coordinator_capability_result as _support_async_get_first_authenticated_coordinator_capability_result,
    _async_get_first_coordinator_capability_result as _support_async_get_first_coordinator_capability_result,
    _build_feedback_envelope as _support_build_feedback_envelope,
    _coerce_service_float as _support_coerce_service_float,
    _coerce_service_int as _support_coerce_service_int,
    _get_optional_note as _support_get_optional_note,
    _get_optional_service_string as _support_get_optional_service_string,
    _get_required_service_string as _support_get_required_service_string,
    _project_feedback_reports as _support_project_feedback_reports,
    build_developer_feedback_payload as _support_build_developer_feedback_payload,
    build_sensor_history_result as _support_build_sensor_history_result,
)
from .types import (
    AnonymousShareManagerFactory,
    ClientSessionGetter,
    DeveloperFeedbackPayload,
    DeveloperFeedbackResponse,
    DeveloperReport,
    DeveloperReportCollector,
    DeveloperReportResponse,
    DiagnosticsCoordinator,
    RuntimeCoordinatorIterator,
    SensorHistoryResponse,
)

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")
_CoordinatorT = TypeVar("_CoordinatorT")
_CAPABILITY_PROJECTION_ERRORS = (RuntimeError, ValueError, TypeError, LookupError)


# Parameter extraction utilities


def _get_optional_service_string(call: ServiceCall, key: str) -> str | None:
    return _support_get_optional_service_string(call, key)


def _get_required_service_string(call: ServiceCall, key: str) -> str:
    return _support_get_required_service_string(call, key)


def _get_optional_note(call: ServiceCall, key: str) -> str:
    return _support_get_optional_note(call, key)


def _coerce_service_int(call: ServiceCall, key: str, default: int) -> int:
    return _support_coerce_service_int(call, key, default)


def _coerce_service_float(call: ServiceCall, key: str, default: float) -> float:
    return _support_coerce_service_float(call, key, default)


# Capability collection utilities


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


def _collect_coordinator_capability_results(
    coordinators: Iterator[_CoordinatorT],
    *,
    capability: str,
    collector: Callable[[_CoordinatorT], _ResultT],
) -> list[_ResultT]:
    """Collect capability results across coordinators with per-entry fault tolerance."""
    results: list[_ResultT] = []
    for coordinator in coordinators:
        try:
            results.append(collector(coordinator))
        except asyncio.CancelledError:
            raise
        except HomeAssistantError:
            raise
        except _CAPABILITY_PROJECTION_ERRORS as err:
            _LOGGER.warning(
                "Skip one %s capability due to error (%s)",
                capability,
                type(err).__name__,
            )
    return results


async def _async_get_first_coordinator_capability_result(
    coordinators: Iterator[DiagnosticsCoordinator],
    *,
    capability: str,
    collector: Callable[[DiagnosticsCoordinator], Awaitable[_ResultT]],
) -> tuple[bool, _ResultT | None, LiproApiError | None]:
    return await _support_async_get_first_coordinator_capability_result(
        coordinators,
        capability=capability,
        collector=collector,
        logger=_LOGGER,
    )


async def _async_get_first_authenticated_coordinator_capability_result(
    coordinators: Iterator[DiagnosticsCoordinator],
    *,
    capability: str,
    collector: Callable[[DiagnosticsCoordinator], Awaitable[_ResultT]],
) -> tuple[bool, _ResultT | None, LiproApiError | None]:
    return await _support_async_get_first_authenticated_coordinator_capability_result(
        coordinators,
        capability=capability,
        collector=collector,
        logger=_LOGGER,
    )


def collect_developer_reports(
    hass: HomeAssistant,
    *,
    iter_runtime_coordinators: RuntimeCoordinatorIterator,
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
            _LOGGER.warning(
                "Skip one %s capability due to error (%s)",
                "coordinator developer report",
                type(err).__name__,
            )
    return reports


def _project_feedback_reports(
    reports: list[DeveloperReport],
) -> list[DeveloperReport]:
    return _support_project_feedback_reports(reports)


def _build_feedback_envelope(
    *,
    entry_count: int,
    note: str,
    domain: str,
    service_name: str,
    requested_entry_id: str | None,
) -> DeveloperFeedbackPayload:
    return _support_build_feedback_envelope(
        entry_count=entry_count,
        note=note,
        domain=domain,
        service_name=service_name,
        requested_entry_id=requested_entry_id,
    )


def build_developer_feedback_payload(
    *,
    reports: list[DeveloperReport],
    note: str,
    domain: str,
    service_name: str,
    requested_entry_id: str | None,
) -> DeveloperFeedbackPayload:
    """Build the canonical developer-feedback service payload."""
    return _support_build_developer_feedback_payload(
        reports=reports,
        note=note,
        domain=domain,
        service_name=service_name,
        requested_entry_id=requested_entry_id,
    )


# Service handlers
async def async_handle_get_developer_report(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    collect_reports: DeveloperReportCollector,
    attr_entry_id: str,
) -> DeveloperReportResponse:
    """Handle the get_developer_report service."""
    requested_entry_id = _get_optional_service_string(call, attr_entry_id)
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
    domain: str,
    service_submit_developer_feedback: str,
    attr_note: str,
    attr_entry_id: str,
    raise_service_error: ServiceErrorRaiser,
) -> DeveloperFeedbackResponse:
    """Handle the submit_developer_feedback service."""
    requested_entry_id = _get_optional_service_string(call, attr_entry_id)
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
        note=_get_optional_note(call, attr_note),
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


# Error handling utilities
def raise_optional_capability_error(
    capability: str,
    err: LiproApiError,
    *,
    logger: logging.Logger,
) -> NoReturn:
    """Raise concise service-layer error for optional diagnostic capabilities."""
    safe_error = safe_error_placeholder(err)
    logger.warning("Optional capability %s failed (%s)", capability, safe_error)
    service_error = HomeAssistantError(
        f"{capability} failed ({safe_error})",
        translation_domain=DOMAIN,
        translation_key="optional_capability_failed",
        translation_placeholders={
            "capability": capability,
            "error": safe_error,
        },
    )
    raise service_error from err


async def async_call_optional_capability(
    capability: str,
    method: Callable[..., Awaitable[_ResultT]],
    *,
    coordinator: LiproCoordinator | None = None,
    raise_optional_error: Callable[[str, LiproApiError], NoReturn],
    raise_service_error: ServiceErrorRaiser | None = None,
    **kwargs: object,
) -> _ResultT:
    """Call one optional capability and optionally route through the auth facade."""

    def _handle_api_error(err: LiproApiError) -> NoReturn:
        raise_optional_error(capability, err)

    if coordinator is not None and raise_service_error is not None:
        return await async_execute_coordinator_call(
            coordinator,
            call=lambda: method(**kwargs),
            raise_service_error=raise_service_error,
            handle_api_error=_handle_api_error,
        )

    try:
        return await method(**kwargs)
    except LiproApiError as err:
        raise_optional_error(capability, err)


# Result building utilities
def build_sensor_history_result(
    serial: str,
    sensor_device_id: str,
    mesh_type: str,
    result: DiagnosticsApiResponse,
) -> SensorHistoryResponse:
    """Build the common response payload for sensor-history diagnostics."""
    return _support_build_sensor_history_result(
        serial=serial,
        sensor_device_id=sensor_device_id,
        mesh_type=mesh_type,
        result=result,
    )
