"""Static-friendly tests for API TypedDict contracts."""

from __future__ import annotations

from typing import assert_type, cast

from custom_components.lipro.core.api.types import (
    CommandResultApiResponse,
    DeviceApiResponse,
    DiagnosticsApiResponse,
    JsonValue,
    ScheduleApiResponse,
    ScheduleTimingRow,
)


def test_device_api_response_contract() -> None:
    payload: DeviceApiResponse = {
        "deviceId": "123",
        "serial": "03ab5ccd7caaaaaa",
        "deviceName": "Desk Light",
        "type": 1,
        "iotName": "lipro_led",
        "properties": [{"key": "powerState", "value": "1"}],
    }

    assert payload["serial"] == "03ab5ccd7caaaaaa"
    assert assert_type(payload["deviceId"], str | int) == "123"



def test_schedule_api_response_contract() -> None:
    row: ScheduleTimingRow = {
        "id": "1",
        "hour": 8,
        "minute": 30,
        "enable": True,
        "repeat": "1111111",
    }
    payload: ScheduleApiResponse = {"success": True, "data": [row]}

    assert payload["data"][0]["hour"] == 8
    assert assert_type(payload["data"][0]["enable"], bool | int | str) is True



def test_command_and_diagnostics_payload_contracts() -> None:
    command_payload: CommandResultApiResponse = {
        "code": 0,
        "message": "ok",
        "success": True,
        "msgSn": "abc",
    }
    diagnostics_payload: DiagnosticsApiResponse = {
        "code": 0,
        "success": True,
        "data": [{"event": "connected", "count": 2}],
    }
    data = cast(list[dict[str, JsonValue]], diagnostics_payload["data"])

    assert command_payload["success"] is True
    assert data[0]["event"] == "connected"
