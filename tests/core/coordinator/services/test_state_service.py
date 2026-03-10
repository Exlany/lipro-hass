"""Tests for the coordinator state-management service."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.coordinator.services.state_service import (
    CoordinatorStateService,
)


def test_state_service_exposes_device_accessors() -> None:
    device = MagicMock()
    coordinator = MagicMock()
    coordinator.state_runtime.get_all_devices.return_value = {"dev1": device}
    coordinator.state_runtime.get_device_by_serial.return_value = device
    coordinator.state_runtime.get_device_by_id.return_value = device
    service = CoordinatorStateService(coordinator)

    assert service.devices == {"dev1": device}
    assert service.get_device("dev1") is device
    assert service.get_device_by_id("dev1") is device
    coordinator.state_runtime.get_device_by_serial.assert_called_once_with("dev1")
    coordinator.state_runtime.get_device_by_id.assert_called_once_with("dev1")
