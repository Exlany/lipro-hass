"""Snapshot coverage for the native Coordinator runtime surface."""

from __future__ import annotations

from unittest.mock import MagicMock

from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.coordinator_entry import Coordinator
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


def test_coordinator_snapshot(snapshot: SnapshotAssertion) -> None:
    device = MagicMock()
    coordinator = object.__new__(Coordinator)
    coordinator._devices = {"dev1": device}
    coordinator._device_identity_index = DeviceIdentityIndex({"dev1": device})
    coordinator.command_service = MagicMock(last_failure=None)
    coordinator.device_refresh_service = MagicMock()
    coordinator.mqtt_service = MagicMock(connected=True)

    data = {
        "devices": sorted(coordinator.devices.keys()),
        "mqtt_connected": coordinator.mqtt_service.connected,
        "last_command_failure": coordinator.command_service.last_failure,
        "runtime_class": type(coordinator).__name__,
    }

    assert data == snapshot
