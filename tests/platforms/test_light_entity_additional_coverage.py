"""Additional coverage for light entity behavior."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest


class TestLiproLightAdditionalCoverage:
    """Additional branch tests for light platform behavior."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_adds_only_light_entities(self, hass, make_device):
        """Setup should create entities only for light and fan-light devices."""
        from custom_components.lipro.light import LiproLight, async_setup_entry

        devices = {
            "light_1": make_device("light"),
            "fan_light": make_device("fanLight"),
            "switch_1": make_device("switch"),
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
        assert all(isinstance(entity, LiproLight) for entity in captured)

    def test_brightness_only_device_color_mode_branches(
        self, mock_coordinator, make_device
    ):
        """Brightness-only devices should expose BRIGHTNESS mode and no color temp."""
        from custom_components.lipro.light import LiproLight
        from homeassistant.components.light.const import ColorMode

        device = make_device(
            "light",
            properties={"brightness": "50"},
            min_color_temp_kelvin=0,
            max_color_temp_kelvin=0,
        )
        mock_coordinator.get_device = MagicMock(return_value=device)
        light = LiproLight(mock_coordinator, device)

        assert light.supported_color_modes == {ColorMode.BRIGHTNESS}
        assert light.color_mode == ColorMode.BRIGHTNESS
        assert light.min_color_temp_kelvin == 0
        assert light.max_color_temp_kelvin == 0
        assert light.color_temp_kelvin is None

    def test_turn_on_on_adjust_option_parsing_int_and_string(
        self, mock_coordinator, make_device
    ):
        """turn_on_on_adjust option should parse int/string variants correctly."""
        from custom_components.lipro.const.config import (
            CONF_LIGHT_TURN_ON_ON_ADJUST,
            DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
        )
        from custom_components.lipro.light import LiproLight

        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        mock_coordinator.config_entry = MagicMock(options={})
        light = LiproLight(mock_coordinator, device)

        mock_coordinator.config_entry.options = {CONF_LIGHT_TURN_ON_ON_ADJUST: 0}
        assert light._turn_on_when_adjusting_while_off() is False

        mock_coordinator.config_entry.options = {CONF_LIGHT_TURN_ON_ON_ADJUST: 2}
        assert light._turn_on_when_adjusting_while_off() is True

        mock_coordinator.config_entry.options = {CONF_LIGHT_TURN_ON_ON_ADJUST: "off"}
        assert light._turn_on_when_adjusting_while_off() is False

        mock_coordinator.config_entry.options = {CONF_LIGHT_TURN_ON_ON_ADJUST: "yes"}
        assert light._turn_on_when_adjusting_while_off() is True

        mock_coordinator.config_entry.options = {
            CONF_LIGHT_TURN_ON_ON_ADJUST: "unexpected"
        }
        assert (
            light._turn_on_when_adjusting_while_off() is DEFAULT_LIGHT_TURN_ON_ON_ADJUST
        )
