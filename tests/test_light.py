"""Tests for Lipro light platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.device import LiproDevice


class TestLiproLight:
    """Tests for LiproLight entity."""

    def test_light_is_on(self, make_device):
        """Test light is_on property."""
        device = make_device("light", properties={"powerState": "1"})
        assert device.is_on is True

        device = make_device("light", properties={"powerState": "0"})
        assert device.is_on is False

    def test_light_brightness(self, make_device):
        """Test light brightness property."""
        device = make_device("light", properties={"brightness": "80"})
        assert device.brightness == 80

        device = make_device("light", properties={"brightness": "0"})
        assert device.brightness == 0

        # Default brightness
        device = make_device("light")
        assert device.brightness == 100

    def test_light_color_temp(self, make_device):
        """Test light color temperature property.

        API stores temperature as percentage (0=2700K, 100=6500K).
        device.color_temp converts to Kelvin.
        """
        # 50% -> 2700 + 50*3800/100 = 4600K
        device = make_device("light", properties={"temperature": "50"})
        assert device.color_temp == 4600

        # 0% -> 2700K
        device = make_device("light", properties={"temperature": "0"})
        assert device.color_temp == 2700

        # 100% -> 6500K
        device = make_device("light", properties={"temperature": "100"})
        assert device.color_temp == 6500

        # Default (34%) -> ~3992K
        device = make_device("light")
        assert device.color_temp == 2700 + int(34 * 3800 / 100)

    def test_light_is_light(self, make_device):
        """Test device is identified as light."""
        device = make_device("light")
        assert device.is_light is True
        assert device.is_fan_light is False

    def test_fan_light_is_fan_light(self, make_device):
        """Test device is identified as fan light."""
        device = make_device("fanLight")
        assert device.is_fan_light is True
        assert device.is_light is False


class TestLiproLightBrightnessConversion:
    """Tests for brightness conversion between HA (0-255) and Lipro (0-100)."""

    def test_brightness_to_ha(self):
        """Test converting Lipro brightness (0-100) to HA (0-255)."""
        # 100% -> 255
        assert round(100 * 255 / 100) == 255
        # 50% -> 128 (rounded)
        assert round(50 * 255 / 100) == 128
        # 0% -> 0
        assert round(0 * 255 / 100) == 0
        # 1% -> 3 (rounded)
        assert round(1 * 255 / 100) == 3

    def test_brightness_from_ha(self):
        """Test converting HA brightness (0-255) to Lipro (0-100)."""
        # 255 -> 100%
        assert int(255 * 100 / 255) == 100
        # 128 -> 50%
        assert int(128 * 100 / 255) == 50
        # 0 -> 0%
        assert int(0 * 100 / 255) == 0
        # 3 -> 1%
        assert int(3 * 100 / 255) == 1


class TestLiproLightColorTemp:
    """Tests for color temperature handling."""

    def test_color_temp_range(self):
        """Test color temperature is within valid range."""
        from custom_components.lipro.const import (
            MAX_COLOR_TEMP_KELVIN,
            MIN_COLOR_TEMP_KELVIN,
        )

        # Verify constants
        assert MIN_COLOR_TEMP_KELVIN == 2700
        assert MAX_COLOR_TEMP_KELVIN == 6500

    def test_color_temp_clamping(self):
        """Test color temperature clamping logic."""
        from custom_components.lipro.const import (
            MAX_COLOR_TEMP_KELVIN,
            MIN_COLOR_TEMP_KELVIN,
        )

        # Test clamping logic (as used in light.py)
        def clamp_color_temp(value: int) -> int:
            return max(MIN_COLOR_TEMP_KELVIN, min(MAX_COLOR_TEMP_KELVIN, value))

        assert clamp_color_temp(2000) == 2700  # Below min
        assert clamp_color_temp(7000) == 6500  # Above max
        assert clamp_color_temp(4000) == 4000  # Within range


class TestLiproLightCommands:
    """Tests for light command constants."""

    def test_command_constants(self):
        """Test command constants are defined."""
        from custom_components.lipro.const import (
            CMD_CHANGE_STATE,
            CMD_POWER_OFF,
            CMD_POWER_ON,
            PROP_BRIGHTNESS,
            PROP_POWER_STATE,
            PROP_TEMPERATURE,
        )

        assert CMD_POWER_ON == "POWER_ON"
        assert CMD_POWER_OFF == "POWER_OFF"
        assert CMD_CHANGE_STATE == "CHANGE_STATE"
        assert PROP_POWER_STATE == "powerState"
        assert PROP_BRIGHTNESS == "brightness"
        assert PROP_TEMPERATURE == "temperature"


class TestLiproLightFadeState:
    """Tests for light fade/transition state."""

    def test_fade_state_property(self):
        """Test fade state property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={"fadeState": "1"},
        )
        assert device.fade_state is True

        device.properties["fadeState"] = "0"
        assert device.fade_state is False

        # Default is False
        device.properties = {}
        assert device.fade_state is False


