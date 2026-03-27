"""Protocol contract boundary decoder suites."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
)
from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.boundary import (
    decode_device_list_payload,
    decode_device_status_payload,
    decode_list_envelope_payload,
    decode_mesh_group_status_payload,
    decode_mqtt_config_payload,
    decode_schedule_json_payload,
)

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "api_contracts"
DEVICE_LIST_FIXTURE_NAMES = ("get_device_list.direct.json", "get_device_list.envelope.json")
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


def _is_success_code(code: object) -> bool:
    return code in {0, "0", "0000"}


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
    list(DEVICE_LIST_FIXTURE_NAMES),
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
    list(DEVICE_LIST_FIXTURE_NAMES),
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


@pytest.mark.parametrize(
    ("fixture_name", "expected_rows_key", "expected_total"),
    [
        ("get_device_list.direct.json", "devices", 3),
        ("get_device_list.envelope.json", "data", None),
    ],
)
def test_protocol_root_contracts_normalize_list_envelope(
    fixture_name: str,
    expected_rows_key: str,
    expected_total: int | None,
) -> None:
    payload = _load_fixture(fixture_name)
    assert isinstance(payload, dict)

    client = LiproProtocolFacade("test-phone-id")
    result = client.contracts.normalize_list_envelope(payload)

    assert result["rows"] == payload[expected_rows_key]
    assert result["has_more"] is True
    if expected_total is not None:
        assert result["total"] == expected_total
    else:
        assert "total" not in result


@pytest.mark.parametrize(
    ("fixture_name", "expected_rows_key", "expected_total"),
    [
        ("get_device_list.direct.json", "devices", 3),
        ("get_device_list.envelope.json", "data", None),
    ],
)
def test_rest_boundary_decoder_returns_canonical_list_envelope(
    fixture_name: str,
    expected_rows_key: str,
    expected_total: int | None,
) -> None:
    payload = _load_fixture(fixture_name)
    assert isinstance(payload, dict)

    result = decode_list_envelope_payload(payload)

    assert result.key.label == "rest.list-envelope@v1"
    assert result.authority == "tests/fixtures/api_contracts/get_device_list.*.json"
    assert result.canonical["rows"] == payload[expected_rows_key]
    assert result.canonical["has_more"] is True
    if expected_total is not None:
        assert result.canonical["total"] == expected_total
    else:
        assert "total" not in result.canonical


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


def test_protocol_root_contracts_normalize_schedule_json() -> None:
    payload = _load_fixture("query_mesh_schedule_json.v1.json")

    client = LiproProtocolFacade("test-phone-id")

    assert client.contracts.normalize_schedule_json(payload) == {
        "days": [1, 3],
        "time": [3600, 7200],
        "evt": [0, 1],
    }


def test_rest_boundary_decoder_returns_canonical_schedule_json() -> None:
    payload = _load_fixture("query_mesh_schedule_json.v1.json")

    result = decode_schedule_json_payload(payload)

    assert result.key.label == "rest.schedule-json@v1"
    assert result.authority == "tests/fixtures/api_contracts/query_mesh_schedule_json.v1.json"
    assert result.canonical == {"days": [1, 3], "time": [3600, 7200], "evt": [0, 1]}


def test_protocol_boundary_registry_lists_initial_decoder_families() -> None:
    client = LiproProtocolFacade("test-phone-id")

    descriptors = client.contracts.describe_boundary_decoders()
    labels = {descriptor.key.label for descriptor in descriptors}
    channels = {descriptor.key.label: descriptor.channel for descriptor in descriptors}

    assert labels >= {
        "mqtt.topic@v1",
        "mqtt.message-envelope@v1",
        "rest.mqtt-config@v1",
        "rest.list-envelope@v1",
        "rest.device-list@v1",
        "rest.device-status@v1",
        "rest.mesh-group-status@v1",
        "rest.schedule-json@v1",
        "mqtt.properties@v1",
    }
    assert channels["mqtt.topic@v1"] == "mqtt"
    assert channels["mqtt.message-envelope@v1"] == "mqtt"
    assert channels["rest.mqtt-config@v1"] == "rest"
    assert channels["rest.list-envelope@v1"] == "rest"
    assert channels["rest.device-list@v1"] == "rest"
    assert channels["rest.device-status@v1"] == "rest"
    assert channels["rest.mesh-group-status@v1"] == "rest"
    assert channels["rest.schedule-json@v1"] == "rest"
    assert channels["mqtt.properties@v1"] == "mqtt"


def test_rest_boundary_decoder_returns_canonical_mqtt_config_with_metadata() -> None:
    payload = _load_fixture("get_mqtt_config.direct.json")

    result = decode_mqtt_config_payload(payload, is_success_code=_is_success_code)

    assert result.key.label == "rest.mqtt-config@v1"
    assert result.authority == "tests/fixtures/api_contracts/get_mqtt_config.*.json"
    assert result.canonical == EXPECTED_MQTT_CONFIG
