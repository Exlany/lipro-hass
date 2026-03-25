"""Tests for Lipro system health callbacks."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN, VERSION
from custom_components.lipro.control.runtime_access import get_entry_runtime_coordinator
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
            mqtt_service=SimpleNamespace(connected=True),
        ),
    )
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d3": object()},
            last_update_success=False,
            mqtt_service=SimpleNamespace(connected=False),
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
async def test_system_health_info_surfaces_failure_entries_from_telemetry(hass) -> None:
    """System health should expose normalized failure summaries when available."""
    entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
    entry.add_to_hass(hass)
    entry.runtime_data = SimpleNamespace(
        protocol=SimpleNamespace(
            protocol_diagnostics_snapshot=lambda: {
                "entry_id": entry.entry_id,
                "telemetry": {"mqtt_last_error_type": "TimeoutError"},
            }
        ),
        telemetry_service=SimpleNamespace(
            build_snapshot=lambda: {
                "device_count": 1,
                "last_update_success": False,
                "mqtt": {
                    "connected": False,
                    "last_transport_error": "RuntimeError",
                },
            }
        ),
        devices={"d1": object()},
        last_update_success=False,
        mqtt_service=SimpleNamespace(connected=False),
    )

    result = await system_health_info(hass)

    failure_entry = result["failure_entries"][0]

    assert failure_entry["entry_ref"].startswith("entry_")
    assert set(failure_entry) == {
        "entry_ref",
        "failure_category",
        "failure_origin",
        "handling_policy",
        "error_type",
    }
    assert result["failure_entries"] == [
        {
            "entry_ref": failure_entry["entry_ref"],
            "failure_category": "network",
            "failure_origin": "protocol.mqtt",
            "handling_policy": "retry",
            "error_type": "TimeoutError",
        }
    ]


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
            mqtt_service=SimpleNamespace(connected=True),
        ),
    )
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object(), "d2": object()},
            last_update_success=False,
            mqtt_service=SimpleNamespace(connected=False),
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
            mqtt_service=SimpleNamespace(connected=True),
        ),
    )
    _add_runtime_entry(
        hass,
        phone="13900000000",
        runtime_data=SimpleNamespace(
            devices={"d1": object()},
            last_update_success=False,
            mqtt_service=SimpleNamespace(connected=False),
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
            mqtt_service=SimpleNamespace(connected="true"),
        ),
    )

    result = await system_health_info(hass)

    assert "mqtt_connected_entries" not in result


@pytest.mark.asyncio
async def test_system_health_info_ignores_probe_only_entries() -> None:
    """System health should only count entries that satisfy the formal runtime port."""

    class ProbeOnlyEntry:
        def __getattr__(self, name: str) -> object:
            return {
                "entry_id": "ghost-entry",
                "options": {},
                "runtime_data": SimpleNamespace(),
            }[name]

    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [
        ProbeOnlyEntry(),
        SimpleNamespace(
            entry_id="entry-1",
            options={},
            runtime_data=SimpleNamespace(
                devices={"d1": object()},
                last_update_success=True,
                mqtt_service=SimpleNamespace(connected=True),
            ),
        ),
    ]

    result = await system_health_info(hass)

    assert result["logged_accounts"] == 1
    assert result["total_devices"] == 1
    assert result["mqtt_connected_entries"] == 1


def test_runtime_access_rejects_partial_foreign_entry() -> None:
    """Runtime access should ignore foreign objects lacking formal entry shape."""
    from custom_components.lipro.control.runtime_access import (
        get_entry_runtime_coordinator,
        is_debug_mode_enabled_for_entry,
    )

    coordinator = SimpleNamespace(devices={}, last_update_success=True)
    entry = SimpleNamespace(runtime_data=coordinator)

    assert get_entry_runtime_coordinator(entry) is None
    assert is_debug_mode_enabled_for_entry(entry) is False
    assert not hasattr(entry, "entry_id")
    assert not hasattr(entry, "options")


def test_runtime_access_rejects_magicmock_runtime_ghost() -> None:
    """Runtime access should ignore implicit MagicMock runtime_data ghosts."""
    entry = MagicMock()
    entry.entry_id = "entry-1"
    entry.options = {}

    assert get_entry_runtime_coordinator(entry) is None
