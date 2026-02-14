"""Tests for Lipro fan platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

try:
    from pytest_homeassistant_custom_component.common import (
        MockConfigEntry,  # noqa: F401
    )

    HAS_HA_TEST_ENV = True
except ImportError:
    HAS_HA_TEST_ENV = False


class TestLiproFan:
    """Tests for LiproFan entity."""

    def test_fan_is_on(self, make_device):
        """Test fan is_on property."""
        device = make_device("fanLight", properties={"fanOnoff": "1"})
        assert device.fan_is_on is True

    def test_fan_is_on_alt_key(self, make_device):
        """Test fan is_on with status query key 'fanOnOff' (capital O)."""
        device = make_device("fanLight", properties={"fanOnOff": "1"})
        assert device.fan_is_on is True

    def test_fan_is_off_alt_key(self, make_device):
        """Test fan is_off with status query key 'fanOnOff' (capital O)."""
        device = make_device("fanLight", properties={"fanOnOff": "0"})
        assert device.fan_is_on is False

    def test_fan_is_off(self, make_device):
        """Test fan is_off property."""
        device = make_device("fanLight", properties={"fanOnoff": "0"})
        assert device.fan_is_on is False

    def test_fan_default_off(self, make_device):
        """Test fan default is off."""
        device = make_device("fanLight")
        assert device.fan_is_on is False

    def test_fan_gear(self, make_device):
        """Test fan gear property."""
        device = make_device("fanLight", properties={"fanGear": "5"})
        assert device.fan_gear == 5

    def test_fan_gear_default(self, make_device):
        """Test fan gear default is 1."""
        device = make_device("fanLight")
        assert device.fan_gear == 1

    def test_fan_mode(self, make_device):
        """Test fan mode property."""
        device = make_device("fanLight", properties={"fanMode": "2"})
        assert device.fan_mode == 2

    def test_fan_mode_default(self, make_device):
        """Test fan mode default is 0 (natural)."""
        device = make_device("fanLight")
        assert device.fan_mode == 0

    def test_fan_speed_range_default(self, make_device):
        """Test default fan speed range is (1, 6)."""
        device = make_device("fanLight")
        assert device.fan_speed_range == (1, 6)
        assert device.max_fan_gear == 6

    def test_fan_speed_range_custom(self, make_device):
        """Test custom fan speed range via max_fan_gear."""
        device = make_device("fanLight", max_fan_gear=10)
        assert device.fan_speed_range == (1, 10)
        assert device.max_fan_gear == 10

    def test_fan_gear_clamped_to_max(self, make_device):
        """Test fan gear is clamped to max_fan_gear."""
        device = make_device("fanLight", properties={"fanGear": "8"}, max_fan_gear=6)
        assert device.fan_gear == 6

    def test_fan_gear_clamped_to_custom_max(self, make_device):
        """Test fan gear is clamped to custom max_fan_gear."""
        device = make_device("fanLight", properties={"fanGear": "5"}, max_fan_gear=3)
        assert device.fan_gear == 3

    def test_fan_gear_clamped_to_min(self, make_device):
        """Test fan gear is clamped to min 1."""
        device = make_device("fanLight", properties={"fanGear": "0"})
        assert device.fan_gear == 1

    @pytest.mark.skipif(
        not HAS_HA_TEST_ENV, reason="Requires HA test env for entity class import"
    )
    def test_translation_key(self, make_device, mock_coordinator):
        """Test translation_key is set for icons.json mapping."""
        from custom_components.lipro.fan import LiproFan

        assert LiproFan.__dict__["__attr_translation_key"] == "fan"


class TestLiproFanPercentage:
    """Tests for fan speed percentage conversion."""

    def test_gear_to_percentage_default_range(self, make_device):
        """Test gear to percentage with default range (1-6)."""
        # HA formula: ((value - low) / (high - low)) * 100, rounded
        device = make_device("fanLight")
        low, high = device.fan_speed_range
        assert (low, high) == (1, 6)
        # gear 6 -> 100%
        assert round((6 - low) / (high - low) * 100) == 100
        # gear 1 -> 0%
        assert round((1 - low) / (high - low) * 100) == 0
        # gear 3 -> 40%
        assert round((3 - low) / (high - low) * 100) == 40

    def test_percentage_to_gear_default_range(self, make_device):
        """Test percentage to gear with default range (1-6)."""
        import math

        device = make_device("fanLight")
        low, high = device.fan_speed_range
        # 100% -> gear 6
        assert math.ceil(low + (high - low) * 100 / 100) == 6
        # 50% -> gear 4
        assert math.ceil(low + (high - low) * 50 / 100) == 4

    def test_gear_to_percentage_custom_range(self, make_device):
        """Test gear to percentage with custom range (1-10)."""
        device = make_device("fanLight", max_fan_gear=10)
        low, high = device.fan_speed_range
        assert (low, high) == (1, 10)
        # gear 10 -> 100%
        assert round((10 - low) / (high - low) * 100) == 100
        # gear 1 -> 0%
        assert round((1 - low) / (high - low) * 100) == 0
        # gear 5 -> ~44%
        assert round((5 - low) / (high - low) * 100) == 44

    def test_percentage_to_gear_custom_range(self, make_device):
        """Test percentage to gear with custom range (1-10)."""
        import math

        device = make_device("fanLight", max_fan_gear=10)
        low, high = device.fan_speed_range
        # 100% -> gear 10
        assert math.ceil(low + (high - low) * 100 / 100) == 10
        # 50% -> gear 6
        assert math.ceil(low + (high - low) * 50 / 100) == 6


@pytest.mark.skipif(
    not HAS_HA_TEST_ENV, reason="Requires HA test env for entity class import"
)
class TestLiproFanPresetModes:
    """Tests for fan preset mode mappings."""

    def test_mode_to_preset_mapping(self):
        """Test MODE_TO_PRESET mapping from real source."""
        from custom_components.lipro.const import (
            FAN_MODE_NATURAL,
            FAN_MODE_NORMAL,
            FAN_MODE_SLEEP,
        )
        from custom_components.lipro.fan import MODE_TO_PRESET

        assert MODE_TO_PRESET[FAN_MODE_NATURAL] == "natural"
        assert MODE_TO_PRESET[FAN_MODE_SLEEP] == "sleep"
        assert MODE_TO_PRESET[FAN_MODE_NORMAL] == "normal"

    def test_preset_to_mode_mapping(self):
        """Test PRESET_TO_MODE mapping from real source."""
        from custom_components.lipro.const import (
            FAN_MODE_NATURAL,
            FAN_MODE_NORMAL,
            FAN_MODE_SLEEP,
        )
        from custom_components.lipro.fan import PRESET_TO_MODE

        assert PRESET_TO_MODE["natural"] == FAN_MODE_NATURAL
        assert PRESET_TO_MODE["sleep"] == FAN_MODE_SLEEP
        assert PRESET_TO_MODE["normal"] == FAN_MODE_NORMAL

    def test_bidirectional_consistency(self):
        """Test MODE_TO_PRESET and PRESET_TO_MODE are consistent."""
        from custom_components.lipro.fan import MODE_TO_PRESET, PRESET_TO_MODE

        for mode, preset in MODE_TO_PRESET.items():
            assert PRESET_TO_MODE[preset] == mode


class TestLiproHeaterVentFan:
    """Tests for LiproHeaterVentFan entity."""

    def test_vent_fan_is_on(self, make_device):
        """Test ventilation fan is on when aerationGear != 0."""
        device = make_device("heater", properties={"aerationGear": "1"})
        assert device.aeration_gear == 1
        assert device.aeration_is_on is True

    def test_vent_fan_is_off(self, make_device):
        """Test ventilation fan is off when aerationGear == 0."""
        device = make_device("heater", properties={"aerationGear": "0"})
        assert device.aeration_gear == 0
        assert device.aeration_is_on is False

    def test_vent_fan_default_off(self, make_device):
        """Test ventilation fan default is off."""
        device = make_device("heater")
        assert device.aeration_gear == 0
        assert device.aeration_is_on is False

    def test_vent_fan_weak(self, make_device):
        """Test ventilation fan weak mode."""
        device = make_device("heater", properties={"aerationGear": "2"})
        assert device.aeration_gear == 2

    def test_is_heater(self, make_device):
        """Test device is identified as heater."""
        device = make_device("heater")
        assert device.is_heater is True


@pytest.mark.skipif(
    not HAS_HA_TEST_ENV, reason="Requires HA test env for entity class import"
)
class TestLiproHeaterVentPresetModes:
    """Tests for heater ventilation preset mode mappings."""

    def test_aeration_to_preset_mapping(self):
        """Test AERATION_TO_PRESET mapping from real source."""
        from custom_components.lipro.const import (
            AERATION_OFF,
            AERATION_STRONG,
            AERATION_WEAK,
        )
        from custom_components.lipro.fan import AERATION_TO_PRESET

        assert AERATION_TO_PRESET[AERATION_OFF] == "off"
        assert AERATION_TO_PRESET[AERATION_STRONG] == "strong"
        assert AERATION_TO_PRESET[AERATION_WEAK] == "weak"

    def test_preset_to_aeration_mapping(self):
        """Test PRESET_TO_AERATION mapping from real source."""
        from custom_components.lipro.const import (
            AERATION_OFF,
            AERATION_STRONG,
            AERATION_WEAK,
        )
        from custom_components.lipro.fan import PRESET_TO_AERATION

        assert PRESET_TO_AERATION["off"] == AERATION_OFF
        assert PRESET_TO_AERATION["strong"] == AERATION_STRONG
        assert PRESET_TO_AERATION["weak"] == AERATION_WEAK

    def test_bidirectional_consistency(self):
        """Test AERATION_TO_PRESET and PRESET_TO_AERATION are consistent."""
        from custom_components.lipro.fan import AERATION_TO_PRESET, PRESET_TO_AERATION

        for aeration, preset in AERATION_TO_PRESET.items():
            assert PRESET_TO_AERATION[preset] == aeration

    def test_aeration_constants(self):
        """Test aeration gear constants."""
        from custom_components.lipro.const import (
            AERATION_OFF,
            AERATION_STRONG,
            AERATION_WEAK,
        )

        assert AERATION_OFF == 0
        assert AERATION_STRONG == 1
        assert AERATION_WEAK == 2


@pytest.mark.skipif(
    not HAS_HA_TEST_ENV, reason="Requires pytest-homeassistant-custom-component"
)
class TestLiproFanEntityCommands:
    """Tests for LiproFan entity command methods."""

    @pytest.mark.asyncio
    async def test_turn_on(self, mock_coordinator, make_device):
        """Test async_turn_on sends CHANGE_STATE with fanOnoff=1."""
        device = make_device("fanLight", properties={"fanOnoff": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.fan import LiproFan

        fan = LiproFan(mock_coordinator, device)
        fan.async_write_ha_state = MagicMock()

        await fan.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once()
        call_args = mock_coordinator.async_send_command.call_args
        assert call_args[0][0] is device
        assert call_args[0][1] == "CHANGE_STATE"
        props = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in props)

    @pytest.mark.asyncio
    async def test_turn_off(self, mock_coordinator, make_device):
        """Test async_turn_off sends CHANGE_STATE with fanOnoff=0."""
        device = make_device("fanLight", properties={"fanOnoff": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.fan import LiproFan

        fan = LiproFan(mock_coordinator, device)
        fan.async_write_ha_state = MagicMock()

        await fan.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once()
        call_args = mock_coordinator.async_send_command.call_args
        assert call_args[0][0] is device
        assert call_args[0][1] == "CHANGE_STATE"
        props = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "0" for p in props)

    @pytest.mark.asyncio
    async def test_set_percentage_debounce_does_not_protect_fan_onoff(
        self, mock_coordinator, make_device
    ):
        """Test set_percentage does NOT include fanOnOff in debounce-protected keys.

        When fan is off and set_percentage is called, fanOnOff should be sent
        in properties but NOT in the optimistic dict passed to debounce,
        so it won't be protected during the debounce window.
        """
        device = make_device("fanLight", properties={"fanOnoff": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.fan import LiproFan

        fan = LiproFan(mock_coordinator, device)
        fan.async_write_ha_state = MagicMock()

        # Mock async_send_command_debounced to capture arguments
        captured_args = {}

        async def capture_debounced(command, properties, optimistic):
            captured_args["command"] = command
            captured_args["properties"] = properties
            captured_args["optimistic"] = optimistic

        fan.async_send_command_debounced = capture_debounced

        await fan.async_set_percentage(50)

        # Properties should include fanOnoff (for the API)
        props = captured_args["properties"]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in props)

        # Optimistic dict should NOT include fanOnoff (to avoid debounce protection)
        optimistic = captured_args["optimistic"]
        assert "fanOnoff" not in optimistic
        assert "fanGear" in optimistic
