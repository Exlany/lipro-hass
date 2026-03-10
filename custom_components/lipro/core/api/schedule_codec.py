"""Schedule payload codec helpers for Lipro APIs."""

from __future__ import annotations

from collections.abc import Callable, Sequence
import json
import logging
from typing import TypeGuard, cast

from .types import ScheduleTimingRow

_LOGGER = logging.getLogger(__name__)
_INVALID_JSON_PREVIEW_MAX_CHARS = 200

type ScheduleJsonPayload = dict[str, list[int]]


def _is_mapping(value: object) -> TypeGuard[dict[str, object]]:
    """Return whether one raw payload value is a mapping."""
    return isinstance(value, dict)


def _align_time_event_pairs(
    times: list[int],
    events: list[int],
) -> tuple[list[int], list[int]]:
    """Align ``time`` and ``evt`` arrays by truncating unmatched values."""
    if len(times) == len(events):
        return times, events
    pair_count = min(len(times), len(events))
    if pair_count <= 0:
        return [], []
    return times[:pair_count], events[:pair_count]


def coerce_int_list(value: object) -> list[int]:
    """Convert mixed list payloads into a clean integer list."""
    if not isinstance(value, list):
        return []

    result: list[int] = []
    for item in value:
        if (coerced := _coerce_int_item(item)) is not None:
            result.append(coerced)
    return result


def _coerce_int_item(item: object) -> int | None:
    """Coerce one mixed payload item into an integer when safe."""
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


def parse_mesh_schedule_json(
    schedule_json: object,
    *,
    mask_sensitive_data: Callable[[str], str],
) -> ScheduleJsonPayload:
    """Parse mesh ``scheduleJson`` into normalized ``days/time/evt`` arrays."""
    empty: ScheduleJsonPayload = {"days": [], "time": [], "evt": []}
    payload = schedule_json

    if isinstance(payload, str):
        raw = payload.strip()
        if not raw:
            return empty
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            _LOGGER.debug(
                "Invalid mesh scheduleJson payload (type=%s): %s",
                type(payload).__name__,
                mask_sensitive_data(str(payload)[:_INVALID_JSON_PREVIEW_MAX_CHARS]),
            )
            return empty

    if not _is_mapping(payload):
        return empty

    days = coerce_int_list(payload.get("days"))
    times = coerce_int_list(payload.get("time"))
    events = coerce_int_list(payload.get("evt"))
    times, events = _align_time_event_pairs(times, events)
    return {"days": days, "time": times, "evt": events}


def normalize_mesh_timing_rows(
    rows: Sequence[object],
    *,
    fallback_device_id: str = "",
    parse_schedule_json: Callable[[object], ScheduleJsonPayload],
    coerce_connect_status: Callable[[object], bool],
) -> list[ScheduleTimingRow]:
    """Normalize mesh timing rows to include ``schedule`` dict payload."""
    normalized_rows: list[ScheduleTimingRow] = []
    for row in rows:
        if not _is_mapping(row):
            continue
        normalized_row = dict(row)
        normalized_row["schedule"] = parse_schedule_json(row.get("scheduleJson"))
        normalized_row["active"] = coerce_connect_status(row.get("active", True))
        if not isinstance(normalized_row.get("deviceId"), str) and fallback_device_id:
            normalized_row["deviceId"] = fallback_device_id
        normalized_rows.append(cast(ScheduleTimingRow, normalized_row))

    return normalized_rows
