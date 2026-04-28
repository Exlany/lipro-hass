"""Tests for small API helper modules."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.core.api.endpoints.payloads import (
    EndpointPayloadNormalizers,
)
from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
    get_mqtt_config,
)
from custom_components.lipro.core.api.power_service import fetch_outlet_power_info
from custom_components.lipro.core.api.types import JsonObject


def _require_mapping_response(_path: str, payload: object) -> JsonObject:
    assert isinstance(payload, dict)
    return cast(JsonObject, dict(payload))


def _mqtt_config_response(_path: str, _payload: object) -> JsonObject:
    return cast(
        JsonObject,
        {
            "accessKey": "ak",
            "secretKey": "sk",
            "endpoint": "mqtt",
        },
    )


class DummyApiError(Exception):
    """Simple API error with optional error code."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            [{"deviceId": "abc"}, {"deviceId": "def"}],
            [{"deviceId": "abc"}, {"deviceId": "def"}],
        ),
        ({"data": [{"deviceId": "abc"}]}, [{"deviceId": "abc"}]),
        ({"data": {"deviceId": "abc"}}, []),
        ({"status": "ok"}, []),
        (None, []),
        ("unexpected", []),
    ],
)
def test_endpoint_payload_normalizers_extract_data_list(
    payload: object,
    expected: list[dict[str, str]],
) -> None:
    assert EndpointPayloadNormalizers.extract_data_list(payload) == expected


@pytest.mark.asyncio
async def test_fetch_outlet_power_info_returns_single_mapping_from_mixed_list() -> None:
    logger = Mock()

    result = await fetch_outlet_power_info(
        device_id="03ab5ccd7c123456",
        normalize_power_target_id=lambda device_id: device_id.lower(),
        iot_request=AsyncMock(return_value=[{"nowPower": 1.0}, "bad-row"]),
        require_mapping_response=Mock(),
        is_invalid_param_error_code=lambda _code: False,
        lipro_api_error=DummyApiError,
        logger=logger,
        path_query_outlet_power="/power",
    )

    assert result == {"nowPower": 1.0}
    logger.debug.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_outlet_power_info_returns_empty_for_list_without_mapping_rows() -> (
    None
):
    result = await fetch_outlet_power_info(
        device_id="03ab5ccd7c123456",
        normalize_power_target_id=lambda device_id: device_id.lower(),
        iot_request=AsyncMock(return_value=["bad-row"]),
        require_mapping_response=Mock(),
        is_invalid_param_error_code=lambda _code: False,
        lipro_api_error=DummyApiError,
        logger=Mock(),
        path_query_outlet_power="/power",
    )

    assert result == {}


@pytest.mark.asyncio
async def test_fetch_outlet_power_info_returns_multiple_mapping_rows_as_explicit_list() -> (
    None
):
    rows = [{"nowPower": 1.0}, {"nowPower": 2.0}]

    result = await fetch_outlet_power_info(
        device_id="03ab5ccd7c123456",
        normalize_power_target_id=lambda device_id: device_id.lower(),
        iot_request=AsyncMock(return_value=rows),
        require_mapping_response=Mock(),
        is_invalid_param_error_code=lambda _code: False,
        lipro_api_error=DummyApiError,
        logger=Mock(),
        path_query_outlet_power="/power",
    )

    assert result == rows


@pytest.mark.asyncio
async def test_fetch_outlet_power_info_returns_empty_for_unexpected_payload_type() -> (
    None
):
    logger = Mock()

    result = await fetch_outlet_power_info(
        device_id="03ab5ccd7c123456",
        normalize_power_target_id=lambda device_id: device_id.lower(),
        iot_request=AsyncMock(return_value="unexpected"),
        require_mapping_response=Mock(),
        is_invalid_param_error_code=lambda _code: False,
        lipro_api_error=DummyApiError,
        logger=logger,
        path_query_outlet_power="/power",
    )

    assert result == {}
    logger.debug.assert_called_once()


def test_extract_mqtt_config_payload_rejects_invalid_shapes() -> None:
    assert (
        _extract_mqtt_config_payload("invalid", is_success_code=lambda _code: True)
        is None
    )
    assert (
        _extract_mqtt_config_payload(
            {"data": {"accessKey": "ak"}},
            is_success_code=lambda _code: True,
        )
        is None
    )


@pytest.mark.asyncio
async def test_get_mqtt_config_uses_wrapped_success_payload_when_direct_shape_is_missing() -> (
    None
):
    result = await get_mqtt_config(
        request_iot_mapping=AsyncMock(
            return_value=({"code": 0, "data": {"raw": 1}}, None)
        ),
        is_success_code=lambda code: code == 0,
        unwrap_iot_success_payload=lambda payload: payload["data"],
        require_mapping_response=_mqtt_config_response,
        lipro_api_error=DummyApiError,
        path_get_mqtt_config="/mqtt/config",
    )

    assert result["accessKey"] == "ak"
    assert result["secretKey"] == "sk"


@pytest.mark.asyncio
async def test_get_mqtt_config_raises_default_error_for_non_mapping_response() -> None:
    with pytest.raises(DummyApiError, match="missing accessKey/secretKey"):
        await get_mqtt_config(
            request_iot_mapping=AsyncMock(return_value=("bad-response", None)),
            is_success_code=lambda code: code == 0,
            unwrap_iot_success_payload=lambda payload: payload,
            require_mapping_response=_require_mapping_response,
            lipro_api_error=DummyApiError,
            path_get_mqtt_config="/mqtt/config",
        )


def test_rest_decoder_family_helpers_stay_near_decoder_homes() -> None:
    root = Path(__file__).resolve().parents[3]
    support_text = (
        root
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "boundary"
        / "rest_decoder_support.py"
    ).read_text(encoding="utf-8")
    decoder_text = (
        root
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "boundary"
        / "rest_decoder.py"
    ).read_text(encoding="utf-8")
    utility_text = (
        root
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "boundary"
        / "rest_decoder_utility.py"
    ).read_text(encoding="utf-8")

    assert "_extract_mqtt_config_mapping" not in support_text
    assert "_build_schedule_json_fingerprint" not in support_text
    assert "parse_mesh_schedule_json" not in support_text
    assert "_decode_list_envelope_canonical" in support_text
    assert "_extract_mqtt_config_mapping" in decoder_text
    assert "_decode_schedule_json_canonical" in decoder_text
    assert "_build_schedule_json_fingerprint" in utility_text
    assert "parse_mesh_schedule_json" in utility_text
