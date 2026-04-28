"""Tests for mesh-group status parsing helpers."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.device.group_status import (
    resolve_mesh_group_lookup_ids,
    sync_mesh_group_extra_data,
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


def test_sync_mesh_group_extra_data_updates_and_clears_group_metadata() -> None:
    device = LiproDevice(
        device_number=1,
        serial="mesh_group_10001",
        name="Mesh Group",
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        is_group=True,
        extra_data={
            "gateway_device_id": "03ab0000000000ff",
            "group_member_ids": ["03ab0000000000aa"],
        },
    )

    changed = sync_mesh_group_extra_data(
        device,
        {
            "groupId": "mesh_group_10001",
            "gatewayDeviceId": " 03AB0000000000A1 ",
            "devices": [
                {"deviceId": "03ab0000000000a2"},
                {"deviceId": " 03AB0000000000A2 "},
                {"deviceId": None},
                {"deviceId": "bad"},
            ],
        },
    )

    assert changed is True
    assert device.extra_data["gateway_device_id"] == "03ab0000000000a1"
    assert device.extra_data["group_member_ids"] == ["03ab0000000000a2"]

    changed = sync_mesh_group_extra_data(
        device,
        {
            "groupId": "mesh_group_10001",
            "gatewayDeviceId": None,
            "devices": [],
        },
    )

    assert changed is True
    assert "gateway_device_id" not in device.extra_data
    assert "group_member_ids" not in device.extra_data
