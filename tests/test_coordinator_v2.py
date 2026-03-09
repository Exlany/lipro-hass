"""Tests for the composed CoordinatorV2 facade."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.coordinator_v2 import CoordinatorV2


@pytest.mark.asyncio
async def test_coordinator_v2_delegates_core_services() -> None:
    device = MagicMock()
    state_service = MagicMock()
    state_service.devices = {"dev1": device}
    state_service.get_device.return_value = device
    state_service.get_device_by_id.return_value = device
    command_service = MagicMock()
    command_service.async_send_command = AsyncMock(return_value=True)
    refresh_service = MagicMock()
    refresh_service.async_refresh_devices = AsyncMock()
    mqtt_service = MagicMock()
    mqtt_service.async_setup = AsyncMock(return_value=True)
    mqtt_service.async_stop = AsyncMock()
    mqtt_service.async_sync_subscriptions = AsyncMock()

    coordinator = CoordinatorV2(
        state_service=state_service,
        command_service=command_service,
        device_refresh_service=refresh_service,
        mqtt_service=mqtt_service,
    )

    assert coordinator.devices == {"dev1": device}
    assert coordinator.get_device("dev1") is device
    assert coordinator.get_device_by_id("dev1") is device
    assert await coordinator.async_send_command(device, "POWER_ON") is True
    assert await coordinator.async_setup_mqtt() is True
    await coordinator.async_refresh_devices()
    await coordinator.async_sync_mqtt_subscriptions()
    await coordinator.async_stop_mqtt()

    command_service.async_send_command.assert_awaited_once_with(
        device,
        "POWER_ON",
        None,
        None,
    )
    refresh_service.async_refresh_devices.assert_awaited_once_with()
    mqtt_service.async_setup.assert_awaited_once_with()
    mqtt_service.async_sync_subscriptions.assert_awaited_once_with()
    mqtt_service.async_stop.assert_awaited_once_with()


def test_coordinator_v2_from_legacy_reuses_services() -> None:
    legacy = MagicMock()
    legacy.state_service = MagicMock()
    legacy.command_service = MagicMock()
    legacy.device_refresh_service = MagicMock()
    legacy.mqtt_service = MagicMock()
    legacy.example_attr = "ok"

    coordinator = CoordinatorV2.from_legacy(legacy)

    assert coordinator.state_service is legacy.state_service
    assert coordinator.command_service is legacy.command_service
    assert coordinator.device_refresh_service is legacy.device_refresh_service
    assert coordinator.mqtt_service is legacy.mqtt_service
    assert coordinator.example_attr == "ok"
