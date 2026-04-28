"""Tests for the thin coordinator device refresh service adapter."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.runtime.state_runtime import StateRuntime
from custom_components.lipro.core.coordinator.services.device_refresh_service import (
    CoordinatorDeviceRefreshService,
)


def test_device_refresh_service_exposes_lookup_and_devices() -> None:
    device = MagicMock()
    state_runtime = MagicMock()
    state_runtime.get_all_devices.return_value = {"dev1": device}
    state_runtime.get_device_by_id.return_value = device
    device_runtime = MagicMock()
    service = CoordinatorDeviceRefreshService(
        device_runtime=device_runtime,
        state_runtime=state_runtime,
        refresh_callback=AsyncMock(),
    )

    assert service.devices == {"dev1": device}
    assert service.get_device_by_id("dev1") is device
    state_runtime.get_device_by_id.assert_called_once_with("dev1")


def test_device_refresh_service_requests_force_refresh_from_device_runtime() -> None:
    device_runtime = MagicMock()
    service = CoordinatorDeviceRefreshService(
        device_runtime=device_runtime,
        state_runtime=MagicMock(),
        refresh_callback=AsyncMock(),
    )

    service.request_force_refresh()

    device_runtime.request_force_refresh.assert_called_once_with()


def test_device_refresh_service_requests_group_reconciliation_via_force_refresh() -> (
    None
):
    device_runtime = MagicMock()
    service = CoordinatorDeviceRefreshService(
        device_runtime=device_runtime,
        state_runtime=MagicMock(),
        refresh_callback=AsyncMock(),
    )

    service.request_group_reconciliation(device_name="Group 1", timestamp=2.0)

    device_runtime.request_force_refresh.assert_called_once_with()


@pytest.mark.asyncio
async def test_device_refresh_service_refreshes_and_exposes_latest_snapshot() -> None:
    device = MagicMock()

    class _StateRuntime:
        def __init__(self) -> None:
            self._devices: dict[str, object] = {}

        def get_all_devices(self) -> dict[str, object]:
            return dict(self._devices)

        def get_device_by_id(self, device_id: str) -> object | None:
            return self._devices.get(device_id)

    raw_state_runtime = _StateRuntime()

    async def _refresh() -> None:
        raw_state_runtime._devices = {"dev1": device}

    state_runtime = cast(StateRuntime, raw_state_runtime)

    refresh_callback = AsyncMock(side_effect=_refresh)
    service = CoordinatorDeviceRefreshService(
        device_runtime=MagicMock(),
        state_runtime=state_runtime,
        refresh_callback=refresh_callback,
    )

    assert service.devices == {}
    assert service.get_device_by_id("dev1") is None

    await service.async_refresh_devices()

    refresh_callback.assert_awaited_once()
    assert service.devices == {"dev1": device}
    assert service.get_device_by_id("dev1") is device


@pytest.mark.asyncio
async def test_device_refresh_service_propagates_refresh_rejection() -> None:
    refresh_callback = AsyncMock(side_effect=RuntimeError("boom"))
    service = CoordinatorDeviceRefreshService(
        device_runtime=MagicMock(),
        state_runtime=MagicMock(),
        refresh_callback=refresh_callback,
    )

    with pytest.raises(RuntimeError, match="boom"):
        await service.async_refresh_devices()

    refresh_callback.assert_awaited_once()
