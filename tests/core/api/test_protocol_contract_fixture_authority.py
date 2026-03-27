"""Protocol contract fixture authority suites."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import PATH_GET_CITY, PATH_QUERY_USER_CLOUD
from custom_components.lipro.core.api.diagnostics_api_service import (
    get_city,
    query_user_cloud,
)
from custom_components.lipro.core.api.types import JsonObject
from tests.harness.protocol import iter_replay_manifests

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "api_contracts"
DEVICE_LIST_AUTHORITY_PATH = "tests/fixtures/api_contracts/get_device_list.envelope.json"


def _load_fixture(name: str) -> object:
    return json.loads((FIXTURE_DIR / name).read_text())


def _require_mapping_response(_path: str, payload: object) -> JsonObject:
    assert isinstance(payload, dict)
    return cast(JsonObject, dict(payload))


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


def test_phase_1_truth_endpoints_are_not_duplicated_into_external_boundary_fixtures() -> None:
    external_boundary_dir = FIXTURE_DIR.parent / "external_boundaries" / "diagnostics_capabilities"

    assert not (external_boundary_dir / "get_city.success.json").exists()
    assert not (external_boundary_dir / "query_user_cloud.success.json").exists()


def test_rest_replay_manifests_reuse_phase_1_contract_fixtures() -> None:
    manifests = list(iter_replay_manifests(channel="rest"))
    expected = [
        ("rest.list-envelope", DEVICE_LIST_AUTHORITY_PATH),
        ("rest.device-list", DEVICE_LIST_AUTHORITY_PATH),
        ("rest.mqtt-config", "tests/fixtures/api_contracts/get_mqtt_config.direct.json"),
        ("rest.mqtt-config", "tests/fixtures/api_contracts/get_mqtt_config.wrapped.json"),
        ("rest.device-status", "tests/fixtures/api_contracts/query_device_status.mixed.json"),
        ("rest.mesh-group-status", "tests/fixtures/api_contracts/query_mesh_group_status.topology.json"),
        ("rest.schedule-json", "tests/fixtures/api_contracts/query_mesh_schedule_json.v1.json"),
    ]

    assert len(expected) == len(manifests)
    for manifest, (family, authority_path) in zip(manifests, expected, strict=True):
        assert manifest.family == family
        assert manifest.authority_path.as_posix().endswith(authority_path)
