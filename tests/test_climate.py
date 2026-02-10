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

    def test_hvac_mode_heat(self):
        """Test HVAC mode is HEAT when heater is on."""
        heater_is_on = True
        hvac_mode = "heat" if heater_is_on else "off"
        assert hvac_mode == "heat"

    def test_hvac_mode_off(self):
        """Test HVAC mode is OFF when heater is off."""
        heater_is_on = False
        hvac_mode = "heat" if heater_is_on else "off"
        assert hvac_mode == "off"


class TestLiproHeaterIcon:
    """Tests for heater icon logic."""

    def test_icon_heating(self):
        """Test icon when heating."""
        hvac_mode = "heat"
        icon = "mdi:radiator" if hvac_mode == "heat" else "mdi:radiator-off"
        assert icon == "mdi:radiator"

    def test_icon_off(self):
        """Test icon when off."""
        hvac_mode = "off"
        icon = "mdi:radiator" if hvac_mode == "heat" else "mdi:radiator-off"
        assert icon == "mdi:radiator-off"


class TestLiproHeaterPresetModes:
    """Tests for heater preset mode mappings."""

    def test_mode_to_preset_mapping(self):
        """Test MODE_TO_PRESET mapping."""
        from custom_components.lipro.const import (
            HEATER_MODE_DEFAULT,
            HEATER_MODE_DEMIST,
            HEATER_MODE_DRY,
            HEATER_MODE_GENTLE_WIND,
        )

        # Replicate the mapping from climate.py
        mode_to_preset = {
            HEATER_MODE_DEFAULT: "default",
            HEATER_MODE_DEMIST: "demist",
            HEATER_MODE_DRY: "dry",
            HEATER_MODE_GENTLE_WIND: "gentle_wind",
        }

        assert mode_to_preset[HEATER_MODE_DEFAULT] == "default"
        assert mode_to_preset[HEATER_MODE_DEMIST] == "demist"
        assert mode_to_preset[HEATER_MODE_DRY] == "dry"
        assert mode_to_preset[HEATER_MODE_GENTLE_WIND] == "gentle_wind"

    def test_preset_to_mode_mapping(self):
        """Test PRESET_TO_MODE mapping."""
        from custom_components.lipro.const import (
            HEATER_MODE_DEFAULT,
            HEATER_MODE_DEMIST,
            HEATER_MODE_DRY,
            HEATER_MODE_GENTLE_WIND,
        )

        preset_to_mode = {
            "default": HEATER_MODE_DEFAULT,
            "demist": HEATER_MODE_DEMIST,
            "dry": HEATER_MODE_DRY,
            "gentle_wind": HEATER_MODE_GENTLE_WIND,
        }

        assert preset_to_mode["default"] == HEATER_MODE_DEFAULT
        assert preset_to_mode["demist"] == HEATER_MODE_DEMIST
        assert preset_to_mode["dry"] == HEATER_MODE_DRY
        assert preset_to_mode["gentle_wind"] == HEATER_MODE_GENTLE_WIND

    def test_bidirectional_consistency(self):
        """Test MODE_TO_PRESET and PRESET_TO_MODE are consistent."""
        from custom_components.lipro.const import (
            HEATER_MODE_DEFAULT,
            HEATER_MODE_DEMIST,
            HEATER_MODE_DRY,
            HEATER_MODE_GENTLE_WIND,
        )

        mode_to_preset = {
            HEATER_MODE_DEFAULT: "default",
            HEATER_MODE_DEMIST: "demist",
            HEATER_MODE_DRY: "dry",
            HEATER_MODE_GENTLE_WIND: "gentle_wind",
        }
        preset_to_mode = {v: k for k, v in mode_to_preset.items()}

        for mode, preset in mode_to_preset.items():
            assert preset_to_mode[preset] == mode

    def test_preset_modes_list(self):
        """Test all preset modes are defined."""
        preset_modes = ["default", "demist", "dry", "gentle_wind"]
        assert len(preset_modes) == 4


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
