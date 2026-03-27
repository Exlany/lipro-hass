"""OTA and fallback diagnostics API service assertions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import (
    PATH_QUERY_CONTROLLER_OTA,
    PATH_QUERY_OTA_INFO,
    PATH_QUERY_OTA_INFO_V2,
)
from custom_components.lipro.core.api.diagnostics_api_service import (
    _build_rich_ota_v2_payload,
    _merge_ota_rows,
    _ota_row_dedupe_key,
    query_ota_info,
    query_ota_info_with_outcome,
)
from custom_components.lipro.core.api.types import OtaInfoRow


class DummyApiError(Exception):
    """Dummy API error used to trigger error branches in tests."""

    def __init__(self, message: str, code: str | int | None = None) -> None:
        super().__init__(message)
        self.code = code


def _extract_rows(payload: object) -> list[object]:
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return rows
    return []


def test_build_rich_ota_v2_payload_requires_enabled_flag_and_iot_name() -> None:
    ota_payload = {"deviceId": "mesh_group_1", "deviceType": "ff000001"}

    assert (
        _build_rich_ota_v2_payload(
            ota_payload,
            iot_name="21P3",
            allow_rich_v2_fallback=False,
        )
        is None
    )
    assert (
        _build_rich_ota_v2_payload(
            ota_payload,
            iot_name="   ",
            allow_rich_v2_fallback=True,
        )
        is None
    )


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
    merged_rows: list[OtaInfoRow] = []
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
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
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
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
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
async def test_query_ota_info_skips_richer_v2_payload_when_v1_has_valid_rows() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": [row]},
            {"rows": []},
            {"rows": []},
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )

    assert result == [row]
    assert iot_request.await_count == 3
    assert [args.args for args in iot_request.await_args_list if args.args[0] == PATH_QUERY_OTA_INFO_V2] == [
        (
            PATH_QUERY_OTA_INFO_V2,
            {"deviceId": "mesh_group_1", "deviceType": "ff000001"},
        )
    ]


@pytest.mark.asyncio
async def test_query_ota_info_probes_richer_v2_payload_when_v1_v2_rows_invalid() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": [None, "bad-row"]},
            {"rows": [0, []]},
            {"rows": [row]},
            {"rows": []},
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )

    assert result == [row]
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
            extract_data_list=_extract_rows,
            is_invalid_param_error_code=lambda code: code == "100000",
            to_device_type_hex=lambda value: str(value),
            lipro_api_error=DummyApiError,
            device_id="mesh_group_1",
            device_type="ff000001",
        )


@pytest.mark.asyncio
async def test_query_ota_info_with_outcome_reports_primary_failure() -> None:
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("v1 failed", code=500),
            DummyApiError("v2 failed", code=503),
        ]
    )

    result = await query_ota_info_with_outcome(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result.rows == []
    assert isinstance(result.error, DummyApiError)
    assert str(result.error) == "v2 failed"
    assert result.outcome.kind == "failed"
    assert result.outcome.reason_code == "primary_endpoints_failed"


@pytest.mark.asyncio
async def test_query_ota_info_handles_invalid_param_on_richer_v2_payload() -> None:
    iot_request = AsyncMock(
        side_effect=[
            {"rows": []},
            {"rows": []},
            DummyApiError("bad richer payload", code="100000"),
            {"rows": []},
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )

    assert result == []


@pytest.mark.asyncio
async def test_query_ota_info_with_outcome_reports_rich_v2_invalid_param() -> None:
    iot_request = AsyncMock(
        side_effect=[
            {"rows": []},
            {"rows": []},
            DummyApiError("bad richer payload", code="100000"),
            {"rows": []},
        ]
    )

    result = await query_ota_info_with_outcome(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )

    assert result.rows == []
    assert result.error is None
    assert result.outcome.kind == "degraded"
    assert result.outcome.reason_code == "rich_v2_invalid_param"


@pytest.mark.asyncio
async def test_query_ota_info_handles_generic_error_on_richer_v2_payload() -> None:
    iot_request = AsyncMock(
        side_effect=[
            {"rows": []},
            {"rows": []},
            DummyApiError("richer payload failed", code=500),
            {"rows": []},
        ]
    )

    result = await query_ota_info(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
        iot_name="21P3",
        allow_rich_v2_fallback=True,
    )

    assert result == []
    assert iot_request.await_count == 4


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
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result == [row]


@pytest.mark.asyncio
async def test_query_ota_info_with_outcome_reports_controller_invalid_param() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": [row]},
            {"rows": []},
            DummyApiError("invalid param", code="100000"),
        ]
    )

    result = await query_ota_info_with_outcome(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result.rows == [row]
    assert result.error is None
    assert result.outcome.kind == "degraded"
    assert result.outcome.reason_code == "controller_invalid_param"


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
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result == [row]


@pytest.mark.asyncio
async def test_query_ota_info_with_outcome_reports_controller_failure() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            {"rows": [row]},
            {"rows": []},
            DummyApiError("server error", code=500),
        ]
    )

    result = await query_ota_info_with_outcome(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result.rows == [row]
    assert result.error is None
    assert result.outcome.kind == "degraded"
    assert result.outcome.reason_code == "controller_failed"
    assert result.outcome.http_status == 500


@pytest.mark.asyncio
async def test_query_ota_info_with_outcome_prefers_primary_recovery_over_later_controller_degradation() -> None:
    row = {"deviceType": "ff000001", "latestVersion": "1.0.1"}
    iot_request = AsyncMock(
        side_effect=[
            DummyApiError("v1 failed", code=500),
            {"rows": [row]},
            DummyApiError("invalid param", code="100000"),
        ]
    )

    result = await query_ota_info_with_outcome(
        iot_request=iot_request,
        extract_data_list=_extract_rows,
        is_invalid_param_error_code=lambda code: code == "100000",
        to_device_type_hex=lambda value: str(value),
        lipro_api_error=DummyApiError,
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result.rows == [row]
    assert result.error is None
    assert result.outcome.kind == "degraded"
    assert result.outcome.reason_code == "primary_endpoint_recovered"
