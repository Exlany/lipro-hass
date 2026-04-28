"""Integration-style tests for the runtime telemetry exporter mainline."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.control.diagnostics_surface import (
    DiagnosticsPayload,
    DiagnosticsValue,
)
from custom_components.lipro.control.telemetry_surface import (
    build_entry_telemetry_views,
)
from custom_components.lipro.diagnostics import async_get_config_entry_diagnostics
from custom_components.lipro.system_health import system_health_info


def _diag_payload(value: DiagnosticsValue) -> DiagnosticsPayload:
    assert isinstance(value, dict)
    return value


def _diag_list(value: DiagnosticsValue) -> list[DiagnosticsValue]:
    assert isinstance(value, list)
    return value


def _diag_str(value: DiagnosticsValue) -> str:
    assert isinstance(value, str)
    return value


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
        protocol=SimpleNamespace(
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
    coordinator_view = _diag_payload(diagnostics["coordinator"])
    telemetry_view = _diag_payload(diagnostics["telemetry"])
    protocol_view = _diag_payload(telemetry_view["protocol"])
    auth_recovery_view = _diag_payload(protocol_view["auth_recovery"])
    runtime_view = _diag_payload(telemetry_view["runtime"])
    command_view = _diag_payload(runtime_view["command"])
    confirmation_view = _diag_payload(command_view["confirmation"])
    recent_command_traces = _diag_list(runtime_view["recent_command_traces"])
    first_command_trace = _diag_payload(recent_command_traces[0])

    assert coordinator_view["device_count"] == 2
    assert coordinator_view["mqtt_connected"] is True
    assert auth_recovery_view["refresh_success_count"] == 2
    assert confirmation_view["avg_latency_seconds"] == 1.25
    assert _diag_str(first_command_trace["device_ref"]).startswith("device_")
    assert "password_hash" not in first_command_trace
    assert views.system_health["device_count"] == 2
    assert views.system_health["command_confirmation_timeout_total"] == 1
    assert views.system_health["refresh_avg_latency_seconds"] == 1.75
    assert views.system_health["failure_summary"] == {
        "failure_category": "network",
        "failure_origin": "protocol.mqtt",
        "handling_policy": "retry",
        "error_type": "TimeoutError",
    }
    assert coordinator_view["failure_summary"] == views.system_health["failure_summary"]
    assert health["total_devices"] == 2
    assert health["mqtt_connected_entries"] == 1
    failure_entry = health["failure_entries"][0]
    assert failure_entry["entry_ref"].startswith("entry_")
    assert {
        key: value for key, value in failure_entry.items() if key != "entry_ref"
    } == (views.system_health["failure_summary"])


@pytest.mark.asyncio
async def test_entry_runtime_telemetry_exporter_requires_protocol_surface(
    hass,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Lipro (13800000000)",
        data={"phone": "13800000000"},
    )
    entry.add_to_hass(hass)
    entry.runtime_data = SimpleNamespace(
        client=SimpleNamespace(
            protocol_diagnostics_snapshot=lambda: {"entry_id": entry.entry_id}
        ),
        telemetry_service=SimpleNamespace(
            build_snapshot=lambda: {"device_count": 0, "last_update_success": True}
        ),
        devices={},
        last_update_success=True,
        update_interval=timedelta(seconds=30),
        mqtt_service=SimpleNamespace(connected=True),
    )

    assert build_entry_telemetry_views(entry) is None
    health = await system_health_info(hass)

    assert health["logged_accounts"] == 1
    assert "failure_entries" not in health


def test_runtime_telemetry_exporter_summarizes_long_redacted_strings() -> None:
    from custom_components.lipro.core.telemetry.exporter import RuntimeTelemetryExporter

    exporter = RuntimeTelemetryExporter(
        protocol_source=SimpleNamespace(
            get_protocol_telemetry_snapshot=lambda: {"entry_id": "entry-1"}
        ),
        runtime_source=SimpleNamespace(
            get_runtime_telemetry_snapshot=lambda: {
                "note": (
                    "prefix-" * 60
                    + "Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789 "
                    + "device=03ab5ccd7c123456 ip=10.0.0.8"
                )
            }
        ),
        report_id_factory=lambda *_args: "report-1",
    )

    snapshot = exporter.export_snapshot()

    note = _diag_str(snapshot.runtime["note"])
    assert "abcdefghijklmnopqrstuvwxyz0123456789" not in note
    assert "03ab5ccd7c123456" not in note
    assert "10.0.0.8" not in note
    assert "[TOKEN]" in note
    assert "[DEVICE_ID]" in note
    assert "[IP]" in note
    assert len(note) <= 256
