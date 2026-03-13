"""Integration-style tests for the runtime telemetry exporter mainline."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.control.telemetry_surface import (
    build_entry_telemetry_views,
)
from custom_components.lipro.diagnostics import async_get_config_entry_diagnostics
from custom_components.lipro.system_health import system_health_info


@pytest.mark.asyncio
async def test_entry_runtime_bridges_to_exporter_diagnostics_and_system_health(
    hass,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
        data={"phone": "13800000000"},
    )
    entry.add_to_hass(hass)

    protocol_snapshot = {
        "entry_id": entry.entry_id,
        "session": {
            "entry_id": entry.entry_id,
            "access_token_present": True,
            "refresh_token_present": False,
            "request_timeout": 30,
        },
        "telemetry": {
            "mqtt_last_error_type": "TimeoutError",
        },
        "auth_recovery": {
            "refresh_success_count": 2,
            "refresh_failure_count": 1,
            "last_refresh_outcome": "success",
        },
    }
    runtime_snapshot = {
        "device_count": 2,
        "polling_interval_seconds": 30,
        "last_update_success": True,
        "mqtt": {
            "connected": True,
            "disconnect_notified": False,
            "last_transport_error": "RuntimeError",
        },
        "command": {
            "trace_count": 3,
            "confirmation": {
                "avg_latency_seconds": 1.25,
                "timeout_total": 1,
            },
        },
        "tuning": {
            "metrics": {
                "avg_latency": 1.75,
            }
        },
        "signals": {
            "connect_state_event_count": 2,
            "group_reconciliation_request_count": 1,
            "recent_connect_state_events": [
                {
                    "device_serial": "03ab5ccd7c111111",
                    "timestamp": 100.0,
                    "is_online": True,
                }
            ],
            "recent_group_reconciliation_requests": [
                {
                    "device_name": "Bedroom",
                    "timestamp": 101.0,
                }
            ],
        },
        "recent_command_traces": [
            {
                "device_id": "03ab5ccd7c999999",
                "route": "mqtt",
                "password_hash": "should-not-leak",
            }
        ],
    }
    coordinator = SimpleNamespace(
        client=SimpleNamespace(
            protocol_diagnostics_snapshot=lambda: protocol_snapshot,
        ),
        telemetry_service=SimpleNamespace(build_snapshot=lambda: runtime_snapshot),
        devices={},
        last_update_success=True,
        update_interval=timedelta(seconds=30),
        mqtt_service=SimpleNamespace(connected=True),
    )
    entry.runtime_data = coordinator

    share_manager = MagicMock()
    share_manager.is_enabled = True
    share_manager.pending_count = (0, 0)

    with patch(
        "custom_components.lipro.diagnostics.get_anonymous_share_manager",
        return_value=share_manager,
    ):
        diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    health = await system_health_info(hass)
    views = build_entry_telemetry_views(entry)

    assert views is not None
    assert diagnostics["coordinator"]["device_count"] == 2
    assert diagnostics["coordinator"]["mqtt_connected"] is True
    assert diagnostics["telemetry"]["protocol"]["auth_recovery"]["refresh_success_count"] == 2
    assert (
        diagnostics["telemetry"]["runtime"]["command"]["confirmation"][
            "avg_latency_seconds"
        ]
        == 1.25
    )
    assert (
        diagnostics["telemetry"]["runtime"]["recent_command_traces"][0]["device_ref"]
        .startswith("device_")
    )
    assert "password_hash" not in diagnostics["telemetry"]["runtime"]["recent_command_traces"][0]
    assert views.system_health["device_count"] == 2
    assert views.system_health["command_confirmation_timeout_total"] == 1
    assert views.system_health["refresh_avg_latency_seconds"] == 1.75
    assert health["total_devices"] == 2
    assert health["mqtt_connected_entries"] == 1
