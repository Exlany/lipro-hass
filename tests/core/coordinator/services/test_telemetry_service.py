"""Tests for the coordinator telemetry service."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.coordinator.services.telemetry_service import (
    CoordinatorTelemetryService,
)


def test_telemetry_service_builds_runtime_snapshot() -> None:
    mqtt_service = MagicMock(connected=True)
    command_runtime = MagicMock()
    command_runtime.get_runtime_metrics.return_value = {"trace_count": 2}
    command_runtime.get_recent_traces.return_value = [{"route": "mqtt"}]
    status_runtime = MagicMock()
    status_runtime.get_runtime_metrics.return_value = {"scheduler": {"batch": 1}}
    tuning_runtime = MagicMock()
    tuning_runtime.get_runtime_metrics.return_value = {"metrics": {"latency": 1.2}}
    mqtt_runtime = MagicMock()
    mqtt_runtime.get_runtime_metrics.return_value = {"is_connected": True}

    service = CoordinatorTelemetryService(
        mqtt_service=mqtt_service,
        command_runtime=command_runtime,
        status_runtime=status_runtime,
        tuning_runtime=tuning_runtime,
        mqtt_runtime_getter=lambda: mqtt_runtime,
        device_count_getter=lambda: 3,
        polling_interval_seconds_getter=lambda: 15,
    )

    assert service.build_snapshot() == {
        "device_count": 3,
        "polling_interval_seconds": 15,
        "mqtt": {"connected": True, "is_connected": True},
        "command": {"trace_count": 2},
        "status": {"scheduler": {"batch": 1}},
        "tuning": {"metrics": {"latency": 1.2}},
        "signals": {
            "connect_state_event_count": 0,
            "group_reconciliation_request_count": 0,
            "recent_connect_state_events": [],
            "recent_group_reconciliation_requests": [],
        },
    }
    assert service.get_recent_command_traces() == [{"route": "mqtt"}]


def test_telemetry_service_records_runtime_signal_events() -> None:
    service = CoordinatorTelemetryService(
        mqtt_service=MagicMock(connected=False),
        command_runtime=MagicMock(get_runtime_metrics=MagicMock(return_value={})),
        status_runtime=MagicMock(get_runtime_metrics=MagicMock(return_value={})),
        tuning_runtime=MagicMock(get_runtime_metrics=MagicMock(return_value={})),
        mqtt_runtime_getter=lambda: MagicMock(get_runtime_metrics=MagicMock(return_value={})),
        device_count_getter=lambda: 0,
        polling_interval_seconds_getter=lambda: None,
    )

    service.record_connect_state(device_serial="dev1", timestamp=1.5, is_online=True)
    service.record_group_reconciliation_request(device_name="Group 1", timestamp=2.5)

    assert service.build_snapshot()["signals"] == {
        "connect_state_event_count": 1,
        "group_reconciliation_request_count": 1,
        "recent_connect_state_events": [
            {"device_serial": "dev1", "timestamp": 1.5, "is_online": True}
        ],
        "recent_group_reconciliation_requests": [
            {"device_name": "Group 1", "timestamp": 2.5}
        ],
    }
