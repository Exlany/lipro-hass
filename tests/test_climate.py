"""Tests for Lipro climate platform."""

from __future__ import annotations


class TestLiproHeaterState:
    """Tests for heater state properties."""

    def test_heater_is_on(self, make_device):
        """Test heater is on."""
        device = make_device("heater", properties={"heaterSwitch": "1"})
        assert device.heater_is_on is True

    def test_heater_is_off(self, make_device):
        """Test heater is off."""
        device = make_device("heater", properties={"heaterSwitch": "0"})
        assert device.heater_is_on is False

    def test_heater_default_off(self, make_device):
        """Test heater default is off."""
        device = make_device("heater")
        assert device.heater_is_on is False

    def test_heater_mode(self, make_device):
        """Test heater mode property."""
        device = make_device("heater", properties={"heaterMode": "2"})
        assert device.heater_mode == 2

    def test_heater_mode_default(self, make_device):
        """Test heater mode default is 0."""
        device = make_device("heater")
        assert device.heater_mode == 0

    def test_is_heater(self, make_device):
        """Test device is identified as heater."""
        device = make_device("heater")
        assert device.is_heater is True


class TestLiproHeaterHvacMode:
    """Tests for heater HVAC mode logic."""

    def test_hvac_mode_heat(self, make_device, mock_coordinator):
        """Test HVAC mode is HEAT when heater is on."""
        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterSwitch": "1"})
        heater = LiproHeater(mock_coordinator, device)
        assert heater.hvac_mode.value == "heat"

    def test_hvac_mode_off(self, make_device, mock_coordinator):
        """Test HVAC mode is OFF when heater is off."""
        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterSwitch": "0"})
        heater = LiproHeater(mock_coordinator, device)
        assert heater.hvac_mode.value == "off"


class TestLiproHeaterTranslationKey:
    """Tests for heater translation_key (icons managed via icons.json)."""

    def test_translation_key(self, make_device, mock_coordinator):
        """Test translation_key is set for icons.json mapping."""
        from custom_components.lipro.climate import LiproHeater

        assert LiproHeater.__dict__["__attr_translation_key"] == "heater"


class TestLiproHeaterPresetModes:
    """Tests for heater preset mode mappings."""

    def test_mode_to_preset_mapping(self):
        """Test MODE_TO_PRESET mapping from real source."""
        from custom_components.lipro.climate import MODE_TO_PRESET
        from custom_components.lipro.const import (
            HEATER_MODE_DEFAULT,
            HEATER_MODE_DEMIST,
            HEATER_MODE_DRY,
            HEATER_MODE_GENTLE_WIND,
        )

        assert MODE_TO_PRESET[HEATER_MODE_DEFAULT] == "default"
        assert MODE_TO_PRESET[HEATER_MODE_DEMIST] == "demist"
        assert MODE_TO_PRESET[HEATER_MODE_DRY] == "dry"
        assert MODE_TO_PRESET[HEATER_MODE_GENTLE_WIND] == "gentle_wind"

    def test_preset_to_mode_mapping(self):
        """Test PRESET_TO_MODE mapping from real source."""
        from custom_components.lipro.climate import PRESET_TO_MODE
        from custom_components.lipro.const import (
            HEATER_MODE_DEFAULT,
            HEATER_MODE_DEMIST,
            HEATER_MODE_DRY,
            HEATER_MODE_GENTLE_WIND,
        )

        assert PRESET_TO_MODE["default"] == HEATER_MODE_DEFAULT
        assert PRESET_TO_MODE["demist"] == HEATER_MODE_DEMIST
        assert PRESET_TO_MODE["dry"] == HEATER_MODE_DRY
        assert PRESET_TO_MODE["gentle_wind"] == HEATER_MODE_GENTLE_WIND

    def test_bidirectional_consistency(self):
        """Test MODE_TO_PRESET and PRESET_TO_MODE are consistent."""
        from custom_components.lipro.climate import MODE_TO_PRESET, PRESET_TO_MODE

        for mode, preset in MODE_TO_PRESET.items():
            assert PRESET_TO_MODE[preset] == mode

    def test_preset_modes_list(self):
        """Test all preset modes are defined in real source."""
        from custom_components.lipro.climate import PRESET_MODES

        assert len(PRESET_MODES) == 4
        assert "default" in PRESET_MODES
        assert "demist" in PRESET_MODES
        assert "dry" in PRESET_MODES
        assert "gentle_wind" in PRESET_MODES


