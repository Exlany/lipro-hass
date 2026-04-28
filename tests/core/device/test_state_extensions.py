"""Tests for Lipro device model."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice


class TestDeviceProperties:
    """Tests for device property getters."""

    def test_get_property(self):
        """Test getting raw property value."""
        device = LiproDevice(
            device_number=1,
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
            device_number=1,
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
                "list_empty": [],
                "list_nonempty": [1],
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
        assert device.get_bool_property("list_empty", True) is False
        assert device.get_bool_property("list_nonempty") is True
        assert device.get_bool_property("missing") is False
        assert device.get_bool_property("missing", True) is True

    def test_get_bool_property_strips_whitespace(self):
        """Test boolean string values are normalized with surrounding spaces."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={
                "str_true_padded": "  true  ",
                "str_one_padded": " 1 ",
                "str_false_padded": " false ",
                "str_zero_padded": " 0 ",
            },
        )

        assert device.get_bool_property("str_true_padded") is True
        assert device.get_bool_property("str_one_padded") is True
        assert device.get_bool_property("str_false_padded") is False
        assert device.get_bool_property("str_zero_padded") is False

    def test_get_int_property(self):
        """Test getting integer property value."""
        device = LiproDevice(
            device_number=1,
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
            device_number=1,
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
            device_number=1,
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
            device_number=1,
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
            device_number=1,
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

    def test_fan_properties_ignore_alias_when_canonical_present(self):
        """Alias keys should not override canonical properties when both exist."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Fan Light",
            device_type=4,
            iot_name="",
            physical_model="fanLight",
            properties={
                "fanOnoff": "1",
                "fanOnOff": "0",
                "fanGear": "5",
            },
        )

        assert device.fan_is_on is True

    def test_heater_properties(self):
        """Test heater state properties."""
        device = LiproDevice(
            device_number=1,
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
            device_number=1,
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
            device_number=2,
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
            device_number=1,
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
            device_number=1,
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


class TestDeviceColorTempRange:
    """Tests for device-specific color temperature range."""

    def test_custom_color_temp_range(self):
        """Test color_temp uses device-specific range."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            min_color_temp_kelvin=3000,
            max_color_temp_kelvin=5700,
            properties={"temperature": "0"},
        )
        assert device.color_temp == 3000

        device.properties["temperature"] = "100"
        assert device.color_temp == 5700

        device.properties["temperature"] = "50"
        assert device.color_temp == 3000 + int(50 * 2700 / 100)

    def test_single_color_temp_device(self):
        """Test supports_color_temp is False when range is 0."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            min_color_temp_kelvin=0,
            max_color_temp_kelvin=0,
        )
        assert device.supports_color_temp is False

    def test_percent_to_kelvin_for_device_zero_range_returns_min(self):
        """Degenerate device range should return min kelvin."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            min_color_temp_kelvin=4000,
            max_color_temp_kelvin=4000,
        )
        assert device.supports_color_temp is True
        assert device.percent_to_kelvin_for_device(0) == 4000
        assert device.percent_to_kelvin_for_device(100) == 4000

    def test_color_temp_conversions_fall_back_when_unsupported(self):
        """When device range is unavailable, conversions use global defaults."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            min_color_temp_kelvin=0,
            max_color_temp_kelvin=0,
        )
        assert device.supports_color_temp is False
        assert device.percent_to_kelvin_for_device(50) == 4600
        assert device.kelvin_to_percent_for_device(4600) == 50

    def test_kelvin_to_percent_for_device_zero_range_returns_midpoint(self):
        """Degenerate device range should map to midpoint percent."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            min_color_temp_kelvin=4000,
            max_color_temp_kelvin=4000,
        )
        assert device.kelvin_to_percent_for_device(4000) == 50

    def test_default_color_temp_range(self):
        """Test default color temp range is 2700-6500K."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
        )
        assert device.min_color_temp_kelvin == 2700
        assert device.max_color_temp_kelvin == 6500
        assert device.supports_color_temp is True


class TestDeviceHeaterExtended:
    """Extended tests for heater properties."""

    def test_wind_direction_mode(self):
        """Test wind direction mode property."""
        device = LiproDevice(
            device_number=1,
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
            device_number=2,
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
            device_number=1,
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
            device_number=2,
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
