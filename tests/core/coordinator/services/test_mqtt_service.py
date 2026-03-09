"""Tests for the thin coordinator MQTT service adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.mqtt_service import (
    CoordinatorMqttService,
)


def test_mqtt_service_connected_reflects_coordinator_flag() -> None:
    coordinator = MagicMock()
    coordinator.mqtt_connected = True
    service = CoordinatorMqttService(coordinator)

    assert service.connected is True


@pytest.mark.asyncio
async def test_mqtt_service_delegates_lifecycle_calls() -> None:
    coordinator = MagicMock()
    coordinator.mqtt_connected = False
    coordinator.async_setup_mqtt_runtime = AsyncMock(return_value=True)
    coordinator.async_stop_mqtt_runtime = AsyncMock()
    coordinator.async_sync_mqtt_subscriptions_runtime = AsyncMock()
    service = CoordinatorMqttService(coordinator)

    assert await service.async_setup() is True
    await service.async_sync_subscriptions()
    await service.async_stop()

    coordinator.async_setup_mqtt_runtime.assert_awaited_once()
    coordinator.async_sync_mqtt_subscriptions_runtime.assert_awaited_once()
    coordinator.async_stop_mqtt_runtime.assert_awaited_once()
