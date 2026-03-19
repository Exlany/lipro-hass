"""Golden-fixture protocol contract tests for north-star API boundaries."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.const.api import PATH_GET_CITY, PATH_QUERY_USER_CLOUD
from custom_components.lipro.core.api import LiproRestFacade
from custom_components.lipro.core.api.diagnostics_api_service import (
    get_city,
    query_user_cloud,
)
from custom_components.lipro.core.api.mqtt_api_service import (
    _extract_mqtt_config_payload,
)
from custom_components.lipro.core.api.session_state import RestSessionState
from custom_components.lipro.core.api.types import JsonObject
from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.boundary import (
    decode_device_list_payload,
    decode_device_status_payload,
    decode_list_envelope_payload,
    decode_mesh_group_status_payload,
    decode_mqtt_config_payload,
    decode_schedule_json_payload,
)
from custom_components.lipro.core.protocol.diagnostics_context import (
    ProtocolDiagnosticsContext,
)
from custom_components.lipro.core.protocol.facade import LiproMqttFacade
from custom_components.lipro.core.protocol.session import ProtocolSessionState
from custom_components.lipro.core.protocol.telemetry import ProtocolTelemetry
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


def _require_mapping_response(_path: str, payload: object) -> JsonObject:
    assert isinstance(payload, dict)
    return cast(JsonObject, dict(payload))


def _is_success_code(code: object) -> bool:
    return code in {0, "0", "0000"}


def test_lipro_protocol_facade_is_available_as_unified_protocol_root() -> None:
    assert LiproProtocolFacade.__name__ == "LiproProtocolFacade"


def test_lipro_rest_facade_is_available_as_phase_2_rest_child_facade() -> None:
    assert LiproRestFacade.__name__ == "LiproRestFacade"


def _build_mqtt_facade(client: MagicMock) -> tuple[LiproMqttFacade, ProtocolTelemetry]:
    telemetry = ProtocolTelemetry()
    session_state = ProtocolSessionState(
        RestSessionState(
            phone_id="test-phone-id",
            session=None,
            request_timeout=30,
            entry_id="entry-1",
        )
    )
    diagnostics_context = ProtocolDiagnosticsContext(
        session_state=session_state,
        telemetry=telemetry,
        entry_id="entry-1",
    )
    return (
        LiproMqttFacade(
            client,
            session_state=session_state,
            telemetry=telemetry,
            diagnostics_context=diagnostics_context,
        ),
        telemetry,
    )


@pytest.mark.asyncio
async def test_lipro_mqtt_facade_records_transport_error_and_reraises() -> None:
    client = MagicMock()
    client.is_connected = False
    client.subscribed_devices = set()
    client.subscribed_count = 0
    client.last_error = None
    client.start = AsyncMock(side_effect=RuntimeError("boom"))

    mqtt_facade, telemetry = _build_mqtt_facade(client)

    with pytest.raises(RuntimeError, match="boom"):
        await mqtt_facade.start(["03ab5ccd7c000001"])

    assert telemetry.mqtt_start_count == 1
    assert telemetry.mqtt_last_error_type == "RuntimeError"
    assert telemetry.mqtt_last_error_stage == "start"


@pytest.mark.asyncio
async def test_lipro_mqtt_facade_reraises_cancelled_without_recording_error() -> None:
    client = MagicMock()
    client.is_connected = False
    client.subscribed_devices = set()
    client.subscribed_count = 0
    client.last_error = None
    client.start = AsyncMock(side_effect=asyncio.CancelledError)

    mqtt_facade, telemetry = _build_mqtt_facade(client)

    with pytest.raises(asyncio.CancelledError):
        await mqtt_facade.start(["03ab5ccd7c000001"])

    assert telemetry.mqtt_start_count == 1
    assert telemetry.mqtt_last_error_type is None
    assert telemetry.mqtt_last_error_stage is None


def test_lipro_rest_facade_uses_explicit_surface_instead_of_dynamic_delegation() -> None:
    for base in LiproRestFacade.__mro__:
        if base is object:
            continue
        assert "__getattr__" not in base.__dict__
        assert "__dir__" not in base.__dict__


def test_lipro_rest_facade_no_longer_exports_aggregate_endpoint_mixin() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "endpoints"
        / "__init__.py"
    ).read_text(encoding="utf-8")
    assert "_ClientEndpointsMixin" not in module_text


def test_schedule_api_service_no_longer_shapes_rest_schedule_surface() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "client.py"
    ).read_text(encoding="utf-8")
    assert "ScheduleApiService" not in module_text


def test_protocol_root_owns_shared_rest_session_and_request_policy() -> None:
    client = LiproProtocolFacade("test-phone-id")

    assert client.rest._session_state is client.session_state.rest_state
    assert client.rest._request_policy is client.request_policy


def test_protocol_root_file_keeps_rest_port_and_mqtt_child_out_of_root_body() -> None:
    module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "facade.py"
    ).read_text(encoding="utf-8")

    assert "from .mqtt_facade import" in module_text
    assert "from .rest_port import" in module_text
    assert "class LiproMqttFacade:" not in module_text
    assert "class _RestFacadePort(" not in module_text


def test_rest_child_facade_file_uses_local_request_and_endpoint_collaborators() -> None:
    client_module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "client.py"
    ).read_text(encoding="utf-8")
    facade_module_text = (
        Path(__file__).resolve().parents[3]
        / "custom_components"
        / "lipro"
        / "core"
        / "api"
        / "rest_facade.py"
    ).read_text(encoding="utf-8")

    assert "from .rest_facade import LiproRestFacade" in client_module_text
    assert "RestAuthRecoveryCoordinator" in facade_module_text
    assert "RestTransportExecutor" in facade_module_text
    assert "RestEndpointSurface" in facade_module_text
    assert "RestSessionState" in facade_module_text


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


@pytest.mark.parametrize(
    ("fixture_name", "expected_rows_key", "expected_total"),
    [
        ("get_device_list.direct.json", "devices", 3),
        ("get_device_list.compat.json", "data", None),
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
        ("get_device_list.compat.json", "data", None),
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


def test_phase_1_truth_endpoints_are_not_duplicated_into_external_boundary_fixtures() -> None:
    external_boundary_dir = FIXTURE_DIR.parent / "external_boundaries" / "diagnostics_capabilities"

    assert not (external_boundary_dir / "get_city.success.json").exists()
    assert not (external_boundary_dir / "query_user_cloud.success.json").exists()


def test_rest_replay_manifests_reuse_phase_1_contract_fixtures() -> None:
    manifests = iter_replay_manifests(channel="rest")

    assert [manifest.authority_path.name for manifest in manifests] == [
        "get_device_list.compat.json",
        "get_device_list.compat.json",
        "get_mqtt_config.direct.json",
        "get_mqtt_config.wrapped.json",
        "query_device_status.mixed.json",
        "query_mesh_group_status.topology.json",
        "query_mesh_schedule_json.v1.json",
    ]
    assert all(
        "tests/fixtures/api_contracts/" in manifest.authority_path.as_posix()
        for manifest in manifests
    )
