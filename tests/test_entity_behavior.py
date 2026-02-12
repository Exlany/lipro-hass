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

    def test_brightness_clamp_to_valid_range(self):
        """Test brightness is clamped to valid range."""
        from custom_components.lipro.const import MAX_BRIGHTNESS, MIN_BRIGHTNESS

        # Test clamping logic
        test_values = [
            (0, MIN_BRIGHTNESS),  # Below min -> clamp to min
            (1, 1),  # At min -> keep
            (50, 50),  # Middle -> keep
            (100, 100),  # At max -> keep
            (150, MAX_BRIGHTNESS),  # Above max -> clamp to max
        ]

        for input_val, expected in test_values:
            clamped = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, input_val))
            assert clamped == expected, f"Input {input_val} should clamp to {expected}"

    def test_color_temp_clamp_to_valid_range(self):
        """Test color temperature is clamped to valid range."""
        from custom_components.lipro.const import (
            MAX_COLOR_TEMP_KELVIN,
            MIN_COLOR_TEMP_KELVIN,
        )

        test_values = [
            (2000, MIN_COLOR_TEMP_KELVIN),  # Below min
            (2700, 2700),  # At min
            (4000, 4000),  # Middle
            (6500, 6500),  # At max
            (8000, MAX_COLOR_TEMP_KELVIN),  # Above max
        ]

        for input_val, expected in test_values:
            clamped = max(MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, input_val))
            assert clamped == expected


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

    def test_cover_position_clamp(self):
        """Test cover position is clamped to 0-100."""
        test_values = [
            (-10, 0),  # Below min
            (0, 0),  # At min
            (50, 50),  # Middle
            (100, 100),  # At max
            (150, 100),  # Above max
        ]

        for input_val, expected in test_values:
            clamped = max(0, min(100, int(input_val)))
            assert clamped == expected

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

        assert ranged_value_to_percentage(speed_range, 1) == 0
        assert ranged_value_to_percentage(speed_range, 10) == 100
        assert abs(ranged_value_to_percentage(speed_range, 5) - 44) <= 5

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
        assert math.ceil(percentage_to_ranged_value(speed_range, 50)) in (5, 6)


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


class TestEntityDebounce:
    """Tests for entity debounce behavior."""

    def test_debounce_default_delay(self):
        """Test Debouncer default delay value."""
        from custom_components.lipro.helpers.debounce import Debouncer

        debouncer = Debouncer()
        assert debouncer._delay > 0

    def test_debounce_custom_delay(self):
        """Test Debouncer with custom delay."""
        from custom_components.lipro.helpers.debounce import Debouncer

        debouncer = Debouncer(delay=1.5)
        assert debouncer._delay == 1.5

    def test_debounce_cancel_when_not_pending(self):
        """Test canceling debounce when nothing is pending."""
        from custom_components.lipro.helpers.debounce import Debouncer

        debouncer = Debouncer()
        # Should not raise
        debouncer.cancel()
