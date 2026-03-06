"""Tests for schedule codec helpers."""

from __future__ import annotations

from custom_components.lipro.core.api.schedule_codec import (
    normalize_mesh_timing_rows,
    parse_mesh_schedule_json,
)


def _coerce_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "on", "yes"}


def _mask(value: str) -> str:
    return value


def test_parse_mesh_schedule_json_invalid_payload_returns_empty() -> None:
    parsed = parse_mesh_schedule_json(
        "{invalid",
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [], "time": [], "evt": []}


def test_parse_mesh_schedule_json_supports_hhmm_and_action_fallbacks() -> None:
    parsed = parse_mesh_schedule_json(
        {
            "weekDays": [1, 3, 5],
            "time": "08:30",
            "action": {
                "command": "power",
                "properties": [{"key": "power", "value": "1"}],
            },
        },
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [1, 3, 5], "time": [30600], "evt": [0]}


def test_parse_mesh_schedule_json_truncates_mismatched_time_event_pairs() -> None:
    parsed = parse_mesh_schedule_json(
        {"days": [1], "time": [100, 200], "evt": [1]},
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [1], "time": [100], "evt": [1]}


def test_normalize_mesh_timing_rows_sets_schedule_and_fallback_device_id() -> None:
    rows = normalize_mesh_timing_rows(
        [
            {"id": 1, "scheduleJson": {"days": [1], "time": [60], "evt": [0]}},
            {
                "id": 2,
                "active": "false",
                "schedule": {"days": [2], "time": [120], "evt": [1]},
            },
        ],
        fallback_device_id="03ab0000000000aa",
        parse_schedule_json=lambda payload: parse_mesh_schedule_json(
            payload,
            coerce_connect_status=_coerce_bool,
            mask_sensitive_data=_mask,
        ),
        coerce_connect_status=_coerce_bool,
    )

    assert rows[0]["deviceId"] == "03ab0000000000aa"
    assert rows[0]["schedule"] == {"days": [1], "time": [60], "evt": [0]}
    assert rows[0]["active"] is True
    assert rows[1]["active"] is False


def test_parse_hhmm_non_string_time_returns_empty() -> None:
    parsed = parse_mesh_schedule_json(
        {"days": [1], "time": 3600},
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed["time"] == []


def test_parse_hhmm_invalid_format_returns_empty() -> None:
    parsed = parse_mesh_schedule_json(
        {"days": [1], "time": "not-a-time"},
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed["time"] == []


def test_parse_hhmm_out_of_range_hours() -> None:
    parsed = parse_mesh_schedule_json(
        {"days": [1], "time": "25:00"},
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed["time"] == []


def test_extract_power_action_non_power_command() -> None:
    parsed = parse_mesh_schedule_json(
        {"days": [1], "time": [60], "action": {"command": "scene"}},
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed["evt"] == []


def test_extract_power_action_props_not_list() -> None:
    parsed = parse_mesh_schedule_json(
        {
            "days": [1],
            "time": [60],
            "action": {"command": "power", "properties": {"key": "power"}},
        },
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed["evt"] == []


def test_extract_power_action_no_power_key_in_props() -> None:
    parsed = parse_mesh_schedule_json(
        {
            "days": [1],
            "time": [60],
            "action": {
                "command": "power",
                "properties": [{"key": "brightness", "value": "50"}],
            },
        },
        coerce_connect_status=_coerce_bool,
        mask_sensitive_data=_mask,
    )
    assert parsed["evt"] == []
