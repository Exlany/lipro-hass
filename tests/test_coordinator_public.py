"""Tests for the native Coordinator runtime surface."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.coordinator_entry import Coordinator
from custom_components.lipro.core.coordinator import LiproDataUpdateCoordinator
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


@pytest.mark.asyncio
async def test_coordinator_exposes_native_runtime_services() -> None:
    """Test that coordinator exposes runtime services and delegates to service layer."""
    device = MagicMock()
    coordinator = object.__new__(Coordinator)
    coordinator._devices = {"dev1": device}
    coordinator._device_identity_index = DeviceIdentityIndex()
    coordinator._device_identity_index.register("dev1", device)

    # Mock service layer
    coordinator.command_service = MagicMock()
    coordinator.command_service.async_send_command = AsyncMock(return_value=True)
    coordinator.state_service = MagicMock()
    coordinator.state_service.get_device = MagicMock(return_value=device)
    coordinator.state_service.get_device_by_id = MagicMock(return_value=device)

    # Test public API - devices property
    assert coordinator.devices == {"dev1": device}

    # Test public API - device lookup delegates to state_service
    assert coordinator.get_device("dev1") is device
    coordinator.state_service.get_device.assert_called_once_with("dev1")

    assert coordinator.get_device_by_id("dev1") is device
    coordinator.state_service.get_device_by_id.assert_called_once_with("dev1")

    # Test public API - command service delegation
    assert await coordinator.async_send_command(device, "POWER_ON") is True
    coordinator.command_service.async_send_command.assert_awaited_once_with(
        device,
        "POWER_ON",
        None,
    )


def test_legacy_coordinator_name_aliases_native_runtime() -> None:
    """Test that LiproDataUpdateCoordinator is an alias for Coordinator."""
    assert LiproDataUpdateCoordinator is Coordinator



