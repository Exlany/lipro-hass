"""Golden-fixture protocol contract tests for north-star API boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import PATH_GET_CITY, PATH_QUERY_USER_CLOUD
from custom_components.lipro.core.api.diagnostics_api_service import (
    get_city,
    query_user_cloud,
)
from custom_components.lipro.core.api.mqtt_api_service import _extract_mqtt_config_payload

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "api_contracts"


def _load_fixture(name: str) -> object:
    return json.loads((FIXTURE_DIR / name).read_text())


def _require_mapping_response(_path: str, payload: object) -> dict[str, object]:
    assert isinstance(payload, dict)
    return dict(payload)


def _is_success_code(code: object) -> bool:
    return code in {0, "0", "0000"}


def test_get_mqtt_config_direct_fixture_matches_canonical_contract() -> None:
    payload = _load_fixture("get_mqtt_config.direct.json")

    result = _extract_mqtt_config_payload(payload, is_success_code=_is_success_code)

    assert result == {
        "accessKey": "ak-direct",
        "secretKey": "sk-direct",
        "endpoint": "tcp://mqtt.example.com:1883",
        "clientId": "cid-direct",
    }


def test_get_mqtt_config_wrapped_fixture_matches_canonical_contract() -> None:
    payload = _load_fixture("get_mqtt_config.wrapped.json")

    result = _extract_mqtt_config_payload(payload, is_success_code=_is_success_code)

    assert result == {
        "accessKey": "ak-wrapped",
        "secretKey": "sk-wrapped",
        "endpoint": "tcp://mqtt.example.com:1883",
        "clientId": "cid-wrapped",
    }


@pytest.mark.asyncio
async def test_get_city_fixture_matches_current_contract() -> None:
    payload = _load_fixture("get_city.success.json")
    iot_request = AsyncMock(return_value=payload)

    result = await get_city(
        iot_request=iot_request,
        require_mapping_response=_require_mapping_response,
    )

    assert result == {
        "province": "广东省",
        "city": "江门市",
        "zone": "蓬江区",
    }
    iot_request.assert_awaited_once_with(PATH_GET_CITY, {})


@pytest.mark.asyncio
async def test_query_user_cloud_fixture_matches_current_contract() -> None:
    payload = _load_fixture("query_user_cloud.success.json")
    request_iot_mapping_raw = AsyncMock(return_value=(payload, "token"))

    result = await query_user_cloud(
        request_iot_mapping_raw=request_iot_mapping_raw,
        require_mapping_response=_require_mapping_response,
    )

    assert result == {
        "data": [{"appName": "assistant", "enabled": True}],
        "success": True,
    }
    request_iot_mapping_raw.assert_awaited_once_with(PATH_QUERY_USER_CLOUD, "")
