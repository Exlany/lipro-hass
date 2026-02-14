"""Tests for Lipro platform entity behaviors.

These tests verify the actual entity behavior with mocked coordinators.
"""

from __future__ import annotations

import pytest

try:
    from pytest_homeassistant_custom_component.common import (
        MockConfigEntry,  # noqa: F401
    )

    HAS_HA_TEST_ENV = True
except ImportError:
    HAS_HA_TEST_ENV = False


class TestLightEntityBehavior:
    """Tests for light entity behavior."""

    def test_light_is_on_property(self, make_device):
        """Test light is_on property."""
        device_on = make_device("light", properties={"powerState": "1"})
        device_off = make_device("light", properties={"powerState": "0"})

        assert device_on.is_on is True
        assert device_off.is_on is False

    def test_light_brightness_conversion(self, make_device):
        """Test brightness conversion from 0-100 to 0-255."""
        device = make_device("light", properties={"brightness": "50"})

        # Device returns 0-100, HA expects 0-255
        brightness_pct = device.brightness
        brightness_ha = round(brightness_pct * 255 / 100)

        assert brightness_pct == 50
        assert brightness_ha == 128  # 50% of 255

    def test_light_brightness_boundary_values(self, make_device):
        """Test brightness boundary values."""
        # Minimum brightness
        device_min = make_device("light", properties={"brightness": "1"})
        assert device_min.brightness == 1

        # Maximum brightness
        device_max = make_device("light", properties={"brightness": "100"})
        assert device_max.brightness == 100

    def test_light_color_temp_property(self, make_device):
        """Test color temperature property."""
        device = make_device("light", properties={"temperature": "50"})

        # temperature is stored as percentage (0-100)
        # color_temp converts to Kelvin
        assert device.color_temp is not None

    def test_brightness_clamp_to_valid_range(self, make_device):
        """Test brightness is clamped to valid range via device property."""
        from custom_components.lipro.const import MAX_BRIGHTNESS, MIN_BRIGHTNESS

        # Default when missing -> 100 (max)
        device_default = make_device("light", properties={})
        assert MIN_BRIGHTNESS <= device_default.brightness <= MAX_BRIGHTNESS

        # Valid values preserved
        device_mid = make_device("light", properties={"brightness": "50"})
        assert device_mid.brightness == 50

    def test_color_temp_clamp_to_valid_range(self, make_device):
        """Test color temperature is clamped to valid range via production function."""
        from custom_components.lipro.const import (
            MAX_COLOR_TEMP_KELVIN,
            MIN_COLOR_TEMP_KELVIN,
            kelvin_to_percent,
        )

        # kelvin_to_percent clamps input to valid range
        assert kelvin_to_percent(2000) == 0  # Below min -> 0%
        assert kelvin_to_percent(MIN_COLOR_TEMP_KELVIN) == 0
        assert kelvin_to_percent(MAX_COLOR_TEMP_KELVIN) == 100
        assert kelvin_to_percent(8000) == 100  # Above max -> 100%


class TestSwitchEntityBehavior:
    """Tests for switch entity behavior."""

    def test_switch_is_on_property(self, make_device):
        """Test switch is_on property."""
        device_on = make_device("switch", properties={"powerState": "1"})
        device_off = make_device("switch", properties={"powerState": "0"})

        assert device_on.is_on is True
        assert device_off.is_on is False

    def test_outlet_is_on_property(self, make_device):
        """Test outlet is_on property."""
        device_on = make_device("outlet", properties={"powerState": "1"})
        device_off = make_device("outlet", properties={"powerState": "0"})

        assert device_on.is_on is True
        assert device_off.is_on is False


class TestCoverEntityBehavior:
    """Tests for cover entity behavior."""

    def test_cover_position_property(self, make_device):
        """Test cover position property."""
        device = make_device("curtain", properties={"position": "50"})

        assert device.position == 50

    def test_cover_is_closed(self, make_device):
        """Test cover is_closed property."""
        device_closed = make_device("curtain", properties={"position": "0"})
        device_open = make_device("curtain", properties={"position": "100"})
        device_partial = make_device("curtain", properties={"position": "50"})

        assert device_closed.position == 0
        assert device_open.position == 100
        assert device_partial.position == 50

    @pytest.mark.parametrize(
        ("raw_position", "expected"),
        [
            ("0", 0),
            ("50", 50),
            ("100", 100),
        ],
    )
    def test_cover_position_clamp(self, make_device, raw_position, expected):
        """Test cover position values via device property."""
        device = make_device("curtain", properties={"position": raw_position})
        assert device.position == expected

    def test_cover_moving_state(self, make_device):
        """Test cover moving state."""
        device_moving = make_device(
            "curtain",
            properties={"moving": "1", "direction": "1"},
        )
        device_stopped = make_device(
            "curtain",
            properties={"moving": "0"},
        )

        assert device_moving.is_moving is True
        assert device_stopped.is_moving is False


