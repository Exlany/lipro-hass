"""Tests for Lipro fan platform."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


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
    async def test_set_percentage_debounce_protects_power_onoff(
        self, mock_coordinator, make_device
    ):
        """Turning on via set_percentage should stay on the debounced optimistic path."""
        device = make_device("fanLight", properties={"fanOnoff": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.fan import LiproFan

        fan = LiproFan(mock_coordinator, device)
        captured_args = {}

        async def capture_debounced(command, properties, optimistic_state):
            captured_args["command"] = command
            captured_args["properties"] = properties
            captured_args["optimistic_state"] = optimistic_state

        with (
            patch.object(
                type(device), "update_properties", autospec=True
            ) as update_properties,
            patch.object(fan, "async_write_ha_state"),
            patch.object(fan, "async_send_command_debounced", new=capture_debounced),
        ):
            await fan.async_set_percentage(50)

        props = captured_args["properties"]
        assert any(p["key"] == "fanOnoff" and p["value"] == "1" for p in props)

        optimistic_state = captured_args["optimistic_state"]
        assert optimistic_state["fanOnoff"] == "1"
        assert "fanGear" in optimistic_state
        update_properties.assert_not_called()


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

        devices = {
            "fan": make_device("fanLight"),
            "heater": make_device("heater"),
            "light": make_device("light"),
        }
        coordinator = SimpleNamespace(
            devices=devices,
            iter_devices=lambda: tuple(devices.values()),
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

    def test_preset_mode_unknown_mode_returns_none(self, mock_coordinator, make_device):
        """Unknown fan mode should stay truthful instead of pretending to be cycle."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanMode": "99"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)
        assert fan.preset_mode is None

    def test_preset_mode_gentle_wind(self, mock_coordinator, make_device):
        """fanMode=3 should map to gentle_wind preset."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanMode": "3"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)
        assert fan.preset_mode == "gentle_wind"
        assert "gentle_wind" in (fan.preset_modes or [])

    @pytest.mark.asyncio
    async def test_set_preset_mode_gentle_wind_dispatches_command(
        self, mock_coordinator, make_device
    ) -> None:
        """gentle_wind should be a supported preset mode."""
        from custom_components.lipro.fan import LiproFan

        device = make_device("fanLight", properties={"fanOnoff": "1", "fanMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        with patch.object(fan, "async_write_ha_state"):
            await fan.async_set_preset_mode("gentle_wind")

        call_args = mock_coordinator.async_send_command.call_args
        properties = call_args[0][2]
        assert any(p["key"] == "fanMode" and p["value"] == "3" for p in properties)

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

    def test_unknown_mode_keeps_speed_feature_without_fake_cycle_projection(
        self, mock_coordinator, make_device
    ) -> None:
        """Unknown vendor modes should keep truthful feature/preset projection."""
        from custom_components.lipro.fan import LiproFan
        from homeassistant.components.fan import FanEntityFeature

        device = make_device("fanLight", properties={"fanMode": "99"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproFan(mock_coordinator, device)

        assert fan.preset_mode is None
        assert fan.supported_features & FanEntityFeature.SET_SPEED

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

        async def capture_debounced(command, properties, optimistic_state):
            captured_args["command"] = command
            captured_args["properties"] = properties
            captured_args["optimistic_state"] = optimistic_state

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

    def test_vent_entity_properties_cover_is_on_and_unknown_preset(
        self, mock_coordinator, make_device
    ) -> None:
        """Vent entity should surface on-state without masking unknown gear."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "99"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        assert fan.is_on is True
        assert fan.preset_mode is None

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
    async def test_turn_on_invalid_preset_is_ignored(
        self, mock_coordinator, make_device
    ) -> None:
        """Explicit invalid preset should not fallback to strong on turn_on."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        await fan.async_turn_on(preset_mode="invalid")

        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_invalid_preset_is_ignored(self, mock_coordinator, make_device):
        """Invalid vent preset should not fallback to strong."""
        from custom_components.lipro.fan import LiproHeaterVentFan

        device = make_device("heater", properties={"aerationGear": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fan = LiproHeaterVentFan(mock_coordinator, device)

        await fan.async_set_preset_mode("invalid")

        mock_coordinator.async_send_command.assert_not_called()

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
