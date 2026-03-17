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
    """async_setup should delegate component setup to the controller."""
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
    """async_setup_entry should delegate entry setup to the controller."""
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
    """async_unload_entry should delegate entry unload to the controller."""
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
    """async_reload_entry should delegate entry reload to the controller."""
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
    entry.options = {}
    entry.runtime_data = coordinator

    with patch(
        "custom_components.lipro.control.runtime_access.build_entry_system_health_view",
        return_value={
            "entry_ref": "entry_deadbeef",
            "device_count": 5,
            "mqtt_connected": True,
            "last_update_success": True,
            "failure_summary": {
                "failure_category": "network",
                "failure_origin": "protocol.mqtt",
                "handling_policy": "retry",
                "error_type": "TimeoutError",
            },
        },
    ):
        snapshot = build_runtime_snapshot(entry)

    assert snapshot is not None
    assert snapshot.entry_ref == "entry_deadbeef"
    assert snapshot.device_count == 5
    assert snapshot.mqtt_connected is True
    assert snapshot.last_update_success is True
    assert snapshot.failure_summary == {
        "failure_category": "network",
        "failure_origin": "protocol.mqtt",
        "handling_policy": "retry",
        "error_type": "TimeoutError",
    }


def test_find_runtime_entry_for_coordinator_prefers_bound_entry() -> None:
    from custom_components.lipro.control.runtime_access import (
        find_runtime_entry_for_coordinator,
    )

    entry = MockConfigEntry(domain=DOMAIN, options={})
    coordinator = MagicMock(config_entry=entry)
    entry.runtime_data = coordinator

    assert find_runtime_entry_for_coordinator(MagicMock(), coordinator) is entry


def test_iter_runtime_entries_preserves_live_entry_identity(hass) -> None:
    from custom_components.lipro.control.runtime_access import iter_runtime_entries

    entry = MockConfigEntry(domain=DOMAIN, options={"debug_mode": True})
    entry.runtime_data = MagicMock(name="runtime")
    entry.add_to_hass(hass)

    [runtime_entry] = iter_runtime_entries(hass)

    assert runtime_entry is entry


def test_build_single_runtime_coordinator_iterator_returns_stable_singleton(
    hass,
) -> None:
    from custom_components.lipro.control.developer_router_support import (
        build_single_runtime_coordinator_iterator,
    )

    coordinator = MagicMock(name="coordinator")
    iterator_factory = build_single_runtime_coordinator_iterator(coordinator)

    assert list(iterator_factory(hass)) == [coordinator]
    assert list(iterator_factory(hass)) == [coordinator]


def test_runtime_access_filters_debug_runtime_coordinators(hass) -> None:
    from custom_components.lipro.control.runtime_access import (
        has_debug_mode_runtime_entry,
        iter_developer_runtime_coordinators,
    )

    debug_entry = MockConfigEntry(domain=DOMAIN, options={"debug_mode": True})
    debug_entry.runtime_data = MagicMock(name="debug")
    quiet_entry = MockConfigEntry(domain=DOMAIN, options={"debug_mode": False})
    quiet_entry.runtime_data = MagicMock(name="quiet")
    unloaded_entry = MockConfigEntry(domain=DOMAIN, options={"debug_mode": True})
    unloaded_entry.runtime_data = None

    debug_entry.add_to_hass(hass)
    quiet_entry.add_to_hass(hass)
    unloaded_entry.add_to_hass(hass)

    coordinators = iter_developer_runtime_coordinators(hass)

    assert coordinators == [debug_entry.runtime_data]
    assert has_debug_mode_runtime_entry(hass) is True
