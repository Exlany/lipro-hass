"""Static-friendly tests for coordinator service protocols."""

from __future__ import annotations

from typing import assert_type
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.protocols import (
    CommandServiceProtocol,
    DeviceRefreshServiceProtocol,
    MqttServiceProtocol,
    StateManagementProtocol,
)
from custom_components.lipro.core.device import LiproDevice


def test_state_protocol_shape() -> None:
    service: StateManagementProtocol = MagicMock(
        devices={},
        get_device=lambda _serial: None,
        get_device_by_id=lambda _device_id: None,
    )

    assert service.devices == {}
    assert assert_type(service.get_device("dev1"), LiproDevice | None) is None


@pytest.mark.asyncio
async def test_async_protocol_shapes() -> None:
    command_service: CommandServiceProtocol = MagicMock(
        async_send_command=AsyncMock(return_value=True),
        last_failure=None,
    )
    refresh_service: DeviceRefreshServiceProtocol = MagicMock(
        devices={},
        get_device_by_id=lambda _device_id: None,
        async_refresh_devices=AsyncMock(),
    )
    mqtt_service: MqttServiceProtocol = MagicMock(
        connected=False,
        async_setup=AsyncMock(return_value=True),
        async_stop=AsyncMock(),
        async_sync_subscriptions=AsyncMock(),
    )

    assert await command_service.async_send_command(MagicMock(), "POWER_ON") is True
    await refresh_service.async_refresh_devices()
    assert await mqtt_service.async_setup() is True
    await mqtt_service.async_sync_subscriptions()
    await mqtt_service.async_stop()
