"""Tests for small API helper modules."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.const.api import MAX_RATE_LIMIT_RETRIES, MAX_RETRY_AFTER
from custom_components.lipro.core.api.endpoints.payloads import (
    EndpointPayloadNormalizers,
)
from custom_components.lipro.core.api.errors import LiproApiError, LiproRateLimitError
from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
    get_mqtt_config,
)
from custom_components.lipro.core.api.power_service import fetch_outlet_power_info
from custom_components.lipro.core.api.request_policy import (
    RequestPolicy,
    compute_rate_limit_wait_time,
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
async def test_request_policy_handle_rate_limit_raises_after_retry_budget() -> None:
    policy = RequestPolicy()

    with pytest.raises(LiproRateLimitError, match="Rate limited after"):
        await policy.handle_rate_limit(
            "/v1/devices",
            {"Retry-After": "5"},
            MAX_RATE_LIMIT_RETRIES,
        )


@pytest.mark.asyncio
async def test_request_policy_handle_rate_limit_waits_for_computed_backoff() -> None:
    policy = RequestPolicy()

    with (
        patch(
            "custom_components.lipro.core.api.request_policy.compute_rate_limit_wait_time",
            return_value=1.25,
        ),
        patch(
            "custom_components.lipro.core.api.request_policy.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep,
    ):
        wait_time = await policy.handle_rate_limit(
            "/v1/devices",
            {"Retry-After": "1"},
            1,
        )

    assert wait_time == 1.25
    sleep.assert_awaited_once_with(1.25)


def test_request_policy_is_command_busy_error_false_for_empty_message() -> None:
    assert RequestPolicy.is_command_busy_error(LiproApiError("", code=500)) is False


@pytest.mark.parametrize(
    ("retry_after", "retry_count", "expected"),
    [
        (999999.0, 0, MAX_RETRY_AFTER),
        (5.0, 0, 5.0),
        (None, 0, 1.0),
        (None, 1, 2.0),
        (None, 2, 4.0),
        (-10.0, 0, 0.1),
        (0.0, 3, 0.1),
    ],
)
def test_compute_rate_limit_wait_time_edges(
    retry_after: float | None,
    retry_count: int,
    expected: float,
) -> None:
    assert (
        compute_rate_limit_wait_time(
            retry_after=retry_after,
            retry_count=retry_count,
            max_retry_after=MAX_RETRY_AFTER,
        )
        == expected
    )


def test_lipro_rate_limit_error_preserves_retry_after() -> None:
    error = LiproRateLimitError("Rate limited", retry_after=30.0)

    assert error.retry_after == 30.0
    assert str(error) == "Rate limited"
    assert error.code == 429


def test_lipro_rate_limit_error_defaults_retry_after_to_none() -> None:
    error = LiproRateLimitError("Rate limited")

    assert error.retry_after is None
    assert isinstance(error, LiproApiError)
