"""Schedule service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import NoReturn, TypeVar

from homeassistant.core import HomeAssistant, ServiceCall

from ..core.api.errors import LiproApiError
from ..core.api.types import ScheduleTimingRow
from ..core.device import LiproDevice
from ..core.utils.log_safety import safe_error_placeholder as _safe_error_placeholder
from ..core.utils.redaction import redact_identifier as _redact_identifier
from ..runtime_types import LiproCoordinator
from .contracts import (
    AddScheduleResult,
    DeleteSchedulesResult,
    GetSchedulesResult,
    NormalizedScheduleRow,
    NormalizedScheduleRows,
    normalize_add_schedule_payload,
    normalize_delete_schedules_payload,
    normalize_get_schedules_payload,
)
from .execution import ServiceErrorRaiser, async_execute_coordinator_call
from .schedule_support import (
    AddScheduleRequest,
    DeleteSchedulesRequest,
    build_add_schedule_request,
    build_delete_schedules_request,
    normalize_schedule_row,
    validate_get_schedules_payload,
)

_ResultT = TypeVar("_ResultT")

type ScheduleRows = list[ScheduleTimingRow]
type ScheduleDevice = LiproDevice
type ScheduleCoordinator = LiproCoordinator
GetDeviceAndCoordinator = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[ScheduleDevice, ScheduleCoordinator]],
]


def _build_get_schedules_result(
    device: ScheduleDevice,
    schedules: NormalizedScheduleRows,
) -> GetSchedulesResult:
    """Build the typed get_schedules result payload."""
    return {
        "serial": device.serial,
        "schedules": schedules,
    }


def _build_add_schedule_result(
    device: ScheduleDevice,
    schedules: ScheduleRows,
) -> AddScheduleResult:
    """Build the typed add_schedule result payload."""
    return {
        "success": True,
        "serial": device.serial,
        "schedule_count": len(schedules),
    }


def _build_delete_schedules_result(
    device: ScheduleDevice,
    remaining: ScheduleRows,
) -> DeleteSchedulesResult:
    """Build the typed delete_schedules result payload."""
    return {
        "success": True,
        "serial": device.serial,
        "remaining_count": len(remaining),
    }


async def async_execute_schedule_operation(
    device: ScheduleDevice,
    protocol_call: Callable[..., Awaitable[_ResultT]],
    *args: object,
    coordinator: ScheduleCoordinator | None = None,
    error_log: str,
    error_translation_key: str,
    logger: logging.Logger,
    raise_service_error: ServiceErrorRaiser,
) -> _ResultT:
    """Call one schedule protocol operation with shared auth and error mapping."""

    async def _call_protocol_operation() -> _ResultT:
        return await protocol_call(device, *args)

    if coordinator is not None:

        def _handle_api_error(err: LiproApiError) -> NoReturn:
            logger.warning(error_log, _safe_error_placeholder(err))
            raise_service_error(error_translation_key, err=err)

        return await async_execute_coordinator_call(
            coordinator,
            call=_call_protocol_operation,
            raise_service_error=raise_service_error,
            handle_api_error=_handle_api_error,
        )

    try:
        return await _call_protocol_operation()
    except LiproApiError as err:
        logger.warning(error_log, _safe_error_placeholder(err))
        raise_service_error(error_translation_key, err=err)


async def async_call_schedule_service(
    coordinator: ScheduleCoordinator,
    device: ScheduleDevice,
    *,
    protocol_call: Callable[..., Awaitable[_ResultT]],
    call_args: tuple[object, ...] = (),
    service_log: str | None = None,
    service_log_args: tuple[object, ...] = (),
    error_log: str,
    error_translation_key: str,
    logger: logging.Logger,
    raise_service_error: ServiceErrorRaiser,
) -> _ResultT:
    """Invoke a schedule protocol operation with shared logging and error mapping."""
    if service_log is not None:
        logger.info(
            service_log,
            _redact_identifier(device.serial) or "***",
            *service_log_args,
        )

    return await async_execute_schedule_operation(
        device,
        protocol_call,
        *call_args,
        coordinator=coordinator,
        error_log=error_log,
        error_translation_key=error_translation_key,
        logger=logger,
        raise_service_error=raise_service_error,
    )


async def async_handle_get_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
) -> GetSchedulesResult:
    """Handle the get_schedules service call."""
    validate_get_schedules_payload(
        call,
        logger=logger,
        normalizer=normalize_get_schedules_payload,
        translation_key="invalid_schedule_request",
    )
    device, coordinator = await get_device_and_coordinator(hass, call)

    schedules: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        protocol_call=coordinator.schedule_service.async_get_schedules,
        service_log="Service call: get_schedules for %s",
        error_log="API error getting schedules: %s",
        error_translation_key="schedule_fetch_failed",
        logger=logger,
        raise_service_error=raise_service_error,
    )

    formatted: NormalizedScheduleRows = []
    for schedule in schedules:
        normalized: NormalizedScheduleRow | None = normalize_schedule_row(schedule)
        if normalized is not None:
            formatted.append(normalized)
    return _build_get_schedules_result(device, formatted)


async def async_handle_add_schedule(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
    domain: str,
    attr_days: str,
    attr_times: str,
    attr_events: str,
) -> AddScheduleResult:
    """Handle the add_schedule service call."""
    request: AddScheduleRequest = build_add_schedule_request(
        call,
        logger=logger,
        attr_days=attr_days,
        attr_times=attr_times,
        attr_events=attr_events,
        normalizer=normalize_add_schedule_payload,
        domain=domain,
        translation_key="invalid_schedule_request",
    )
    device, coordinator = await get_device_and_coordinator(hass, call)

    schedules: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        protocol_call=coordinator.schedule_service.async_add_schedule,
        call_args=(request.days, request.times, request.events),
        service_log="Service call: add_schedule for %s (days=%s, times=%s, events=%s)",
        service_log_args=(
            len(request.days),
            len(request.times),
            len(request.events),
        ),
        error_log="API error adding schedule: %s",
        error_translation_key="schedule_add_failed",
        logger=logger,
        raise_service_error=raise_service_error,
    )
    return _build_add_schedule_result(device, schedules)


async def async_handle_delete_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
    attr_schedule_ids: str,
) -> DeleteSchedulesResult:
    """Handle the delete_schedules service call."""
    request: DeleteSchedulesRequest = build_delete_schedules_request(
        call,
        logger=logger,
        attr_schedule_ids=attr_schedule_ids,
        normalizer=normalize_delete_schedules_payload,
        translation_key="invalid_schedule_request",
    )
    device, coordinator = await get_device_and_coordinator(hass, call)

    remaining: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        protocol_call=coordinator.schedule_service.async_delete_schedules,
        call_args=(request.schedule_ids,),
        service_log="Service call: delete_schedules for %s (ids=%s)",
        service_log_args=(len(request.schedule_ids),),
        error_log="API error deleting schedules: %s",
        error_translation_key="schedule_delete_failed",
        logger=logger,
        raise_service_error=raise_service_error,
    )
    return _build_delete_schedules_result(device, remaining)