class TestLiproHeaterConstants:
    """Tests for heater-related constants."""

    def test_heater_mode_constants(self):
        """Test heater mode constants."""
        from custom_components.lipro.const import (
            HEATER_MODE_DEFAULT,
            HEATER_MODE_DEMIST,
            HEATER_MODE_DRY,
            HEATER_MODE_GENTLE_WIND,
        )

        assert HEATER_MODE_DEFAULT == 0
        assert HEATER_MODE_DEMIST == 1
        assert HEATER_MODE_DRY == 2
        assert HEATER_MODE_GENTLE_WIND == 3

    def test_property_constants(self):
        """Test heater property constants."""
        from custom_components.lipro.const import PROP_HEATER_MODE, PROP_HEATER_SWITCH

        assert PROP_HEATER_SWITCH == "heaterSwitch"
        assert PROP_HEATER_MODE == "heaterMode"


class TestLiproHeaterEntityCommands:
    """Tests for LiproHeater entity command methods."""

    @pytest.mark.asyncio
    async def test_set_hvac_mode_heat(self, mock_coordinator, make_device):
        """Test async_set_hvac_mode(HEAT) sends POWER_ON command."""
        from unittest.mock import MagicMock

        from homeassistant.components.climate import HVACMode

        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterSwitch": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)
        heater.async_write_ha_state = MagicMock()

        await heater.async_set_hvac_mode(HVACMode.HEAT)

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_ON", None
        )

    @pytest.mark.asyncio
    async def test_set_hvac_mode_off(self, mock_coordinator, make_device):
        """Test async_set_hvac_mode(OFF) sends POWER_OFF command."""
        from unittest.mock import MagicMock

        from homeassistant.components.climate import HVACMode

        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterSwitch": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)
        heater.async_write_ha_state = MagicMock()

        await heater.async_set_hvac_mode(HVACMode.OFF)

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_OFF", None
        )

    @pytest.mark.asyncio
    async def test_set_preset_mode(self, mock_coordinator, make_device):
        """Test async_set_preset_mode sends CHANGE_STATE with heaterMode."""
        from unittest.mock import MagicMock

        from custom_components.lipro.climate import LiproHeater
        from custom_components.lipro.const import HEATER_MODE_DRY

        device = make_device("heater", properties={"heaterSwitch": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)
        heater.async_write_ha_state = MagicMock()

        await heater.async_set_preset_mode("dry")

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "heaterMode", "value": str(HEATER_MODE_DRY)}],
        )

    @pytest.mark.asyncio
    async def test_turn_on_delegates_to_set_hvac_mode(self, mock_coordinator, make_device):
        """Test async_turn_on delegates to async_set_hvac_mode(HEAT)."""
        from unittest.mock import MagicMock

        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterSwitch": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)
        heater.async_write_ha_state = MagicMock()

        await heater.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_ON", None
        )

    @pytest.mark.asyncio
    async def test_turn_off_delegates_to_set_hvac_mode(self, mock_coordinator, make_device):
        """Test async_turn_off delegates to async_set_hvac_mode(OFF)."""
        from unittest.mock import MagicMock

        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterSwitch": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)
        heater.async_write_ha_state = MagicMock()

        await heater.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_OFF", None
        )

    def test_preset_mode_property(self, mock_coordinator, make_device):
        """Test preset_mode returns correct preset for current heater mode."""
        from unittest.mock import MagicMock

        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterMode": "2"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)

        assert heater.preset_mode == "dry"

    def test_preset_mode_default_fallback(self, mock_coordinator, make_device):
        """Test preset_mode falls back to 'default' for unknown mode."""
        from unittest.mock import MagicMock

        from custom_components.lipro.climate import LiproHeater

        device = make_device("heater", properties={"heaterMode": "99"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        heater = LiproHeater(mock_coordinator, device)

        assert heater.preset_mode == "default"
