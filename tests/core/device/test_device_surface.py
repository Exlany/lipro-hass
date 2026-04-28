"""Tests for Lipro device model."""

from __future__ import annotations

from typing import Any

from custom_components.lipro.const.categories import DeviceCategory
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.core.utils.identifiers import (
    is_valid_iot_device_id,
    is_valid_mesh_group_id,
)


class TestDeviceIdValidation:
    """Tests for device ID validation functions."""

    def test_valid_iot_device_id(self):
        """Test valid IoT device ID format."""
        assert is_valid_iot_device_id("03ab5ccd7caaaaaa")
        assert is_valid_iot_device_id("03abffffffffffff")
        assert is_valid_iot_device_id("03ab000000000000")
        assert is_valid_iot_device_id("03AB5CCD7C123456")

    def test_invalid_iot_device_id(self):
        """Test invalid IoT device ID formats."""
        assert not is_valid_iot_device_id("")
        assert not is_valid_iot_device_id("03ab")
        assert not is_valid_iot_device_id("03ab5ccd7c12345")  # Too short
        assert not is_valid_iot_device_id("03ab5ccd7caaaaaa7")  # Too long
        assert not is_valid_iot_device_id("04ab5ccd7c123456")  # Wrong prefix
        assert not is_valid_iot_device_id("03ab5ccd7c12345g")  # Invalid hex

    def test_valid_mesh_group_id(self):
        """Test valid Mesh group ID format."""
        assert is_valid_mesh_group_id("mesh_group_10001")
        assert is_valid_mesh_group_id("mesh_group_0")
        assert is_valid_mesh_group_id("mesh_group_100016789")

    def test_invalid_mesh_group_id(self):
        """Test invalid Mesh group ID formats."""
        assert not is_valid_mesh_group_id("")
        assert not is_valid_mesh_group_id("mesh_group_")
        assert not is_valid_mesh_group_id("mesh_group_abc")
        assert not is_valid_mesh_group_id("meshgroup_123")
        assert not is_valid_mesh_group_id("MESH_GROUP_123")


