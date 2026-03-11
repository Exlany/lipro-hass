"""Tests for small runtime support helpers."""

from __future__ import annotations

from custom_components.lipro.core.coordinator.runtime.device.batch_optimizer import (
    DeviceBatchOptimizer,
)


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
