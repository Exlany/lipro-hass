"""Tests for small runtime support helpers."""

from __future__ import annotations

from unittest.mock import Mock

from custom_components.lipro.core.coordinator.runtime.device.batch_optimizer import (
    DeviceBatchOptimizer,
)
from custom_components.lipro.core.coordinator.runtime.shared_state import (
    CoordinatorSharedState,
)


def test_coordinator_shared_state_builds_new_snapshots_and_exports_diagnostics() -> None:
    device = Mock()
    initial = CoordinatorSharedState()

    updated = (
        initial.with_devices({"device-1": device})
        .with_mqtt_connected(True)
        .with_biz_id("biz-1")
        .with_last_refresh_at(123.4)
        .with_polling_interval(15.0)
        .with_command_confirmation_timeout(9.0)
        .with_debug_mode(True)
    )

    assert initial.devices == {}
    assert initial.has_devices is False
    assert updated.get_device("missing") is None
    assert updated.get_device("device-1") is device
    assert updated.get_all_devices() == {"device-1": device}
    assert updated.device_count == 1
    assert updated.has_devices is True
    assert updated.to_diagnostic_dict() == {
        "device_count": 1,
        "mqtt_connected": True,
        "biz_id": "biz-1",
        "last_refresh_at": 123.4,
        "polling_interval": 15.0,
        "command_confirmation_timeout": 9.0,
        "debug_mode": True,
    }


def test_device_batch_optimizer_splits_batches_validates_pages_and_estimates_queries() -> (
    None
):
    optimizer = DeviceBatchOptimizer(max_devices_per_query=2, max_pages=3)

    assert optimizer.split_into_batches([]) == []
    assert optimizer.split_into_batches(["a", "b", "c", "d", "e"]) == [
        ["a", "b"],
        ["c", "d"],
        ["e"],
    ]

    assert optimizer.validate_page_count(3) is True
    assert optimizer.validate_page_count(4) is False

    assert (
        optimizer.estimate_query_count(
            iot_ids=["i1", "i2", "i3"],
            group_ids=["g1"],
            outlet_ids=["o1", "o2"],
        )
        == 4
    )
    assert (
        optimizer.estimate_query_count(iot_ids=[], group_ids=[], outlet_ids=[])
        == 0
    )
