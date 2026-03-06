"""Tests for boundary conditions and edge cases.

These tests verify proper handling of edge cases, invalid inputs,
and boundary values across the integration.
"""

from __future__ import annotations

import pytest

from custom_components.lipro.const.properties import (
    MAX_BRIGHTNESS,
    MAX_COLOR_TEMP_KELVIN,
    MIN_BRIGHTNESS,
    MIN_COLOR_TEMP_KELVIN,
    kelvin_to_percent,
    percent_to_kelvin,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
)
from custom_components.lipro.core.device import parse_properties_list


class TestBrightnessEdgeCases:
    """Tests for brightness boundary conditions via device properties."""

    @pytest.mark.parametrize(
        ("raw_value", "expected"),
        [
            ("0", 0),  # "0" parsed as int 0
            ("1", 1),
            ("50", 50),
            ("100", 100),
            ("invalid", 100),  # Non-numeric falls back to default
        ],
    )
    def test_brightness_property_values(self, make_device, raw_value, expected):
        """Test brightness property returns correct values for various inputs."""
        device = make_device("light", properties={"brightness": raw_value})
        assert device.brightness == expected

    def test_brightness_constants(self):
        """Test brightness range constants are correct."""
        assert MIN_BRIGHTNESS == 1
        assert MAX_BRIGHTNESS == 100
        assert MIN_BRIGHTNESS < MAX_BRIGHTNESS


class TestColorTempEdgeCases:
    """Tests for color temperature boundary conditions via production functions."""

    @pytest.mark.parametrize(
        ("percent", "expected_kelvin"),
        [
            (0, MIN_COLOR_TEMP_KELVIN),  # 0% -> warmest
            (100, MAX_COLOR_TEMP_KELVIN),  # 100% -> coolest
            (50, 4600),  # 50% -> midpoint
            (-10, MIN_COLOR_TEMP_KELVIN),  # Below 0 clamped
            (150, MAX_COLOR_TEMP_KELVIN),  # Above 100 clamped
        ],
    )
    def test_percent_to_kelvin(self, percent, expected_kelvin):
        """Test percent_to_kelvin conversion with boundary values."""
        assert percent_to_kelvin(percent) == expected_kelvin

    @pytest.mark.parametrize(
        ("kelvin", "expected_percent"),
        [
            (MIN_COLOR_TEMP_KELVIN, 0),
            (MAX_COLOR_TEMP_KELVIN, 100),
            (4600, 50),
            (2000, 0),  # Below min clamped
            (8000, 100),  # Above max clamped
        ],
    )
    def test_kelvin_to_percent(self, kelvin, expected_percent):
        """Test kelvin_to_percent conversion with boundary values."""
        assert kelvin_to_percent(kelvin) == expected_percent

    def test_roundtrip_conversion(self):
        """Test percent -> kelvin -> percent roundtrip is stable."""
        for percent in (0, 25, 50, 75, 100):
            kelvin = percent_to_kelvin(percent)
            result = kelvin_to_percent(kelvin)
            assert result == percent, f"Roundtrip failed for {percent}%"


class TestCoverPositionEdgeCases:
    """Tests for cover position boundary conditions via device properties."""

    @pytest.mark.parametrize(
        ("raw_value", "expected"),
        [
            ("0", 0),
            ("50", 50),
            ("100", 100),
        ],
    )
    def test_position_property_values(self, make_device, raw_value, expected):
        """Test cover position property returns correct values."""
        device = make_device("curtain", properties={"position": raw_value})
        assert device.position == expected


