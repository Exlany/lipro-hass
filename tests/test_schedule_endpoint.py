"""Tests for schedule endpoint helpers."""

from __future__ import annotations

from typing import Any

from custom_components.lipro.core.schedule_endpoint import (
    build_mesh_schedule_add_body,
    build_mesh_schedule_delete_body,
    build_mesh_schedule_get_body,
    build_schedule_add_body,
    build_schedule_delete_body,
    build_schedule_get_body,
    encode_mesh_schedule_json,
    is_mesh_group_id,
    resolve_mesh_schedule_candidate_ids,
)


def _normalize_iot_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized.startswith("03ab") and len(normalized) == 16:
        return normalized
    return None


def test_is_mesh_group_id_matches_case_and_whitespace() -> None:
    assert is_mesh_group_id("mesh_group_10001") is True
    assert is_mesh_group_id("  MESH_GROUP_10001  ") is True
    assert is_mesh_group_id("03ab5ccd7c123456") is False


def test_resolve_mesh_schedule_candidate_ids_prefers_gateway_member_then_group() -> (
    None
):
    result = resolve_mesh_schedule_candidate_ids(
        "mesh_group_10001",
        mesh_gateway_id=" 03AB0000000000A1 ",
        mesh_member_ids=[
            "03AB0000000000A2",
            "03ab0000000000a1",
            "invalid",
            "03AB0000000000A3",
        ],
        normalize_iot_device_id=_normalize_iot_id,
    )

    assert result == [
        "03ab0000000000a1",
        "03ab0000000000a2",
        "03ab0000000000a3",
    ]


def test_encode_mesh_schedule_json_compact_payload() -> None:
    encoded = encode_mesh_schedule_json([1, 2], [3600], [0])

    assert encoded == '{"days":[1,2],"time":[3600],"evt":[0]}'


def test_build_mesh_schedule_bodies() -> None:
    assert build_mesh_schedule_get_body("03ab0000000000a1") == {
        "deviceId": "03ab0000000000a1",
        "deviceType": "mesh",
    }
    assert build_mesh_schedule_add_body(
        "03ab0000000000a1",
        schedule_json='{"days":[1],"time":[3600],"evt":[0]}',
    ) == {
        "deviceId": "03ab0000000000a1",
        "id": 0,
        "scheduleJson": '{"days":[1],"time":[3600],"evt":[0]}',
        "active": True,
    }
    assert build_mesh_schedule_delete_body(
        "03ab0000000000a1",
        schedule_ids=[1, 2],
    ) == {
        "deviceId": "03ab0000000000a1",
        "idList": [1, 2],
    }


def test_build_standard_schedule_bodies() -> None:
    assert build_schedule_get_body(
        "03ab0000000000a1",
        device_type_hex="0x1032",
    ) == {
        "deviceId": "03ab0000000000a1",
        "deviceType": "0x1032",
    }
    assert build_schedule_add_body(
        "03ab0000000000a1",
        device_type_hex="0x1032",
        days=[1, 2],
        times=[3600],
        events=[0],
        group_id="mesh_group_10001",
    ) == {
        "deviceId": "03ab0000000000a1",
        "deviceType": "0x1032",
        "scheduleInfo": {"days": [1, 2], "time": [3600], "evt": [0]},
        "groupId": "mesh_group_10001",
        "singleBle": False,
    }
    assert build_schedule_delete_body(
        "03ab0000000000a1",
        device_type_hex="0x1032",
        schedule_ids=[3, 4],
        group_id="mesh_group_10001",
    ) == {
        "deviceId": "03ab0000000000a1",
        "deviceType": "0x1032",
        "idList": [3, 4],
        "groupId": "mesh_group_10001",
        "singleBle": False,
    }
