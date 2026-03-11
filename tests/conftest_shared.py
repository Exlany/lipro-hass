"""Shared test utilities and fixtures for refactored tests.

This module provides common helpers for testing the new runtime-based architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from custom_components.lipro.core.coordinator import Coordinator


def make_api_device(
    *,
    serial: str = "03ab5ccd7cxxxxxx",
    name: str = "Test Light",
    device_type: int = 1,
    iot_name: str = "lipro_led",
    physical_model: str = "light",
    is_group: bool = False,
    product_id: int | None = None,
    room_id: int | None = None,
    room_name: str | None = None,
) -> dict[str, Any]:
    """Build a device dict matching the API response format.

    Args:
        serial: Device serial number
        name: Device name
        device_type: Device type code
        iot_name: IoT model name
        physical_model: Physical model type
        is_group: Whether device is a group
        product_id: Optional product ID
        room_id: Optional room ID
        room_name: Optional room name

    Returns:
        Device dictionary in API format
    """
    device = {
        "deviceId": 1,
        "serial": serial,
        "deviceName": name,
        "type": device_type,
        "iotName": iot_name,
        "physicalModel": physical_model,
        "isGroup": is_group,
    }
    if product_id is not None:
        device["productId"] = product_id
    if room_id is not None:
        device["roomId"] = room_id
    if room_name is not None:
        device["roomName"] = room_name
    return device


async def refresh_and_sync_devices(coordinator: Coordinator) -> None:
    """Refresh devices and sync to coordinator state.

    This helper mimics what _async_update_data does internally:
    1. Call device_runtime.refresh_devices() to get snapshot
    2. Update coordinator._devices with snapshot.devices

    Args:
        coordinator: Coordinator instance
    """
    snapshot = await coordinator.device_runtime.refresh_devices()
    coordinator._devices.clear()
    coordinator._devices.update(snapshot.devices)


def mock_anonymous_share_manager() -> MagicMock:
    """Create a mock anonymous share manager.

    Returns:
        Mock with is_enabled=False
    """
    mock = MagicMock()
    mock.is_enabled = False
    mock.set_enabled = MagicMock()
    return mock


__all__ = [
    "make_api_device",
    "mock_anonymous_share_manager",
    "refresh_and_sync_devices",
]
