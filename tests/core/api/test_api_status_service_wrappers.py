"""Wrapper-focused API status service assertions."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import rest_facade_endpoint_methods
from custom_components.lipro.core.api.endpoint_surface import RestEndpointSurface
from custom_components.lipro.core.api.status_service import (
    query_connect_status,
    query_device_status,
)

if TYPE_CHECKING:
    from custom_components.lipro.core.api.rest_facade import LiproRestFacade

class _DummyApiError(Exception):
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
async def test_query_device_status_splits_batches() -> None:
    iot_request = AsyncMock(return_value={"data": [{"ok": True}]})

    result = await query_device_status(
        device_ids=["a", "b", "c"],
        max_devices_per_query=2,
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: False,
        lipro_api_error=_DummyApiError,
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
        lipro_api_error=_DummyApiError,
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
        lipro_api_error=_DummyApiError,
        logger=MagicMock(),
        path_query_connect_status="/v2/status/connect",
    )

    assert result == {"03ab": True}

@pytest.mark.asyncio
async def test_query_device_status_reports_batch_metrics_with_fallback_depth() -> None:
    metrics: list[tuple[int, float, int]] = []
    iot_request = AsyncMock(
        side_effect=[
            _DummyApiError("batch fail", 140003),
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
        lipro_api_error=_DummyApiError,
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

@pytest.mark.asyncio
async def test_rest_endpoint_surface_forwards_typed_batch_metric_callback() -> None:
    rows = [{"deviceId": "a"}]
    on_batch_metric = MagicMock()
    status_endpoints = SimpleNamespace(
        query_device_status=AsyncMock(return_value=rows)
    )

    result = await RestEndpointSurface(
        device_endpoints=MagicMock(),
        status_endpoints=status_endpoints,
        command_endpoints=MagicMock(),
        misc_endpoints=MagicMock(),
        schedule_endpoints=MagicMock(),
    ).query_device_status(
        ["a"],
        max_devices_per_query=7,
        on_batch_metric=on_batch_metric,
    )

    assert result == rows
    status_endpoints.query_device_status.assert_awaited_once_with(
        ["a"],
        max_devices_per_query=7,
        on_batch_metric=on_batch_metric,
    )

@pytest.mark.asyncio
async def test_rest_facade_misc_endpoint_wrappers_preserve_payload_contracts() -> None:
    mqtt_payload = {"accessKey": "ak", "secretKey": "sk", "endpoint": "mqtt"}
    command_result_payload = {
        "code": "0000",
        "message": "success",
        "success": True,
    }
    city_payload = {"province": "广东省", "city": "江门市", "zone": "蓬江区"}
    user_cloud_payload = {
        "data": [{"appName": "assistant", "enabled": True}],
        "success": True,
    }
    surface = SimpleNamespace(
        get_mqtt_config=AsyncMock(return_value=mqtt_payload),
        query_command_result=AsyncMock(return_value=command_result_payload),
        get_city=AsyncMock(return_value=city_payload),
        query_user_cloud=AsyncMock(return_value=user_cloud_payload),
    )
    facade = cast(
        object,
        SimpleNamespace(_endpoint_surface=surface),
    )

    assert await rest_facade_endpoint_methods.get_mqtt_config(cast("LiproRestFacade", facade)) == mqtt_payload
    assert (
        await rest_facade_endpoint_methods.query_command_result(
            cast("LiproRestFacade", facade),
            msg_sn="msg-1",
            device_id="mesh_group_1",
            device_type="ff000001",
        )
        == command_result_payload
    )
    assert await rest_facade_endpoint_methods.get_city(cast("LiproRestFacade", facade)) == city_payload
    assert (
        await rest_facade_endpoint_methods.query_user_cloud(cast("LiproRestFacade", facade))
        == user_cloud_payload
    )

    surface.get_mqtt_config.assert_awaited_once_with()
    surface.query_command_result.assert_awaited_once_with(
        msg_sn="msg-1",
        device_id="mesh_group_1",
        device_type="ff000001",
    )
    surface.get_city.assert_awaited_once_with()
    surface.query_user_cloud.assert_awaited_once_with()

@pytest.mark.asyncio
async def test_query_device_status_skips_empty_batch_rows_in_merged_results() -> None:
    async def _request(
        _path: str, body: dict[str, list[str]]
    ) -> dict[str, list[dict[str, str]]]:
        ids = body["deviceIdList"]
        if ids == ["a", "b"]:
            return {"data": []}
        return {"data": [{"deviceId": "c"}]}

    result = await query_device_status(
        device_ids=["a", "b", "c", "d"],
        max_devices_per_query=2,
        iot_request=AsyncMock(side_effect=_request),
        extract_data_list=lambda payload: payload.get("data", []),
        is_retriable_device_error=lambda _: True,
        lipro_api_error=_DummyApiError,
        normalize_response_code=lambda code: code,
        expected_offline_codes=(140003, "140003"),
        logger=MagicMock(),
        path_query_device_status="/v2/status/device",
    )

    assert result == [{"deviceId": "c"}]
