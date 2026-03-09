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
