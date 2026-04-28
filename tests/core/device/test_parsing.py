"""Tests for Lipro device model."""

from __future__ import annotations

from custom_components.lipro.core.device import LiproDevice, parse_properties_list


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


class TestGetOptionalIntProperty:
    """Tests for get_optional_int_property method."""

    def test_returns_int_for_valid_string(self):
        """Test returns int when property is a valid numeric string."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={"wifiRssi": "-65"},
        )
        assert device.get_optional_int_property("wifi_rssi") == -65

    def test_returns_int_for_int_value(self):
        """Test returns int when property is already an int."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={"address": 42},
        )
        assert device.get_optional_int_property("address") == 42

    def test_returns_none_for_missing_key(self):
        """Test returns None when property key is missing."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={},
        )
        assert device.get_optional_int_property("wifi_rssi") is None

    def test_returns_none_for_invalid_string(self):
        """Test returns None when property is not a valid int."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Test",
            device_type=1,
            iot_name="",
            properties={"wifiRssi": "not_a_number"},
        )
        assert device.get_optional_int_property("wifi_rssi") is None
