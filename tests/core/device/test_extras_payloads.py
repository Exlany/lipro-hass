"""Tests for Lipro device model."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice


class TestDeviceGearList:
    """Tests for gear list functionality."""

    def test_gear_list_from_string(self):
        """Test parsing gear list from JSON string."""
        device = LiproDevice(
            device_number=1,
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
            device_number=1,
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
            device_number=1,
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
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": "invalid json",
            },
        )

        assert device.gear_list == []

    def test_gear_list_json_object_returns_empty(self):
        """Non-list JSON payload should return empty gear list."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": '{"temperature": 50, "brightness": 80}',
            },
        )

        assert device.gear_list == []

    def test_gear_list_invalid_json_that_looks_like_json_returns_empty(self):
        """Invalid JSON starting with '{' or '[' should be caught and return empty."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            properties={
                "gearList": "{",
            },
        )

        assert device.gear_list == []

    def test_gear_list_caching(self):
        """Test gear list caching."""
        device = LiproDevice(
            device_number=1,
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
            device_number=1,
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
            device_number=1,
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
            device_number=2,
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
            device_number=1,
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
            device_number=2,
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
            device_number=1,
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
            device_number=2,
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
            device_number=3,
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
            device_number=1,
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
            device_number=2,
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
            device_number=3,
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
            device_number=1,
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
            device_number=2,
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
            device_number=3,
            serial="03ab5ccd7czzzzzz",
            name="Light",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device_no_battery.battery_level is None
        assert device_no_battery.has_battery is False
