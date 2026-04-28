"""Behavior tests for Lipro switch platform entities."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestLiproSwitchEntityCommands:
    """Tests for LiproSwitch entity command methods."""

    def test_is_on_reflects_device_state(self, mock_coordinator, make_device):
        """Entity is_on should proxy device.is_on."""
        device = make_device("switch", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.switch import LiproSwitch

        switch = LiproSwitch(mock_coordinator, device)
        assert switch.is_on is True

        device.update_properties({"powerState": "0"})
        assert switch.is_on is False

    @pytest.mark.asyncio
    async def test_turn_on(self, mock_coordinator, make_device):
        """Test async_turn_on sends POWER_ON command."""
        device = make_device("switch", properties={"powerState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.switch import LiproSwitch

        switch = LiproSwitch(mock_coordinator, device)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_ON", None
        )

    @pytest.mark.asyncio
    async def test_turn_off(self, mock_coordinator, make_device):
        """Test async_turn_off sends POWER_OFF command."""
        device = make_device("switch", properties={"powerState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)

        from custom_components.lipro.switch import LiproSwitch

        switch = LiproSwitch(mock_coordinator, device)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once_with(
            device, "POWER_OFF", None
        )

    @pytest.mark.asyncio
    async def test_outlet_device_class(self, mock_coordinator, make_device):
        """Test outlet gets SwitchDeviceClass.OUTLET."""
        from custom_components.lipro.switch import LiproSwitch
        from homeassistant.components.switch import SwitchDeviceClass

        device = make_device("outlet")
        mock_coordinator.get_device = MagicMock(return_value=device)
        switch = LiproSwitch(mock_coordinator, device)

        assert switch.device_class == SwitchDeviceClass.OUTLET

    @pytest.mark.asyncio
    async def test_switch_device_class(self, mock_coordinator, make_device):
        """Test switch gets SwitchDeviceClass.SWITCH."""
        from custom_components.lipro.switch import LiproSwitch
        from homeassistant.components.switch import SwitchDeviceClass

        device = make_device("switch")
        mock_coordinator.get_device = MagicMock(return_value=device)
        switch = LiproSwitch(mock_coordinator, device)

        assert switch.device_class == SwitchDeviceClass.SWITCH


class TestLiproFeatureSwitchEntityCommands:
    """Tests for feature switch entity command methods (fade, sleep_aid, etc.)."""

    @pytest.mark.asyncio
    async def test_fade_switch_turn_on(self, mock_coordinator, make_device):
        """Test LiproPropertySwitch (fade) turn_on sends CHANGE_STATE with fadeState=1."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"fadeState": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fade_config = next(
            c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "fade"
        )
        switch = LiproPropertySwitch(mock_coordinator, device, fade_config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "fadeState", "value": "1"}],
        )

    @pytest.mark.asyncio
    async def test_fade_switch_turn_off(self, mock_coordinator, make_device):
        """Test LiproPropertySwitch (fade) turn_off sends CHANGE_STATE with fadeState=0."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"fadeState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fade_config = next(
            c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "fade"
        )
        switch = LiproPropertySwitch(mock_coordinator, device, fade_config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "fadeState", "value": "0"}],
        )

    @pytest.mark.asyncio
    async def test_sleep_aid_switch_turn_on(self, mock_coordinator, make_device):
        """Test LiproPropertySwitch (sleep_aid) turn_on sends sleepAidEnable=1."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"sleepAidEnable": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        config = next(
            c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "sleep_aid"
        )
        switch = LiproPropertySwitch(mock_coordinator, device, config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "sleepAidEnable", "value": "1"}],
        )

    @pytest.mark.asyncio
    async def test_wake_up_switch_turn_on(self, mock_coordinator, make_device):
        """Test LiproPropertySwitch (wake_up) turn_on sends wakeUpEnable=1."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"wakeUpEnable": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "wake_up")
        switch = LiproPropertySwitch(mock_coordinator, device, config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "wakeUpEnable", "value": "1"}],
        )

    @pytest.mark.asyncio
    async def test_focus_mode_switch_turn_on(self, mock_coordinator, make_device):
        """Test LiproPropertySwitch (focus_mode) turn_on sends focusMode=1."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"focusMode": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        config = next(
            c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "focus_mode"
        )
        switch = LiproPropertySwitch(mock_coordinator, device, config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "focusMode", "value": "1"}],
        )

    @pytest.mark.asyncio
    async def test_body_reactive_switch_turn_on(self, mock_coordinator, make_device):
        """Test LiproPropertySwitch (body_reactive) turn_on sends bodyReactive=1."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"bodyReactive": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        config = next(
            c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "body_reactive"
        )
        switch = LiproPropertySwitch(mock_coordinator, device, config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "CHANGE_STATE",
            [{"key": "bodyReactive", "value": "1"}],
        )

    def test_feature_switch_is_on_reads_device_property(
        self, mock_coordinator, make_device
    ):
        """Test feature switch is_on reads from device property."""
        from custom_components.lipro.switch import (
            LIGHT_FEATURE_SWITCHES,
            LiproPropertySwitch,
        )

        device = make_device("light", properties={"fadeState": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        fade_config = next(
            c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "fade"
        )
        switch = LiproPropertySwitch(mock_coordinator, device, fade_config)

        assert switch.is_on is True

        device.update_properties({"fadeState": "0"})
        assert switch.is_on is False


class TestLiproPanelFeatureSwitch:
    """Tests for switch-panel feature switches."""

    def test_panel_led_enabled(self, make_device):
        """Test panel LED state is read from device properties."""
        device = make_device("switch", properties={"led": "1"})
        assert device.panel_led_enabled is True

    def test_panel_memory_enabled(self, make_device):
        """Test panel memory state is read from device properties."""
        device = make_device("switch", properties={"memory": "0"})
        assert device.panel_memory_enabled is False

    def test_panel_type_uses_switch_l_discriminator(self, make_device):
        """Test panel type flag follows the APK's SWITCH_L rule."""
        assert make_device("switch", iot_name="21JD").panel_type == 1
        assert make_device("switch", iot_name="21J8").panel_type == 0

    @pytest.mark.asyncio
    async def test_panel_led_switch_turn_on(self, mock_coordinator, make_device):
        """Test panel LED switch uses PANEL_CHANGE_STATE with panelType."""
        from custom_components.lipro.switch import (
            PANEL_FEATURE_SWITCHES,
            LiproPanelPropertySwitch,
        )

        device = make_device("switch", iot_name="21JD", properties={"led": "0"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        config = next(
            c for c in PANEL_FEATURE_SWITCHES if c.entity_suffix == "panel_led"
        )
        switch = LiproPanelPropertySwitch(mock_coordinator, device, config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "PANEL_CHANGE_STATE",
            [
                {"key": "led", "value": "1"},
                {"key": "panelType", "value": "1"},
            ],
        )

    @pytest.mark.asyncio
    async def test_panel_memory_switch_turn_off(self, mock_coordinator, make_device):
        """Test panel memory switch uses PANEL_CHANGE_STATE with panelType."""
        from custom_components.lipro.switch import (
            PANEL_FEATURE_SWITCHES,
            LiproPanelPropertySwitch,
        )

        device = make_device("switch", iot_name="21J8", properties={"memory": "1"})
        mock_coordinator.get_device = MagicMock(return_value=device)
        config = next(
            c for c in PANEL_FEATURE_SWITCHES if c.entity_suffix == "panel_memory"
        )
        switch = LiproPanelPropertySwitch(mock_coordinator, device, config)

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_off()

        mock_coordinator.async_send_command.assert_called_once_with(
            device,
            "PANEL_CHANGE_STATE",
            [
                {"key": "memory", "value": "0"},
                {"key": "panelType", "value": "0"},
            ],
        )
