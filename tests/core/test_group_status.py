"""Tests for mesh-group status parsing helpers."""

from __future__ import annotations

from custom_components.lipro.core.device.group_status import (
    resolve_mesh_group_lookup_ids,
)


def test_resolve_mesh_group_lookup_ids_with_mixed_member_rows() -> None:
    resolved = resolve_mesh_group_lookup_ids(
        {
            "groupId": "mesh_group_10001",
            "gatewayDeviceId": "03ab5ccd7cgw",
            "devices": [
                {"deviceId": "03ab5ccd7c111111"},
                {"deviceId": " 03AB5CCD7C222222 "},
                {"deviceId": None},
                {"deviceId": 123},
                {"other": "ignored"},
                "bad-row",
            ],
        }
    )

    assert resolved.gateway_id == "03ab5ccd7cgw"
    assert resolved.member_lookup_ids == [
        "03ab5ccd7c111111",
        " 03AB5CCD7C222222 ",
        None,
        123,
        None,
    ]
    assert resolved.member_ids == ["03ab5ccd7c111111", "03AB5CCD7C222222"]


def test_resolve_mesh_group_lookup_ids_without_member_list() -> None:
    resolved = resolve_mesh_group_lookup_ids(
        {
            "groupId": "mesh_group_10001",
            "gatewayDeviceId": None,
            "devices": "not-a-list",
        }
    )

    assert resolved.gateway_id is None
    assert resolved.member_lookup_ids == []
    assert resolved.member_ids == []
