"""Focused tests for the formal control-plane adapters."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import (
    async_reload_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.lipro.const.base import DOMAIN


@pytest.mark.asyncio
async def test_async_setup_delegates_to_entry_lifecycle_controller(hass) -> None:
    controller = MagicMock()
    controller.async_setup_component = AsyncMock(return_value=True)
    with patch(
        "custom_components.lipro._build_entry_lifecycle_controller",
        return_value=controller,
    ):
        assert await async_setup(hass, {}) is True

    controller.async_setup_component.assert_awaited_once_with(hass, {})


@pytest.mark.asyncio
async def test_async_setup_entry_delegates_to_entry_lifecycle_controller(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    controller = MagicMock()
    controller.async_setup_entry = AsyncMock(return_value=True)
    with patch(
        "custom_components.lipro._build_entry_lifecycle_controller",
        return_value=controller,
    ):
        assert await async_setup_entry(hass, entry) is True

    controller.async_setup_entry.assert_awaited_once_with(hass, entry)


@pytest.mark.asyncio
async def test_async_unload_entry_delegates_to_entry_lifecycle_controller(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    controller = MagicMock()
    controller.async_unload_entry = AsyncMock(return_value=True)
    with patch(
        "custom_components.lipro._build_entry_lifecycle_controller",
        return_value=controller,
    ):
        assert await async_unload_entry(hass, entry) is True

    controller.async_unload_entry.assert_awaited_once_with(hass, entry)


@pytest.mark.asyncio
async def test_async_reload_entry_delegates_to_entry_lifecycle_controller(hass) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    controller = MagicMock()
    controller.async_reload_entry = AsyncMock(return_value=None)
    with patch(
        "custom_components.lipro._build_entry_lifecycle_controller",
        return_value=controller,
    ):
        await async_reload_entry(hass, entry)

    controller.async_reload_entry.assert_awaited_once_with(hass, entry)


def test_runtime_snapshot_uses_telemetry_surface_projection() -> None:
    from custom_components.lipro.control.runtime_access import build_runtime_snapshot

    coordinator = MagicMock()
    coordinator.last_update_success = False
    entry = MagicMock()
    entry.entry_id = "entry-1"
    entry.runtime_data = coordinator

    with patch(
        "custom_components.lipro.control.runtime_access.build_entry_system_health_view",
        return_value={
            "device_count": 5,
            "mqtt_connected": True,
            "last_update_success": True,
        },
    ):
        snapshot = build_runtime_snapshot(entry)

    assert snapshot is not None
    assert snapshot.device_count == 5
    assert snapshot.mqtt_connected is True
    assert snapshot.last_update_success is True
