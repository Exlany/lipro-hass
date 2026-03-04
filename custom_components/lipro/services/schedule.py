"""Schedule service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..core import LiproApiError
from ..core.api.schedule_codec import coerce_int_list
from ..core.utils.redaction import redact_identifier as _redact_identifier


def format_schedule_time(seconds: int) -> str | None:
    """Convert seconds since midnight to HH:MM, ignoring invalid values."""
    if seconds < 0 or seconds >= 86400:
        return None

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def normalize_schedule_row(schedule: Any) -> dict[str, Any] | None:
    """Normalize a raw schedule row into service response format."""
    if not isinstance(schedule, dict):
        return None

    sched_info = schedule.get("schedule")
    if not isinstance(sched_info, dict):
        sched_info = {}

    times = coerce_int_list(sched_info.get("time"))
    events = coerce_int_list(sched_info.get("evt"))
    days = coerce_int_list(sched_info.get("days"))

    time_strs: list[str] = []
    for value in times:
        time_str = format_schedule_time(value)
        if time_str is not None:
            time_strs.append(time_str)

    return {
        "id": schedule.get("id"),
        "active": schedule.get("active", True),
        "days": days,
        "times": time_strs,
        "events": events,
    }


def get_mesh_context(device: Any) -> tuple[str, list[Any]]:
    """Extract mesh gateway and member IDs from device metadata."""
    mesh_gateway_id = device.extra_data.get("gateway_device_id", "")
    raw_mesh_member_ids = device.extra_data.get("group_member_ids", [])
    mesh_member_ids = (
        raw_mesh_member_ids if isinstance(raw_mesh_member_ids, list) else []
    )
    return mesh_gateway_id, mesh_member_ids


async def async_call_schedule_client(
    device: Any,
    client_call: Callable[..., Awaitable[Any]],
    *args: Any,
    error_log: str,
    error_translation_key: str,
    logger: Any,
    raise_service_error: Callable[..., Any],
) -> Any:
    """Call a schedule client API with mesh context and consistent error mapping."""
    mesh_gateway_id, mesh_member_ids = get_mesh_context(device)

    try:
        return await client_call(
            device.iot_device_id,
            device.device_type_hex,
            *args,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )
    except LiproApiError as err:
        logger.warning(error_log, err)
        raise_service_error(error_translation_key, err=err)


async def async_call_schedule_service(
    device: Any,
    *,
    client_call: Callable[..., Awaitable[Any]],
    call_args: tuple[Any, ...] = (),
    service_log: str | None = None,
    service_log_args: tuple[Any, ...] = (),
    error_log: str,
    error_translation_key: str,
    logger: Any,
    raise_service_error: Callable[..., Any],
) -> Any:
    """Invoke a schedule client method with consistent logging and error mapping."""
    if service_log is not None:
        logger.info(
            service_log,
            _redact_identifier(getattr(device, "serial", None)) or "***",
            *service_log_args,
        )

    return await async_call_schedule_client(
        device,
        client_call,
        *call_args,
        error_log=error_log,
        error_translation_key=error_translation_key,
        logger=logger,
        raise_service_error=raise_service_error,
    )


async def async_handle_get_schedules(
    hass: HomeAssistant,
    call: ServiceCall,
    *,
    get_device_and_coordinator: Any,
    raise_service_error: Callable[..., Any],
    logger: Any,
) -> dict[str, Any]:
    """Handle the get_schedules service call."""
    device, coordinator = await get_device_and_coordinator(hass, call)

    schedules = await async_call_schedule_service(
        device,
        client_call=coordinator.client.get_device_schedules,
        service_log="Service call: get_schedules for %s",
        error_log="API error getting schedules: %s",
        error_translation_key="schedule_fetch_failed",
        logger=logger,
        raise_service_error=raise_service_error,
    )

    formatted = [
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
    get_device_and_coordinator: Any,
    raise_service_error: Callable[..., Any],
    logger: Any,
    domain: str,
    attr_days: str,
    attr_times: str,
    attr_events: str,
) -> dict[str, Any]:
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

    schedules = await async_call_schedule_service(
        device,
        client_call=coordinator.client.add_device_schedule,
        call_args=(days, times, events),
        service_log="Service call: add_schedule for %s, days=%s, times=%s, events=%s",
        service_log_args=(days, times, events),
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
    get_device_and_coordinator: Any,
    raise_service_error: Callable[..., Any],
    logger: Any,
    attr_schedule_ids: str,
) -> dict[str, Any]:
    """Handle the delete_schedules service call."""
    device, coordinator = await get_device_and_coordinator(hass, call)
    schedule_ids = call.data[attr_schedule_ids]

    remaining = await async_call_schedule_service(
        device,
        client_call=coordinator.client.delete_device_schedules,
        call_args=(schedule_ids,),
        service_log="Service call: delete_schedules for %s, ids=%s",
        service_log_args=(schedule_ids,),
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
