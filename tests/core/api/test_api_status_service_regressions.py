"""Focused fallback/connect regressions for the status service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api.status_fallback import query_with_fallback
from custom_components.lipro.core.api.status_service import (
    query_connect_status,
    query_device_status,
    query_mesh_group_status,
)


class DummyApiError(Exception):
    """Test-only API error with optional code field."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


def _extract_rows(payload: object) -> list[dict[str, str]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        rows = payload.get("data")
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


@pytest.mark.asyncio
async def test_query_with_fallback_logs_summary_when_all_single_queries_fail() -> None:
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("offline", 140003),
            DummyApiError("single fail", 500),
            DummyApiError("single fail", 500),
        ]
    )
    logger = MagicMock()

    result = await query_with_fallback(
        path="/query",
        body_key="deviceIdList",
        ids=["03ab5ccd7caaaaaa", "03ab5ccd7cbbbbbb"],
        item_name="device",
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda _: True,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003", 140004, "140004"),
        logger=logger,
    )

    assert result == []
    assert any(
        "fallback returned no data" in str(call.args[0])
        and call.args[1] == "device"
        and call.args[2] == 2
        and call.args[3] == 2
        and call.args[4] == 140003
        for call in logger.warning.call_args_list
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("error_code", [140101, 140004])
async def test_query_device_status_retriable_batch_error_falls_back_to_single_queries(
    error_code: int,
) -> None:
    call_count = 0

    async def iot_request(_path: str, body: dict[str, list[str]]) -> object:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise DummyApiError("retryable", error_code)
        device_id = body["deviceIdList"][0]
        return [{"deviceId": device_id, "powerState": "1"}]

    result = await query_device_status(
        device_ids=["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"],
        max_devices_per_query=100,
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda err: getattr(err, "code", None) == error_code,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        path_query_device_status="/v2/status/device",
    )

    assert result == [
        {"deviceId": "03ab5ccd7cxxxxxx", "powerState": "1"},
        {"deviceId": "03ab5ccd7cyyyyyy", "powerState": "1"},
    ]
    assert call_count == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("error_code", [140101, 140004])
async def test_query_mesh_group_status_retriable_batch_error_falls_back_to_single_queries(
    error_code: int,
) -> None:
    call_count = 0

    async def iot_request(_path: str, body: dict[str, list[str]]) -> object:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise DummyApiError("retryable", error_code)
        group_id = body["groupIdList"][0]
        return [{"groupId": group_id, "powerState": "1"}]

    result = await query_mesh_group_status(
        group_ids=["mesh_group_10001", "mesh_group_10002"],
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_retriable_device_error=lambda err: getattr(err, "code", None) == error_code,
        lipro_api_error=DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        path_query_mesh_group_status="/v2/status/group",
    )

    assert result == [
        {"groupId": "mesh_group_10001", "powerState": "1"},
        {"groupId": "mesh_group_10002", "powerState": "1"},
    ]
    assert call_count == 3


@pytest.mark.asyncio
async def test_query_connect_status_empty_input_returns_empty_dict() -> None:
    result = await query_connect_status(
        device_ids=[],
        sanitize_iot_device_ids=lambda device_ids, endpoint: device_ids,
        iot_request=AsyncMock(),
        coerce_connect_status=lambda value: str(value) == "1",
        lipro_api_error=DummyApiError,
        logger=MagicMock(),
        path_query_connect_status="/v2/status/connect",
    )

    assert result == {}


@pytest.mark.asyncio
async def test_query_connect_status_returns_empty_for_wrapped_non_mapping_data() -> (
    None
):
    result = await query_connect_status(
        device_ids=["03ab5ccd7caaaaaa"],
        sanitize_iot_device_ids=lambda device_ids, endpoint: device_ids,
        iot_request=AsyncMock(return_value={"code": "0000", "data": []}),
        coerce_connect_status=lambda value: str(value) == "1",
        lipro_api_error=DummyApiError,
        logger=MagicMock(),
        path_query_connect_status="/v2/status/connect",
    )

    assert result == {}


@pytest.mark.asyncio
async def test_query_connect_status_returns_empty_on_api_error() -> None:
    result = await query_connect_status(
        device_ids=["03ab5ccd7caaaaaa"],
        sanitize_iot_device_ids=lambda device_ids, endpoint: device_ids,
        iot_request=AsyncMock(side_effect=DummyApiError("down", 500)),
        coerce_connect_status=lambda value: str(value) == "1",
        lipro_api_error=DummyApiError,
        logger=MagicMock(),
        path_query_connect_status="/v2/status/connect",
    )

    assert result == {}
