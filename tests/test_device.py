"""Tests for Lipro device model."""

from __future__ import annotations

from custom_components.lipro.core.device import (
    LiproDevice,
    is_valid_iot_device_id,
    is_valid_mesh_group_id,
    parse_properties_list,
)


class TestDeviceIdValidation:
    """Tests for device ID validation functions."""

    def test_valid_iot_device_id(self):
        """Test valid IoT device ID format."""
        assert is_valid_iot_device_id("03ab5ccd7caaaaaa")
        assert is_valid_iot_device_id("03abffffffffffff")
        assert is_valid_iot_device_id("03ab000000000000")

    def test_invalid_iot_device_id(self):
        """Test invalid IoT device ID formats."""
        assert not is_valid_iot_device_id("")
        assert not is_valid_iot_device_id("03ab")
        assert not is_valid_iot_device_id("03ab5ccd7c12345")  # Too short
        assert not is_valid_iot_device_id("03ab5ccd7caaaaaa7")  # Too long
        assert not is_valid_iot_device_id("04ab5ccd7c123456")  # Wrong prefix
        assert not is_valid_iot_device_id("03AB5CCD7C123456")  # Uppercase
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
            device_id=123,
            serial="03ab5ccd7caaaaaa",
            name="Test Light",
            device_type=1,
            iot_name="lipro_light",
            room_id=1,
            room_name="Living Room",
        )

        assert device.device_id == 123
        assert device.serial == "03ab5ccd7caaaaaa"
        assert device.name == "Test Light"
        assert device.device_type == 1
        assert device.room_name == "Living Room"
        assert device.is_group is False
        assert device.available is True

    def test_device_type_hex_from_physical_model(self):
        """Test device type hex is determined by physical_model."""
        device = LiproDevice(
            device_id=1,
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
        """Test device type hex falls back to type field."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7caaaaaa",
            name="Unknown Device",
            device_type=6,
            iot_name="",
            physical_model=None,  # No physical model
        )

        # Should fall back to device_type
        assert device.device_type_hex == "ff000006"  # Outlet type

    def test_unique_id(self):
        """Test unique ID generation."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7caaaaaa",
            name="Test",
            device_type=1,
            iot_name="",
        )

        assert device.unique_id == "lipro_03ab5ccd7caaaaaa"

    def test_iot_device_id(self):
        """Test IoT device ID is alias for serial."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7caaaaaa",
            name="Test",
            device_type=1,
            iot_name="",
        )

        assert device.iot_device_id == "03ab5ccd7caaaaaa"
        assert device.iot_device_id == device.serial

    def test_has_valid_iot_id_device(self):
        """Test valid IoT ID check for regular device."""
        device = LiproDevice(
            device_id=1,
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
            device_id=1,
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
            device_id=1,
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
            device_id=2,
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
            device_id=3,
            serial="03ab5ccd7czzzzzz",
            name="Curtain",
            device_type=2,
            iot_name="",
            physical_model="curtain",
        )
        assert curtain.is_curtain is True

        # Switch
        switch = LiproDevice(
            device_id=4,
            serial="03ab000000000004",
            name="Switch",
            device_type=3,
            iot_name="",
            physical_model="switch",
        )
        assert switch.is_switch is True

        # Outlet
        outlet = LiproDevice(
            device_id=5,
            serial="03ab000000000005",
            name="Outlet",
            device_type=6,
            iot_name="",
            physical_model="outlet",
        )
        assert outlet.is_switch is True

        # Heater
        heater = LiproDevice(
            device_id=6,
            serial="03ab000000000006",
            name="Heater",
            device_type=7,
            iot_name="",
            physical_model="heater",
        )
        assert heater.is_heater is True

        # Body sensor
        body_sensor = LiproDevice(
            device_id=7,
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
            device_id=8,
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
            device_id=9,
            serial="03ab000000000009",
            name="Gateway",
            device_type=11,
            iot_name="",
            physical_model="gateway",
        )
        assert gateway.is_gateway is True


class TestDeviceProperties:
    """Tests for device property getters."""

    def test_get_property(self):
        """Test getting raw property value."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={"key1": "value1", "key2": 123},
        )

        assert device.get_property("key1") == "value1"
        assert device.get_property("key2") == 123
        assert device.get_property("missing") is None
        assert device.get_property("missing", "default") == "default"

    def test_get_bool_property(self):
        """Test getting boolean property value."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={
                "bool_true": True,
                "bool_false": False,
                "str_1": "1",
                "str_0": "0",
                "str_true": "true",
                "str_false": "false",
                "int_1": 1,
                "int_0": 0,
            },
        )

        assert device.get_bool_property("bool_true") is True
        assert device.get_bool_property("bool_false") is False
        assert device.get_bool_property("str_1") is True
        assert device.get_bool_property("str_0") is False
        assert device.get_bool_property("str_true") is True
        assert device.get_bool_property("str_false") is False
        assert device.get_bool_property("int_1") is True
        assert device.get_bool_property("int_0") is False
        assert device.get_bool_property("missing") is False
        assert device.get_bool_property("missing", True) is True

    def test_get_int_property(self):
        """Test getting integer property value."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={
                "int_val": 42,
                "str_val": "100",
                "invalid": "abc",
            },
        )

        assert device.get_int_property("int_val") == 42
        assert device.get_int_property("str_val") == 100
        assert device.get_int_property("invalid") == 0
        assert device.get_int_property("missing") == 0
        assert device.get_int_property("missing", 50) == 50

    def test_get_float_property(self):
        """Test getting float property value."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={
                "float_val": 3.14,
                "str_val": "2.5",
                "invalid": "abc",
            },
        )

        assert device.get_float_property("float_val") == 3.14
        assert device.get_float_property("str_val") == 2.5
        assert device.get_float_property("invalid") == 0.0
        assert device.get_float_property("missing") == 0.0
        assert device.get_float_property("missing", 1.5) == 1.5


class TestDeviceStateProperties:
    """Tests for device state properties."""

    def test_light_properties(self):
        """Test light state properties."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={
                "powerState": "1",
                "brightness": "80",
                "temperature": "50",
                "connectState": "1",
            },
        )

        assert device.is_on is True
        assert device.brightness == 80
        assert device.color_temp == 4600  # 50% -> 2700 + 50*3800/100 = 4600K
        assert device.is_connected is True

    def test_curtain_properties(self):
        """Test curtain state properties."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Curtain",
            device_type=2,
            iot_name="",
            physical_model="curtain",
            properties={
                "position": "50",
                "moving": "1",
                "direction": "1",
            },
        )

        assert device.position == 50
        assert device.is_moving is True
        assert device.direction == "opening"

        # Test closing direction
        device.properties["direction"] = "0"
        assert device.direction == "closing"

        # Test no direction
        device.properties["direction"] = None
        assert device.direction is None

    def test_fan_properties(self):
        """Test fan state properties."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Fan Light",
            device_type=4,
            iot_name="",
            physical_model="fanLight",
            properties={
                "fanOnoff": "1",
                "fanGear": "5",
                "fanMode": "1",
            },
        )

        assert device.fan_is_on is True
        assert device.fan_gear == 5
        assert device.fan_mode == 1

    def test_heater_properties(self):
        """Test heater state properties."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Heater",
            device_type=7,
            iot_name="",
            physical_model="heater",
            properties={
                "heaterSwitch": "1",
                "heaterMode": "2",
                "windGear": "3",
                "lightMode": "1",
            },
        )

        assert device.heater_is_on is True
        assert device.heater_mode == 2
        assert device.wind_gear == 3
        assert device.light_mode == 1

    def test_sensor_properties(self):
        """Test sensor state properties."""
        # Body sensor
        body_sensor = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Motion",
            device_type=8,
            iot_name="",
            physical_model="bodySensor",
            properties={
                "human": "1",
                "dark": "0",
                "lowBattery": "0",
            },
        )

        assert body_sensor.is_activated is True
        assert body_sensor.is_dark is False
        assert body_sensor.low_battery is False

        # Door sensor
        door_sensor = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Door",
            device_type=10,
            iot_name="",
            physical_model="doorSensor",
            properties={
                "doorOpen": "1",
                "dark": "1",
                "lowBattery": "1",
            },
        )

        assert door_sensor.door_is_open is True
        assert door_sensor.is_dark is True
        assert door_sensor.low_battery is True


class TestDeviceUpdateProperties:
    """Tests for device property updates."""

    def test_update_properties(self):
        """Test updating device properties."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={"powerState": "0", "brightness": "50"},
        )

        device.update_properties({"powerState": "1", "temperature": "4000"})

        assert device.properties["powerState"] == "1"
        assert device.properties["brightness"] == "50"  # Unchanged
        assert device.properties["temperature"] == "4000"  # Added

    def test_update_properties_availability(self):
        """Test availability is updated based on connectState."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            available=True,
        )

        # Disconnect
        device.update_properties({"connectState": "0"})
        assert device.available is False

        # Reconnect
        device.update_properties({"connectState": "1"})
        assert device.available is True


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

        assert device.device_id == 10001
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
        api_data = {}

        device = LiproDevice.from_api_data(api_data)

        assert device.device_id == 0
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


class TestParsePropertiesList:
    """Tests for parse_properties_list function."""

    def test_parse_properties_list(self):
        """Test parsing properties list."""
        properties_list = [
            {"key": "powerState", "value": "1"},
            {"key": "brightness", "value": "80"},
            {"key": "temperature", "value": "4000"},
        ]

        result = parse_properties_list(properties_list)

        assert result == {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }

    def test_parse_properties_list_empty(self):
        """Test parsing empty properties list."""
        assert parse_properties_list([]) == {}
        assert parse_properties_list(None) == {}

    def test_parse_properties_list_missing_key(self):
        """Test parsing properties list with missing keys."""
        properties_list = [
            {"key": "powerState", "value": "1"},
            {"value": "80"},  # Missing key
            {"key": None, "value": "test"},  # None key
        ]

        result = parse_properties_list(properties_list)

        assert result == {"powerState": "1"}


class TestDeviceGearList:
    """Tests for gear list functionality."""

    def test_gear_list_from_string(self):
        """Test parsing gear list from JSON string."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": '[{"temperature": 50, "brightness": 80}]',
            },
        )

        gear_list = device.gear_list
        assert len(gear_list) == 1
        assert gear_list[0]["temperature"] == 50
        assert gear_list[0]["brightness"] == 80

    def test_gear_list_from_list(self):
        """Test gear list when already a list."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": [{"temperature": 30, "brightness": 60}],
            },
        )

        gear_list = device.gear_list
        assert len(gear_list) == 1
        assert gear_list[0]["temperature"] == 30

    def test_gear_list_empty(self):
        """Test gear list when empty or missing."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={},
        )

        assert device.gear_list == []

    def test_gear_list_invalid_json(self):
        """Test gear list with invalid JSON."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": "invalid json",
            },
        )

        assert device.gear_list == []

    def test_gear_list_caching(self):
        """Test gear list caching."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": '[{"temperature": 50, "brightness": 80}]',
            },
        )

        # First access - parses JSON
        gear_list1 = device.gear_list
        # Second access - uses cache
        gear_list2 = device.gear_list

        assert gear_list1 is gear_list2  # Same object (cached)

    def test_gear_list_cache_cleared_on_update(self):
        """Test gear list cache is cleared when gearList property is updated."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": '[{"temperature": 50, "brightness": 80}]',
            },
        )

        # Access to populate cache
        gear_list1 = device.gear_list
        assert len(gear_list1) == 1

        # Update gearList property
        device.update_properties(
            {
                "gearList": '[{"temperature": 30, "brightness": 60}]',
            }
        )

        # Cache should be cleared, new value returned
        gear_list2 = device.gear_list
        assert len(gear_list2) == 1
        assert gear_list2[0]["temperature"] == 30

    def test_has_gear_presets(self):
        """Test has_gear_presets property."""
        device_with_presets = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": '[{"temperature": 50, "brightness": 80}]',
            },
        )
        assert device_with_presets.has_gear_presets is True

        device_without_presets = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Light",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device_without_presets.has_gear_presets is False

    def test_last_gear_index(self):
        """Test last_gear_index property."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "lastGearIndex": "2",
            },
        )
        assert device.last_gear_index == 2

        device_no_index = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Light",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device_no_index.last_gear_index == -1


