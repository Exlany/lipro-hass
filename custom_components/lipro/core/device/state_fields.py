"""Shared field maps for ``DeviceState`` accessors."""

from __future__ import annotations

from ...const.properties import (
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_CHARGING,
    PROP_DARK,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_MODE,
    PROP_FAN_ONOFF,
    PROP_FOCUS_MODE,
    PROP_HEATER_MODE,
    PROP_HEATER_SWITCH,
    PROP_IR_SWITCH,
    PROP_LED,
    PROP_LIGHT_MODE,
    PROP_LOW_BATTERY,
    PROP_MEMORY,
    PROP_MOVING,
    PROP_PAIR_KEY_FULL,
    PROP_POWER_STATE,
    PROP_SLEEP_AID_ENABLE,
    PROP_WAKE_UP_ENABLE,
    PROP_WIND_DIRECTION_MODE,
    PROP_WIND_GEAR,
)

BOOL_PROPERTY_MAP: dict[str, str] = {
    "is_on": PROP_POWER_STATE,
    "fade_state": PROP_FADE_STATE,
    "sleep_aid_enabled": PROP_SLEEP_AID_ENABLE,
    "wake_up_enabled": PROP_WAKE_UP_ENABLE,
    "focus_mode_enabled": PROP_FOCUS_MODE,
    "body_reactive_enabled": PROP_BODY_REACTIVE,
    "panel_led_enabled": PROP_LED,
    "panel_memory_enabled": PROP_MEMORY,
    "panel_pair_key_full": PROP_PAIR_KEY_FULL,
    "ir_switch_enabled": PROP_IR_SWITCH,
    "is_charging": PROP_CHARGING,
    "is_moving": PROP_MOVING,
    "fan_is_on": PROP_FAN_ONOFF,
    "heater_is_on": PROP_HEATER_SWITCH,
    "door_is_open": PROP_DOOR_OPEN,
    "is_activated": PROP_ACTIVATED,
    "is_dark": PROP_DARK,
    "low_battery": PROP_LOW_BATTERY,
}
INT_PROPERTY_MAP: dict[str, tuple[str, int]] = {
    "brightness": (PROP_BRIGHTNESS, 100),
    "fan_mode": (PROP_FAN_MODE, 0),
    "heater_mode": (PROP_HEATER_MODE, 0),
    "wind_gear": (PROP_WIND_GEAR, 0),
    "light_mode": (PROP_LIGHT_MODE, 0),
    "wind_direction_mode": (PROP_WIND_DIRECTION_MODE, 1),
    "aeration_gear": (PROP_AERATION_GEAR, 0),
}
DEVICE_STATE_EXPORTED_ATTRIBUTES: tuple[str, ...] = (
    *tuple(BOOL_PROPERTY_MAP),
    *tuple(INT_PROPERTY_MAP),
    "supports_color_temp",
    "is_connected",
    "color_temp",
    "battery_level",
    "has_battery",
    "position",
    "direction",
    "fan_gear",
    "aeration_is_on",
)

__all__ = [
    "BOOL_PROPERTY_MAP",
    "DEVICE_STATE_EXPORTED_ATTRIBUTES",
    "INT_PROPERTY_MAP",
]
