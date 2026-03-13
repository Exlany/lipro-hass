"""Tests for the coordinator state-management service."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from custom_components.lipro.core.coordinator.services.state_service import (
    CoordinatorStateService,
)


def test_state_service_exposes_device_accessors() -> None:
    device = MagicMock()
    state_runtime = MagicMock()
    state_runtime.get_all_devices.return_value = {"dev1": device}
    state_runtime.get_device_by_serial.return_value = device
    state_runtime.get_device_by_id.return_value = device
    service = CoordinatorStateService(state_runtime=state_runtime)

    assert service.devices == {"dev1": device}
    assert service.get_device("dev1") is device
    assert service.get_device_by_id("dev1") is device
    state_runtime.get_device_by_serial.assert_called_once_with("dev1")
    state_runtime.get_device_by_id.assert_called_once_with("dev1")


def test_state_service_returns_wrapped_device_lock() -> None:
    device = MagicMock()
    known_lock = asyncio.Lock()
    state_runtime = MagicMock()
    state_runtime.get_device_by_serial.return_value = device
    state_runtime.get_device_lock.return_value = known_lock
    service = CoordinatorStateService(state_runtime=state_runtime)

    assert service.get_device_lock("dev1") is known_lock
    state_runtime.get_device_lock.assert_called_once_with(device)


def test_state_service_creates_fallback_lock_for_unknown_device() -> None:
    state_runtime = MagicMock()
    state_runtime.get_device_by_serial.return_value = None
    service = CoordinatorStateService(state_runtime=state_runtime)

    fallback_lock = service.get_device_lock("missing")

    assert isinstance(fallback_lock, asyncio.Lock)
    state_runtime.get_device_lock.assert_not_called()
