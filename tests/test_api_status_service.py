"""Tests for API status service helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api.status_service import (
    query_connect_status,
    query_device_status,
    query_with_fallback,
)


class DummyApiError(Exception):
    """Test-only API error with optional code field."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


@pytest.mark.asyncio
async def test_query_with_fallback_non_retriable_raises() -> None:
    iot_request = AsyncMock(side_effect=DummyApiError("fatal", 500))

    with pytest.raises(DummyApiError, match="fatal"):
        await query_with_fallback(
            path="/v2/status/device",
            body_key="deviceIdList",
            ids=["03ab5ccd7caaaaaa"],
            item_name="device",
            iot_request=iot_request,
            extract_data_list=lambda result: result.get("data", []),
            is_retriable_device_error=lambda _: False,
            lipro_api_error=DummyApiError,
            normalize_response_code=lambda code: code,
            expected_offline_codes=(140003, "140003"),
            logger=MagicMock(),
        )


@pytest.mark.asyncio
async def test_query_with_fallback_retriable_returns_partial_results() -> None:
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("offline", 140003),
            DummyApiError("single fail", 500),
            {"data": [{"deviceId": "03ab5ccd7cbbbbbb"}]},
        ]
    )

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=["03ab5ccd7caaaaaa", "03ab5ccd7cbbbbbb"],
        item_name="device",
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: True,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
    )

    assert result == [{"deviceId": "03ab5ccd7cbbbbbb"}]


@pytest.mark.asyncio
async def test_query_device_status_splits_batches() -> None:
    iot_request = AsyncMock(return_value={"data": [{"ok": True}]})

    result = await query_device_status(
        device_ids=["a", "b", "c"],
        max_devices_per_query=2,
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: False,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        path_query_device_status="/v2/status/device",
    )

    assert result == [{"ok": True}, {"ok": True}]
    assert iot_request.await_count == 2


@pytest.mark.asyncio
async def test_query_device_status_applies_adaptive_soft_batch_limit() -> None:
    iot_request = AsyncMock(return_value={"data": [{"ok": True}]})
    device_ids = [f"d{i}" for i in range(130)]

    result = await query_device_status(
        device_ids=device_ids,
        max_devices_per_query=100,
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: False,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        path_query_device_status="/v2/status/device",
    )

    assert result == [{"ok": True}, {"ok": True}, {"ok": True}]
    assert iot_request.await_count == 3
    called_batches = [
        call.args[1]["deviceIdList"] for call in iot_request.await_args_list
    ]
    assert len(called_batches[0]) == 64
    assert len(called_batches[1]) == 64
    assert len(called_batches[2]) == 2


@pytest.mark.asyncio
async def test_query_connect_status_handles_wrapped_payload() -> None:
    result = await query_connect_status(
        device_ids=["03ab5ccd7caaaaaa"],
        sanitize_iot_device_ids=lambda device_ids, endpoint: device_ids,
        iot_request=AsyncMock(return_value={"code": "0000", "data": {"03ab": "1"}}),
        coerce_connect_status=lambda value: str(value) == "1",
        lipro_api_error=DummyApiError,
        logger=MagicMock(),
        path_query_connect_status="/v2/status/connect",
    )

    assert result == {"03ab": True}


@pytest.mark.asyncio
async def test_query_with_fallback_small_subset_uses_batch_then_single_fallback() -> (
    None
):
    """Small subsets should try multi-device batches before per-device fallback."""
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("batch fail", 140003),
            DummyApiError("mini batch fail", 140003),
            DummyApiError("single a fail", 140003),
            {"data": [{"deviceId": "b"}]},
            {"data": [{"deviceId": "c"}, {"deviceId": "d"}]},
        ]
    )

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=["a", "b", "c", "d"],
        item_name="device",
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: True,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
    )

    assert result == [{"deviceId": "b"}, {"deviceId": "c"}, {"deviceId": "d"}]
    # 1 initial batch + 1 mini-batch + 2 single fallback + 1 mini-batch success
    assert iot_request.await_count == 5
    called_bodies = [
        call.args[1]["deviceIdList"] for call in iot_request.await_args_list
    ]
    assert ["a", "b", "c", "d"] in called_bodies
    assert ["a", "b"] in called_bodies
    assert ["c", "d"] in called_bodies


@pytest.mark.asyncio
async def test_query_with_fallback_large_batch_does_not_retry_same_full_batch() -> None:
    ids = ["a", "b", "c", "d", "e", "f"]
    recorded_depth: list[int] = []

    async def _request(_path, body):
        batch = body["deviceIdList"]
        if batch == ids:
            raise DummyApiError("batch fail", 140003)
        return {"data": [{"deviceId": item_id} for item_id in batch]}

    iot_request = AsyncMock(side_effect=_request)

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=ids,
        item_name="device",
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: True,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        record_fallback_depth=recorded_depth.append,
    )

    assert sorted(item["deviceId"] for item in result) == ids
    # 1 initial full-batch failure + 2 sub-batches (size=3) split into mini-batches
    assert iot_request.await_count == 5
    called_bodies = [
        call.args[1]["deviceIdList"] for call in iot_request.await_args_list
    ]
    assert called_bodies.count(ids) == 1
    assert recorded_depth == [2]


@pytest.mark.asyncio
async def test_query_device_status_reports_batch_metrics_with_fallback_depth() -> None:
    metrics: list[tuple[int, float, int]] = []
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("batch fail", 140003),
            {"data": [{"deviceId": "a"}]},
            {"data": [{"deviceId": "b"}]},
        ]
    )

    result = await query_device_status(
        device_ids=["a", "b"],
        max_devices_per_query=2,
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: True,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        path_query_device_status="/v2/status/device",
        on_batch_metric=lambda size, duration, depth: metrics.append(
            (size, duration, depth)
        ),
    )

    assert result == [{"deviceId": "a"}, {"deviceId": "b"}]
    assert len(metrics) == 1
    assert metrics[0][0] == 2
    assert metrics[0][1] >= 0.0
    assert metrics[0][2] == 1
