"""Tests for the thin coordinator MQTT service adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.mqtt_service import (
    CoordinatorMqttService,
)


def test_mqtt_service_connected_reflects_coordinator_flag() -> None:
    coordinator = MagicMock()
    coordinator._mqtt_runtime._connection_manager.is_connected.return_value = True
    service = CoordinatorMqttService(coordinator)

    assert service.connected is True


@pytest.mark.asyncio
async def test_mqtt_service_delegates_lifecycle_calls() -> None:
    coordinator = MagicMock()
    coordinator._mqtt_runtime.setup = AsyncMock(return_value=True)
    coordinator._mqtt_runtime.stop = AsyncMock()
    coordinator._mqtt_runtime.sync_subscriptions = AsyncMock()
    coordinator._state_runtime.get_all_devices.return_value = {}
    service = CoordinatorMqttService(coordinator)

    assert await service.async_setup() is True
    await service.async_sync_subscriptions()
    await service.async_stop()

    coordinator._mqtt_runtime.setup.assert_awaited_once()
    coordinator._mqtt_runtime.sync_subscriptions.assert_awaited_once_with({})
    coordinator._mqtt_runtime.stop.assert_awaited_once()
