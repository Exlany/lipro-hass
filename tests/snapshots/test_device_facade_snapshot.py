"""Snapshot guard for the decomposed device facade."""

from __future__ import annotations

from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.core.device import LiproDevice


def test_device_facade_snapshot(snapshot: SnapshotAssertion) -> None:
    device = LiproDevice(
        device_number=1,
        serial="rmt_id_appremote_realremote_03ab5ccd7c123456",
        name="IR Remote",
        device_type=11,
        iot_name="irRemote",
        physical_model="irRemote",
        properties={
            "irSwitch": "0",
            "wifiRssi": "-72",
            "connectState": "1",
        },
    )

    assert {
        "unique_id": device.unique_id,
        "iot_device_id": device.iot_device_id,
        "supports_ir_switch": device.supports_ir_switch,
        "ir_remote_gateway_device_id": device.ir_remote_gateway_device_id,
        "connection_quality": device.connection_quality,
        "is_connected": device.is_connected,
    } == snapshot
