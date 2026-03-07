"""Tests for MQTT setup helper functions."""

from __future__ import annotations

from custom_components.lipro.const.config import CONF_BIZ_ID, CONF_USER_ID
from custom_components.lipro.core.coordinator.mqtt.setup import (
    build_mqtt_subscription_device_ids,
    extract_mqtt_encrypted_credentials,
    iter_mesh_group_serials,
    resolve_mqtt_biz_id,
)
from custom_components.lipro.core.device import LiproDevice


def _make_device(*, serial: str, is_group: bool = False) -> LiproDevice:
    return LiproDevice(
        device_number=1,
        serial=serial,
        name=serial,
        device_type=1,
        iot_name="lipro_light",
        is_group=is_group,
    )


def test_extract_mqtt_encrypted_credentials_success() -> None:
    assert extract_mqtt_encrypted_credentials(
        {"accessKey": "enc-ak", "secretKey": "enc-sk"}
    ) == ("enc-ak", "enc-sk")


def test_extract_mqtt_encrypted_credentials_missing_value_returns_none() -> None:
    assert extract_mqtt_encrypted_credentials({"accessKey": "enc-ak"}) is None
    assert extract_mqtt_encrypted_credentials({"secretKey": "enc-sk"}) is None
    assert extract_mqtt_encrypted_credentials({}) is None


def test_resolve_mqtt_biz_id_prefers_biz_id_with_prefix_removal() -> None:
    assert resolve_mqtt_biz_id({CONF_BIZ_ID: "lip_10001", CONF_USER_ID: 88}) == "10001"


def test_resolve_mqtt_biz_id_falls_back_to_user_id() -> None:
    assert resolve_mqtt_biz_id({CONF_USER_ID: 12345}) == "12345"


def test_resolve_mqtt_biz_id_missing_returns_none() -> None:
    assert resolve_mqtt_biz_id({}) is None


def test_build_mqtt_subscription_device_ids_prefers_mesh_groups() -> None:
    devices = {
        "dev1": _make_device(serial="dev1"),
        "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
    }
    assert build_mqtt_subscription_device_ids(devices) == ["mesh_group_1"]


def test_build_mqtt_subscription_device_ids_falls_back_to_direct_devices() -> None:
    devices = {
        "dev1": _make_device(serial="dev1"),
        "dev2": _make_device(serial="dev2"),
    }
    assert build_mqtt_subscription_device_ids(devices) == ["dev1", "dev2"]


def test_iter_mesh_group_serials_only_returns_groups() -> None:
    devices = {
        "dev1": _make_device(serial="dev1"),
        "mesh_group_1": _make_device(serial="mesh_group_1", is_group=True),
        "mesh_group_2": _make_device(serial="mesh_group_2", is_group=True),
    }
    assert iter_mesh_group_serials(devices) == ["mesh_group_1", "mesh_group_2"]
