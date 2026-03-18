"""Schedule service handlers for Lipro integration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
import logging
from typing import Any, NoReturn, Protocol, TypeVar, cast

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..core.api.errors import (
    LiproApiError,
    LiproAuthError,
    LiproRefreshTokenExpiredError,
)
from ..core.api.schedule_codec import coerce_int_list
from ..core.api.types import ScheduleTimingRow
from ..core.utils.identifiers import normalize_iot_device_id
from ..core.utils.log_safety import safe_error_placeholder
from ..core.utils.redaction import redact_identifier as _redact_identifier
from ..runtime_types import ProtocolServiceLike

_ResultT = TypeVar("_ResultT")
_NormalizedSchedule = dict[str, object]
ScheduleRows = list[ScheduleTimingRow]
GetDeviceAndCoordinator = Callable[
    [HomeAssistant, ServiceCall],
    Awaitable[tuple[Any, Any]],
]


class CoordinatorAuthSurface(Protocol):
    """Formal runtime-auth surface used by schedule services."""

    async def async_ensure_authenticated(self) -> None:
        """Validate runtime auth state before a schedule service call."""

    async def async_trigger_reauth(self, reason: str) -> None:
        """Start the Home Assistant reauth flow for one failure reason."""


class ServiceErrorRaiser(Protocol):
    """Callable that raises translated Home Assistant schedule service errors."""

    def __call__(
        self,
        translation_key: str,
        *,
        err: Exception | None = None,
        translation_placeholders: Mapping[str, str] | None = None,
    ) -> NoReturn:
        """Raise a translated Home Assistant service error."""


class ScheduleDevice(Protocol):
    """Service-layer schedule device contract."""

    iot_device_id: str
    device_type_hex: str
    serial: str
    extra_data: object
    ir_remote_gateway_device_id: str | None


class ScheduleCoordinator(Protocol):
    """Coordinator contract used by schedule services."""

    @property
    def auth_service(self) -> CoordinatorAuthSurface:
        """Return the formal coordinator auth surface."""

    @property
    def protocol_service(self) -> ProtocolServiceLike:
        """Return the formal runtime-owned protocol capability service."""


async def _async_execute_schedule_coordinator_call(
    coordinator: ScheduleCoordinator,
    *,
    call: Callable[[], Awaitable[_ResultT]],
    raise_service_error: ServiceErrorRaiser,
    handle_api_error: Callable[[LiproApiError], NoReturn] | None = None,
) -> _ResultT:
    """Execute one schedule call through shared auth and error handling."""
    try:
        await coordinator.auth_service.async_ensure_authenticated()
        return await call()
    except LiproRefreshTokenExpiredError as err:
        await coordinator.auth_service.async_trigger_reauth("auth_expired")
        raise_service_error("auth_expired", err=err)
    except LiproAuthError as err:
        await coordinator.auth_service.async_trigger_reauth("auth_error")
        raise_service_error(
            "auth_error",
            err=err,
            translation_placeholders={"error": safe_error_placeholder(err)},
        )
    except LiproApiError as err:
        if handle_api_error is not None:
            handle_api_error(err)
        raise


def format_schedule_time(seconds: int) -> str | None:
    """Convert seconds since midnight to HH:MM, ignoring invalid values."""
    if seconds < 0 or seconds >= 86400:
        return None

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def _normalize_schedule_time_events(sched_info: Mapping[str, Any]) -> tuple[list[str], list[int]]:
    """Normalize schedule time/event pairs while preserving pair alignment."""
    times = coerce_int_list(sched_info.get("time"))
    events = coerce_int_list(sched_info.get("evt"))

    normalized_times: list[str] = []
    normalized_events: list[int] = []
    for seconds, event in zip(times, events, strict=False):
        if (time_str := format_schedule_time(seconds)) is None:
            continue
        normalized_times.append(time_str)
        normalized_events.append(event)

    return normalized_times, normalized_events


def normalize_schedule_row(schedule: object) -> _NormalizedSchedule | None:
    """Normalize a raw schedule row into service response format."""
    if not isinstance(schedule, dict):
        return None

    sched_info = schedule.get("schedule")
    if not isinstance(sched_info, dict):
        sched_info = {}

    time_strs, events = _normalize_schedule_time_events(sched_info)
    days = coerce_int_list(sched_info.get("days"))

    return {
        "id": schedule.get("id"),
        "active": schedule.get("active", True),
        "days": days,
        "times": time_strs,
        "events": events,
    }


def get_mesh_context(device: ScheduleDevice) -> tuple[str, list[str]]:
    """Extract mesh gateway and member IDs from device metadata."""
    extra_data = getattr(device, "extra_data", None)
    if not isinstance(extra_data, Mapping):
        extra_data = {}

    gateway_candidate = extra_data.get("gateway_device_id")
    if gateway_candidate is None:
        gateway_candidate = getattr(device, "ir_remote_gateway_device_id", None)
    mesh_gateway_id = normalize_iot_device_id(gateway_candidate) or ""

    mesh_member_ids: list[str] = []
    seen_member_ids: set[str] = set()
    raw_mesh_member_ids = extra_data.get("group_member_ids")
    if isinstance(raw_mesh_member_ids, list):
        for member_id in raw_mesh_member_ids:
            normalized = normalize_iot_device_id(member_id)
            if normalized is None or normalized in seen_member_ids:
                continue
            seen_member_ids.add(normalized)
            mesh_member_ids.append(normalized)

    return mesh_gateway_id, mesh_member_ids


async def async_call_schedule_client(
    device: ScheduleDevice,
    client_call: Callable[..., Awaitable[_ResultT]],
    *args: object,
    coordinator: ScheduleCoordinator | None = None,
    error_log: str,
    error_translation_key: str,
    logger: logging.Logger,
    raise_service_error: ServiceErrorRaiser,
) -> _ResultT:
    """Call a schedule API with optional coordinator-authenticated execution."""
    mesh_gateway_id, mesh_member_ids = get_mesh_context(device)

    async def _call_client() -> _ResultT:
        return await client_call(
            device.iot_device_id,
            device.device_type_hex,
            *args,
            mesh_gateway_id=mesh_gateway_id,
            mesh_member_ids=mesh_member_ids,
        )

    if coordinator is not None:

        def _handle_api_error(err: LiproApiError) -> NoReturn:
            logger.warning(error_log, err)
            raise_service_error(error_translation_key, err=err)

        return await _async_execute_schedule_coordinator_call(
            coordinator,
            call=_call_client,
            raise_service_error=raise_service_error,
            handle_api_error=_handle_api_error,
        )

    try:
        return await _call_client()
    except LiproApiError as err:
        logger.warning(error_log, err)
        raise_service_error(error_translation_key, err=err)


async def async_call_schedule_service(
    coordinator: ScheduleCoordinator,
    device: ScheduleDevice,
    *,
    client_call: Callable[..., Awaitable[_ResultT]],
    call_args: tuple[object, ...] = (),
    service_log: str | None = None,
    service_log_args: tuple[object, ...] = (),
    error_log: str,
    error_translation_key: str,
    logger: logging.Logger,
    raise_service_error: ServiceErrorRaiser,
) -> _ResultT:
    """Invoke a schedule client method with shared logging and error mapping."""
    if service_log is not None:
        logger.info(
            service_log,
            _redact_identifier(device.serial) or "***",
            *service_log_args,
        )

    return await async_call_schedule_client(
        device,
        client_call,
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
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(ScheduleDevice, raw_device)
    coordinator = cast(ScheduleCoordinator, raw_coordinator)

    schedules: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        client_call=coordinator.protocol_service.async_get_device_schedules,
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
    get_device_and_coordinator: GetDeviceAndCoordinator,
    raise_service_error: ServiceErrorRaiser,
    logger: logging.Logger,
    domain: str,
    attr_days: str,
    attr_times: str,
    attr_events: str,
) -> dict[str, object]:
    """Handle the add_schedule service call."""
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(ScheduleDevice, raw_device)
    coordinator = cast(ScheduleCoordinator, raw_coordinator)

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
        client_call=coordinator.protocol_service.async_add_device_schedule,
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
    raw_device, raw_coordinator = await get_device_and_coordinator(hass, call)
    device = cast(ScheduleDevice, raw_device)
    coordinator = cast(ScheduleCoordinator, raw_coordinator)
    schedule_ids = call.data[attr_schedule_ids]

    remaining: ScheduleRows = await async_call_schedule_service(
        coordinator,
        device,
        client_call=coordinator.protocol_service.async_delete_device_schedules,
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
