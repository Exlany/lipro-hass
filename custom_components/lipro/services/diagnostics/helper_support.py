"""Support-only helpers for diagnostics service mechanics."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterator
from datetime import UTC, datetime
import logging
from typing import TypeVar

from homeassistant.core import ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ...core import LiproApiError
from ...core.anonymous_share.report_builder import project_developer_feedback_upload
from ...core.api.types import DiagnosticsApiResponse
from ..execution import async_capture_coordinator_call
from .types import (
    DeveloperFeedbackPayload,
    DeveloperReport,
    DiagnosticsCoordinator,
    SensorHistoryResponse,
)

_ResultT = TypeVar("_ResultT")
_CoordinatorT = TypeVar("_CoordinatorT")
_CAPABILITY_PROJECTION_ERRORS = (RuntimeError, ValueError, TypeError, LookupError)


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


def _collect_coordinator_capability_results(
    coordinators: Iterator[_CoordinatorT],
    *,
    capability: str,
    collector: Callable[[_CoordinatorT], _ResultT],
    logger: logging.Logger,
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
            logger.warning(
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
    logger: logging.Logger,
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
        except _CAPABILITY_PROJECTION_ERRORS as err:
            logger.warning(
                "Skip one %s capability due to unexpected error (%s)",
                capability,
                type(err).__name__,
            )
    return False, None, last_api_error


async def _async_get_first_authenticated_coordinator_capability_result(
    coordinators: Iterator[DiagnosticsCoordinator],
    *,
    capability: str,
    collector: Callable[[DiagnosticsCoordinator], Awaitable[_ResultT]],
    logger: logging.Logger,
) -> tuple[bool, _ResultT | None, LiproApiError | None]:
    """Return the first successful auth-aware capability result across coordinators."""
    last_api_error: LiproApiError | None = None
    for coordinator in coordinators:
        try:
            def _collector_call(
                coordinator_ref: DiagnosticsCoordinator = coordinator,
            ) -> Awaitable[_ResultT]:
                return collector(coordinator_ref)

            has_result, result, captured_error = await async_capture_coordinator_call(
                coordinator,
                call=_collector_call,
            )
            if has_result:
                return True, result, None
            if captured_error is not None:
                last_api_error = captured_error
        except asyncio.CancelledError:
            raise
        except HomeAssistantError:
            raise
        except _CAPABILITY_PROJECTION_ERRORS as err:
            logger.warning(
                "Skip one %s capability due to unexpected error (%s)",
                capability,
                type(err).__name__,
            )
    return False, None, last_api_error


def _project_feedback_reports(
    reports: list[DeveloperReport],
) -> list[DeveloperReport]:
    """Project local developer reports into the upload-safe boundary shape."""
    projected_reports = project_developer_feedback_upload(reports)
    if not isinstance(projected_reports, list):
        return reports
    return [report for report in projected_reports if isinstance(report, dict)]


def _build_feedback_envelope(
    *,
    entry_count: int,
    note: str,
    domain: str,
    service_name: str,
    requested_entry_id: str | None,
) -> DeveloperFeedbackPayload:
    """Build the outer developer-feedback envelope without upload projection."""
    payload: DeveloperFeedbackPayload = {
        "source": "home_assistant_service",
        "service": f"{domain}.{service_name}",
        "generated_at": datetime.now(UTC).isoformat(),
        "entry_count": entry_count,
        "note": note,
        "reports": [],
    }
    if requested_entry_id is not None:
        payload["requested_entry_id"] = requested_entry_id
    return payload


def build_developer_feedback_payload(
    *,
    reports: list[DeveloperReport],
    note: str,
    domain: str,
    service_name: str,
    requested_entry_id: str | None,
) -> DeveloperFeedbackPayload:
    """Build the canonical developer-feedback service payload."""
    payload = _build_feedback_envelope(
        entry_count=len(reports),
        note=note,
        domain=domain,
        service_name=service_name,
        requested_entry_id=requested_entry_id,
    )
    payload["reports"] = _project_feedback_reports(reports)
    return payload


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
