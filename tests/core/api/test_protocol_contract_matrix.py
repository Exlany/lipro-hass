"""Golden-fixture protocol contract tests for north-star API boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import PATH_GET_CITY, PATH_QUERY_USER_CLOUD
from custom_components.lipro.core.api.client import LiproRestFacade
from custom_components.lipro.core.api.diagnostics_api_service import (
    get_city,
    query_user_cloud,
)
from custom_components.lipro.core.api.endpoints import _ClientEndpointsMixin
from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
)
from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.boundary import (
    decode_device_list_payload,
    decode_device_status_payload,
    decode_mesh_group_status_payload,
    decode_mqtt_config_payload,
)
from tests.harness.protocol import iter_replay_manifests

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "api_contracts"
EXPECTED_MQTT_CONFIG = {
    "accessKey": "ak-direct",
    "secretKey": "sk-direct",
    "endpoint": "tcp://mqtt.example.com:1883",
    "clientId": "cid-direct",
}
EXPECTED_DEVICE_LIST_DEVICES = [
    {
        "deviceId": 1,
        "serial": "03ab5ccd7c000001",
        "deviceName": "Living Light",
        "type": 1,
        "iotName": "lipro_led",
        "roomId": 11,
        "roomName": "Living Room",
        "productId": 101,
        "physicalModel": "light",
        "isGroup": False,
        "properties": {
            "fanOnoff": "1",
            "brightness": "80",
        },
        "identityAliases": ["03ab5ccd7c000001"],
    },
    {
        "deviceId": "mesh_group_10001",
        "serial": "mesh_group_10001",
        "deviceName": "Zone Group",
        "type": 9,
        "iotName": "lipro_group",
        "physicalModel": "group",
        "isGroup": True,
        "properties": {},
        "identityAliases": ["mesh_group_10001"],
    },
]
EXPECTED_DEVICE_STATUS_ROWS = [
    {
        "deviceId": "03ab5ccd7c000001",
        "properties": {
            "fanOnoff": "1",
            "wifi_ssid": "mesh-net",
        },
    },
    {
        "deviceId": "mesh_group_10001",
        "properties": {
            "powerState": "1",
            "wifi_rssi": "-60",
        },
    },
    {
        "deviceId": "03ab5ccd7c000002",
        "properties": {
            "brightness": "40",
            "position": "50",
        },
    },
]
EXPECTED_MESH_GROUP_STATUS_ROWS = [
    {
        "groupId": "mesh_group_10001",
        "gatewayDeviceId": "03ab5ccd7c0000a1",
        "devices": [
            {"deviceId": "03ab5ccd7c000001"},
            {"deviceId": "03ab5ccd7c000002"},
        ],
        "properties": {
            "powerState": "1",
        },
    },
    {
        "groupId": "mesh_group_10002",
        "gatewayDeviceId": None,
        "devices": [],
        "properties": {},
    },
]


def _load_fixture(name: str) -> object:
    return json.loads((FIXTURE_DIR / name).read_text())


def _require_mapping_response(_path: str, payload: object) -> dict[str, object]:
    assert isinstance(payload, dict)
    return dict(payload)


def _is_success_code(code: object) -> bool:
    return code in {0, "0", "0000"}


def test_lipro_protocol_facade_is_available_as_unified_protocol_root() -> None:
    assert LiproProtocolFacade.__name__ == "LiproProtocolFacade"


def test_lipro_rest_facade_is_available_as_phase_2_rest_child_facade() -> None:
    assert LiproRestFacade.__name__ == "LiproRestFacade"


def test_lipro_rest_facade_no_longer_uses_aggregate_endpoint_mixin() -> None:
    assert _ClientEndpointsMixin not in LiproRestFacade.__mro__


def test_protocol_root_owns_shared_rest_session_and_request_policy() -> None:
    client = LiproProtocolFacade("test-phone-id")

    assert client.rest._session_state is client.session_state.rest_state
    assert client.rest._request_policy is client.request_policy


@pytest.mark.parametrize(
    "fixture_name",
    ["get_mqtt_config.direct.json", "get_mqtt_config.wrapped.json"],
)
def test_get_mqtt_config_fixtures_normalize_to_same_canonical_contract(
    fixture_name: str,
) -> None:
    payload = _load_fixture(fixture_name)

    result = _extract_mqtt_config_payload(payload, is_success_code=_is_success_code)

    assert result == EXPECTED_MQTT_CONFIG


@pytest.mark.parametrize(
    "fixture_name",
    ["get_mqtt_config.direct.json", "get_mqtt_config.wrapped.json"],
)
def test_protocol_root_contracts_normalize_mqtt_config(
    fixture_name: str,
) -> None:
    payload = _load_fixture(fixture_name)

    client = LiproProtocolFacade("test-phone-id")

    assert client.contracts.normalize_mqtt_config(payload) == EXPECTED_MQTT_CONFIG


@pytest.mark.parametrize(
    "fixture_name",
    ["get_device_list.direct.json", "get_device_list.compat.json"],
)
def test_protocol_root_contracts_normalize_device_list_pages(
    fixture_name: str,
) -> None:
    payload = _load_fixture(fixture_name)

    client = LiproProtocolFacade("test-phone-id")
    result = client.contracts.normalize_device_list_page(payload)

    assert result["devices"] == EXPECTED_DEVICE_LIST_DEVICES
    assert result["has_more"] is True


@pytest.mark.parametrize(
    "fixture_name",
    ["get_device_list.direct.json", "get_device_list.compat.json"],
)
def test_rest_boundary_decoder_returns_canonical_device_list_page(
    fixture_name: str,
) -> None:
    payload = _load_fixture(fixture_name)

    result = decode_device_list_payload(payload)

    assert result.key.label == "rest.device-list@v1"
    assert result.authority == "tests/fixtures/api_contracts/get_device_list.*.json"
    assert result.canonical["devices"] == EXPECTED_DEVICE_LIST_DEVICES
    assert result.canonical["has_more"] is True


def test_protocol_root_contracts_normalize_device_status_rows() -> None:
    payload = _load_fixture("query_device_status.mixed.json")

    client = LiproProtocolFacade("test-phone-id")

    assert client.contracts.normalize_device_status_rows(payload) == EXPECTED_DEVICE_STATUS_ROWS
    assert client.contracts.build_device_status_map(payload) == {
        "03ab5ccd7c000001": {"fanOnoff": "1", "wifi_ssid": "mesh-net"},
        "mesh_group_10001": {"powerState": "1", "wifi_rssi": "-60"},
        "03ab5ccd7c000002": {"brightness": "40", "position": "50"},
    }


def test_rest_boundary_decoder_returns_canonical_device_status_rows() -> None:
    payload = _load_fixture("query_device_status.mixed.json")

    result = decode_device_status_payload(payload)

    assert result.key.label == "rest.device-status@v1"
    assert result.authority == "tests/fixtures/api_contracts/query_device_status.*.json"
    assert result.canonical == EXPECTED_DEVICE_STATUS_ROWS


def test_protocol_root_contracts_normalize_mesh_group_status_rows() -> None:
    payload = _load_fixture("query_mesh_group_status.topology.json")

    client = LiproProtocolFacade("test-phone-id")

    assert (
        client.contracts.normalize_mesh_group_status_rows(payload)
        == EXPECTED_MESH_GROUP_STATUS_ROWS
    )


def test_rest_boundary_decoder_returns_canonical_mesh_group_status_rows() -> None:
    payload = _load_fixture("query_mesh_group_status.topology.json")

    result = decode_mesh_group_status_payload(payload)

    assert result.key.label == "rest.mesh-group-status@v1"
    assert (
        result.authority
        == "tests/fixtures/api_contracts/query_mesh_group_status.*.json"
    )
    assert result.canonical == EXPECTED_MESH_GROUP_STATUS_ROWS


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


def test_protocol_boundary_registry_lists_initial_decoder_families() -> None:
    client = LiproProtocolFacade("test-phone-id")

    descriptors = client.contracts.describe_boundary_decoders()
    labels = {descriptor.key.label for descriptor in descriptors}
    channels = {descriptor.key.label: descriptor.channel for descriptor in descriptors}

    assert labels >= {
        "rest.mqtt-config@v1",
        "rest.device-list@v1",
        "rest.device-status@v1",
        "rest.mesh-group-status@v1",
        "mqtt.properties@v1",
    }
    assert channels["rest.mqtt-config@v1"] == "rest"
    assert channels["rest.device-list@v1"] == "rest"
    assert channels["rest.device-status@v1"] == "rest"
    assert channels["rest.mesh-group-status@v1"] == "rest"
    assert channels["mqtt.properties@v1"] == "mqtt"


def test_rest_boundary_decoder_returns_canonical_mqtt_config_with_metadata() -> None:
    payload = _load_fixture("get_mqtt_config.direct.json")

    result = decode_mqtt_config_payload(payload, is_success_code=_is_success_code)

    assert result.key.label == "rest.mqtt-config@v1"
    assert result.authority == "tests/fixtures/api_contracts/get_mqtt_config.*.json"
    assert result.canonical == EXPECTED_MQTT_CONFIG


def test_phase_1_truth_endpoints_are_not_duplicated_into_external_boundary_fixtures() -> None:
    external_boundary_dir = FIXTURE_DIR.parent / "external_boundaries" / "diagnostics_capabilities"

    assert not (external_boundary_dir / "get_city.success.json").exists()
    assert not (external_boundary_dir / "query_user_cloud.success.json").exists()


def test_rest_replay_manifests_reuse_phase_1_contract_fixtures() -> None:
    manifests = iter_replay_manifests(channel="rest")

    assert [manifest.authority_path.name for manifest in manifests] == [
        "get_device_list.compat.json",
        "get_mqtt_config.direct.json",
        "get_mqtt_config.wrapped.json",
        "query_device_status.mixed.json",
        "query_mesh_group_status.topology.json",
    ]
    assert all(
        "tests/fixtures/api_contracts/" in manifest.authority_path.as_posix()
        for manifest in manifests
    )
