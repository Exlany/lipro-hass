"""Tests for small API helper modules."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.const.api import MAX_RATE_LIMIT_RETRIES
from custom_components.lipro.core.api.client_pacing import _ClientPacingMixin
from custom_components.lipro.core.api.errors import LiproApiError, LiproRateLimitError
from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
    get_mqtt_config,
)
from custom_components.lipro.core.api.power_service import fetch_outlet_power_info


class DummyApiError(Exception):
    """Simple API error with optional error code."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


class DummyPacingClient(_ClientPacingMixin):
    """Minimal concrete pacing mixin host for direct unit tests."""

    def __init__(self) -> None:
        self._init_pacing()


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
async def test_fetch_outlet_power_info_wraps_multiple_mapping_rows_in_data_key() -> None:
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

    assert result == {"data": rows}


@pytest.mark.asyncio
async def test_fetch_outlet_power_info_returns_empty_for_unexpected_payload_type() -> None:
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
    assert _extract_mqtt_config_payload("invalid", is_success_code=lambda _code: True) is None
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
        request_iot_mapping=AsyncMock(return_value=({"code": 0, "data": {"raw": 1}}, None)),
        is_success_code=lambda code: code == 0,
        unwrap_iot_success_payload=lambda payload: payload["data"],
        require_mapping_response=lambda _path, _payload: {
            "accessKey": "ak",
            "secretKey": "sk",
            "endpoint": "mqtt",
        },
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
            require_mapping_response=lambda _path, payload: payload,
            lipro_api_error=DummyApiError,
            path_get_mqtt_config="/mqtt/config",
        )


@pytest.mark.asyncio
async def test_client_pacing_handle_rate_limit_raises_after_retry_budget() -> None:
    client = DummyPacingClient()

    with pytest.raises(LiproRateLimitError, match="Rate limited after"):
        await client._handle_rate_limit(
            "/v1/devices",
            {"Retry-After": "5"},
            MAX_RATE_LIMIT_RETRIES,
        )


@pytest.mark.asyncio
async def test_client_pacing_handle_rate_limit_waits_for_computed_backoff() -> None:
    client = DummyPacingClient()

    with patch(
        "custom_components.lipro.core.api.client_pacing._compute_rate_limit_wait_time",
        return_value=1.25,
    ), patch(
        "custom_components.lipro.core.api.client_pacing.asyncio.sleep",
        new=AsyncMock(),
    ) as sleep:
        wait_time = await client._handle_rate_limit(
            "/v1/devices",
            {"Retry-After": "1"},
            1,
        )

    assert wait_time == 1.25
    sleep.assert_awaited_once_with(1.25)


def test_client_pacing_is_command_busy_error_false_for_empty_message() -> None:
    client = DummyPacingClient()

    assert client._is_command_busy_error(LiproApiError("", code=500)) is False
