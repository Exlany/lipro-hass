"""Snapshot coverage for the native Coordinator runtime surface."""

from __future__ import annotations

from unittest.mock import MagicMock

from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.coordinator_entry import Coordinator
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


def test_coordinator_snapshot(snapshot: SnapshotAssertion) -> None:
    from custom_components.lipro.core.coordinator.factory import (
        CoordinatorStateContainers,
    )

    device = MagicMock()
    coordinator = object.__new__(Coordinator)

    # Initialize _state container
    coordinator._state = CoordinatorStateContainers(
        devices={"dev1": device},
        entities={},
        entities_by_device={},
        device_identity_index=DeviceIdentityIndex({"dev1": device}),
        background_task_manager=MagicMock(),
        confirmation_tracker=MagicMock(),
    )

    coordinator.command_service = MagicMock(last_failure=None)
    coordinator.device_refresh_service = MagicMock()
    coordinator.mqtt_service = MagicMock(connected=True)
    coordinator.telemetry_service = MagicMock(
        build_snapshot=MagicMock(
            return_value={
                "device_count": 1,
                "mqtt": {"connected": True},
                "command": {"trace_count": 0},
            }
        )
    )

    data = {
        "devices": sorted(coordinator.devices.keys()),
        "mqtt_connected": coordinator.mqtt_service.connected,
        "last_command_failure": coordinator.command_service.last_failure,
        "telemetry": coordinator.telemetry_service.build_snapshot(),
        "runtime_class": type(coordinator).__name__,
    }

    assert data == snapshot
