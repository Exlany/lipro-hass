"""Fallback-focused API status service assertions."""

from __future__ import annotations

from typing import cast
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import status_fallback as status_fallback_module
from custom_components.lipro.core.api.status_fallback import (
    _query_items_by_binary_split,
    _resolve_device_status_batch_size,
    query_with_fallback,
)
from custom_components.lipro.core.api.types import JsonObject


class _DummyApiError(Exception):
    """Test-only API error with optional code field."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


def _json_object(payload: object) -> JsonObject:
    assert isinstance(payload, dict)
    return cast(JsonObject, payload)


def _extract_rows(payload: object) -> list[JsonObject]:
    if isinstance(payload, list):
        return [cast(JsonObject, row) for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        rows = payload.get("data")
        if isinstance(rows, list):
            return [cast(JsonObject, row) for row in rows if isinstance(row, dict)]
    return []


def _normalize_response_code(code: object) -> str | int | None:
    if isinstance(code, bool):
        return None
    if isinstance(code, (str, int)):
        return code
    return None


def _payload_ids(payload: JsonObject, key: str) -> list[str]:
    value = payload.get(key)
    assert isinstance(value, list)
    assert all(isinstance(item, str) for item in value)
    return [item for item in value if isinstance(item, str)]


def _row_string(row: JsonObject, key: str) -> str:
    value = row.get(key)
    assert isinstance(value, str)
    return value

@pytest.mark.asyncio
async def test_query_with_fallback_non_retriable_raises() -> None:
    iot_request = AsyncMock(side_effect=_DummyApiError("fatal", 500))

    with pytest.raises(_DummyApiError, match="fatal"):
        await query_with_fallback(
            path="/v2/status/device",
            body_key="deviceIdList",
            ids=["03ab5ccd7caaaaaa"],
            item_name="device",
            iot_request=iot_request,
            extract_data_list=_extract_rows,
            is_retriable_device_error=lambda _: False,
            lipro_api_error=_DummyApiError,
            normalize_response_code=_normalize_response_code,
            expected_offline_codes=(140003, "140003"),
            logger=MagicMock(),
        )

@pytest.mark.asyncio
async def test_query_with_fallback_retriable_returns_partial_results() -> None:
    iot_request = AsyncMock(
        side_effect=[
            _DummyApiError("offline", 140003),
            _DummyApiError("single fail", 500),
            {"data": [{"deviceId": "03ab5ccd7cbbbbbb"}]},
        ]
    )

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=["03ab5ccd7caaaaaa", "03ab5ccd7cbbbbbb"],
        item_name="device",
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda _: True,
        lipro_api_error=_DummyApiError,
        normalize_response_code=_normalize_response_code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
    )

    assert result == [{"deviceId": "03ab5ccd7cbbbbbb"}]

@pytest.mark.asyncio
async def test_query_with_fallback_small_subset_uses_batch_then_single_fallback() -> (
    None
):
    """Small subsets should try multi-device batches before per-device fallback."""
    iot_request = AsyncMock(
        side_effect=[
            _DummyApiError("batch fail", 140003),
            _DummyApiError("mini batch fail", 140003),
            _DummyApiError("single a fail", 140003),
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
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda _: True,
        lipro_api_error=_DummyApiError,
        normalize_response_code=_normalize_response_code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
    )

    assert result == [{"deviceId": "b"}, {"deviceId": "c"}, {"deviceId": "d"}]
    # 1 initial batch + 1 mini-batch + 2 single fallback + 1 mini-batch success
    assert iot_request.await_count == 5
    called_bodies = [
        _payload_ids(_json_object(call.args[1]), "deviceIdList")
        for call in iot_request.await_args_list
    ]
    assert ["a", "b", "c", "d"] in called_bodies
    assert ["a", "b"] in called_bodies
    assert ["c", "d"] in called_bodies

@pytest.mark.asyncio
async def test_query_with_fallback_large_batch_does_not_retry_same_full_batch() -> None:
    ids = ["a", "b", "c", "d", "e", "f"]
    recorded_depth: list[int] = []

    async def _request(_path: str, body: JsonObject) -> object:
        batch = _payload_ids(body, "deviceIdList")
        if batch == ids:
            raise _DummyApiError("batch fail", 140003)
        return {"data": [{"deviceId": item_id} for item_id in batch]}

    iot_request = AsyncMock(side_effect=_request)

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=ids,
        item_name="device",
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda _: True,
        lipro_api_error=_DummyApiError,
        normalize_response_code=_normalize_response_code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        record_fallback_depth=recorded_depth.append,
    )

    assert sorted(_row_string(item, "deviceId") for item in result) == ids
    # 1 initial full-batch failure + 2 sub-batches (size=3) split into mini-batches
    assert iot_request.await_count == 5
    called_bodies = [
        _payload_ids(_json_object(call.args[1]), "deviceIdList")
        for call in iot_request.await_args_list
    ]
    assert called_bodies.count(ids) == 1
    assert recorded_depth == [2]

def test_resolve_device_status_batch_size_for_non_positive_total_devices() -> None:
    assert (
        _resolve_device_status_batch_size(total_devices=0, max_devices_per_query=0) == 1
    )
    assert (
        _resolve_device_status_batch_size(total_devices=-1, max_devices_per_query=5)
        == 5
    )

@pytest.mark.asyncio
async def test_query_items_by_binary_split_returns_empty_when_ids_empty() -> None:
    iot_request = AsyncMock()
    result = await _query_items_by_binary_split(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=[],
        item_name="device",
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda _: True,
        lipro_api_error=_DummyApiError,
        normalize_response_code=_normalize_response_code,
        logger=MagicMock(),
    )
    assert result == ([], 0, {}, 0)
    iot_request.assert_not_called()

@pytest.mark.asyncio
async def test_query_with_fallback_logs_unknown_batch_code_when_normalizer_returns_none() -> (
    None
):
    async def _request(
        _path: str, body: JsonObject
    ) -> dict[str, list[dict[str, str]]]:
        ids = _payload_ids(body, "deviceIdList")
        if len(ids) == 2:
            raise _DummyApiError("batch failed", code=None)
        return {"data": []}

    logger = MagicMock()
    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=["a", "b"],
        item_name="device",
        iot_request=AsyncMock(side_effect=_request),
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda _: True,
        lipro_api_error=_DummyApiError,
        normalize_response_code=lambda _code: None,
        expected_offline_codes=(140003, "140003"),
        logger=logger,
    )

    assert result == []
    logger.warning.assert_any_call(
        "Batch %s query failed (code=%s, endpoint=%s): %s. "
        "Falling back to individual queries.",
        "device",
        "unknown",
        "/v2/status/device",
        ANY,
    )

@pytest.mark.asyncio
async def test_query_with_fallback_raises_on_non_retriable_single_query_error() -> None:
    async def _request(
        _path: str, body: JsonObject
    ) -> dict[str, list[dict[str, str]]]:
        ids = _payload_ids(body, "deviceIdList")
        if ids == ["a", "b"]:
            raise _DummyApiError("batch offline", 140003)
        if ids == ["a"]:
            raise _DummyApiError("single fatal", 500)
        return {"data": [{"deviceId": "b"}]}

    with pytest.raises(_DummyApiError, match="single fatal"):
        await query_with_fallback(
            path="/v2/status/device",
            body_key="deviceIdList",
            ids=["a", "b"],
            item_name="device",
            iot_request=AsyncMock(side_effect=_request),
            extract_data_list=_extract_rows,
            is_retriable_device_error=lambda err: getattr(err, "code", None) == 140003,
            lipro_api_error=_DummyApiError,
            normalize_response_code=_normalize_response_code,
            expected_offline_codes=(140003, "140003"),
            logger=MagicMock(),
        )

@pytest.mark.asyncio
async def test_query_with_fallback_raises_on_non_retriable_small_subset_batch_error() -> (
    None
):
    async def _request(
        _path: str, body: JsonObject
    ) -> dict[str, list[dict[str, str]]]:
        ids = _payload_ids(body, "deviceIdList")
        if ids == ["a", "b", "c"]:
            raise _DummyApiError("batch offline", 140003)
        if ids == ["a", "b"]:
            raise _DummyApiError("mini fatal", 500)
        return {"data": [{"deviceId": "c"}]}

    with pytest.raises(_DummyApiError, match="mini fatal"):
        await query_with_fallback(
            path="/v2/status/device",
            body_key="deviceIdList",
            ids=["a", "b", "c"],
            item_name="device",
            iot_request=AsyncMock(side_effect=_request),
            extract_data_list=_extract_rows,
            is_retriable_device_error=lambda err: getattr(err, "code", None) == 140003,
            lipro_api_error=_DummyApiError,
            normalize_response_code=_normalize_response_code,
            expected_offline_codes=(140003, "140003"),
            logger=MagicMock(),
        )

@pytest.mark.asyncio
async def test_query_with_fallback_large_subset_split_paths() -> None:
    ids = [f"id{i}" for i in range(10)]

    async def _request(
        _path: str, body: JsonObject
    ) -> dict[str, list[dict[str, str]]]:
        batch = _payload_ids(body, "deviceIdList")
        if batch == ids:
            raise _DummyApiError("top fail", 140003)
        if batch == ids[:5]:
            raise _DummyApiError("left half fail", 140003)
        return {"data": [{"deviceId": item_id} for item_id in batch]}

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=ids,
        item_name="device",
        iot_request=AsyncMock(side_effect=_request),
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda err: getattr(err, "code", None) == 140003,
        lipro_api_error=_DummyApiError,
        normalize_response_code=_normalize_response_code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
    )

    assert sorted(_row_string(row, "deviceId") for row in result) == sorted(ids)

@pytest.mark.asyncio
async def test_query_with_fallback_large_subset_non_retriable_error_raises() -> None:
    ids = [f"id{i}" for i in range(10)]

    async def _request(
        _path: str, body: JsonObject
    ) -> dict[str, list[dict[str, str]]]:
        batch = _payload_ids(body, "deviceIdList")
        if batch == ids:
            raise _DummyApiError("top fail", 140003)
        if len(batch) == 5:
            raise _DummyApiError("half fatal", 500)
        return {"data": [{"deviceId": item_id} for item_id in batch]}

    with pytest.raises(_DummyApiError, match="half fatal"):
        await query_with_fallback(
            path="/v2/status/device",
            body_key="deviceIdList",
            ids=ids,
            item_name="device",
            iot_request=AsyncMock(side_effect=_request),
            extract_data_list=_extract_rows,
            is_retriable_device_error=lambda err: getattr(err, "code", None) == 140003,
            lipro_api_error=_DummyApiError,
            normalize_response_code=_normalize_response_code,
            expected_offline_codes=(140003, "140003"),
            logger=MagicMock(),
        )

@pytest.mark.asyncio
async def test_query_with_fallback_can_recurse_into_empty_subset_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(status_fallback_module, "_SMALL_SUBSET_BATCH_QUERY_THRESHOLD", 0)

    attempts: dict[tuple[str, ...], int] = {}

    async def _request(
        _path: str, body: JsonObject
    ) -> dict[str, list[dict[str, str]]]:
        batch = tuple(_payload_ids(body, "deviceIdList"))
        attempts[batch] = attempts.get(batch, 0) + 1
        if batch == ("a", "b"):
            raise _DummyApiError("top fail", 140003)
        if batch == ("a",) and attempts[batch] == 1:
            raise _DummyApiError("retry once", 140003)
        return {"data": [{"deviceId": batch[0]}]}

    result = await query_with_fallback(
        path="/v2/status/device",
        body_key="deviceIdList",
        ids=["a", "b"],
        item_name="device",
        iot_request=AsyncMock(side_effect=_request),
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda err: getattr(err, "code", None) == 140003,
        lipro_api_error=_DummyApiError,
        normalize_response_code=_normalize_response_code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
    )

    assert sorted(_row_string(row, "deviceId") for row in result) == ["a", "b"]
