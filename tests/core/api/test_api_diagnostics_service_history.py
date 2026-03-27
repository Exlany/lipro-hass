"""History and command-result diagnostics API service assertions."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import PATH_QUERY_COMMAND_RESULT
from custom_components.lipro.core.api.diagnostics_api_service import (
    fetch_sensor_history,
    query_command_result,
)
from custom_components.lipro.core.api.types import JsonObject


class DummyApiError(Exception):
    """Dummy API error used to trigger error branches in tests."""

    def __init__(self, message: str, code: str | int | None = None) -> None:
        super().__init__(message)
        self.code = code


def _require_mapping_response(_path: str, payload: object) -> JsonObject:
    if isinstance(payload, dict):
        return cast(JsonObject, payload)
    return {}


@pytest.mark.asyncio
async def test_fetch_sensor_history_propagates_mapping_error() -> None:
    iot_request = AsyncMock(return_value={"rows": []})

    def _raise_mapping_error(_path: str, _result: object) -> JsonObject:
        msg = "mapping error"
        raise DummyApiError(msg)

    with pytest.raises(DummyApiError, match="mapping error"):
        await fetch_sensor_history(
            iot_request=iot_request,
            require_mapping_response=_raise_mapping_error,
            to_device_type_hex=lambda value: str(value),
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


@pytest.mark.asyncio
async def test_query_command_result_matches_external_boundary_fixture() -> None:
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    payload = load_external_boundary_fixture(
        "diagnostics_capabilities",
        "query_command_result.success.json",
    )
    request_iot_mapping = AsyncMock(return_value=(payload, "token"))

    result = await query_command_result(
        request_iot_mapping=request_iot_mapping,
        require_mapping_response=_require_mapping_response,
        to_device_type_hex=lambda value: str(value),
        msg_sn="msg-1",
        device_id="mesh_group_1",
        device_type="ff000001",
    )

    assert result == payload
    request_iot_mapping.assert_awaited_once_with(
        PATH_QUERY_COMMAND_RESULT,
        {
            "msgSn": "msg-1",
            "deviceId": "mesh_group_1",
            "deviceType": "ff000001",
        },
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fixture_name", "path"),
    [
        ("body_sensor_history.success.json", "/sensor/body/history"),
        ("door_sensor_history.success.json", "/sensor/door/history"),
    ],
)
async def test_fetch_sensor_history_matches_external_boundary_fixture(
    fixture_name: str,
    path: str,
) -> None:
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    payload = load_external_boundary_fixture(
        "diagnostics_capabilities",
        fixture_name,
    )
    iot_request = AsyncMock(return_value=payload)

    result = await fetch_sensor_history(
        iot_request=iot_request,
        require_mapping_response=_require_mapping_response,
        to_device_type_hex=lambda value: str(value),
        path=path,
        device_id="mesh_group_1",
        device_type="ff000001",
        sensor_device_id="03ab5ccd7c123456",
        mesh_type="2",
    )

    assert result == payload
