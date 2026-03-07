"""Tests for outlet power runtime helper edge branches."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, call

import pytest

from custom_components.lipro.core.coordinator.runtime.outlet_power_runtime import (
    query_outlet_power,
    resolve_outlet_power_cycle_size,
)


def test_resolve_outlet_power_cycle_size_returns_static_limit_when_target_non_positive() -> (
    None
):
    assert (
        resolve_outlet_power_cycle_size(
            20,
            max_devices_per_cycle=10,
            target_full_cycle_count=0,
        )
        == 10
    )


@pytest.mark.asyncio
async def test_query_outlet_power_returns_index_when_no_outlet_ids() -> None:
    fetch = AsyncMock()

    updated = await query_outlet_power(
        outlet_ids_to_query=[],
        round_robin_index=7,
        resolve_cycle_size=lambda _: 3,
        fetch_outlet_power_info=fetch,
        get_device_by_id=lambda _device_id: None,
        apply_outlet_power_info=lambda _device, _payload: False,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logging.getLogger(__name__),
        concurrency=2,
    )

    assert updated == 7
    fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_query_outlet_power_returns_index_when_truthy_iterable_expands_empty() -> (
    None
):
    class _TruthyEmptyIterable:
        def __bool__(self) -> bool:
            return True

        def __iter__(self):
            return iter(())

    fetch = AsyncMock()

    updated = await query_outlet_power(
        outlet_ids_to_query=_TruthyEmptyIterable(),  # type: ignore[arg-type]
        round_robin_index=11,
        resolve_cycle_size=lambda _: 3,
        fetch_outlet_power_info=fetch,
        get_device_by_id=lambda _device_id: None,
        apply_outlet_power_info=lambda _device, _payload: False,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logging.getLogger(__name__),
        concurrency=2,
    )

    assert updated == 11
    fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_query_outlet_power_wraps_slice_when_round_robin_crosses_tail() -> None:
    fetch = AsyncMock(
        side_effect=[
            {"nowPower": 1},
            {"nowPower": 2},
            {"nowPower": 3},
        ]
    )
    device = SimpleNamespace(name="Test Outlet")

    updated = await query_outlet_power(
        outlet_ids_to_query=["a", "b", "c", "d", "e"],
        round_robin_index=4,
        resolve_cycle_size=lambda _: 3,
        fetch_outlet_power_info=fetch,
        get_device_by_id=lambda _device_id: device,
        apply_outlet_power_info=lambda _device, _payload: True,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logging.getLogger(__name__),
        concurrency=1,
    )

    assert updated == 2
    assert fetch.await_args_list == [call("e"), call("a"), call("b")]


@pytest.mark.asyncio
async def test_query_outlet_power_queries_each_selected_device_individually() -> None:
    fetch = AsyncMock(
        side_effect=[
            {"nowPower": 1.0},
            {"nowPower": 2.0},
        ]
    )
    device = SimpleNamespace(name="Test Outlet")

    await query_outlet_power(
        outlet_ids_to_query=["a", "b"],
        round_robin_index=0,
        resolve_cycle_size=lambda _: 2,
        fetch_outlet_power_info=fetch,
        get_device_by_id=lambda _device_id: device,
        apply_outlet_power_info=lambda _device, _payload: True,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logging.getLogger(__name__),
        concurrency=1,
    )

    assert fetch.await_args_list == [call("a"), call("b")]


@pytest.mark.asyncio
async def test_query_outlet_power_accepts_single_payload_nested_by_device_id() -> None:
    fetch = AsyncMock(return_value={"a": {"nowPower": 1.0}})
    device = SimpleNamespace(name="Test Outlet")

    await query_outlet_power(
        outlet_ids_to_query=["a"],
        round_robin_index=0,
        resolve_cycle_size=lambda _: 1,
        fetch_outlet_power_info=fetch,
        get_device_by_id=lambda _device_id: device,
        apply_outlet_power_info=lambda _device, _payload: True,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logging.getLogger(__name__),
        concurrency=1,
    )

    fetch.assert_awaited_once_with("a")
