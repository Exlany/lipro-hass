"""Tests for Lipro switch platform."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestLiproSwitch:
    """Tests for LiproSwitch entity."""

    def test_switch_is_on(self, make_device):
        """Test switch is_on property."""
        device = make_device("switch", properties={"powerState": "1"})
        assert device.is_on is True

        device = make_device("switch", properties={"powerState": "0"})
        assert device.is_on is False

    def test_switch_is_switch(self, make_device):
        """Test device is identified as switch."""
        device = make_device("switch")
        assert device.is_switch is True
        assert device.is_light is False

    def test_outlet_is_switch(self, make_device):
        """Test outlet is also identified as switch."""
        device = make_device("outlet")
        assert device.is_switch is True


class TestLiproSwitchCommands:
    """Tests for switch command constants."""

    def test_command_constants(self):
        """Test command constants are defined."""
        from custom_components.lipro.const.properties import (
            CMD_POWER_OFF,
            CMD_POWER_ON,
            PROP_POWER_STATE,
        )

        assert CMD_POWER_ON == "POWER_ON"
        assert CMD_POWER_OFF == "POWER_OFF"
        assert PROP_POWER_STATE == "powerState"


class TestLiproFadeSwitch:
    """Tests for LiproFadeSwitch entity."""

    def test_fade_state_on(self, make_device):
        """Test fade state is on."""
        device = make_device("light", properties={"fadeState": "1"})
        assert device.fade_state is True

    def test_fade_state_off(self, make_device):
        """Test fade state is off."""
        device = make_device("light", properties={"fadeState": "0"})
        assert device.fade_state is False

    def test_fade_state_default(self, make_device):
        """Test fade state default is off."""
        device = make_device("light")
        assert device.fade_state is False


class TestLiproSleepAidSwitch:
    """Tests for LiproSleepAidSwitch entity (Natural Light)."""

    def test_sleep_aid_enabled(self, make_device):
        """Test sleep aid is enabled."""
        device = make_device(
            "light", iot_name="lipro_natural_light", properties={"sleepAidEnable": "1"}
        )
        assert device.sleep_aid_enabled is True

    def test_sleep_aid_disabled(self, make_device):
        """Test sleep aid is disabled."""
        device = make_device(
            "light", iot_name="lipro_natural_light", properties={"sleepAidEnable": "0"}
        )
        assert device.sleep_aid_enabled is False

    def test_has_sleep_wake_features(self, make_device):
        """Test has_sleep_wake_features detection."""
        # Has sleep aid
        device = make_device("light", properties={"sleepAidEnable": "0"})
        assert device.has_sleep_wake_features is True

        # Has wake up
        device = make_device("light", properties={"wakeUpEnable": "0"})
        assert device.has_sleep_wake_features is True

        # Has neither
        device = make_device("light")
        assert device.has_sleep_wake_features is False


class TestLiproWakeUpSwitch:
    """Tests for LiproWakeUpSwitch entity (Natural Light)."""

    def test_wake_up_enabled(self, make_device):
        """Test wake up is enabled."""
        device = make_device(
            "light", iot_name="lipro_natural_light", properties={"wakeUpEnable": "1"}
        )
        assert device.wake_up_enabled is True

    def test_wake_up_disabled(self, make_device):
        """Test wake up is disabled."""
        device = make_device(
            "light", iot_name="lipro_natural_light", properties={"wakeUpEnable": "0"}
        )
        assert device.wake_up_enabled is False


class TestLiproFocusModeSwitch:
    """Tests for LiproFocusModeSwitch entity (Floor Lamp)."""

    def test_focus_mode_enabled(self, make_device):
        """Test focus mode is enabled."""
        device = make_device(
            "light", iot_name="lipro_floor_lamp", properties={"focusMode": "1"}
        )
        assert device.focus_mode_enabled is True

    def test_focus_mode_disabled(self, make_device):
        """Test focus mode is disabled."""
        device = make_device(
            "light", iot_name="lipro_floor_lamp", properties={"focusMode": "0"}
        )
        assert device.focus_mode_enabled is False

    def test_has_floor_lamp_features(self, make_device):
        """Test has_floor_lamp_features detection."""
        # Has focus mode
        device = make_device("light", properties={"focusMode": "0"})
        assert device.has_floor_lamp_features is True

        # Has body reactive
        device = make_device("light", properties={"bodyReactive": "0"})
        assert device.has_floor_lamp_features is True

        # Has neither
        device = make_device("light")
        assert device.has_floor_lamp_features is False


class TestLiproBodyReactiveSwitch:
    """Tests for LiproBodyReactiveSwitch entity (Floor Lamp)."""

    def test_body_reactive_enabled(self, make_device):
        """Test body reactive is enabled."""
        device = make_device(
            "light", iot_name="lipro_floor_lamp", properties={"bodyReactive": "1"}
        )
        assert device.body_reactive_enabled is True

    def test_body_reactive_disabled(self, make_device):
        """Test body reactive is disabled."""
        device = make_device(
            "light", iot_name="lipro_floor_lamp", properties={"bodyReactive": "0"}
        )
        assert device.body_reactive_enabled is False


class TestSwitchDeviceTypes:
    """Tests for switch device type constants."""

    def test_device_type_outlet(self):
        """Test outlet device type constant."""
        from custom_components.lipro.const.device_types import DEVICE_TYPE_OUTLET

        assert DEVICE_TYPE_OUTLET == "ff000006"

    def test_outlet_device_type_hex(self, make_device):
        """Test outlet device returns correct type hex."""
        device = make_device("outlet")
        assert device.device_type_hex == "ff000006"


class TestSwitchPropertyConstants:
    """Tests for switch property constants."""

    def test_property_constants(self):
        """Test property constants are defined."""
        from custom_components.lipro.const.properties import (
            PROP_BODY_REACTIVE,
            PROP_FADE_STATE,
            PROP_FOCUS_MODE,
            PROP_SLEEP_AID_ENABLE,
            PROP_WAKE_UP_ENABLE,
        )

        assert PROP_FADE_STATE == "fadeState"
        assert PROP_SLEEP_AID_ENABLE == "sleepAidEnable"
        assert PROP_WAKE_UP_ENABLE == "wakeUpEnable"
        assert PROP_FOCUS_MODE == "focusMode"
        assert PROP_BODY_REACTIVE == "bodyReactive"


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
        fade_config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "fade")
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
        fade_config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "fade")
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
        config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "sleep_aid")
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
        config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "focus_mode")
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
        config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "body_reactive")
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
        fade_config = next(c for c in LIGHT_FEATURE_SWITCHES if c.entity_suffix == "fade")
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
        config = next(c for c in PANEL_FEATURE_SWITCHES if c.entity_suffix == "panel_led")
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
        config = next(c for c in PANEL_FEATURE_SWITCHES if c.entity_suffix == "panel_memory")
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
