"""Tests for AnonymousShareManager."""

from __future__ import annotations

from custom_components.lipro.const.properties import (
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BATTERY,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_DARK,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_GEAR,
    PROP_FAN_MODE,
    PROP_FOCUS_MODE,
    PROP_HEATER_MODE,
    PROP_LIGHT_MODE,
    PROP_POSITION,
    PROP_SLEEP_AID_ENABLE,
    PROP_TEMPERATURE,
    PROP_WAKE_UP_ENABLE,
    PROP_WIND_GEAR,
)
from custom_components.lipro.core.anonymous_share.capabilities import (
    detect_device_capabilities,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
from .support import _make_mock_device


class TestCapabilities:
    """Tests for capability detection matrix."""

    def test_detect_capabilities_light_order_stable(self):
        """Light capability output order should remain stable."""
        device = _make_mock_device(
            properties={
                PROP_BRIGHTNESS: 1,
                PROP_TEMPERATURE: 5000,
                PROP_FADE_STATE: 1,
                PROP_FOCUS_MODE: 1,
                PROP_SLEEP_AID_ENABLE: 1,
                PROP_WAKE_UP_ENABLE: 1,
            },
            is_light=True,
            has_gear_presets=True,
        )

        assert detect_device_capabilities(device) == [
            "light",
            "brightness",
            "color_temp",
            "gear_presets",
            "fade",
            "focus_mode",
            "sleep_aid",
            "wake_up",
        ]

    def test_detect_capabilities_full_matrix(self):
        device = _make_mock_device(
            properties={
                PROP_BRIGHTNESS: 1,
                PROP_TEMPERATURE: 5000,
                PROP_FADE_STATE: 1,
                PROP_FOCUS_MODE: 1,
                PROP_SLEEP_AID_ENABLE: 1,
                PROP_WAKE_UP_ENABLE: 1,
                PROP_FAN_GEAR: 1,
                PROP_FAN_MODE: 1,
                PROP_POSITION: 1,
                PROP_BATTERY: 99,
                PROP_DOOR_OPEN: 1,
                PROP_BODY_REACTIVE: 1,
                PROP_ACTIVATED: 1,
                PROP_DARK: 1,
                PROP_HEATER_MODE: 1,
                PROP_WIND_GEAR: 1,
                PROP_AERATION_GEAR: 1,
                PROP_LIGHT_MODE: 1,
            },
            is_light=True,
            is_fan_light=True,
            is_curtain=True,
            is_sensor=True,
            is_heater=True,
            is_switch=True,
            is_outlet=True,
            has_gear_presets=True,
        )
        caps = detect_device_capabilities(device)
        expected = {
            "light",
            "brightness",
            "color_temp",
            "gear_presets",
            "fade",
            "focus_mode",
            "sleep_aid",
            "wake_up",
            "fan",
            "fan_speed",
            "fan_mode",
            "cover",
            "position",
            "sensor",
            "battery",
            "door_sensor",
            "motion_sensor",
            "light_sensor",
            "heater",
            "heater_mode",
            "wind_speed",
            "aeration",
            "heater_light",
            "switch",
        }
        assert expected.issubset(set(caps))
