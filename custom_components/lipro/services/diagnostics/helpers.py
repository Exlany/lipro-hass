"""Helper utilities for diagnostics services.

This module contains utility functions for parameter extraction,
capability collection, error handling, and result building.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterator, Mapping
from datetime import UTC, datetime
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
from ...core.anonymous_share.report_builder import project_developer_feedback_upload
from ...core.api.types import DiagnosticsApiResponse
from ...core.utils.log_safety import safe_error_placeholder
from ...runtime_types import LiproCoordinator
from ..execution import (
    AuthenticatedCoordinator,
    ServiceErrorRaiser,
    async_execute_coordinator_call,
)
from .types import (
    AnonymousShareManagerFactory,
    ClientSessionGetter,
    DeveloperFeedbackPayload,
    DeveloperFeedbackResponse,
    DeveloperReport,
    DeveloperReportCollector,
    DeveloperReportCoordinatorIterator,
    DeveloperReportResponse,
    DiagnosticsCoordinator,
    FailureSummaryPayload,
    SensorHistoryResponse,
)

_LOGGER = logging.getLogger(__name__)
_ResultT = TypeVar("_ResultT")
_CoordinatorT = TypeVar("_CoordinatorT")


# Parameter extraction utilities
def _get_optional_service_string(call: ServiceCall, key: str) -> str | None:
    """Return one optional string service field after light normalization."""
    value = call.data.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _get_required_service_string(call: ServiceCall, key: str) -> str:
    """Return one required string service field validated by the schema layer."""
    value = call.data[key]
    if not isinstance(value, str):
        msg = f"Service field {key} must be text"
        raise TypeError(msg)
    return value


def _get_optional_note(call: ServiceCall, key: str) -> str:
    """Return one optional note field while preserving caller formatting."""
    value = call.data.get(key, "")
    return value if isinstance(value, str) else ""


def _coerce_service_int(call: ServiceCall, key: str, default: int) -> int:
    """Coerce one optional numeric service field to int."""
    value = call.data.get(key, default)
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float, str)):
        return int(value)
    return default


def _coerce_service_float(call: ServiceCall, key: str, default: float) -> float:
    """Coerce one optional numeric service field to float."""
    value = call.data.get(key, default)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float, str)):
        return float(value)
    return default


# Capability collection utilities


def _collect_exporter_developer_report(
    hass: HomeAssistant,
    coordinator: LiproCoordinator,
) -> DeveloperReport | None:
    """Return exporter-backed developer view when coordinator lacks a legacy builder."""
    entry = _find_runtime_entry_for_coordinator(hass, coordinator)
    if entry is None:
        return None
    view = _telemetry_surface.get_entry_telemetry_view(entry, "developer")
    if isinstance(view, dict):
        return view
    return None


def _normalize_failure_summary(value: object) -> FailureSummaryPayload | None:
    """Return the shared failure-summary shape when present."""
    if not isinstance(value, Mapping):
        return None

    failure_category = value.get("failure_category")
    failure_origin = value.get("failure_origin")
    handling_policy = value.get("handling_policy")
    error_type = value.get("error_type")
    has_signal = any(
        isinstance(item, str)
        for item in (failure_category, failure_origin, handling_policy, error_type)
    )
    if not has_signal:
        return None

    normalized: FailureSummaryPayload = {
        "failure_category": (
            failure_category if isinstance(failure_category, str) else None
        ),
        "failure_origin": failure_origin if isinstance(failure_origin, str) else None,
        "handling_policy": (
            handling_policy if isinstance(handling_policy, str) else None
        ),
        "error_type": error_type if isinstance(error_type, str) else None,
    }
    return normalized


def _merge_exporter_failure_signals(
    report: DeveloperReport,
    exporter_report: DeveloperReport | None,
) -> DeveloperReport:
    """Attach shared failure signals to one developer report when available."""
    merged = dict(report)
    if not isinstance(exporter_report, Mapping):
        return merged

    entry_ref = exporter_report.get("entry_ref")
    if isinstance(entry_ref, str):
        merged["entry_ref"] = entry_ref

    failure_summary = _normalize_failure_summary(exporter_report.get("failure_summary"))
    if failure_summary is not None:
        merged["failure_summary"] = failure_summary
    return merged


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
        except Exception as err:  # noqa: BLE001
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
    """Return the first successful capability result and retain the last API error."""
    last_api_error: LiproApiError | None = None
    for coordinator in coordinators:
        try:
            return True, await collector(coordinator), None
        except asyncio.CancelledError:
            raise
        except HomeAssistantError:
            raise
        except LiproApiError as err:
            last_api_error = err
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
                "Skip one %s capability due to unexpected error (%s)",
                capability,
                type(err).__name__,
            )
    return False, None, last_api_error


def collect_developer_reports(
    hass: HomeAssistant,
    *,
    iter_runtime_coordinators: DeveloperReportCoordinatorIterator,
) -> list[DeveloperReport]:
    """Collect developer reports from active config entries."""
    reports: list[DeveloperReport] = []
    for coordinator in iter_runtime_coordinators(hass):
        try:
            exporter_report = _collect_exporter_developer_report(hass, coordinator)
            builder = getattr(coordinator, "build_developer_report", None)
            if callable(builder):
                report = builder()
                if isinstance(report, dict):
                    reports.append(
                        _merge_exporter_failure_signals(report, exporter_report)
                    )
                continue
            if exporter_report is not None:
                reports.append(
                    _merge_exporter_failure_signals(exporter_report, exporter_report)
                )
        except asyncio.CancelledError:
            raise
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning(
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
) -> DeveloperFeedbackPayload:
    """Build the canonical developer-feedback service payload."""
    payload: DeveloperFeedbackPayload = {
        "source": "home_assistant_service",
        "service": f"{domain}.{service_name}",
        "generated_at": datetime.now(UTC).isoformat(),
        "entry_count": len(reports),
        "note": note,
        "reports": reports,
    }
    projected_reports = project_developer_feedback_upload(reports)
    if isinstance(projected_reports, list):
        payload["reports"] = [
            report for report in projected_reports if isinstance(report, dict)
        ]
    if requested_entry_id is not None:
        payload["requested_entry_id"] = requested_entry_id
    return payload


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
    coordinator: AuthenticatedCoordinator | None = None,
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
    payload: SensorHistoryResponse = {
        "serial": serial,
        "sensor_device_id": sensor_device_id,
        "mesh_type": mesh_type,
        "result": result,
    }
    return payload
