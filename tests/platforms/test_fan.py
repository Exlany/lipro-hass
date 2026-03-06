"""Tests for Lipro fan platform."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


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
        """Test fan mode default is 0 (direct)."""
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


class TestLiproFanPresetModes:
    """Tests for fan preset mode mappings."""

    def test_mode_to_preset_mapping(self):
        """Test MODE_TO_PRESET mapping from real source."""
        from custom_components.lipro.const.properties import (
            FAN_MODE_CYCLE,
            FAN_MODE_DIRECT,
            FAN_MODE_GENTLE_WIND,
            FAN_MODE_NATURAL,
        )
        from custom_components.lipro.fan import MODE_TO_PRESET

        assert MODE_TO_PRESET[FAN_MODE_DIRECT] == "direct"
        assert MODE_TO_PRESET[FAN_MODE_NATURAL] == "natural"
        assert MODE_TO_PRESET[FAN_MODE_CYCLE] == "cycle"
        assert MODE_TO_PRESET[FAN_MODE_GENTLE_WIND] == "gentle_wind"

    def test_preset_to_mode_mapping(self):
        """Test PRESET_TO_MODE mapping from real source."""
        from custom_components.lipro.const.properties import (
            FAN_MODE_CYCLE,
            FAN_MODE_DIRECT,
            FAN_MODE_NATURAL,
        )
        from custom_components.lipro.fan import PRESET_TO_MODE

        assert PRESET_TO_MODE["direct"] == FAN_MODE_DIRECT
        assert PRESET_TO_MODE["natural"] == FAN_MODE_NATURAL
        assert PRESET_TO_MODE["cycle"] == FAN_MODE_CYCLE
        assert "gentle_wind" not in PRESET_TO_MODE

    def test_bidirectional_consistency(self):
        """Test MODE_TO_PRESET and PRESET_TO_MODE are consistent."""
        from custom_components.lipro.fan import MODE_TO_PRESET, PRESET_TO_MODE

        for mode, preset in MODE_TO_PRESET.items():
            if preset in PRESET_TO_MODE:
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


class TestLiproHeaterVentPresetModes:
    """Tests for heater ventilation preset mode mappings."""

    def test_aeration_to_preset_mapping(self):
        """Test AERATION_TO_PRESET mapping from real source."""
        from custom_components.lipro.const.properties import (
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
        from custom_components.lipro.const.properties import (
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
        from custom_components.lipro.const.properties import (
            AERATION_OFF,
            AERATION_STRONG,
            AERATION_WEAK,
        )

        assert AERATION_OFF == 0
        assert AERATION_STRONG == 1
        assert AERATION_WEAK == 2


class TestLiproFanEntityCommands:
    """Tests for LiproFan entity command methods."""

    @pytest.mark.asyncio
    async def test_turn_on(self, mock_coordinator, make_device):
        """Test async_turn_on sends CHANGE_STATE with fanOnoff=1."""
        device = make_device("fanLight", properties={"fanOnoff": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.fan import LiproFan

        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
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

        with patch.object(fan, "async_write_ha_state"):
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
        """Test set_percentage does NOT include fanOnoff in debounce-protected keys.

        When fan is off and set_percentage is called, fanOnoff should be sent
        in properties but NOT in the optimistic dict passed to debounce,
        so it won't be protected during the debounce window.
        """
        device = make_device("fanLight", properties={"fanOnoff": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.fan import LiproFan

        fan = LiproFan(mock_coordinator, device)

        # Mock async_send_command_debounced to capture arguments
        captured_args = {}

        async def capture_debounced(command, properties, optimistic):
            captured_args["command"] = command
            captured_args["properties"] = properties
            captured_args["optimistic"] = optimistic

        with (
            patch.object(fan, "async_write_ha_state"),
            patch.object(fan, "async_send_command_debounced", new=capture_debounced),
        ):
            await fan.async_set_percentage(50)

        # Properties should include fan power + gear.
        props = captured_args["properties"]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in props)

        # Optimistic dict should NOT include fan power keys (to avoid debounce protection)
        optimistic = captured_args["optimistic"]
        assert "fanOnoff" not in optimistic
        assert "fanGear" in optimistic


class TestLiproFanEntityBehavior:
    """Behavior tests for fan entities."""

    def test_speed_count_reads_device_max_gear(self, mock_coordinator, make_device):
        """speed_count should come from device max_fan_gear."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", max_fan_gear=10)
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        assert fan.speed_count == 10

    def test_supported_features_non_cycle_keeps_set_speed(
        self, mock_coordinator, make_device
    ):
        """Non-cycle mode should still expose SET_SPEED."""
        from custom_components.lipro.fan import LiproFan
        from homeassistant.components.fan import FanEntityFeature

        device = make_device("fanLight", properties={"fanMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        assert fan.supported_features & FanEntityFeature.PRESET_MODE
        assert fan.supported_features & FanEntityFeature.SET_SPEED

    @pytest.mark.parametrize(
        ("properties", "expected_percentage"),
        [
            ({"fanOnoff": "0", "fanGear": "3"}, 0),
            ({"fanOnoff": "1", "fanGear": "3"}, 50),
        ],
    )
    def test_percentage_property_on_and_off_branches(
        self,
        mock_coordinator,
        make_device,
        properties,
        expected_percentage,
    ) -> None:
        """percentage should be 0 when off, otherwise converted from gear."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties=properties)
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        assert fan.percentage == expected_percentage

    @pytest.mark.asyncio
    async def test_async_setup_entry_creates_fan_and_heater_entities(
        self, hass, make_device
    ) -> None:
        """Platform setup should create fan entities for fanLight and heater."""
        from custom_components.lipro.fan import (
            LiproFan,
            LiproHeaterVentFan,
            async_setup_entry,
        )

        coordinator = SimpleNamespace(
            devices={
                "fan": make_device("fanLight"),
                "heater": make_device("heater"),
                "light": make_device("light"),
            }
        )
        entry = SimpleNamespace(runtime_data=coordinator)
        from custom_components.lipro import LiproConfigEntry
        from homeassistant.helpers.entity import Entity
        from homeassistant.helpers.entity_platform import AddEntitiesCallback

        captured: list[Entity] = []

        def _add_entities(
            entities: Iterable[Entity],
            update_before_add: bool = False,
        ) -> None:
            captured.extend(entities)

        await async_setup_entry(
            hass,
            cast(LiproConfigEntry, entry),
            cast(AddEntitiesCallback, _add_entities),
        )

        assert len(captured) == 2
        assert any(isinstance(entity, LiproFan) for entity in captured)
        assert any(isinstance(entity, LiproHeaterVentFan) for entity in captured)

    @pytest.mark.asyncio
    async def test_turn_on_with_percentage_and_preset(
        self, mock_coordinator, make_device
    ):
        """async_turn_on should include fan power, speed and preset mode."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_turn_on(percentage=50, preset_mode="natural")

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in properties)
        assert any(p["key"] == "fanGear" for p in properties)
        assert any(p["key"] == "fanMode" for p in properties)

    @pytest.mark.asyncio
    async def test_turn_on_with_invalid_preset_ignores_mode(
        self, mock_coordinator, make_device
    ) -> None:
        """Unsupported preset should be ignored when turning on."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "0", "fanMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_turn_on(preset_mode="invalid")

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in properties)
        assert not any(p["key"] == "fanMode" for p in properties)

    @pytest.mark.asyncio
    async def test_turn_on_cycle_mode_ignores_percentage(
        self, mock_coordinator, make_device
    ) -> None:
        """When turning on in cycle mode, speed percentage should be ignored."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "0", "fanMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_turn_on(percentage=75, preset_mode="cycle")

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in properties)
        assert any(p["key"] == "fanMode" and p["value"] == "2" for p in properties)
        assert not any(p["key"] == "fanGear" for p in properties)

    @pytest.mark.asyncio
    async def test_set_percentage_zero_turns_off(self, mock_coordinator, make_device):
        """Setting 0% speed should call turn_off branch."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_set_percentage(0)

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "0" for p in properties)

    @pytest.mark.asyncio
    async def test_set_preset_mode_when_off_adds_power(
        self, mock_coordinator, make_device
    ):
        """Setting preset while off should add fan power-on property."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "0", "fanMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_set_preset_mode("cycle")

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in properties)
        assert any(p["key"] == "fanMode" for p in properties)

    def test_preset_mode_fallbacks_to_cycle(self, mock_coordinator, make_device):
        """Unknown fan mode should fallback to cycle preset."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanMode": "99"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)
        assert fan.preset_mode == "cycle"

    def test_preset_mode_gentle_wind(self, mock_coordinator, make_device):
        """fanMode=3 should map to gentle_wind preset."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanMode": "3"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)
        assert fan.preset_mode == "gentle_wind"
        assert "gentle_wind" not in (fan.preset_modes or [])

    @pytest.mark.asyncio
    async def test_set_preset_mode_gentle_wind_is_ignored(
        self, mock_coordinator, make_device
    ) -> None:
        """Unsupported gentle_wind should be ignored (keep current mode)."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "1", "fanMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_set_preset_mode("gentle_wind")

        mock_coordinator.async_send_command.assert_not_called()

    def test_supported_features_cycle_mode_disables_set_speed(
        self, mock_coordinator, make_device
    ):
        """Cycle mode should not expose SET_SPEED feature."""
        from custom_components.lipro.fan import LiproFan
        from homeassistant.components.fan import FanEntityFeature

        device = make_device("fanLight", properties={"fanMode": "2"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        assert fan.supported_features & FanEntityFeature.PRESET_MODE
        assert not (fan.supported_features & FanEntityFeature.SET_SPEED)

    @pytest.mark.asyncio
    async def test_set_percentage_cycle_mode_is_ignored(
        self, mock_coordinator, make_device
    ):
        """Cycle mode should ignore speed-change commands."""
        from custom_components.lipro.fan import LiproFan

        device = make_device(
            "fanLight",
            properties={"fanOnoff": "1", "fanMode": "2", "fanGear": "10"},
        )
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(fan, "async_write_ha_state"),
            patch.object(
                fan,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await fan.async_set_percentage(44)

        mock_send_command_debounced.assert_not_awaited()
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_percentage_when_on_does_not_add_power_property(
        self, mock_coordinator, make_device
    ) -> None:
        """When already on, set_percentage should not resend fanOnoff."""
        from custom_components.lipro.fan import LiproFan

        device = make_device(
            "fanLight",
            properties={"fanOnoff": "1", "fanMode": "0", "fanGear": "2"},
        )
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        captured_args: dict[str, object] = {}

        async def capture_debounced(command, properties, optimistic):
            captured_args["command"] = command
            captured_args["properties"] = properties
            captured_args["optimistic"] = optimistic

        with (
            patch.object(fan, "async_write_ha_state"),
            patch.object(fan, "async_send_command_debounced", new=capture_debounced),
        ):
            await fan.async_set_percentage(50)

        properties = cast(list[dict[str, str]], captured_args["properties"])
        assert any(p["key"] == "fanGear" for p in properties)
        assert not any(p["key"] == "fanOnoff" for p in properties)


class TestLiproHeaterVentFanBehavior:
    """Behavior tests for heater ventilation fan entity."""

    def test_vent_entity_properties_cover_is_on_and_preset_fallback(
        self, mock_coordinator, make_device
    ) -> None:
        """Vent entity should expose on-state and fallback preset mapping."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "99"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        assert fan.is_on is True
        assert fan.preset_mode == "off"

    @pytest.mark.asyncio
    async def test_turn_on_default_uses_strong(self, mock_coordinator, make_device):
        """Turning on without preset should default to strong gear."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_turn_on()

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "aerationGear" and p["value"] == "1" for p in properties)

    @pytest.mark.asyncio
    async def test_set_invalid_preset_fallbacks_to_strong(
        self, mock_coordinator, make_device
    ):
        """Invalid vent preset should fallback to strong."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_set_preset_mode("invalid")

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "aerationGear" and p["value"] == "1" for p in properties)

    @pytest.mark.asyncio
    async def test_turn_off_sets_aeration_to_off(self, mock_coordinator, make_device):
        """Turning off ventilation fan should set aeration gear to 0."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_turn_off()

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "aerationGear" and p["value"] == "0" for p in properties)
