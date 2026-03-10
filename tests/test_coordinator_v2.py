"""Tests for the composed CoordinatorV2 facade."""

from __future__ import annotations

from datetime import timedelta
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
    command_service.last_failure = {"reason": "ok"}
    refresh_service = MagicMock()
    refresh_service.async_refresh_devices = AsyncMock()
    mqtt_service = MagicMock()
    mqtt_service.connected = True
    mqtt_service.async_setup = AsyncMock(return_value=True)
    mqtt_service.async_sync_subscriptions = AsyncMock()
    mqtt_service.async_stop = AsyncMock()
    coordinator = CoordinatorV2(
        state_service=state_service,
        command_service=command_service,
        device_refresh_service=refresh_service,
        mqtt_service=mqtt_service,
    )

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


@pytest.mark.asyncio
async def test_coordinator_v2_from_legacy_copies_services_and_runtime_hooks() -> None:
    legacy = MagicMock()
    legacy.state_service = MagicMock(devices={})
    legacy.command_service = MagicMock(last_failure={"reason": "api"})
    legacy.command_service.async_send_command = AsyncMock(return_value=False)
    legacy.device_refresh_service = MagicMock()
    legacy.device_refresh_service.async_refresh_devices = AsyncMock()
    legacy.mqtt_service = MagicMock(connected=False)
    legacy.mqtt_service.async_setup = AsyncMock(return_value=False)
    legacy.mqtt_service.async_sync_subscriptions = AsyncMock()
    legacy.mqtt_service.async_stop = AsyncMock()
    legacy.client = MagicMock()
    legacy.update_interval = timedelta(seconds=30)
    legacy.last_update_success = True
    legacy.async_request_refresh = AsyncMock()
    legacy.async_config_entry_first_refresh = AsyncMock()
    legacy.async_shutdown = AsyncMock()
    legacy.async_update_listeners = MagicMock()
    legacy.register_entity = MagicMock()
    legacy.unregister_entity = MagicMock()
    legacy.build_developer_report = MagicMock(return_value={"ok": True})

    coordinator = CoordinatorV2.from_legacy(legacy)

    assert coordinator.state_service is legacy.state_service
    assert coordinator.command_service is legacy.command_service
    assert coordinator.device_refresh_service is legacy.device_refresh_service
    assert coordinator.mqtt_service is legacy.mqtt_service
    assert coordinator.client is legacy.client
    assert coordinator.update_interval == timedelta(seconds=30)
    assert coordinator.last_update_success is True
    assert coordinator.mqtt_connected is False
    assert coordinator.last_command_failure == {"reason": "api"}
    assert coordinator.build_developer_report() == {"ok": True}

    await coordinator.async_request_refresh()
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_shutdown()
    coordinator.async_update_listeners()
    coordinator.register_entity(MagicMock())
    coordinator.unregister_entity(MagicMock())

    legacy.async_request_refresh.assert_awaited_once_with()
    legacy.async_config_entry_first_refresh.assert_awaited_once_with()
    legacy.async_shutdown.assert_awaited_once_with()
    legacy.async_update_listeners.assert_called_once_with()
    legacy.register_entity.assert_called_once()
    legacy.unregister_entity.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_v2_missing_runtime_hook_raises_clear_error() -> None:
    coordinator = CoordinatorV2(
        state_service=MagicMock(devices={}),
        command_service=MagicMock(last_failure=None),
        device_refresh_service=MagicMock(),
        mqtt_service=MagicMock(connected=False),
    )

    with pytest.raises(AttributeError, match="async_request_refresh"):
        await coordinator.async_request_refresh()
