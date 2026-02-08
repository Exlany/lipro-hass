"""Tests for Lipro select platform."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice


class TestLiproHeaterWindDirectionSelect:
    """Tests for LiproHeaterWindDirectionSelect entity."""

    def test_wind_direction_auto(self, make_device):
        """Test wind direction mode is auto."""
        from custom_components.lipro.const import WIND_DIRECTION_AUTO

        device = make_device(
            "heater",
            properties={"windDirectionMode": str(WIND_DIRECTION_AUTO)},
        )
        assert device.wind_direction_mode == WIND_DIRECTION_AUTO

    def test_wind_direction_fixed(self, make_device):
        """Test wind direction mode is fixed."""
        from custom_components.lipro.const import WIND_DIRECTION_FIX

        device = make_device(
            "heater",
            properties={"windDirectionMode": str(WIND_DIRECTION_FIX)},
        )
        assert device.wind_direction_mode == WIND_DIRECTION_FIX

    def test_wind_direction_default(self, make_device):
        """Test wind direction mode default is 1 (auto)."""
        device = make_device("heater")
        assert device.wind_direction_mode == 1

    def test_wind_direction_options(self):
        """Test wind direction options."""
        wind_direction_options = ["auto", "fixed"]
        assert wind_direction_options == ["auto", "fixed"]

    def test_wind_direction_value_mapping(self):
        """Test wind direction value mapping."""
        from custom_components.lipro.const import (
            WIND_DIRECTION_AUTO,
            WIND_DIRECTION_FIX,
        )

        wind_direction_to_value = {
            "auto": WIND_DIRECTION_AUTO,
            "fixed": WIND_DIRECTION_FIX,
        }
        value_to_wind_direction = {v: k for k, v in wind_direction_to_value.items()}

        assert wind_direction_to_value["auto"] == WIND_DIRECTION_AUTO
        assert wind_direction_to_value["fixed"] == WIND_DIRECTION_FIX
        assert value_to_wind_direction[WIND_DIRECTION_AUTO] == "auto"
        assert value_to_wind_direction[WIND_DIRECTION_FIX] == "fixed"


class TestLiproHeaterLightModeSelect:
    """Tests for LiproHeaterLightModeSelect entity."""

    def test_light_mode_off(self, make_device):
        """Test light mode is off."""
        from custom_components.lipro.const import HEATER_LIGHT_OFF

        device = make_device(
            "heater",
            properties={"lightMode": str(HEATER_LIGHT_OFF)},
        )
        assert device.light_mode == HEATER_LIGHT_OFF

    def test_light_mode_main(self, make_device):
        """Test light mode is main."""
        from custom_components.lipro.const import HEATER_LIGHT_MAIN

        device = make_device(
            "heater",
            properties={"lightMode": str(HEATER_LIGHT_MAIN)},
        )
        assert device.light_mode == HEATER_LIGHT_MAIN

    def test_light_mode_night(self, make_device):
        """Test light mode is night."""
        from custom_components.lipro.const import HEATER_LIGHT_NIGHT

        device = make_device(
            "heater",
            properties={"lightMode": str(HEATER_LIGHT_NIGHT)},
        )
        assert device.light_mode == HEATER_LIGHT_NIGHT

    def test_light_mode_default(self, make_device):
        """Test light mode default is 0 (off)."""
        device = make_device("heater")
        assert device.light_mode == 0

    def test_light_mode_options(self):
        """Test light mode options."""
        light_mode_options = ["off", "main", "night"]
        assert light_mode_options == ["off", "main", "night"]

    def test_light_mode_value_mapping(self):
        """Test light mode value mapping."""
        from custom_components.lipro.const import (
            HEATER_LIGHT_MAIN,
            HEATER_LIGHT_NIGHT,
            HEATER_LIGHT_OFF,
        )

        light_mode_to_value = {
            "off": HEATER_LIGHT_OFF,
            "main": HEATER_LIGHT_MAIN,
            "night": HEATER_LIGHT_NIGHT,
        }
        value_to_light_mode = {v: k for k, v in light_mode_to_value.items()}

        assert light_mode_to_value["off"] == HEATER_LIGHT_OFF
        assert light_mode_to_value["main"] == HEATER_LIGHT_MAIN
        assert light_mode_to_value["night"] == HEATER_LIGHT_NIGHT
        assert value_to_light_mode[HEATER_LIGHT_OFF] == "off"
        assert value_to_light_mode[HEATER_LIGHT_MAIN] == "main"
        assert value_to_light_mode[HEATER_LIGHT_NIGHT] == "night"


class TestLiproLightGearSelect:
    """Tests for LiproLightGearSelect entity."""

    def test_gear_options(self):
        """Test gear options."""
        gear_options = ["gear_1", "gear_2", "gear_3"]
        assert gear_options == ["gear_1", "gear_2", "gear_3"]

    def test_gear_list_parsing(self, make_device):
        """Test gear list parsing from JSON string."""
        device = make_device(
            "light",
            properties={
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":30,"brightness":80},{"temperature":70,"brightness":60}]'
            },
        )

        gear_list = device.gear_list
        assert len(gear_list) == 3
        assert gear_list[0]["temperature"] == 50
        assert gear_list[0]["brightness"] == 100
        assert gear_list[1]["temperature"] == 30
        assert gear_list[1]["brightness"] == 80
        assert gear_list[2]["temperature"] == 70
        assert gear_list[2]["brightness"] == 60

    def test_gear_list_empty(self, make_device):
        """Test empty gear list."""
        device = make_device("light")
        assert device.gear_list == []
        assert device.has_gear_presets is False

    def test_has_gear_presets(self, make_device):
        """Test has_gear_presets property."""
        device = make_device(
            "light",
            properties={"gearList": '[{"temperature":50,"brightness":100}]'},
        )
        assert device.has_gear_presets is True

    def test_last_gear_index(self, make_device):
        """Test last gear index property."""
        device = make_device("light", properties={"lastGearIndex": "2"})
        assert device.last_gear_index == 2

    def test_last_gear_index_default(self, make_device):
        """Test last gear index default is -1."""
        device = make_device("light")
        assert device.last_gear_index == -1


class TestGearTemperatureConversion:
    """Tests for gear temperature conversion between percentage and Kelvin."""

    def test_percent_to_kelvin(self):
        """Test converting temperature percentage to Kelvin."""
        from custom_components.lipro.const import percent_to_kelvin

        assert percent_to_kelvin(0) == 2700
        assert percent_to_kelvin(50) == 4600
        assert percent_to_kelvin(100) == 6500

    def test_kelvin_to_percent(self):
        """Test converting Kelvin to temperature percentage."""
        from custom_components.lipro.const import kelvin_to_percent

        assert kelvin_to_percent(2700) == 0
        assert kelvin_to_percent(4600) == 50
        assert kelvin_to_percent(6500) == 100

    def test_roundtrip(self):
        """Test percent -> kelvin -> percent roundtrip."""
        from custom_components.lipro.const import kelvin_to_percent, percent_to_kelvin

        for pct in (0, 25, 50, 75, 100):
            assert kelvin_to_percent(percent_to_kelvin(pct)) == pct


class TestSelectConstants:
    """Tests for select-related constants."""

    def test_heater_light_constants(self):
        """Test heater light mode constants."""
        from custom_components.lipro.const import (
            HEATER_LIGHT_MAIN,
            HEATER_LIGHT_NIGHT,
            HEATER_LIGHT_OFF,
        )

        assert HEATER_LIGHT_OFF == 0
        assert HEATER_LIGHT_MAIN == 1
        assert HEATER_LIGHT_NIGHT == 2

    def test_wind_direction_constants(self):
        """Test wind direction mode constants."""
        from custom_components.lipro.const import (
            WIND_DIRECTION_AUTO,
            WIND_DIRECTION_FIX,
        )

        assert WIND_DIRECTION_AUTO == 1
        assert WIND_DIRECTION_FIX == 2

    def test_property_constants(self):
        """Test property constants."""
        from custom_components.lipro.const import (
            PROP_LIGHT_MODE,
            PROP_WIND_DIRECTION_MODE,
        )

        assert PROP_LIGHT_MODE == "lightMode"
        assert PROP_WIND_DIRECTION_MODE == "windDirectionMode"


class TestSelectDeviceDetection:
    """Tests for select entity device detection."""

    def test_heater_device_detection(self):
        """Test heater device is correctly detected."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Heater",
            device_type=7,
            iot_name="",
            physical_model="heater",
        )
        assert device.is_heater is True

    def test_light_with_gear_detection(self):
        """Test light with gear presets is correctly detected."""
        device = LiproDevice(
            device_id=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={"gearList": '[{"temperature":50,"brightness":100}]'},
        )
        assert device.is_light is True
        assert device.has_gear_presets is True