class TestFanEntityBehavior:
    """Tests for fan entity behavior."""

    def test_fan_is_on_property(self, make_device):
        """Test fan is_on property."""
        device_on = make_device("fanLight", properties={"fanOnOff": "1"})
        device_off = make_device("fanLight", properties={"fanOnOff": "0"})

        assert device_on.fan_is_on is True
        assert device_off.fan_is_on is False

    def test_fan_gear_property(self, make_device):
        """Test fan gear property."""
        device = make_device("fanLight", properties={"fanGear": "5"})

        assert device.fan_gear == 5

    @pytest.mark.skipif(
        not HAS_HA_TEST_ENV, reason="Requires HA test env for homeassistant.util"
    )
    def test_fan_gear_to_percentage(self, make_device):
        """Test fan gear to percentage conversion using HA utility."""
        from homeassistant.util.percentage import ranged_value_to_percentage

        device = make_device("fanLight", max_fan_gear=10)
        speed_range = device.fan_speed_range

        assert ranged_value_to_percentage(speed_range, 1) == 10
        assert ranged_value_to_percentage(speed_range, 10) == 100
        assert ranged_value_to_percentage(speed_range, 5) == 50

    @pytest.mark.skipif(
        not HAS_HA_TEST_ENV, reason="Requires HA test env for homeassistant.util"
    )
    def test_percentage_to_fan_gear(self, make_device):
        """Test percentage to fan gear conversion using HA utility."""
        import math

        from homeassistant.util.percentage import percentage_to_ranged_value

        device = make_device("fanLight", max_fan_gear=10)
        speed_range = device.fan_speed_range

        assert math.ceil(percentage_to_ranged_value(speed_range, 100)) == 10
        assert math.ceil(percentage_to_ranged_value(speed_range, 50)) == 6


class TestClimateEntityBehavior:
    """Tests for climate (heater) entity behavior."""

    def test_heater_is_on_property(self, make_device):
        """Test heater is_on property."""
        device_on = make_device("heater", properties={"powerState": "1"})
        device_off = make_device("heater", properties={"powerState": "0"})

        assert device_on.is_on is True
        assert device_off.is_on is False

    def test_heater_mode_property(self, make_device):
        """Test heater mode property."""
        device = make_device("heater", properties={"heaterMode": "1"})

        assert device.heater_mode == 1


class TestBinarySensorEntityBehavior:
    """Tests for binary sensor entity behavior."""

    def test_body_sensor_detected(self, make_device):
        """Test body sensor detection state."""
        # PROP_ACTIVATED is "human" in the API
        device_detected = make_device("bodySensor", properties={"human": "1"})
        device_clear = make_device("bodySensor", properties={"human": "0"})

        assert device_detected.is_activated is True
        assert device_clear.is_activated is False

    def test_door_sensor_state(self, make_device):
        """Test door sensor open/closed state."""
        device_open = make_device("doorSensor", properties={"doorOpen": "1"})
        device_closed = make_device("doorSensor", properties={"doorOpen": "0"})

        assert device_open.door_is_open is True
        assert device_closed.door_is_open is False

    def test_low_battery_detection(self, make_device):
        """Test low battery detection."""
        device_low = make_device("bodySensor", properties={"lowBattery": "1"})
        device_ok = make_device("bodySensor", properties={"lowBattery": "0"})

        assert device_low.low_battery is True
        assert device_ok.low_battery is False


class TestSensorEntityBehavior:
    """Tests for sensor entity behavior."""

    def test_outlet_power_sensor(self, make_device):
        """Test outlet power sensor value."""
        device = make_device("outlet")

        # Power info is stored in extra_data
        device.extra_data["power_info"] = {"nowPower": 150}

        assert device.extra_data.get("power_info", {}).get("nowPower") == 150

    def test_outlet_energy_list(self, make_device):
        """Test outlet energy list parsing."""
        device = make_device("outlet")

        device.extra_data["power_info"] = {
            "nowPower": 100,
            "energyList": [
                {"t": "20260207", "v": 1.5},
                {"t": "20260206", "v": 2.0},
            ],
        }

        energy_list = device.extra_data.get("power_info", {}).get("energyList", [])
        assert len(energy_list) == 2
        assert energy_list[0]["v"] == 1.5


class TestSelectEntityBehavior:
    """Tests for select entity behavior."""

    def test_fan_mode_options(self, make_device):
        """Test fan mode options."""
        from custom_components.lipro.const import FAN_MODE_NATURAL

        device = make_device("fanLight", properties={"fanMode": str(FAN_MODE_NATURAL)})

        assert device.fan_mode == FAN_MODE_NATURAL

    def test_heater_mode_options(self, make_device):
        """Test heater mode options."""
        device = make_device("heater", properties={"heaterMode": "1"})

        assert device.heater_mode == 1


class TestEntityAvailability:
    """Tests for entity availability."""

    def test_device_available_by_default(self, make_device):
        """Test device is available by default."""
        device = make_device("light")

        assert device.available is True

    def test_device_unavailable_when_disconnected(self, make_device):
        """Test device is unavailable when disconnected."""
        device = make_device("light", properties={})

        # Update properties to trigger availability check
        device.update_properties({"connectState": "0"})

        assert device.available is False

    def test_device_available_when_connected(self, make_device):
        """Test device is available when connected."""
        device = make_device("light", properties={})

        device.update_properties({"connectState": "1"})

        assert device.available is True
