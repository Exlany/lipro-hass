"""Snapshot coverage for the composed coordinator facade."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.coordinator_v2 import CoordinatorV2


def test_coordinator_v2_snapshot(snapshot: SnapshotAssertion) -> None:
    legacy = MagicMock()
    legacy.state_service = MagicMock(devices={"dev1": MagicMock()})
    legacy.command_service = MagicMock(last_failure=None)
    legacy.device_refresh_service = MagicMock()
    legacy.mqtt_service = MagicMock(connected=True)
    legacy.client = MagicMock()
    legacy.update_interval = timedelta(seconds=30)
    legacy.last_update_success = True
    legacy.async_request_refresh = MagicMock()
    legacy.async_config_entry_first_refresh = MagicMock()
    legacy.async_shutdown = MagicMock()
    legacy.async_update_listeners = MagicMock()
    legacy.register_entity = MagicMock()
    legacy.unregister_entity = MagicMock()
    legacy.build_developer_report = MagicMock(return_value={"ok": True})

    coordinator = CoordinatorV2.from_legacy(legacy)

    update_interval = coordinator.update_interval
    assert update_interval is not None

    data = {
        "devices": sorted(coordinator.devices.keys()),
        "mqtt_connected": coordinator.mqtt_connected,
        "has_client": coordinator.client is legacy.client,
        "update_interval_seconds": int(update_interval.total_seconds()),
        "last_update_success": coordinator.last_update_success,
    }

    assert data == snapshot
