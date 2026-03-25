"""Schedule service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import NoReturn, TypedDict, TypeGuard, TypeVar

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..core.api.errors import LiproApiError
from ..core.api.types import SchedulePayload, ScheduleTimingRow
from ..core.device import LiproDevice
from ..core.utils.redaction import redact_identifier as _redact_identifier
from ..runtime_types import LiproCoordinator
from .execution import ServiceErrorRaiser, async_execute_coordinator_call

_ResultT = TypeVar("_ResultT")


class NormalizedScheduleRow(TypedDict):
    """Schedule row shape returned by the schedule service."""

    id: object
    active: object
    days: list[int]
    times: list[str]
    events: list[int]


type ScheduleRows = list[ScheduleTimingRow]
type NormalizedScheduleRows = list[NormalizedScheduleRow]
type ScheduleDevice = LiproDevice
type ScheduleCoordinator = LiproCoordinator
GetDeviceAndCoordinator = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[ScheduleDevice, ScheduleCoordinator]],
]


def _is_schedule_payload(value: object) -> TypeGuard[SchedulePayload]:
    """Return whether one raw value can be treated as a schedule payload."""
    return isinstance(value, dict)


def _is_schedule_timing_row(value: object) -> TypeGuard[ScheduleTimingRow]:
    """Return whether one raw value can be treated as a schedule row."""
    return isinstance(value, dict)


def _coerce_schedule_int_item(item: object) -> int | None:
    """Coerce one schedule payload item into an integer when safe."""
    if isinstance(item, bool):
        return None
    if isinstance(item, int):
        return item
    if isinstance(item, float):
        return int(item) if item.is_integer() else None
    if isinstance(item, str):
        normalized = item.strip()
        if normalized.lstrip("+-").isdigit():
            try:
                return int(normalized)
            except ValueError:
                return None
    return None


def _coerce_schedule_int_list(value: object) -> list[int]:
    """Convert mixed schedule payload lists into a clean integer list."""
    if not isinstance(value, list):
        return []

    result: list[int] = []
    for item in value:
        if (coerced := _coerce_schedule_int_item(item)) is not None:
            result.append(coerced)
    return result


def format_schedule_time(seconds: int) -> str | None:
    """Convert seconds since midnight to HH:MM, ignoring invalid values."""
    if seconds < 0 or seconds >= 86400:
        return None

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def _normalize_schedule_time_events(
    sched_info: SchedulePayload,
) -> tuple[list[str], list[int]]:
    """Normalize schedule time/event pairs while preserving pair alignment."""
    times = _coerce_schedule_int_list(sched_info.get("time"))
    events = _coerce_schedule_int_list(sched_info.get("evt"))

    normalized_times: list[str] = []
    normalized_events: list[int] = []
    for seconds, event in zip(times, events, strict=False):
        if (time_str := format_schedule_time(seconds)) is None:
            continue
        normalized_times.append(time_str)
        normalized_events.append(event)

    return normalized_times, normalized_events


def normalize_schedule_row(schedule: object) -> NormalizedScheduleRow | None:
    """Normalize a raw schedule row into service response format."""
    if not _is_schedule_timing_row(schedule):
        return None

    sched_info = schedule.get("schedule")
    if not _is_schedule_payload(sched_info):
        sched_info = {}

    time_strs, events = _normalize_schedule_time_events(sched_info)
    days = _coerce_schedule_int_list(sched_info.get("days"))

    return {
        "id": schedule.get("id"),
        "active": schedule.get("active", True),
        "days": days,
        "times": time_strs,
        "events": events,
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
            logger.warning(error_log, err)
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
        logger.warning(error_log, err)
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
) -> dict[str, object]:
    """Handle the get_schedules service call."""
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

    formatted: NormalizedScheduleRows = [
        normalized
        for schedule in schedules
        if (normalized := normalize_schedule_row(schedule)) is not None
    ]

    return {
        "serial": device.serial,
        "schedules": formatted,
    }


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
) -> dict[str, object]:
    """Handle the add_schedule service call."""
    device, coordinator = await get_device_and_coordinator(hass, call)

    days = call.data[attr_days]
    times = call.data[attr_times]
    events = call.data[attr_events]

    if len(times) != len(events):
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="times_events_mismatch",
        )

    schedules: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        protocol_call=coordinator.schedule_service.async_add_schedule,
        call_args=(days, times, events),
        service_log=(
            "Service call: add_schedule for %s (days=%s, times=%s, events=%s)"
        ),
        service_log_args=(
            len(days) if hasattr(days, "__len__") else 0,
            len(times) if hasattr(times, "__len__") else 0,
            len(events) if hasattr(events, "__len__") else 0,
        ),
        error_log="API error adding schedule: %s",
        error_translation_key="schedule_add_failed",
        logger=logger,
        raise_service_error=raise_service_error,
    )

    return {
        "success": True,
        "serial": device.serial,
        "schedule_count": len(schedules),
    }


async def async_handle_delete_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: GetDeviceAndCoordinator,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
    attr_schedule_ids: str,
) -> dict[str, object]:
    """Handle the delete_schedules service call."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    schedule_ids = call.data[attr_schedule_ids]

    remaining: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        protocol_call=coordinator.schedule_service.async_delete_schedules,
        call_args=(schedule_ids,),
        service_log="Service call: delete_schedules for %s (ids=%s)",
        service_log_args=(
            len(schedule_ids) if hasattr(schedule_ids, "__len__") else 0,
        ),
        error_log="API error deleting schedules: %s",
        error_translation_key="schedule_delete_failed",
        logger=logger,
        raise_service_error=raise_service_error,
    )

    return {
        "success": True,
        "serial": device.serial,
        "remaining_count": len(remaining),
    }
