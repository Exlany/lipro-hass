"""Focused facade coverage for the modularized ``LiproDevice`` model."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from custom_components.lipro.core.capability import CapabilitySnapshot
from custom_components.lipro.core.device import (
    DeviceIdentity,
    DeviceNetworkInfo,
    DeviceState,
    LiproDevice,
    parse_properties_list,
)


def test_lipro_device_surface_is_explicit() -> None:
    """The device facade should no longer rely on dynamic attribute delegation."""
    assert "__getattr__" not in LiproDevice.__dict__
    assert "is_light" in LiproDevice.__dict__
    assert "brightness" in LiproDevice.__dict__
    assert "wifi_rssi" in LiproDevice.__dict__
    assert "gear_list" in LiproDevice.__dict__


def test_lipro_device_exposes_extracted_helper_objects(make_device) -> None:
    """The facade should compose extracted helper models consistently."""
    device = make_device(
        "light",
        serial="03ab5ccd7c654321",
        name="Desk Light",
        room_name="Office",
        properties={
            "powerState": "1",
            "brightness": "66",
            "temperature": "50",
            "connectState": "1",
            "ip": "192.168.1.88",
            "wifi_ssid": "Home WiFi",
            "wifi_rssi": "-65",
            "gateway": "1",
        },
    )

    assert isinstance(device.identity, DeviceIdentity)
    assert isinstance(device.capabilities, CapabilitySnapshot)
    assert isinstance(device.state, DeviceState)
    assert isinstance(device.network_info, DeviceNetworkInfo)
    assert device.identity.serial == device.serial
    assert device.identity.room_name == device.room_name
    assert device.capabilities.category == device.category
    assert device.capabilities.supports_color_temp == device.supports_color_temp
    assert device.state.brightness == device.brightness
    assert device.state.color_temp == device.color_temp
    assert device.network_info.ip_address == device.ip_address
    assert device.network_info.wifi_ssid == device.wifi_ssid
    assert device.network_info.wifi_rssi == device.wifi_rssi
    assert device.network_info.is_mesh_gateway == device.is_mesh_gateway


def test_lipro_device_type_hex_prefers_physical_model() -> None:
    """Physical model should override mismatched raw device type codes."""
    device = LiproDevice(
        device_number=1,
        serial="03ab5ccd7caaaaaa",
        name="Light Strip",
        device_type=6,
        iot_name="",
        physical_model="light",
    )

    assert device.device_type_hex == "ff000001"
    assert device.is_light is True
    assert device.is_switch is False


def test_lipro_device_type_hex_falls_back_to_type_and_iot_name() -> None:
    """When physical model is absent, fallback order should remain stable."""
    from_type = LiproDevice(
        device_number=1,
        serial="03ab5ccd7caaaaab",
        name="Unknown Device",
        device_type=99,
        iot_name="",
        physical_model=None,
    )
    from_iot_name = LiproDevice(
        device_number=2,
        serial="03ab5ccd7caaaaac",
        name="Fan by iotName",
        device_type=1,
        iot_name="fanLight",
        physical_model=None,
    )
    case_insensitive = LiproDevice(
        device_number=3,
        serial="03ab5ccd7caaaaad",
        name="FloorLight by iotName",
        device_type=1,
        iot_name="FloorLight",
        physical_model=None,
    )

    assert from_type.device_type_hex == "ff000063"
    assert from_iot_name.device_type_hex == "ff000004"
    assert case_insensitive.device_type_hex == "ff000009"


def test_lipro_device_identity_helpers_and_valid_iot_ids(make_device) -> None:
    """Facade identity helpers should remain stable for entities and groups."""
    device = make_device("light", serial="03ab5ccd7caaaaaa", name="Test Light")
    group = make_device(
        "light",
        serial="mesh_group_10001",
        name="All Lights",
        is_group=True,
    )

    assert device.unique_id == "lipro_03ab5ccd7caaaaaa"
    assert device.iot_device_id == device.serial
    assert device.has_valid_iot_id is True
    assert device.fan_speed_range == (1, device.max_fan_gear)
    assert group.has_valid_iot_id is True


def test_lipro_device_from_api_data_coerces_group_flags_and_fan_defaults() -> None:
    """Factory parsing should preserve grouping and model fan defaults."""
    standard = LiproDevice.from_api_data(
        {
            "deviceId": 10001,
            "serial": "03ab5ccd7caaaaaa",
            "deviceName": "Living Room Light",
            "type": 1,
            "iotName": "lipro_led",
            "roomId": 100,
            "roomName": "Living Room",
            "isGroup": False,
            "productId": 999,
            "physicalModel": "light",
        }
    )
    true_group = LiproDevice.from_api_data(
        {"serial": "mesh_group_10001", "isGroup": "false", "group": "1"}
    )
    false_group = LiproDevice.from_api_data(
        {"serial": "mesh_group_10001", "isGroup": "0", "group": "false"}
    )
    known_fan = LiproDevice.from_api_data(
        {
            "serial": "mesh_group_12345",
            "deviceName": "Fan Light",
            "iotName": "21F1",
            "physicalModel": "fanLight",
        }
    )
    unknown_fan = LiproDevice.from_api_data(
        {
            "serial": "mesh_group_67890",
            "deviceName": "Fan Light",
            "iotName": "unknown_model",
            "physicalModel": "fanLight",
        }
    )

    assert standard.device_number == 10001
    assert standard.room_id == 100
    assert standard.product_id == 999
    assert standard.is_group is False
    assert true_group.is_group is True
    assert false_group.is_group is False
    assert known_fan.default_max_fan_gear_in_model == 10
    assert known_fan.max_fan_gear == 10
    assert unknown_fan.default_max_fan_gear_in_model == 6
    assert unknown_fan.max_fan_gear == 6


def test_parse_properties_list_normalizes_keys_and_skips_invalid_entries() -> None:
    """Property parser should ignore broken rows and normalize alias keys."""
    result = parse_properties_list(
        [
            {"key": "connectState", "value": "0"},
            {"key": "wifiRssi", "value": "-72"},
            {"key": "bleMac", "value": "11:22:33:44:55:66"},
            {"value": "missing key"},
            object(),
        ]
    )

    assert result == {
        "connectState": "0",
        "wifi_rssi": "-72",
        "bleMac": "11:22:33:44:55:66",
    }
    assert parse_properties_list([]) == {}
    assert parse_properties_list(None) == {}


def test_lipro_device_update_properties_refreshes_state_availability_and_extras_cache(
    make_device,
) -> None:
    """Runtime property updates should refresh delegated state and extras data."""
    device = make_device(
        "light",
        properties={
            "connectState": "1",
            "brightness": "20",
            "gearList": '[{"label":"Night"}]',
        },
    )

    available_before = device.available
    brightness_before = device.brightness
    gear_list_before = device.extras.gear_list

    assert available_before is True
    assert brightness_before == 20
    assert gear_list_before == [{"label": "Night"}]

    device.update_properties(
        {
            "connectState": "0",
            "brightness": "88",
            "gearList": '[{"label":"Read"}]',
        }
    )

    available_after = device.available
    brightness_after = device.brightness
    gear_list_after = device.extras.gear_list

    assert available_after is False
    assert brightness_after == 88
    assert gear_list_after == [{"label": "Read"}]


def test_lipro_device_from_api_data_exposes_identity_snapshot() -> None:
    """Facade identity property should surface the parsed immutable snapshot."""
    device = LiproDevice.from_api_data(
        {
            "deviceId": "123",
            "serial": "03ab5ccd7caaaaaa",
            "deviceName": "Living Room",
            "type": 6,
            "iotName": "lipro_led",
            "roomId": "99",
            "roomName": "Bedroom",
            "productId": 888,
            "physicalModel": "light",
        }
    )

    assert device.identity == DeviceIdentity(
        device_number=123,
        serial="03ab5ccd7caaaaaa",
        name="Living Room",
        device_type=6,
        iot_name="lipro_led",
        room_id=99,
        room_name="Bedroom",
        product_id=888,
        physical_model="light",
    )


def test_lipro_device_last_gear_index_returns_negative_one_for_invalid_value() -> None:
    device = LiproDevice(
        device_number=1,
        serial="03ab5ccd7cbbbbbb",
        name="Desk Light",
        device_type=1,
        iot_name="lipro_led",
        properties={"lastGearIndex": object()},
    )

    assert device.last_gear_index == -1


def test_lipro_device_unknown_attribute_raises_attribute_error(make_device) -> None:
    device = make_device("light")

    with pytest.raises(AttributeError, match="has no attribute"):
        _ = device.not_a_real_attribute


def test_lipro_device_outlet_power_info_copies_payload_and_clears_legacy_sidecar(make_device) -> None:
    device = make_device("outlet", extra_data={"power_info": {"voltage": 220}})
    payload = {"voltage": 220, "power": 10}

    device.outlet_power_info = payload
    payload["power"] = 20

    assert device.outlet_power_info == {"voltage": 220, "power": 10}
    assert "power_info" not in device.extra_data


def test_lipro_device_recent_mqtt_update_window(make_device) -> None:
    device = make_device("light")

    assert device.has_recent_mqtt_update() is False

    device.mark_mqtt_update(timestamp=100.0)

    with patch("custom_components.lipro.core.device.device.monotonic", return_value=250.0):
        assert device.has_recent_mqtt_update(stale_window_seconds=180.0) is True
    with patch("custom_components.lipro.core.device.device.monotonic", return_value=281.0):
        assert device.has_recent_mqtt_update(stale_window_seconds=180.0) is False
