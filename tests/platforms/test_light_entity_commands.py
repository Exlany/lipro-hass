"""Command-path light entity behavior assertions."""

from __future__ import annotations

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
