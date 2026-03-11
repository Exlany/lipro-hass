"""Tests for outlet power runtime helper edge branches."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, Mock, call

import pytest

from custom_components.lipro.core.api import LiproApiError
from custom_components.lipro.core.coordinator.runtime.outlet_power_runtime import (
    _normalize_device_id,
    _normalize_single_outlet_power_payload,
    query_outlet_power,
    query_single_outlet_power,
    resolve_outlet_power_cycle_size,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(*, name: str = "Test Outlet") -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial="outlet",
        name=name,
        device_type=1,
        iot_name="lipro_outlet",
        physical_model="outlet",
        is_group=False,
        properties={"powerState": "1"},
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


def test_normalize_device_id_and_single_payload_handle_invalid_shapes() -> None:
    assert _normalize_device_id(None) is None
    assert _normalize_device_id("   ") is None
    assert _normalize_device_id("  ABC  ") == "abc"

    assert _normalize_single_outlet_power_payload({"abc": {"nowPower": 1}}, requested_id="ABC") == {
        "nowPower": 1
    }
    assert _normalize_single_outlet_power_payload([{"nowPower": 1}, {"nowPower": 2}], requested_id="abc") == {
        "data": [{"nowPower": 1}, {"nowPower": 2}]
    }
    assert _normalize_single_outlet_power_payload(["bad-row"], requested_id="abc") is None
    assert _normalize_single_outlet_power_payload("bad", requested_id="abc") is None
    assert _normalize_single_outlet_power_payload({}, requested_id="   ") is None


def test_resolve_outlet_power_cycle_size_handles_zero_and_dynamic_limits() -> None:
    assert (
        resolve_outlet_power_cycle_size(
            0,
            max_devices_per_cycle=10,
            target_full_cycle_count=3,
        )
        == 0
    )
    assert (
        resolve_outlet_power_cycle_size(
            3,
            max_devices_per_cycle=10,
            target_full_cycle_count=3,
        )
        == 3
    )
    assert (
        resolve_outlet_power_cycle_size(
            20,
            max_devices_per_cycle=10,
            target_full_cycle_count=4,
        )
        == 5
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
    device = _make_device(name="Test Outlet")

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
    device = _make_device(name="Test Outlet")

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
    device = _make_device(name="Test Outlet")

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


@pytest.mark.asyncio
async def test_query_single_outlet_power_ignores_invalid_device_id() -> None:
    fetch = AsyncMock()

    await query_single_outlet_power(
        device_id="   ",
        fetch_outlet_power_info=fetch,
        get_device_by_id=lambda _device_id: None,
        apply_outlet_power_info=lambda _device, _payload: False,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=Mock(),
    )

    fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_query_single_outlet_power_logs_successful_apply() -> None:
    logger = Mock()
    device = _make_device(name="Desk Outlet")

    await query_single_outlet_power(
        device_id="ABC",
        fetch_outlet_power_info=AsyncMock(return_value={"nowPower": 1.2}),
        get_device_by_id=lambda _device_id: device,
        apply_outlet_power_info=lambda _device, _payload: True,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logger,
    )

    logger.debug.assert_called_once()


@pytest.mark.asyncio
async def test_query_single_outlet_power_swallows_non_retryable_api_errors() -> None:
    logger = Mock()

    await query_single_outlet_power(
        device_id="abc",
        fetch_outlet_power_info=AsyncMock(side_effect=LiproApiError("boom", 500)),
        get_device_by_id=lambda _device_id: None,
        apply_outlet_power_info=lambda _device, _payload: False,
        should_reraise_outlet_power_error=lambda _err: False,
        logger=logger,
    )

    logger.debug.assert_called_once()


@pytest.mark.asyncio
async def test_query_single_outlet_power_reraises_retryable_api_errors() -> None:
    with pytest.raises(LiproApiError, match="boom"):
        await query_single_outlet_power(
            device_id="abc",
            fetch_outlet_power_info=AsyncMock(side_effect=LiproApiError("boom", 401)),
            get_device_by_id=lambda _device_id: None,
            apply_outlet_power_info=lambda _device, _payload: False,
            should_reraise_outlet_power_error=lambda _err: True,
            logger=Mock(),
        )