class TestLiproDevice:
    """Tests for LiproDevice class."""

    def test_create_device(self):
        """Test creating a device."""
        device = LiproDevice(
            device_number=123,
            serial="03ab5ccd7caaaaaa",
            name="Test Light",
            device_type=1,
            iot_name="lipro_light",
            room_id=1,
            room_name="Living Room",
        )

        assert device.device_number == 123
        assert device.serial == "03ab5ccd7caaaaaa"
        assert device.name == "Test Light"
        assert device.device_type == 1
        assert device.room_name == "Living Room"
        assert device.is_group is False
        assert device.available is True

    def test_device_type_hex_from_physical_model(self):
        """Test device type hex is determined by physical_model."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Light Strip",
            device_type=6,  # This is outlet type in Mesh protocol
            iot_name="",
            physical_model="light",  # But physical model says it's a light
        )

        # Should use physical_model, not device_type
        assert device.device_type_hex == "ff000001"  # LED type
        assert device.is_light is True
        assert device.is_switch is False

    def test_device_type_hex_fallback(self):
        """Test device type hex falls back to type field when not in map."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Unknown Device",
            device_type=99,  # Unknown type not in DEVICE_TYPE_MAP
            iot_name="",
            physical_model=None,  # No physical model
        )

        # Should fall back to formatted device_type
        assert device.device_type_hex == "ff000063"  # 99 in hex = 0x63

    def test_device_type_hex_from_iot_name_literal_fallback(self):
        """When physicalModel is missing, iotName literal should resolve type."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Fan by iotName",
            device_type=1,
            iot_name="fanLight",
            physical_model=None,
        )

        assert device.device_type_hex == "ff000004"

    def test_device_type_hex_from_iot_name_is_case_insensitive(self):
        """iotName fallback lookup should be case-insensitive."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="FloorLight by iotName",
            device_type=1,
            iot_name="FloorLight",
            physical_model=None,
        )

        assert device.device_type_hex == "ff000009"

    def test_unique_id(self):
        """Test unique ID generation."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Test",
            device_type=1,
            iot_name="",
        )

        assert device.unique_id == "lipro_03ab5ccd7caaaaaa"

    def test_iot_device_id(self):
        """Test IoT device ID is alias for serial."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Test",
            device_type=1,
            iot_name="",
        )

        assert device.iot_device_id == "03ab5ccd7caaaaaa"
        assert device.iot_device_id == device.serial

    def test_category(self):
        """category property should expose the host-neutral device kind."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Test Light",
            device_type=1,
            iot_name="",
            physical_model="light",
        )

        assert device.category == DeviceCategory.LIGHT
        assert device.capabilities.category == DeviceCategory.LIGHT

    def test_has_valid_iot_id_device(self):
        """Test valid IoT ID check for regular device."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Test",
            device_type=1,
            iot_name="",
            is_group=False,
        )

        assert device.has_valid_iot_id is True

    def test_has_valid_iot_id_group(self):
        """Test valid IoT ID check for mesh group."""
        device = LiproDevice(
            device_number=1,
            serial="mesh_group_10001",
            name="Test Group",
            device_type=1,
            iot_name="",
            is_group=True,
        )

        assert device.has_valid_iot_id is True

    def test_device_type_checks(self):
        """Test device type check properties."""
        # Light
        light = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
        )
        assert light.is_light is True
        assert light.is_fan_light is False

        # Fan light
        fan_light = LiproDevice(
            device_number=2,
            serial="03ab5ccd7cyyyyyy",
            name="Fan Light",
            device_type=4,
            iot_name="",
            physical_model="fanLight",
        )
        assert fan_light.is_fan_light is True
        assert fan_light.is_light is False

        # Curtain
        curtain = LiproDevice(
            device_number=3,
            serial="03ab5ccd7czzzzzz",
            name="Curtain",
            device_type=2,
            iot_name="",
            physical_model="curtain",
        )
        assert curtain.is_curtain is True

        # Switch
        switch = LiproDevice(
            device_number=4,
            serial="03ab000000000004",
            name="Switch",
            device_type=3,
            iot_name="",
            physical_model="switch",
        )
        assert switch.is_switch is True

        # Outlet
        outlet = LiproDevice(
            device_number=5,
            serial="03ab000000000005",
            name="Outlet",
            device_type=6,
            iot_name="",
            physical_model="outlet",
        )
        assert outlet.is_switch is True
        assert outlet.is_outlet is True

        # Heater
        heater = LiproDevice(
            device_number=6,
            serial="03ab000000000006",
            name="Heater",
            device_type=7,
            iot_name="",
            physical_model="heater",
        )
        assert heater.is_heater is True

        # Body sensor
        body_sensor = LiproDevice(
            device_number=7,
            serial="03ab000000000007",
            name="Motion",
            device_type=8,
            iot_name="",
            physical_model="bodySensor",
        )
        assert body_sensor.is_body_sensor is True
        assert body_sensor.is_sensor is True

        # Door sensor
        door_sensor = LiproDevice(
            device_number=8,
            serial="03ab000000000008",
            name="Door",
            device_type=10,
            iot_name="",
            physical_model="doorSensor",
        )
        assert door_sensor.is_door_sensor is True
        assert door_sensor.is_sensor is True

        # Gateway
        gateway = LiproDevice(
            device_number=9,
            serial="03ab000000000009",
            name="Gateway",
            device_type=11,
            iot_name="",
            physical_model="gateway",
        )
        assert gateway.is_gateway is True


