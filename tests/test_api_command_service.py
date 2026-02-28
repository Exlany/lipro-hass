"""Tests for API command service helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api_command_service import (
    build_command_request_body,
    iot_request_with_busy_retry,
    send_command_to_target,
)


class DummyApiError(Exception):
    """Test-only API error with a code attribute."""

    def __init__(self, message: str, code: int | str | None = None) -> None:
        super().__init__(message)
        self.code = code


class TestBuildCommandRequestBody:
    """Tests for build_command_request_body helper."""

    def test_build_command_request_body_without_group_id(self) -> None:
        body = build_command_request_body(
            target_id="03ab5ccd7caaaaaa",
            command="POWER_ON",
            device_type=1,
            properties=None,
            iot_name="20X1",
            to_device_type_hex=lambda _: "00000001",
        )

        assert body == {
            "command": "POWER_ON",
            "deviceId": "03ab5ccd7caaaaaa",
            "deviceType": "00000001",
            "iotName": "20X1",
            "properties": [],
            "skuId": "",
            "hasMacRule": False,
        }

    def test_build_command_request_body_with_group_id(self) -> None:
        body = build_command_request_body(
            target_id="mesh_group_10001",
            command="CHANGE_STATE",
            device_type="ff000001",
            properties=[{"key": "brightness", "value": "60"}],
            iot_name="",
            to_device_type_hex=lambda value: str(value),
            group_id="mesh_group_10001",
        )

        assert body["groupId"] == "mesh_group_10001"
        assert body["properties"] == [{"key": "brightness", "value": "60"}]


class TestSendCommandToTarget:
    """Tests for send_command_to_target helper."""

    @pytest.mark.asyncio
    async def test_send_command_to_target_builds_payload_and_dispatches(self) -> None:
        busy_retry = AsyncMock(return_value={"pushSuccess": True})

        result = await send_command_to_target(
            path="/v2/device/send",
            target_id="03ab5ccd7caaaaaa",
            command="POWER_ON",
            device_type=1,
            properties=None,
            iot_name="20X1",
            to_device_type_hex=lambda _: "00000001",
            iot_request_with_busy_retry=busy_retry,
        )

        assert result == {"pushSuccess": True}
        busy_retry.assert_awaited_once()
        call = busy_retry.await_args
        assert call.args[0] == "/v2/device/send"
        assert call.args[1]["deviceId"] == "03ab5ccd7caaaaaa"
        assert call.args[1]["deviceType"] == "00000001"
        assert call.kwargs["target_id"] == "03ab5ccd7caaaaaa"
        assert call.kwargs["command"] == "POWER_ON"


class TestIotRequestWithBusyRetry:
    """Tests for iot_request_with_busy_retry helper."""

    @pytest.mark.asyncio
    async def test_iot_request_with_busy_retry_returns_empty_for_non_mapping_success(
        self,
    ) -> None:
        result = await iot_request_with_busy_retry(
            path="/v2/device/send",
            body_data={"command": "POWER_ON"},
            target_id="03ab5ccd7caaaaaa",
            command="POWER_ON",
            attempt_limit=3,
            base_delay_seconds=0.25,
            iot_request=AsyncMock(return_value=[1, 2, 3]),
            throttle_change_state=AsyncMock(),
            record_change_state_success=AsyncMock(),
            is_command_busy_error=lambda _: False,
            lipro_api_error=DummyApiError,
            record_change_state_busy=AsyncMock(return_value=(0.2, 0)),
            sleep=AsyncMock(),
            logger=MagicMock(),
        )

        assert result == {}

    @pytest.mark.asyncio
    async def test_iot_request_with_busy_retry_retries_then_succeeds(self) -> None:
        iot_request = AsyncMock(
            side_effect=[
                DummyApiError("busy", 250001),
                {"pushSuccess": True},
            ]
        )
        sleep = AsyncMock()
        logger = MagicMock()

        result = await iot_request_with_busy_retry(
            path="/v2/device/send",
            body_data={"command": "CHANGE_STATE"},
            target_id="mesh_group_10001",
            command="CHANGE_STATE",
            attempt_limit=3,
            base_delay_seconds=0.25,
            iot_request=iot_request,
            throttle_change_state=AsyncMock(),
            record_change_state_success=AsyncMock(),
            is_command_busy_error=lambda _: True,
            lipro_api_error=DummyApiError,
            record_change_state_busy=AsyncMock(return_value=(0.32, 1)),
            sleep=sleep,
            logger=logger,
        )

        assert result == {"pushSuccess": True}
        assert iot_request.await_count == 2
        sleep.assert_awaited_once_with(0.25)
        logger.debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_iot_request_with_busy_retry_non_busy_error_raises(self) -> None:
        with pytest.raises(DummyApiError, match="offline"):
            await iot_request_with_busy_retry(
                path="/v2/device/send",
                body_data={"command": "POWER_ON"},
                target_id="03ab5ccd7caaaaaa",
                command="POWER_ON",
                attempt_limit=3,
                base_delay_seconds=0.25,
                iot_request=AsyncMock(side_effect=DummyApiError("offline", 140003)),
                throttle_change_state=AsyncMock(),
                record_change_state_success=AsyncMock(),
                is_command_busy_error=lambda _: False,
                lipro_api_error=DummyApiError,
                record_change_state_busy=AsyncMock(return_value=(0.2, 0)),
                sleep=AsyncMock(),
                logger=MagicMock(),
            )

    @pytest.mark.asyncio
    async def test_iot_request_with_busy_retry_exhausted_raises(self) -> None:
        iot_request = AsyncMock(side_effect=DummyApiError("busy", 250001))

        with pytest.raises(DummyApiError, match="busy"):
            await iot_request_with_busy_retry(
                path="/v2/device/send",
                body_data={"command": "CHANGE_STATE"},
                target_id="mesh_group_10001",
                command="CHANGE_STATE",
                attempt_limit=3,
                base_delay_seconds=0.25,
                iot_request=iot_request,
                throttle_change_state=AsyncMock(),
                record_change_state_success=AsyncMock(),
                is_command_busy_error=lambda _: True,
                lipro_api_error=DummyApiError,
                record_change_state_busy=AsyncMock(return_value=(0.32, 1)),
                sleep=AsyncMock(),
                logger=MagicMock(),
            )

        assert iot_request.await_count == 4
