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
from tests.helpers.service_call import service_call


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
            "lifecycle_contract": "setup_failed",
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
    assert not hasattr(snapshot, "lifecycle_contract")


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


def test_iter_runtime_entry_coordinators_preserves_entry_coordinator_pairs(hass) -> None:
    from custom_components.lipro.control.runtime_access import (
        iter_runtime_entry_coordinators,
    )

    entry = MockConfigEntry(domain=DOMAIN, options={})
    coordinator = MagicMock(name="runtime")
    entry.runtime_data = coordinator
    entry.add_to_hass(hass)

    assert iter_runtime_entry_coordinators(hass) == [(entry, coordinator)]


def test_find_runtime_device_ignores_magicmock_ghost_lookup_and_uses_mapping() -> None:
    from custom_components.lipro.control.runtime_access import find_runtime_device

    device = MagicMock(name="device")
    coordinator = MagicMock()
    coordinator.devices = {"03ab0000000000a1": device}

    assert find_runtime_device(coordinator, "03ab0000000000a1") is device


def test_find_runtime_device_and_coordinator_prefers_formal_lookup_helpers(hass) -> None:
    from custom_components.lipro.control.runtime_access import (
        find_runtime_device_and_coordinator,
    )

    device = MagicMock(name="device")
    entry = MockConfigEntry(domain=DOMAIN, options={})
    coordinator = MagicMock(name="runtime")
    coordinator.get_device = MagicMock(return_value=None)
    coordinator.get_device_by_id = MagicMock(return_value=device)
    coordinator.devices = {}
    entry.runtime_data = coordinator
    entry.add_to_hass(hass)

    assert find_runtime_device_and_coordinator(hass, device_id="alias") == (
        device,
        coordinator,
    )
    coordinator.get_device.assert_called_once_with("alias")
    coordinator.get_device_by_id.assert_called_once_with("alias")


@pytest.mark.asyncio
async def test_service_router_support_resolves_device_via_service_and_runtime_bridges(
    hass,
) -> None:
    import re

    from custom_components.lipro.control.service_router_support import (
        async_get_device_and_coordinator,
    )

    call = service_call(hass, {})
    serial_pattern = re.compile(r"03ab[0-9a-f]{12}", re.IGNORECASE)
    device = MagicMock(name="device")
    coordinator = MagicMock(name="runtime")

    with patch(
        "custom_components.lipro.control.service_router_support.resolve_device_id_from_service_call",
        return_value="03ab0000000000a1",
    ) as resolve_device_id, patch(
        "custom_components.lipro.control.service_router_support.find_runtime_device_and_coordinator",
        return_value=(device, coordinator),
    ) as runtime_lookup:
        resolved = await async_get_device_and_coordinator(
            hass,
            call,
            domain=DOMAIN,
            serial_pattern=serial_pattern,
            attr_device_id="device_id",
        )

    assert resolved == (device, coordinator)
    resolve_device_id.assert_called_once_with(
        hass,
        call,
        domain=DOMAIN,
        serial_pattern=serial_pattern,
        attr_device_id="device_id",
    )
    runtime_lookup.assert_called_once_with(hass, device_id="03ab0000000000a1")


@pytest.mark.asyncio
async def test_service_router_support_raises_when_runtime_device_is_missing(hass) -> None:
    import re

    from custom_components.lipro.control.service_router_support import (
        async_get_device_and_coordinator,
    )
    from homeassistant.exceptions import ServiceValidationError

    serial_pattern = re.compile(r"03ab[0-9a-f]{12}", re.IGNORECASE)

    with patch(
        "custom_components.lipro.control.service_router_support.resolve_device_id_from_service_call",
        return_value="03ab0000000000a1",
    ), patch(
        "custom_components.lipro.control.service_router_support.find_runtime_device_and_coordinator",
        return_value=None,
    ), pytest.raises(ServiceValidationError) as exc_info:
        await async_get_device_and_coordinator(
            hass,
            service_call(hass, {}),
            domain=DOMAIN,
            serial_pattern=serial_pattern,
            attr_device_id="device_id",
        )

    assert exc_info.value.translation_key == "device_not_found"


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


def test_runtime_diagnostics_projection_exposes_typed_projection() -> None:
    from custom_components.lipro.control.runtime_access import (
        build_runtime_diagnostics_projection,
    )

    coordinator = MagicMock()
    coordinator.last_update_success = False
    coordinator.update_interval = "0:00:30"
    coordinator.devices = {}
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
        projection = build_runtime_diagnostics_projection(entry)

    assert projection is not None
    assert projection.snapshot.entry_ref == "entry_deadbeef"
    assert projection.snapshot.device_count == 5
    assert projection.snapshot.mqtt_connected is True
    assert projection.update_interval == "0:00:30"
    assert projection.degraded_fields == ()
