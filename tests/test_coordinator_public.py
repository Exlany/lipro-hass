"""Tests for the native Coordinator runtime surface."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.coordinator import Coordinator
from custom_components.lipro.core.coordinator import LiproDataUpdateCoordinator
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


@pytest.mark.asyncio
async def test_coordinator_exposes_native_runtime_services() -> None:
    device = MagicMock()
    coordinator = object.__new__(Coordinator)
    coordinator._devices = {"dev1": device}
    coordinator._device_identity_index = DeviceIdentityIndex({"dev1": device})
    coordinator._last_command_failure = {"reason": "ok"}
    coordinator._mqtt_connected = True
    coordinator.command_service = MagicMock()
    coordinator.command_service.async_send_command = AsyncMock(return_value=True)
    coordinator.device_refresh_service = MagicMock()
    coordinator.device_refresh_service.async_refresh_devices = AsyncMock()
    coordinator.mqtt_service = MagicMock()
    coordinator.mqtt_service.async_setup = AsyncMock(return_value=True)
    coordinator.mqtt_service.async_sync_subscriptions = AsyncMock()
    coordinator.mqtt_service.async_stop = AsyncMock()

    assert coordinator.devices == {"dev1": device}
    assert coordinator.mqtt_connected is True
    assert coordinator.last_command_failure == {"reason": "ok"}
    assert coordinator.get_device("dev1") is device
    assert coordinator.get_device_by_id("dev1") is device
    assert await coordinator.async_send_command(device, "POWER_ON") is True
    assert await coordinator.async_setup_mqtt() is True
    await coordinator.async_refresh_devices()
    await coordinator.async_sync_mqtt_subscriptions()
    await coordinator.async_stop_mqtt()

    coordinator.command_service.async_send_command.assert_awaited_once_with(
        device,
        "POWER_ON",
        None,
        None,
    )
    coordinator.device_refresh_service.async_refresh_devices.assert_awaited_once_with()
    coordinator.mqtt_service.async_setup.assert_awaited_once_with()
    coordinator.mqtt_service.async_sync_subscriptions.assert_awaited_once_with()
    coordinator.mqtt_service.async_stop.assert_awaited_once_with()


def test_legacy_coordinator_name_aliases_native_runtime() -> None:
    assert LiproDataUpdateCoordinator is Coordinator
