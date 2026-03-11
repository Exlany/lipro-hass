"""Tests for the native Coordinator runtime surface."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.coordinator_entry import Coordinator
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


@pytest.mark.asyncio
async def test_coordinator_exposes_native_runtime_services() -> None:
    """Coordinator should delegate public APIs to the new service layer."""
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
        device_identity_index=DeviceIdentityIndex(),
        background_task_manager=MagicMock(),
        confirmation_tracker=MagicMock(),
    )
    coordinator._state.device_identity_index.register("dev1", device)

    coordinator.command_service = MagicMock()
    coordinator.command_service.async_send_command = AsyncMock(return_value=True)
    coordinator.state_service = MagicMock()
    coordinator.state_service.get_device = MagicMock(return_value=device)
    coordinator.state_service.get_device_by_id = MagicMock(return_value=device)

    assert coordinator.devices == {"dev1": device}
    assert coordinator.get_device("dev1") is device
    coordinator.state_service.get_device.assert_called_once_with("dev1")
    assert coordinator.get_device_by_id("dev1") is device
    coordinator.state_service.get_device_by_id.assert_called_once_with("dev1")
    assert await coordinator.async_send_command(device, "POWER_ON") is True
    coordinator.command_service.async_send_command.assert_awaited_once_with(
        device,
        "POWER_ON",
        None,
    )
