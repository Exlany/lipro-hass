"""Focused facade coverage for the modularized ``LiproDevice`` model."""

from __future__ import annotations

from custom_components.lipro.core.device import (
    DeviceCapabilities,
    DeviceIdentity,
    DeviceNetworkInfo,
    DeviceState,
    LiproDevice,
    parse_properties_list,
)
from tests.core import test_device as legacy_device


def test_lipro_device_exposes_extracted_helper_objects(make_device) -> None:
    """The facade should compose the extracted helper models consistently."""
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
    assert isinstance(device.capabilities, DeviceCapabilities)
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
    """Keep the physical-model precedence from the legacy regression suite."""
    legacy_device.TestLiproDevice().test_device_type_hex_from_physical_model()


def test_lipro_device_type_hex_falls_back_when_model_missing() -> None:
    """Keep the type/iotName fallback rules covered in the new location."""
    legacy_device.TestLiproDevice().test_device_type_hex_fallback()
    legacy_device.TestLiproDevice().test_device_type_hex_from_iot_name_literal_fallback()


def test_lipro_device_ids_and_platforms_stay_stable() -> None:
    """Keep facade identifiers and platform mapping behavior stable."""
    legacy_device.TestLiproDevice().test_unique_id()
    legacy_device.TestLiproDevice().test_platforms()
    legacy_device.TestLiproDevice().test_has_valid_iot_id_device()
    legacy_device.TestLiproDevice().test_has_valid_iot_id_group()


def test_lipro_device_from_api_data_keeps_identity_and_group_rules() -> None:
    """Keep API payload coercion aligned with the legacy creation matrix."""
    legacy_device.TestDeviceFromApiData().test_from_api_data()
    legacy_device.TestDeviceFromApiData().test_from_api_data_minimal()
    legacy_device.TestDeviceFromApiData().test_from_api_data_group()
    legacy_device.TestDeviceFromApiData().test_from_api_data_group_string_false_values()
    legacy_device.TestDeviceFromApiData().test_from_api_data_group_string_true_values()


def test_lipro_device_from_api_data_keeps_fan_defaults() -> None:
    """Keep iotName-based fan gear defaults visible in the facade tests."""
    legacy_device.TestDeviceFromApiData().test_from_api_data_fan_model_uses_model_default_max_gear()
    legacy_device.TestDeviceFromApiData().test_from_api_data_unknown_fan_model_uses_global_default_max_gear()


def test_parse_properties_list_normalizes_valid_entries() -> None:
    """Keep the list-to-dict parsing bridge covered after the split."""
    legacy_device.TestParsePropertiesList().test_parse_properties_list()
    legacy_device.TestParsePropertiesList().test_parse_properties_list_empty()
    legacy_device.TestParsePropertiesList().test_parse_properties_list_missing_key()


def test_parse_properties_list_returns_normalized_keys() -> None:
    """The facade helper should still normalize camelCase property keys."""
    result = parse_properties_list(
        [
            {"key": "connectState", "value": "0"},
            {"key": "wifiRssi", "value": "-72"},
            {"key": "bleMac", "value": "11:22:33:44:55:66"},
        ]
    )

    assert result == {
        "connectState": "0",
        "wifi_rssi": "-72",
        "bleMac": "11:22:33:44:55:66",
    }


def test_lipro_device_from_api_data_exposes_identity_snapshot() -> None:
    """The facade should surface the extracted identity object after creation."""
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