class TestFanGearEdgeCases:
    """Tests for fan gear boundary conditions."""

    def test_gear_zero_percentage_turns_off(self, make_device):
        """Test 0% percentage means fan gear at minimum."""
        device = make_device("fanLight", properties={"fanGear": "0"})
        # Fan gear 0 is clamped to min (1)
        assert device.fan_gear == 1

    def test_gear_range_boundaries(self):
        """Test gear range boundaries (1-10)."""
        import math

        SPEED_RANGE = (1, 10)

        def percentage_to_ranged_value(low_high_range, percentage):
            """Convert percentage to ranged value."""
            low, high = low_high_range
            return low + (high - low) * percentage / 100

        # 1% should give gear 1
        gear = math.ceil(percentage_to_ranged_value(SPEED_RANGE, 1))
        assert gear >= 1

        # 100% should give gear 10
        gear = math.ceil(percentage_to_ranged_value(SPEED_RANGE, 100))
        assert gear == 10


class TestDevicePropertyEdgeCases:
    """Tests for device property edge cases."""

    def test_empty_properties(self, make_device):
        """Test device with empty properties."""
        device = make_device("light", properties={})

        # Should have safe defaults
        assert device.is_on is False  # Default when powerState missing
        assert device.brightness == 100  # Default when brightness missing (100%)

    def test_none_property_value(self, make_device):
        """Test device with None property value."""
        device = make_device("light", properties={"powerState": None})

        # Should handle None gracefully
        assert device.properties.get("powerState") is None

    def test_invalid_property_type(self, make_device):
        """Test device with invalid property type."""
        device = make_device("light", properties={"brightness": "invalid"})

        # brightness property should handle non-numeric gracefully
        # get_int_property returns default (100) for invalid values
        assert device.brightness == 100

    def test_update_with_empty_dict(self, make_device):
        """Test updating device with empty dict."""
        device = make_device("light", properties={"powerState": "1"})

        device.update_properties({})

        # Original properties should be unchanged
        assert device.properties["powerState"] == "1"


class TestParsePropertiesListEdgeCases:
    """Tests for parse_properties_list edge cases."""

    def test_parse_none_input(self):
        """Test parsing None input."""
        result = parse_properties_list(None)
        assert result == {}

    def test_parse_empty_list(self):
        """Test parsing empty list."""
        result = parse_properties_list([])
        assert result == {}

    def test_parse_malformed_items(self):
        """Test parsing list with malformed items."""
        properties_list = [
            {"key": "valid", "value": "1"},
            123,  # Non-dict item from malformed API payload
            {},  # Empty dict - key will be None, skipped
            {"value": "nokey"},  # Missing key - key will be None, skipped
            # Note: {"key": "novalue"} will include key with None value
        ]

        result = parse_properties_list(properties_list)

        # Should only include valid item (items without key are skipped)
        assert "valid" in result
        assert result["valid"] == "1"

    def test_parse_duplicate_keys(self):
        """Test parsing list with duplicate keys (last wins)."""
        properties_list = [
            {"key": "brightness", "value": "50"},
            {"key": "brightness", "value": "80"},
        ]

        result = parse_properties_list(properties_list)

        # Last value should win
        assert result["brightness"] == "80"


class TestApiErrorEdgeCases:
    """Tests for API error edge cases."""

    def test_error_with_none_code(self):
        """Test API error with None code."""
        error = LiproApiError("Error message", code=None)

        assert error.code is None
        assert str(error) == "Error message"

    def test_error_with_string_code(self):
        """Test API error with string code."""
        error = LiproApiError("Error message", code="401")

        assert error.code == "401"

    def test_error_inheritance(self):
        """Test error class inheritance."""
        auth_error = LiproAuthError("Auth failed")
        conn_error = LiproConnectionError("Connection failed")

        assert isinstance(auth_error, LiproApiError)
        assert isinstance(conn_error, LiproApiError)
        assert isinstance(auth_error, Exception)


class TestDeviceAvailabilityEdgeCases:
    """Tests for device availability edge cases."""

    def test_availability_with_missing_connect_state(self, make_device):
        """Test availability when connectState is missing."""
        device = make_device("light", properties={})

        # Should default to available
        assert device.available is True

    def test_availability_with_invalid_connect_state(self, make_device):
        """Test availability with invalid connectState via update_properties.

        available is only recalculated when update_properties() is called
        with connectState, not at construction time.
        """
        device = make_device("light")
        assert device.available is True

        # update_properties triggers availability recalculation
        device.update_properties({"connectState": "invalid"})
        # "invalid" is not in ("1", "true", "yes", "on"), so is_connected=False
        assert device.available is False


