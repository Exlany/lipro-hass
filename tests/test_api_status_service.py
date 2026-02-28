"""Tests for API status service helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api_status_service import (
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