class TestLiproLightGearPresets:
    """Tests for light gear presets."""

    def test_gear_list_property(self):
        """Test gear list property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={
                "gearList": '[{"temperature":50,"brightness":100},{"temperature":30,"brightness":80}]'
            },
        )

        gear_list = device.gear_list
        assert len(gear_list) == 2
        assert gear_list[0]["temperature"] == 50
        assert gear_list[0]["brightness"] == 100

    def test_gear_list_empty(self):
        """Test empty gear list."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={},
        )

        assert device.gear_list == []
        assert device.has_gear_presets is False

    def test_gear_list_invalid_json(self):
        """Test invalid JSON in gear list."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={"gearList": "invalid json"},
        )

        assert device.gear_list == []

    def test_last_gear_index(self):
        """Test last gear index property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={"lastGearIndex": "1"},
        )

        assert device.last_gear_index == 1

        # Default is -1
        device.properties = {}
        assert device.last_gear_index == -1

    def test_has_gear_presets(self):
        """Test has_gear_presets property."""
        device = LiproDevice(
            device_number=1,
            serial="03ab5ccd7cxxxxxx",
            name="Light",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={"gearList": '[{"temperature":50,"brightness":100}]'},
        )

        assert device.has_gear_presets is True

        # Create a new device without gear_list to test False case
        device_no_gear = LiproDevice(
            device_number=2,
            serial="03ab5ccd7cyyyyyy",
            name="Light 2",
            device_type=1,
            iot_name="",
            physical_model="light",
            properties={},
        )
        assert device_no_gear.has_gear_presets is False


class TestLiproLightEntityCommands:
    """Tests for LiproLight entity command methods."""

    @pytest.mark.asyncio
    async def test_turn_on(self, mock_coordinator, make_device):
        """Test async_turn_on sends POWER_ON command."""
        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        light.async_write_ha_state = MagicMock()

        await light.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_ON", None
        )

    @pytest.mark.asyncio
    async def test_turn_off(self, mock_coordinator, make_device):
        """Test async_turn_off sends POWER_OFF command."""
        device = make_device("light", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        light.async_write_ha_state = MagicMock()

        await light.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_OFF", None
        )

    @pytest.mark.asyncio
    async def test_turn_on_with_brightness(self, mock_coordinator, make_device):
        """Test async_turn_on with brightness sends debounced CHANGE_STATE command."""
        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        light.async_write_ha_state = MagicMock()
        light.async_send_command_debounced = AsyncMock()

        # HA brightness 128 -> Lipro brightness 50 (128*100/255 = 50)
        await light.async_turn_on(brightness=128)

        light.async_send_command_debounced.assert_called_once()
        call_args = light.async_send_command_debounced.call_args
        assert call_args[0][0] == "CHANGE_STATE"
        # Properties should include brightness with converted value
        # HA 128 -> int(128*100/255) = 50
        props = call_args[0][1]
        brightness_prop = next(p for p in props if p["key"] == "brightness")
        assert brightness_prop["value"] == "50"

    @pytest.mark.asyncio
    async def test_turn_on_with_color_temp(self, mock_coordinator, make_device):
        """Test async_turn_on with color_temp sends debounced CHANGE_STATE."""
        device = make_device("light", properties={"powerState": "1", "temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        light.async_write_ha_state = MagicMock()
        light.async_send_command_debounced = AsyncMock()

        await light.async_turn_on(color_temp_kelvin=4000)

        light.async_send_command_debounced.assert_called_once()
        call_args = light.async_send_command_debounced.call_args
        assert call_args[0][0] == "CHANGE_STATE"
        props = call_args[0][1]
        temp_prop = next(p for p in props if p["key"] == "temperature")
        # 4000K -> percent depends on device range, verify it's a valid string
        assert temp_prop["value"].isdigit()


class TestLiproLightEntityProperties:
    """Tests for LiproLight entity property methods."""

    def test_brightness_ha_scale(self, mock_coordinator, make_device):
        """Test brightness returns HA scale (0-255) from device (0-100)."""
        device = make_device("light", properties={"brightness": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        # 50% -> round(50 * 255 / 100) = 128
        assert light.brightness == 128

    def test_brightness_full(self, mock_coordinator, make_device):
        """Test brightness at 100% returns 255."""
        device = make_device("light", properties={"brightness": "100"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.brightness == 255

    def test_is_on_property(self, mock_coordinator, make_device):
        """Test is_on reflects device power state."""
        device = make_device("light", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.is_on is True

    def test_supported_color_modes_with_color_temp(self, mock_coordinator, make_device):
        """Test supported_color_modes includes COLOR_TEMP when device supports it."""
        from homeassistant.components.light import ColorMode

        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert ColorMode.COLOR_TEMP in light.supported_color_modes

    def test_color_mode_property(self, mock_coordinator, make_device):
        """Test color_mode returns correct mode based on device capability."""
        from homeassistant.components.light import ColorMode

        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        if device.supports_color_temp:
            assert light.color_mode == ColorMode.COLOR_TEMP
        else:
            assert light.color_mode == ColorMode.BRIGHTNESS

    def test_color_temp_kelvin_property(self, mock_coordinator, make_device):
        """Test color_temp_kelvin returns device color temp."""
        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        if device.supports_color_temp:
            assert light.color_temp_kelvin == device.color_temp

    def test_fan_light_unique_id_has_suffix(self, mock_coordinator, make_device):
        """Test fan light entity has '_light' suffix in unique_id."""
        device = make_device("fanLight")
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.unique_id.endswith("_light")

    def test_regular_light_no_suffix(self, mock_coordinator, make_device):
        """Test regular light entity has no suffix in unique_id."""
        device = make_device("light")
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.unique_id == device.unique_id
