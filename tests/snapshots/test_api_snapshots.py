"""Snapshot coverage for API typed payload contracts."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from syrupy.assertion import SnapshotAssertion

from custom_components.lipro.const.api import PATH_GET_CITY, PATH_QUERY_USER_CLOUD
from custom_components.lipro.core.api.diagnostics_api_service import (
    get_city,
    query_user_cloud,
)
from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
)
from custom_components.lipro.core.api.types import (
    CommandResultApiResponse,
    DiagnosticsApiResponse,
    ScheduleApiResponse,
)

CONTRACT_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "api_contracts"


def _load_contract_fixture(name: str) -> object:
    return json.loads((CONTRACT_FIXTURE_DIR / name).read_text())


def _require_mapping_response(_path: str, payload: object) -> dict[str, object]:
    assert isinstance(payload, dict)
    return dict(payload)


def _is_success_code(code: object) -> bool:
    return code in {0, "0", "0000"}


def test_api_payload_snapshots(snapshot: SnapshotAssertion) -> None:
    command_payload: CommandResultApiResponse = {
        "code": 0,
        "message": "ok",
        "success": True,
        "msgSn": "abc123",
    }
    diagnostics_payload: DiagnosticsApiResponse = {
        "code": 0,
        "success": True,
        "data": [{"event": "connected", "count": 2}],
    }
    schedule_payload: ScheduleApiResponse = {
        "success": True,
        "data": [{"id": "1", "hour": 8, "minute": 30, "enable": True}],
    }

    assert {
        "command": command_payload,
        "diagnostics": diagnostics_payload,
        "schedule": schedule_payload,
    } == snapshot


@pytest.mark.asyncio
async def test_protocol_contract_baseline_snapshots(
    snapshot: SnapshotAssertion,
) -> None:
    mqtt_direct_payload = _load_contract_fixture("get_mqtt_config.direct.json")
    mqtt_wrapped_payload = _load_contract_fixture("get_mqtt_config.wrapped.json")
    city_payload = _load_contract_fixture("get_city.success.json")
    user_cloud_payload = _load_contract_fixture("query_user_cloud.success.json")

    mqtt_direct = _extract_mqtt_config_payload(
        mqtt_direct_payload,
        is_success_code=_is_success_code,
    )
    mqtt_wrapped = _extract_mqtt_config_payload(
        mqtt_wrapped_payload,
        is_success_code=_is_success_code,
    )
    assert mqtt_direct == mqtt_wrapped

    city_request = AsyncMock(return_value=city_payload)
    user_cloud_request = AsyncMock(return_value=(user_cloud_payload, "token"))

    city_contract = await get_city(
        iot_request=city_request,
        require_mapping_response=_require_mapping_response,
    )
    user_cloud_contract = await query_user_cloud(
        request_iot_mapping_raw=user_cloud_request,
        require_mapping_response=_require_mapping_response,
    )

    city_request.assert_awaited_once_with(PATH_GET_CITY, {})
    user_cloud_request.assert_awaited_once_with(PATH_QUERY_USER_CLOUD, "")

    assert {
        "mqtt_config": {
            "accepted_input_shapes": ["direct", "wrapped"],
            "canonical_output": mqtt_direct,
        },
        "get_city": city_contract,
        "query_user_cloud": user_cloud_contract,
    } == snapshot
