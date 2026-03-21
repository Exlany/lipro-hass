"""Tests for API command service helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.core.api.command_api_service import (
    build_command_request_body,
    send_command_to_target,
)


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
            properties=[{"key": "brightness", "value": "80"}],
            iot_name="20X1",
            to_device_type_hex=lambda _: "ff000001",
            group_id="mesh_group_10001",
        )

        assert body["groupId"] == "mesh_group_10001"
        assert body["properties"] == [{"key": "brightness", "value": "80"}]


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
            properties=[{"key": "powerState", "value": "1"}],
            iot_name="20X1",
            to_device_type_hex=lambda _: "00000001",
            iot_request_with_busy_retry=busy_retry,
        )

        assert result == {"pushSuccess": True}
        busy_retry.assert_awaited_once()
        call = busy_retry.await_args
        assert call is not None
        assert call.args[0] == "/v2/device/send"
        assert call.args[1]["deviceId"] == "03ab5ccd7caaaaaa"
        assert call.args[1]["deviceType"] == "00000001"
        assert call.kwargs["target_id"] == "03ab5ccd7caaaaaa"
        assert call.kwargs["command"] == "POWER_ON"


def test_command_api_service_no_longer_owns_busy_retry_algorithm() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "command_api_service.py"
    ).read_text(encoding="utf-8")

    assert "async def iot_request_with_busy_retry(" not in module_text
