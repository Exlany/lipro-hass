"""Support helpers for schedule service payload validation and normalization."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import logging
from typing import TypeGuard, TypeVar, cast

import voluptuous as vol

from homeassistant.core import ServiceCall
from homeassistant.exceptions import ServiceValidationError

from ..const.base import DOMAIN
from ..core.api.types import SchedulePayload, ScheduleTimingRow
from .contracts import ATTR_DEVICE_ID, NormalizedScheduleRow

_SchedulePayloadT = TypeVar("_SchedulePayloadT", bound=Mapping[str, object])


@dataclass(slots=True, frozen=True)
class AddScheduleRequest:
    """Normalized add-schedule request payload."""

    days: list[int]
    times: list[int]
    events: list[int]


@dataclass(slots=True, frozen=True)
class DeleteSchedulesRequest:
    """Normalized delete-schedules request payload."""

    schedule_ids: list[int]


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


def _extract_schedule_payload(call: ServiceCall, *attr_names: str) -> dict[str, object]:
    """Copy only the declared service payload keys from one call."""
    return {
        attr_name: call.data[attr_name]
        for attr_name in attr_names
        if attr_name in call.data
    }


def normalize_schedule_service_payload(
    payload: Mapping[str, object],
    *,
    normalizer: Callable[[Mapping[str, object]], _SchedulePayloadT],
    logger: logging.Logger,
    service_name: str,
    translation_key: str = "invalid_schedule_request",
) -> _SchedulePayloadT:
    """Validate one schedule direct-call payload against the formal contract."""
    try:
        return normalizer(payload)
    except vol.Invalid as err:
        logger.warning(
            "Rejecting invalid %s service payload: %s",
            service_name,
            err,
        )
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key=translation_key,
        ) from err


def validate_get_schedules_payload(
    call: ServiceCall,
    *,
    logger: logging.Logger,
    normalizer: Callable[[Mapping[str, object]], _SchedulePayloadT],
    translation_key: str = "invalid_schedule_request",
) -> _SchedulePayloadT:
    """Validate the get-schedules direct-call payload."""
    return normalize_schedule_service_payload(
        _extract_schedule_payload(call, ATTR_DEVICE_ID),
        normalizer=normalizer,
        logger=logger,
        service_name="get_schedules",
        translation_key=translation_key,
    )


def build_add_schedule_request(
    call: ServiceCall,
    *,
    logger: logging.Logger,
    attr_days: str,
    attr_times: str,
    attr_events: str,
    normalizer: Callable[[Mapping[str, object]], _SchedulePayloadT],
    domain: str = DOMAIN,
    translation_key: str = "invalid_schedule_request",
) -> AddScheduleRequest:
    """Build one normalized add-schedule request from direct service data."""
    payload = normalize_schedule_service_payload(
        _extract_schedule_payload(call, ATTR_DEVICE_ID, attr_days, attr_times, attr_events),
        normalizer=normalizer,
        logger=logger,
        service_name="add_schedule",
        translation_key=translation_key,
    )
    days = list(cast(list[int], payload[attr_days]))
    times = list(cast(list[int], payload[attr_times]))
    events = list(cast(list[int], payload[attr_events]))
    if len(times) != len(events):
        raise ServiceValidationError(
            translation_domain=domain,
            translation_key="times_events_mismatch",
        )
    return AddScheduleRequest(days=days, times=times, events=events)


def build_delete_schedules_request(
    call: ServiceCall,
    *,
    logger: logging.Logger,
    attr_schedule_ids: str,
    normalizer: Callable[[Mapping[str, object]], _SchedulePayloadT],
    translation_key: str = "invalid_schedule_request",
) -> DeleteSchedulesRequest:
    """Build one normalized delete-schedules request from direct service data."""
    payload = normalize_schedule_service_payload(
        _extract_schedule_payload(call, ATTR_DEVICE_ID, attr_schedule_ids),
        normalizer=normalizer,
        logger=logger,
        service_name="delete_schedules",
        translation_key=translation_key,
    )
    return DeleteSchedulesRequest(
        schedule_ids=list(cast(list[int], payload[attr_schedule_ids]))
    )


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
