"""Tests for Lipro system health callbacks."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const import DOMAIN, VERSION
from custom_components.lipro.system_health import async_register, system_health_info


def _add_runtime_entry(
    hass,
    *,
    phone: str,
    runtime_data: object | None,
) -> MockConfigEntry:
    """Attach one Lipro config entry with optional runtime coordinator."""
    entry = MockConfigEntry(domain=DOMAIN, data={"phone": phone})
    entry.add_to_hass(hass)
    entry.runtime_data = runtime_data
    return entry


@pytest.mark.asyncio
async def test_async_register_registers_system_health_callback(hass) -> None:
    """async_register should register the system health info callback."""
    register = MagicMock()

    await async_register(hass, register)

    register.async_register_info.assert_called_once_with(system_health_info)


@pytest.mark.asyncio
async def test_system_health_info_aggregates_entries(hass) -> None:
    """System health payload should aggregate runtime coordinator statistics."""
    _add_runtime_entry(
        hass,
        phone="13800000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object(), "d2": object()},
            last_update_success=True,
            mqtt_connected=True,
        ),
    )
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d3": object()},
            last_update_success=False,
            mqtt_connected=False,
        ),
    )

    result = await system_health_info(hass)

    assert result == {
        "component_version": VERSION,
        "can_reach_server": True,
        "logged_accounts": 2,
        "total_devices": 3,
        "mqtt_connected_entries": 1,
    }


@pytest.mark.asyncio
async def test_system_health_info_omits_mqtt_count_when_unavailable(hass) -> None:
    """mqtt_connected_entries should be omitted when runtime has no mqtt field."""
    _add_runtime_entry(hass, phone="13800000000", runtime_data=None)
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object()},
            last_update_success=False,
        ),
    )

    result = await system_health_info(hass)

    assert result["component_version"] == VERSION
    assert result["can_reach_server"] is False
    assert result["logged_accounts"] == 2
    assert result["total_devices"] == 1
    assert "mqtt_connected_entries" not in result


@pytest.mark.asyncio
async def test_system_health_info_without_entries(hass) -> None:
    """System health payload should still be valid without config entries."""
    result = await system_health_info(hass)

    assert result == {
        "component_version": VERSION,
        "can_reach_server": False,
        "logged_accounts": 0,
        "total_devices": 0,
    }


@pytest.mark.asyncio
async def test_system_health_info_skips_non_sized_devices(hass) -> None:
    """Non-sized coordinator devices should be ignored for total_devices."""
    _add_runtime_entry(
        hass,
        phone="13800000000",
        runtime_data=SimpleNamespace(
            devices=123,
            last_update_success=True,
            mqtt_connected=True,
        ),
    )
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object(), "d2": object()},
            last_update_success=False,
            mqtt_connected=False,
        ),
    )

    result = await system_health_info(hass)

    assert result["total_devices"] == 2
    assert result["mqtt_connected_entries"] == 1
    assert result["can_reach_server"] is True


@pytest.mark.asyncio
async def test_system_health_info_skips_none_devices_field(hass) -> None:
    """Coordinators with devices=None should be ignored for total_devices."""
    _add_runtime_entry(
        hass,
        phone="13800000000",
        runtime_data=SimpleNamespace(
            devices=None,
            last_update_success=True,
            mqtt_connected=True,
        ),
    )
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object()},
            last_update_success=False,
            mqtt_connected=False,
        ),
    )

    result = await system_health_info(hass)

    assert result["total_devices"] == 1
    assert result["mqtt_connected_entries"] == 1
    assert result["can_reach_server"] is True


@pytest.mark.asyncio
async def test_system_health_info_omits_mqtt_count_when_mqtt_connected_is_non_bool(
    hass,
) -> None:
    """Non-bool mqtt_connected values should not produce mqtt_connected_entries."""
    _add_runtime_entry(
        hass,
        phone="13800000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object()},
            last_update_success=True,
            mqtt_connected="true",
        ),
    )

    result = await system_health_info(hass)

    assert "mqtt_connected_entries" not in result
