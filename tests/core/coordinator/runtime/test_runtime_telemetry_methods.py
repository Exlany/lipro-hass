"""Tests for lightweight runtime telemetry helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.lipro.core.coordinator.runtime.command_runtime import (
    CommandRuntime,
)
from custom_components.lipro.core.coordinator.runtime.mqtt_runtime import MqttRuntime


class _DeviceResolver:
    def get_device_by_id(self, device_id: str):
        return None


class _ListenerNotifier:
    def schedule_listener_update(self) -> None:
        return None


class _ConnectStateTracker:
    def record_connect_state(self, device_serial: str, timestamp: float, is_online: bool) -> None:
        return None


class _GroupReconciler:
    def schedule_group_reconciliation(self, device_name: str, timestamp: float) -> None:
        return None


def test_command_runtime_exposes_recent_traces_and_metrics() -> None:
    runtime = CommandRuntime(
        builder=MagicMock(),
        sender=MagicMock(),
        retry=MagicMock(),
        confirmation=MagicMock(),
        trigger_reauth=AsyncMock(),
        debug_mode=True,
    )

    runtime._record_trace({"route": "rest"})
    runtime._record_trace({"route": "mqtt"})

    assert runtime.get_recent_traces() == [{"route": "mqtt"}, {"route": "rest"}]
    assert runtime.get_recent_traces(limit=1) == [{"route": "mqtt"}]
    assert runtime.get_runtime_metrics() == {
        "debug_enabled": True,
        "trace_count": 2,
        "last_failure": None,
        "confirmation": {},
    }


def test_mqtt_runtime_exposes_runtime_metrics() -> None:
    runtime = MqttRuntime(
        hass=MagicMock(),
        mqtt_transport=None,
        base_scan_interval=15,
        polling_updater=MagicMock(),
        device_resolver=_DeviceResolver(),
        property_applier=AsyncMock(return_value=False),
        listener_notifier=_ListenerNotifier(),
        connect_state_tracker=_ConnectStateTracker(),
        group_reconciler=_GroupReconciler(),
    )

    runtime.handle_transport_error(RuntimeError("boom"))

    assert runtime.get_runtime_metrics() == {
        "has_transport": False,
        "is_connected": False,
        "disconnect_time": None,
        "disconnect_notified": False,
        "last_transport_error": "RuntimeError",
        "last_transport_error_stage": "transport",
        "failure_summary": {
            "failure_category": "runtime",
            "failure_origin": "runtime.mqtt",
            "handling_policy": "inspect",
            "error_type": "RuntimeError",
        },
        "backoff_gate_logged": False,
    }
