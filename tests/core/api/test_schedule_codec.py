"""Tests for schedule codec helpers."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.api.schedule_codec import (
    coerce_int_list,
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
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [], "time": [], "evt": []}


def test_parse_mesh_schedule_json_accepts_verified_canonical_payload() -> None:
    parsed = parse_mesh_schedule_json(
        '{"days":[2],"time":[86340],"evt":[1]}',
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [2], "time": [86340], "evt": [1]}


def test_parse_mesh_schedule_json_truncates_mismatched_time_event_pairs() -> None:
    parsed = parse_mesh_schedule_json(
        {"days": [1], "time": [100, 200], "evt": [1]},
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [1], "time": [100], "evt": [1]}


def test_parse_mesh_schedule_json_rejects_legacy_wrapped_payload() -> None:
    parsed = parse_mesh_schedule_json(
        {"schedule": {"days": [1], "time": [3600], "evt": [0]}},
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [], "time": [], "evt": []}


def test_normalize_mesh_timing_rows_sets_schedule_from_verified_payload() -> None:
    rows = normalize_mesh_timing_rows(
        [
            {
                "id": 0,
                "deviceId": "03ab0000000000aa",
                "scheduleJson": '{"days":[2],"time":[86340],"evt":[1]}',
                "active": True,
            },
            {
                "id": 2,
                "deviceId": "03ab0000000000bb",
                "active": "false",
                "schedule": {"days": [2], "time": [120], "evt": [1]},
            },
        ],
        parse_schedule_json=lambda payload: parse_mesh_schedule_json(
            payload,
            mask_sensitive_data=_mask,
        ),
        coerce_connect_status=_coerce_bool,
    )

    assert rows[0]["deviceId"] == "03ab0000000000aa"
    assert rows[0]["schedule"] == {"days": [2], "time": [86340], "evt": [1]}
    assert rows[0]["active"] is True
    assert rows[1]["schedule"] == {"days": [], "time": [], "evt": []}
    assert rows[1]["active"] is False


@pytest.mark.parametrize("payload", ["   ", 123])
def test_parse_mesh_schedule_json_blank_or_non_mapping_returns_empty(
    payload: object,
) -> None:
    parsed = parse_mesh_schedule_json(
        payload,
        mask_sensitive_data=_mask,
    )
    assert parsed == {"days": [], "time": [], "evt": []}


def test_coerce_int_list_skips_bool_and_invalid_numeric_string() -> None:
    assert coerce_int_list([True, 1, 2.0, 2.5, " 3 ", "+-1", "abc"]) == [1, 2, 3]


def test_normalize_mesh_timing_rows_skips_non_mapping_rows_and_fills_fallback_id() -> (
    None
):
    normalized = normalize_mesh_timing_rows(
        [
            1,
            {
                "id": 1,
                "active": 1,
                "scheduleJson": '{"days":[1],"time":[3600],"evt":[0]}',
            },
        ],
        fallback_device_id="03ab0000000000a1",
        parse_schedule_json=lambda payload: parse_mesh_schedule_json(
            payload,
            mask_sensitive_data=_mask,
        ),
        coerce_connect_status=_coerce_bool,
    )

    assert normalized == [
        {
            "id": 1,
            "active": True,
            "scheduleJson": '{"days":[1],"time":[3600],"evt":[0]}',
            "schedule": {"days": [1], "time": [3600], "evt": [0]},
            "deviceId": "03ab0000000000a1",
        }
    ]
