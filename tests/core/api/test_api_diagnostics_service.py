"""Tests for core.api.diagnostics_service helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import (
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
    PATH_QUERY_USER_CLOUD,
)
from custom_components.lipro.core.api.diagnostics_service import (
    _merge_ota_rows,
    _ota_row_dedupe_key,
    fetch_sensor_history,
    query_ota_info,
    query_user_cloud,
)


class DummyApiError(Exception):
    """Dummy API error used to trigger error branches in tests."""

    def __init__(self, message: str, code: str | int | None = None) -> None:
        super().__init__(message)
        self.code = code


def test_ota_row_dedupe_key_uses_fallback_fields_and_normalizes() -> None:
    key = _ota_row_dedupe_key(
        {
            "iotId": " 03AB5CCD7CABCDEF ",
            "bleName": " T21JC ",
            "version": " 2.6.43 ",
            "url": " HTTPS://FW.EXAMPLE.COM/A.BIN ",
            "md5": " ABCDEF ",
        }
    )
    assert key == (
        "03ab5ccd7cabcdef",
        "t21jc",
        "2.6.43",
        "https://fw.example.com/a.bin",
        "abcdef",
    )


def test_merge_ota_rows_skips_non_dict_and_dedupes_rows() -> None:
    merged_rows: list[dict[str, object]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    rows: list[object] = [
        None,
        "bad-row",
        1,
        {"deviceId": "03ab", "latestVersion": "1.0.1"},
        {"deviceId": "03AB", "latestVersion": "1.0.1"},
    ]

    _merge_ota_rows(merged_rows, seen, rows)

    assert merged_rows == [{"deviceId": "03ab", "latestVersion": "1.0.1"}]
    assert len(seen) == 1


@pytest.mark.asyncio
async def test_query_user_cloud_uses_raw_empty_body_contract() -> None:
    request_iot_mapping_raw = AsyncMock(return_value=({"data": []}, "token"))

    result = await query_user_cloud(
        request_iot_mapping_raw=request_iot_mapping_raw,
        require_mapping_response=lambda _path, payload: payload,
    )

    assert result == {"data": []}
    request_iot_mapping_raw.assert_awaited_once_with(PATH_QUERY_USER_CLOUD, "")


@pytest.mark.asyncio
async def test_query_ota_info_continues_when_v1_fails_and_v2_succeeds() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("v1 failed", code=500),
            {"rows": [row]},
            {"rows": []},
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("rows", []),
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=str,
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result == [row]
    assert iot_request.await_count == 3
    iot_request.assert_any_await(
        PATH_QUERY_OTA_INFO,
        {"deviceId": "mesh_group_1", "deviceType": "ff000001"},
    )
    iot_request.assert_any_await(
        PATH_QUERY_OTA_INFO_V2,
        {"deviceId": "mesh_group_1", "deviceType": "ff000001"},
    )
    iot_request.assert_any_await(PATH_QUERY_CONTROLLER_OTA, {})


@pytest.mark.asyncio
async def test_query_ota_info_probes_richer_v2_payload_for_light_devices() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": []},
            {"rows": []},
            {"rows": [row]},
            {"rows": []},
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("rows", []),
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=str,
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )

    assert result == [row]
    iot_request.assert_any_await(
        PATH_QUERY_OTA_INFO_V2,
        {"deviceId": "mesh_group_1", "deviceType": "ff000001"},
    )
    iot_request.assert_any_await(
        PATH_QUERY_OTA_INFO_V2,
        {
            "deviceId": "mesh_group_1",
            "deviceType": "ff000001",
            "iotName": "21P3",
            "skuId": "",
            "hasMacRule": True,
        },
    )


@pytest.mark.asyncio
async def test_query_ota_info_raises_last_error_when_v1_and_v2_both_fail() -> None:
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("v1 failed", code=500),
            DummyApiError("v2 failed", code=503),
        ]
    )

    with pytest.raises(DummyApiError, match="v2 failed"):
        await query_ota_info(
            iot_request=iot_request,
            extract_data_list=lambda payload: payload.get("rows", []),
            is_invalid_param_error_code=lambda code: code == "100000",
            to_device_type_hex=str,
            lipro_api_error=DummyApiError,
            device_id="mesh_group_1",
            device_type="ff000001",
        )

    assert iot_request.await_count == 2


@pytest.mark.asyncio
async def test_query_ota_info_degrades_when_controller_invalid_param() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": [row]},
            {"rows": []},
            DummyApiError("invalid param", code="100000"),
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("rows", []),
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=str,
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result == [row]


@pytest.mark.asyncio
async def test_query_ota_info_degrades_when_controller_other_api_error() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": [row]},
            {"rows": []},
            DummyApiError("server error", code=500),
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=lambda payload: payload.get("rows", []),
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=str,
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result == [row]


@pytest.mark.asyncio
async def test_fetch_sensor_history_propagates_mapping_error() -> None:
    iot_request = AsyncMock(return_value={"rows": []})

    def _raise_mapping_error(_path: str, _result: object) -> dict[str, object]:
        msg = "mapping error"
        raise DummyApiError(msg)

    with pytest.raises(DummyApiError, match="mapping error"):
        await fetch_sensor_history(
            iot_request=iot_request,
            require_mapping_response=_raise_mapping_error,
            to_device_type_hex=str,
            path="/sensor/history",
            device_id="mesh_group_1",
            device_type="ff000001",
            sensor_device_id="03ab5ccd7c123456",
            mesh_type="2",
        )

    iot_request.assert_awaited_once_with(
        "/sensor/history",
        {
            "deviceId": "mesh_group_1",
            "deviceType": "ff000001",
            "sensorDeviceId": "03ab5ccd7c123456",
            "meshType": "2",
        },
    )
