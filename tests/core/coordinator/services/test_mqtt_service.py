"""Tests for the thin coordinator MQTT service adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.mqtt_service import (
    CoordinatorMqttService,
)


def _make_device(*, serial: str, is_group: bool = False) -> MagicMock:
    device = MagicMock()
    device.serial = serial
    device.is_group = is_group
    return device


def test_mqtt_service_connected_reflects_coordinator_flag() -> None:
    coordinator = MagicMock()
    mqtt_runtime = MagicMock()
    mqtt_runtime.is_connected = True
    coordinator.mqtt_runtime = mqtt_runtime
    service = CoordinatorMqttService(coordinator)

    assert service.connected is True


@pytest.mark.asyncio
async def test_mqtt_service_delegates_lifecycle_calls() -> None:
    coordinator = MagicMock()
    coordinator.async_setup_mqtt = AsyncMock(return_value=True)
    coordinator.mqtt_runtime = MagicMock()
    coordinator.mqtt_runtime.disconnect = AsyncMock()
    coordinator.mqtt_runtime.sync_subscriptions = AsyncMock(return_value=True)
    coordinator.mqtt_client = MagicMock()
    coordinator.devices = {
        "dev1": _make_device(serial="dev1"),
        "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
    }
    service = CoordinatorMqttService(coordinator)

    assert await service.async_setup() is True
    await service.async_sync_subscriptions()
    await service.async_stop()

    coordinator.async_setup_mqtt.assert_awaited_once()
    coordinator.mqtt_runtime.sync_subscriptions.assert_awaited_once_with(["mesh_group_1"])
    coordinator.mqtt_runtime.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_mqtt_service_sync_subscriptions_sets_up_client_when_missing() -> None:
    coordinator = MagicMock()
    coordinator.async_setup_mqtt = AsyncMock(return_value=True)
    coordinator.mqtt_runtime = MagicMock()
    coordinator.mqtt_client = None
    coordinator.devices = {
        "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
    }
    service = CoordinatorMqttService(coordinator)

    await service.async_sync_subscriptions()

    coordinator.async_setup_mqtt.assert_awaited_once()
    coordinator.mqtt_runtime.sync_subscriptions.assert_not_called()