class TestDeviceSpecialFeatures:
    """Tests for special device features."""

    def test_sleep_wake_features(self):
        """Test sleep/wake feature detection."""
        device_with_sleep = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Natural Light",
            device_type=1,
            iot_name="",
            properties={
                "sleepAidEnable": "1",
            },
        )
        assert device_with_sleep.has_sleep_wake_features is True
        assert device_with_sleep.sleep_aid_enabled is True

        device_with_wake = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Natural Light",
            device_type=1,
            iot_name="",
            properties={
                "wakeUpEnable": "1",
            },
        )
        assert device_with_wake.has_sleep_wake_features is True
        assert device_with_wake.wake_up_enabled is True

        device_without = LiproDevice(
            device_id=3,
            serial="03ab5ccd7czzzzzz",
            name="Regular Light",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device_without.has_sleep_wake_features is False

    def test_floor_lamp_features(self):
        """Test floor lamp feature detection."""
        device_with_focus = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Floor Lamp",
            device_type=9,
            iot_name="",
            properties={
                "focusMode": "1",
            },
        )
        assert device_with_focus.has_floor_lamp_features is True
        assert device_with_focus.focus_mode_enabled is True

        device_with_body = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Floor Lamp",
            device_type=9,
            iot_name="",
            properties={
                "bodyReactive": "1",
            },
        )
        assert device_with_body.has_floor_lamp_features is True
        assert device_with_body.body_reactive_enabled is True

        device_without = LiproDevice(
            device_id=3,
            serial="03ab5ccd7czzzzzz",
            name="Regular Light",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device_without.has_floor_lamp_features is False

    def test_battery_properties(self):
        """Test battery-related properties."""
        device_with_battery = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Sensor",
            device_type=8,
            iot_name="",
            properties={
                "battery": "85",
                "charging": "0",
            },
        )
        assert device_with_battery.battery_level == 85
        assert device_with_battery.is_charging is False
        assert device_with_battery.has_battery is True

        device_charging = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Sensor",
            device_type=8,
            iot_name="",
            properties={
                "battery": "50",
                "charging": "1",
            },
        )
        assert device_charging.is_charging is True

        device_no_battery = LiproDevice(
            device_id=3,
            serial="03ab5ccd7czzzzzz",
            name="Light",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device_no_battery.battery_level is None
        assert device_no_battery.has_battery is False


class TestDeviceHeaterExtended:
    """Extended tests for heater properties."""

    def test_wind_direction_mode(self):
        """Test wind direction mode property."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Heater",
            device_type=7,
            iot_name="",
            properties={
                "windDirectionMode": "2",
            },
        )
        assert device.wind_direction_mode == 2

        device_default = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Heater",
            device_type=7,
            iot_name="",
            properties={},
        )
        assert device_default.wind_direction_mode == 1  # Default

    def test_aeration_gear(self):
        """Test aeration/ventilation gear property."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Heater",
            device_type=7,
            iot_name="",
            properties={
                "aerationGear": "1",
            },
        )
        assert device.aeration_gear == 1
        assert device.aeration_is_on is True

        device_off = LiproDevice(
            device_id=2,
            serial="03ab5ccd7cyyyyyy",
            name="Heater",
            device_type=7,
            iot_name="",
            properties={
                "aerationGear": "0",
            },
        )
        assert device_off.aeration_gear == 0
        assert device_off.aeration_is_on is False


class TestDeviceTypeHexEdgeCases:
    """Tests for device_type_hex edge cases."""

    def test_unknown_physical_model(self):
        """Test unknown physical model falls back to type field."""
        device = LiproDevice(
            device_id=1,
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
            device_id=1,
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
            device_id=1,
            serial="03ab5ccd7caaaaaa",
            name="Light",
            device_type=1,
            iot_name="",
        )

        assert device.iot_device_id == "03ab5ccd7caaaaaa"
        assert device.iot_device_id == device.serial
