"""Tests for the thin coordinator device refresh service adapter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.services.device_refresh_service import (
    CoordinatorDeviceRefreshService,
)


def test_device_refresh_service_exposes_lookup_and_devices() -> None:
    device = MagicMock()
    coordinator = MagicMock()
    coordinator.state_runtime.get_all_devices.return_value = {"dev1": device}
    coordinator.state_runtime.get_device_by_id.return_value = device
    service = CoordinatorDeviceRefreshService(coordinator)

    assert service.devices == {"dev1": device}
    assert service.get_device_by_id("dev1") is device
    coordinator.state_runtime.get_device_by_id.assert_called_once_with("dev1")


@pytest.mark.asyncio
async def test_device_refresh_service_delegates_refresh() -> None:
    coordinator = MagicMock()
    coordinator.device_runtime.refresh_devices = AsyncMock()
    service = CoordinatorDeviceRefreshService(coordinator)

    await service.async_refresh_devices()

    coordinator.device_runtime.refresh_devices.assert_awaited_once_with(force=True)
