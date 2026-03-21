"""Tests for Lipro light platform."""

from __future__ import annotations

from collections.abc import Iterable
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestLiproLightEntityCommands:
    """Tests for LiproLight entity command methods."""

    @pytest.mark.asyncio
    async def test_turn_on(self, mock_coordinator, make_device):
        """Test async_turn_on sends POWER_ON command."""
        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)

        with patch.object(light, "async_write_ha_state"):
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

        with patch.object(light, "async_write_ha_state"):
            await light.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_OFF", None
        )

    @pytest.mark.asyncio
    async def test_turn_on_with_brightness(self, mock_coordinator, make_device):
        """Brightness turn_on should send CHANGE_STATE and ensure power on."""
        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        # HA brightness 128 -> Lipro brightness 50 (128*100/255 = 50)
        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(brightness=128)

        mock_send_command_debounced.assert_called_once()
        mock_coordinator.async_send_command.assert_not_called()
        call_args = mock_send_command_debounced.call_args
        assert call_args[0][0] == "CHANGE_STATE"
        # Properties should include brightness with converted value
        # HA 128 -> int(128*100/255) = 50
        props = call_args[0][1]
        power_prop = next(p for p in props if p["key"] == "powerState")
        assert power_prop["value"] == "1"
        brightness_prop = next(p for p in props if p["key"] == "brightness")
        assert brightness_prop["value"] == "50"

    @pytest.mark.asyncio
    async def test_turn_on_with_color_temp(self, mock_coordinator, make_device):
        """Test async_turn_on with color_temp sends debounced CHANGE_STATE."""
        device = make_device(
            "light", properties={"powerState": "1", "temperature": "50"}
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(color_temp_kelvin=4000)

        mock_send_command_debounced.assert_called_once()
        call_args = mock_send_command_debounced.call_args
        assert call_args[0][0] == "CHANGE_STATE"
        props = call_args[0][1]
        temp_prop = next(p for p in props if p["key"] == "temperature")
        # 4000K -> percent depends on device range, verify it's a valid string
        assert temp_prop["value"].isdigit()
        mock_coordinator.async_send_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_turn_on_with_color_temp_off_state_sets_power(
        self, mock_coordinator, make_device
    ):
        """Color temp turn_on should also include powerState when currently off."""
        device = make_device(
            "light", properties={"powerState": "0", "temperature": "50"}
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(color_temp_kelvin=4000)

        call_args = mock_send_command_debounced.call_args
        props = {p["key"]: p["value"] for p in call_args[0][1]}
        assert props["powerState"] == "1"
        assert props["temperature"].isdigit()

    @pytest.mark.asyncio
    async def test_fan_light_turn_on_with_brightness_off_state_sets_power(
        self, mock_coordinator, make_device
    ):
        """Fan light should also follow HA turn_on semantics by default."""
        device = make_device("fanLight", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(brightness=128)

        call_args = mock_send_command_debounced.call_args
        props = {p["key"]: p["value"] for p in call_args[0][1]}
        assert props["powerState"] == "1"
        assert props["brightness"] == "50"

    @pytest.mark.asyncio
    async def test_turn_on_with_brightness_off_state_can_skip_power_on_by_option(
        self, mock_coordinator, make_device
    ):
        """Option can keep native behavior: adjust brightness without turning on."""
        from custom_components.lipro.const.config import CONF_LIGHT_TURN_ON_ON_ADJUST
        from custom_components.lipro.light import LiproLight

        device = make_device(
            "light", properties={"powerState": "0", "temperature": "50"}
        )
        mock_coordinator.get_device = MagicMock(return_value=device)
        mock_coordinator.config_entry = MagicMock(
            options={CONF_LIGHT_TURN_ON_ON_ADJUST: False}
        )

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(brightness=128)

        call_args = mock_send_command_debounced.call_args
        props = {p["key"]: p["value"] for p in call_args[0][1]}
        assert "powerState" not in props
        assert props["brightness"] == "50"

    @pytest.mark.asyncio
    async def test_turn_on_with_color_temp_off_state_can_skip_power_on_by_option(
        self, mock_coordinator, make_device
    ):
        """Option can keep native behavior: adjust color temp without turning on."""
        from custom_components.lipro.const.config import CONF_LIGHT_TURN_ON_ON_ADJUST
        from custom_components.lipro.light import LiproLight

        device = make_device(
            "fanLight", properties={"powerState": "0", "brightness": "60"}
        )
        mock_coordinator.get_device = MagicMock(return_value=device)
        mock_coordinator.config_entry = MagicMock(
            options={CONF_LIGHT_TURN_ON_ON_ADJUST: False}
        )

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(color_temp_kelvin=4200)

        call_args = mock_send_command_debounced.call_args
        props = {p["key"]: p["value"] for p in call_args[0][1]}
        assert "powerState" not in props
        assert props["brightness"] == "60"
        assert props["temperature"].isdigit()

    @pytest.mark.asyncio
    async def test_turn_on_with_brightness_merges_existing_temperature(
        self, mock_coordinator, make_device
    ):
        """Brightness updates should carry current temperature when available."""
        device = make_device(
            "light",
            properties={"powerState": "1", "brightness": "40", "temperature": "55"},
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(brightness=128)

        call_args = mock_send_command_debounced.call_args
        props = {p["key"]: p["value"] for p in call_args[0][1]}
        assert props["brightness"] == "50"
        assert props["temperature"] == "55"

    @pytest.mark.asyncio
    async def test_turn_on_with_color_temp_merges_existing_brightness(
        self, mock_coordinator, make_device
    ):
        """Color temperature updates should carry current brightness when available."""
        device = make_device(
            "light",
            properties={"powerState": "1", "brightness": "73", "temperature": "20"},
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        mock_send_command_debounced = AsyncMock()

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(
                light,
                "async_send_command_debounced",
                new=mock_send_command_debounced,
            ),
        ):
            await light.async_turn_on(color_temp_kelvin=4000)

        call_args = mock_send_command_debounced.call_args
        props = {p["key"]: p["value"] for p in call_args[0][1]}
        assert props["brightness"] == "73"
        assert props["temperature"].isdigit()

    @pytest.mark.asyncio
    async def test_rapid_cross_slider_updates_keep_paired_payload(
        self, mock_coordinator, make_device
    ):
        """Rapid brightness->temperature updates should keep both properties."""
        device = make_device(
            "light",
            properties={"powerState": "1", "brightness": "20", "temperature": "10"},
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        captured: list[tuple[str, list[dict[str, str]], dict[str, str]]] = []

        async def _capture(
            command: str,
            properties: list[dict[str, str]],
            optimistic_state: dict[str, str],
        ) -> None:
            captured.append((command, properties, optimistic_state))
            device.update_properties(optimistic_state)

        with (
            patch.object(light, "async_write_ha_state"),
            patch.object(light, "async_send_command_debounced", new=_capture),
        ):
            await light.async_turn_on(brightness=200)
            await light.async_turn_on(color_temp_kelvin=5000)

        assert len(captured) == 2
        _, properties, _ = captured[-1]
        prop_map = {item["key"]: item["value"] for item in properties}
        assert prop_map["brightness"] == "78"
        assert prop_map["temperature"] == "61"


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

    def test_brightness_clamped_above_100(self, mock_coordinator, make_device):
        """Brightness above 100% should be clamped to 255 in HA scale."""
        device = make_device("light", properties={"brightness": "150"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.brightness == 255

    def test_brightness_clamped_below_0(self, mock_coordinator, make_device):
        """Brightness below 0% should be clamped to 0 in HA scale."""
        device = make_device("light", properties={"brightness": "-10"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.brightness == 0

    def test_is_on_property(self, mock_coordinator, make_device):
        """Test is_on reflects device power state."""
        device = make_device("light", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.is_on is True

    def test_extra_state_attributes_off_state_no_tip_color_temp(
        self, mock_coordinator, make_device
    ):
        """No extra attributes are exposed for plain lights in off-state."""
        device = make_device("light", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.extra_state_attributes is None

    def test_extra_state_attributes_off_state_no_tip_brightness_only(
        self, mock_coordinator, make_device
    ):
        """Brightness-only lights should also rely on the base None behavior."""
        device = make_device(
            "light",
            properties={"powerState": "0"},
            min_color_temp_kelvin=0,
            max_color_temp_kelvin=0,
        )
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.extra_state_attributes is None

    def test_extra_state_attributes_on_state_no_tip(
        self, mock_coordinator, make_device
    ):
        """On-state plain lights still expose no extra attributes."""
        device = make_device("light", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.extra_state_attributes is None

    def test_supported_color_modes_with_color_temp(self, mock_coordinator, make_device):
        """Test supported_color_modes includes COLOR_TEMP when device supports it."""
        from homeassistant.components.light.const import ColorMode

        device = make_device("light", properties={"temperature": "50"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert ColorMode.COLOR_TEMP in light.supported_color_modes

    def test_color_mode_property(self, mock_coordinator, make_device):
        """Test color_mode returns correct mode based on device capability."""
        from homeassistant.components.light.const import ColorMode

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
        unique_id = light.unique_id
        assert unique_id is not None
        assert unique_id.endswith("_light")

    def test_regular_light_no_suffix(self, mock_coordinator, make_device):
        """Test regular light entity has no suffix in unique_id."""
        device = make_device("light")
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.light import LiproLight

        light = LiproLight(mock_coordinator, device)
        assert light.unique_id == device.unique_id


class TestLiproLightAdditionalCoverage:
    """Additional branch tests for light platform behavior."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_adds_only_light_entities(self, hass, make_device):
        """Setup should create entities only for light and fan-light devices."""
        from custom_components.lipro.light import LiproLight, async_setup_entry

        coordinator = SimpleNamespace(
            devices={
                "light_1": make_device("light"),
                "fan_light": make_device("fanLight"),
                "switch_1": make_device("switch"),
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
