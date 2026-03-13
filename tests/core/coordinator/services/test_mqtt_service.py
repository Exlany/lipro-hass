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


def test_mqtt_service_connected_reflects_runtime_flag() -> None:
    mqtt_runtime = MagicMock()
    mqtt_runtime.is_connected = True
    mqtt_runtime.has_transport = True
    service = CoordinatorMqttService(
        devices_getter=dict,
        mqtt_runtime_getter=lambda: mqtt_runtime,
        setup_callback=AsyncMock(return_value=True),
    )

    assert service.connected is True


@pytest.mark.asyncio
async def test_mqtt_service_delegates_lifecycle_calls() -> None:
    mqtt_runtime = MagicMock()
    mqtt_runtime.disconnect = AsyncMock()
    mqtt_runtime.sync_subscriptions = AsyncMock(return_value=True)
    mqtt_runtime.has_transport = True
    setup_callback = AsyncMock(return_value=True)
    service = CoordinatorMqttService(
        devices_getter=lambda: {
            "dev1": _make_device(serial="dev1"),
            "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
        },
        mqtt_runtime_getter=lambda: mqtt_runtime,
        setup_callback=setup_callback,
    )

    assert await service.async_setup() is True
    await service.async_sync_subscriptions()
    await service.async_stop()

    setup_callback.assert_awaited_once()
    mqtt_runtime.sync_subscriptions.assert_awaited_once_with(["mesh_group_1"])
    mqtt_runtime.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_mqtt_service_sync_subscriptions_sets_up_client_when_missing() -> None:
    mqtt_runtime = MagicMock()
    mqtt_runtime.sync_subscriptions = AsyncMock()
    mqtt_runtime.has_transport = False
    setup_callback = AsyncMock(return_value=True)
    service = CoordinatorMqttService(
        devices_getter=lambda: {
            "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
        },
        mqtt_runtime_getter=lambda: mqtt_runtime,
        setup_callback=setup_callback,
    )

    await service.async_sync_subscriptions()

    setup_callback.assert_awaited_once()
    mqtt_runtime.sync_subscriptions.assert_not_called()


@pytest.mark.asyncio
async def test_mqtt_service_sync_subscriptions_skips_when_no_devices() -> None:
    mqtt_runtime = MagicMock()
    mqtt_runtime.sync_subscriptions = AsyncMock()
    setup_callback = AsyncMock(return_value=True)
    service = CoordinatorMqttService(
        devices_getter=dict,
        mqtt_runtime_getter=lambda: mqtt_runtime,
        setup_callback=setup_callback,
    )

    await service.async_sync_subscriptions()

    setup_callback.assert_not_awaited()
    mqtt_runtime.sync_subscriptions.assert_not_called()