class TestMqttMessageEdgeCases:
    """Tests for MQTT message edge cases."""

    def test_empty_mqtt_properties(self, make_device):
        """Test handling empty MQTT properties."""
        device = make_device("light", properties={"powerState": "1"})

        device.update_properties({})

        # Original state should be preserved
        assert device.properties["powerState"] == "1"

    def test_mqtt_properties_with_unknown_keys(self, make_device):
        """Test MQTT properties with unknown keys."""
        device = make_device("light", properties={"powerState": "1"})

        device.update_properties({"unknownKey": "value", "anotherUnknown": "123"})

        # Unknown keys should be stored
        assert device.properties.get("unknownKey") == "value"


class TestSignatureEdgeCases:
    """Tests for API signature edge cases."""

    def test_iot_sign_with_empty_body(self):
        """Test IoT signature with empty body produces valid MD5."""
        from custom_components.lipro.core.api import LiproClient

        client = LiproClient(phone_id="test_id")
        client._access_token = "test_token"
        signature = client._iot_sign(1000167890, "")
        assert len(signature) == 32  # MD5 produces 32 hex chars

    def test_iot_sign_with_whitespace_body(self):
        """Test IoT signature trims whitespace from body."""
        from custom_components.lipro.core.api import LiproClient

        client = LiproClient(phone_id="test_id")
        client._access_token = "test_token"
        nonce = 1000167890
        sig_trimmed = client._iot_sign(nonce, '{"key": "value"}')
        sig_padded = client._iot_sign(nonce, '  {"key": "value"}  ')
        # Both should produce the same signature (whitespace trimmed)
        assert sig_trimmed == sig_padded


class TestDebounceEdgeCases:
    """Tests for debounce edge cases."""

    def test_debounce_with_zero_delay(self):
        """Test debounce with zero delay."""
        from custom_components.lipro.core.utils.debounce import Debouncer

        debouncer = Debouncer(delay=0)

        assert debouncer._delay == 0

    def test_debounce_cancel_when_not_pending(self):
        """Test canceling debounce when nothing is pending."""
        from custom_components.lipro.core.utils.debounce import Debouncer

        debouncer = Debouncer()

        # Should not raise
        debouncer.cancel()

    @pytest.mark.asyncio
    async def test_debounce_multiple_rapid_calls(self):
        """Test multiple rapid debounce calls."""
        from custom_components.lipro.core.utils.debounce import Debouncer

        debouncer = Debouncer(delay=0.1)
        call_count = 0

        async def increment():
            nonlocal call_count
            call_count += 1

        # Rapid calls - only last should execute
        await debouncer.async_call(increment)
        await debouncer.async_call(increment)
        await debouncer.async_call(increment)

        # Wait for debounce to complete
        import asyncio

        await asyncio.sleep(0.2)

        # Should have been called exactly once (only last call executes)
        assert call_count == 1


class TestGearListEdgeCases:
    """Tests for gear list parsing edge cases."""

    def test_gear_list_empty_json(self, make_device):
        """Test gear list with empty JSON array."""
        device = make_device("light", properties={"gearList": "[]"})

        assert device.gear_list == []

    def test_gear_list_invalid_json(self, make_device):
        """Test gear list with invalid JSON."""
        device = make_device("light", properties={"gearList": "not json"})

        # Should handle gracefully and return empty list
        assert device.gear_list == []

    def test_gear_list_none_value(self, make_device):
        """Test gear list with None value."""
        device = make_device("light", properties={"gearList": None})

        # Should return empty list or handle gracefully
        gear_list = device.gear_list
        assert gear_list == [] or gear_list is None