class TestDeviceFromApiData:
    """Tests for creating device from API data."""

    def test_from_api_data(self):
        """Test creating device from API response."""
        api_data = {
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

        device = LiproDevice.from_api_data(api_data)

        assert device.device_number == 10001
        assert device.serial == "03ab5ccd7caaaaaa"
        assert device.name == "Living Room Light"
        assert device.device_type == 1
        assert device.iot_name == "lipro_led"
        assert device.room_id == 100
        assert device.room_name == "Living Room"
        assert device.is_group is False
        assert device.product_id == 999
        assert device.physical_model == "light"

    def test_from_api_data_minimal(self):
        """Test creating device from minimal API data."""
        api_data: dict[str, Any] = {}

        device = LiproDevice.from_api_data(api_data)

        assert device.device_number == 0
        assert device.serial == ""
        assert device.name == "Unknown"
        assert device.device_type == 1

    def test_from_api_data_group(self):
        """Test creating device from group API data."""
        api_data = {
            "deviceId": 100,
            "serial": "mesh_group_10001",
            "deviceName": "All Lights",
            "type": 1,
            "iotName": "",
            "group": True,  # Alternative field name
        }

        device = LiproDevice.from_api_data(api_data)

        assert device.is_group is True

    def test_from_api_data_group_string_false_values(self):
        """Test string false-like values are not treated as True."""
        device = LiproDevice.from_api_data(
            {
                "serial": "mesh_group_10001",
                "isGroup": "0",
                "group": "false",
            }
        )
        assert device.is_group is False

    def test_from_api_data_group_string_true_values(self):
        """Test string true-like values are treated as True."""
        from_is_group = LiproDevice.from_api_data({"isGroup": "1"})
        from_group = LiproDevice.from_api_data({"group": "true"})
        mixed = LiproDevice.from_api_data({"isGroup": "false", "group": "1"})

        assert from_is_group.is_group is True
        assert from_group.is_group is True
        assert mixed.is_group is True

    def test_from_api_data_group_unknown_values_default_false(self):
        """Test unknown boolean-like values default to False."""
        device = LiproDevice.from_api_data(
            {
                "serial": "mesh_group_10001",
                "isGroup": "offline",
                "group": {"value": True},
            }
        )
        assert device.is_group is False

    def test_from_api_data_fan_model_uses_model_default_max_gear(self):
        """Known fan model should use iotName-based default max gear."""
        device = LiproDevice.from_api_data(
            {
                "serial": "mesh_group_12345",
                "deviceName": "Fan Light",
                "iotName": "21F1",
                "physicalModel": "fanLight",
            }
        )
        assert device.default_max_fan_gear_in_model == 10
        assert device.max_fan_gear == 10

    def test_from_api_data_unknown_fan_model_uses_global_default_max_gear(self):
        """Unknown fan model should fallback to integration default max gear."""
        device = LiproDevice.from_api_data(
            {
                "serial": "mesh_group_67890",
                "deviceName": "Fan Light",
                "iotName": "unknown_model",
                "physicalModel": "fanLight",
            }
        )
        assert device.default_max_fan_gear_in_model == 6
        assert device.max_fan_gear == 6


class TestDeviceTypeHexEdgeCases:
    """Tests for device_type_hex edge cases."""

    def test_unknown_physical_model(self):
        """Test unknown physical model falls back to type field."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Unknown Device",
            device_type=99,
            iot_name="",
            physical_model="unknownModel",  # Unknown model
        )

        # Should fall back to type field with ff prefix
        assert device.device_type_hex == "ff000063"  # 99 in hex

    def test_device_type_hex_with_known_type(self):
        """Test device_type_hex with known type but no physical_model."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model=None,
        )

        assert device.device_type_hex == "ff000001"


class TestDeviceIotId:
    """Tests for IoT ID property."""

    def test_iot_device_id_alias(self):
        """Test iot_device_id is alias for serial."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7caaaaaa",
            name="Light",
            device_type=1,
            iot_name="",
        )

        assert device.iot_device_id == "03ab5ccd7caaaaaa"
        assert device.iot_device_id == device.serial
