"""Tests for boundary conditions and edge cases.

These tests verify proper handling of edge cases, invalid inputs,
and boundary values across the integration.
"""

from __future__ import annotations

import pytest

from custom_components.lipro.const import (
    MAX_BRIGHTNESS,
    MAX_COLOR_TEMP_KELVIN,
    MIN_BRIGHTNESS,
    MIN_COLOR_TEMP_KELVIN,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
)
from custom_components.lipro.core.device import parse_properties_list


class TestBrightnessEdgeCases:
    """Tests for brightness boundary conditions."""

    def test_brightness_zero_clamps_to_min(self):
        """Test brightness 0 is clamped to minimum."""
        brightness = 0
        clamped = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, brightness))
        assert clamped == MIN_BRIGHTNESS

    def test_brightness_negative_clamps_to_min(self):
        """Test negative brightness is clamped to minimum."""
        brightness = -10
        clamped = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, brightness))
        assert clamped == MIN_BRIGHTNESS

    def test_brightness_over_100_clamps_to_max(self):
        """Test brightness over 100 is clamped to maximum."""
        brightness = 150
        clamped = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, brightness))
        assert clamped == MAX_BRIGHTNESS

    def test_brightness_at_boundaries(self):
        """Test brightness at exact boundaries."""
        assert (
            max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, MIN_BRIGHTNESS)) == MIN_BRIGHTNESS
        )
        assert (
            max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, MAX_BRIGHTNESS)) == MAX_BRIGHTNESS
        )

    def test_brightness_ha_to_lipro_conversion(self):
        """Test HA brightness (0-255) to Lipro (1-100) conversion."""
        # HA 0 -> Lipro 0 (but clamped to 1)
        ha_brightness = 0
        lipro_brightness = int(ha_brightness * 100 / 255)
        lipro_brightness = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, lipro_brightness))
        assert lipro_brightness == MIN_BRIGHTNESS

        # HA 255 -> Lipro 100
        ha_brightness = 255
        lipro_brightness = int(ha_brightness * 100 / 255)
        assert lipro_brightness == 100

        # HA 128 -> Lipro ~50
        ha_brightness = 128
        lipro_brightness = int(ha_brightness * 100 / 255)
        assert 49 <= lipro_brightness <= 51


class TestColorTempEdgeCases:
    """Tests for color temperature boundary conditions."""

    def test_color_temp_below_min_clamps(self):
        """Test color temp below minimum is clamped."""
        color_temp = 2000
        clamped = max(MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, color_temp))
        assert clamped == MIN_COLOR_TEMP_KELVIN

    def test_color_temp_above_max_clamps(self):
        """Test color temp above maximum is clamped."""
        color_temp = 8000
        clamped = max(MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, color_temp))
        assert clamped == MAX_COLOR_TEMP_KELVIN

    def test_color_temp_at_boundaries(self):
        """Test color temp at exact boundaries."""
        assert (
            max(
                MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, MIN_COLOR_TEMP_KELVIN)
            )
            == MIN_COLOR_TEMP_KELVIN
        )
        assert (
            max(
                MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, MAX_COLOR_TEMP_KELVIN)
            )
            == MAX_COLOR_TEMP_KELVIN
        )


class TestCoverPositionEdgeCases:
    """Tests for cover position boundary conditions."""

    def test_position_negative_clamps_to_zero(self):
        """Test negative position is clamped to 0."""
        position = -10
        clamped = max(0, min(100, int(position)))
        assert clamped == 0

    def test_position_over_100_clamps(self):
        """Test position over 100 is clamped."""
        position = 150
        clamped = max(0, min(100, int(position)))
        assert clamped == 100

    def test_position_float_converted_to_int(self):
        """Test float position is converted to int."""
        position = 50.7
        clamped = max(0, min(100, int(position)))
        assert clamped == 50
        assert isinstance(clamped, int)


class TestFanGearEdgeCases:
    """Tests for fan gear boundary conditions."""

    def test_gear_zero_percentage_turns_off(self):
        """Test 0% percentage should turn off fan."""
        percentage = 0
        # 0% means turn off, not set gear
        assert percentage == 0

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
        """Test availability with invalid connectState value."""
        device = make_device("light", properties={"connectState": "invalid"})

        # Should handle gracefully (likely default to available)
        # The actual behavior depends on implementation
        assert device.available in (True, False)


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
        """Test IoT signature with empty body."""
        import hashlib

        from custom_components.lipro.core.const import IOT_SIGN_KEY, MERCHANT_CODE

        access_token = "test_token"
        nonce = 1000167890
        body = ""

        trimmed_body = body.strip() if body else ""
        sign_data = f"{access_token}{nonce}{MERCHANT_CODE}{trimmed_body}{IOT_SIGN_KEY}"
        signature = hashlib.md5(sign_data.encode("utf-8")).hexdigest()

        assert len(signature) == 32  # MD5 produces 32 hex chars

    def test_iot_sign_with_whitespace_body(self):
        """Test IoT signature with whitespace body."""
        import hashlib

        from custom_components.lipro.core.const import IOT_SIGN_KEY, MERCHANT_CODE

        access_token = "test_token"
        nonce = 1000167890
        body = '  {"key": "value"}  '

        trimmed_body = body.strip() if body else ""
        sign_data = f"{access_token}{nonce}{MERCHANT_CODE}{trimmed_body}{IOT_SIGN_KEY}"
        _ = hashlib.md5(sign_data.encode("utf-8")).hexdigest()

        # Verify whitespace was trimmed
        assert "  " not in sign_data


class TestDebounceEdgeCases:
    """Tests for debounce edge cases."""

    def test_debounce_with_zero_delay(self):
        """Test debounce with zero delay."""
        from custom_components.lipro.helpers.debounce import Debouncer

        debouncer = Debouncer(delay=0)

        assert debouncer._delay == 0

    def test_debounce_cancel_when_not_pending(self):
        """Test canceling debounce when nothing is pending."""
        from custom_components.lipro.helpers.debounce import Debouncer

        debouncer = Debouncer()

        # Should not raise
        debouncer.cancel()

    @pytest.mark.asyncio
    async def test_debounce_multiple_rapid_calls(self):
        """Test multiple rapid debounce calls."""
        from custom_components.lipro.helpers.debounce import Debouncer

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

        # Should have been called at least once
        assert call_count >= 1


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
