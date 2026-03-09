"""Mutable device-state helpers extracted from ``LiproDevice``."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from ...const.properties import (
    DEFAULT_COLOR_TEMP_PERCENT,
    DIRECTION_CLOSING,
    DIRECTION_OPENING,
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BATTERY,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_CHARGING,
    PROP_CONNECT_STATE,
    PROP_DARK,
    PROP_DIRECTION,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_GEAR,
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
    PROP_POSITION,
    PROP_POWER_STATE,
    PROP_SLEEP_AID_ENABLE,
    PROP_TEMPERATURE,
    PROP_WAKE_UP_ENABLE,
    PROP_WIND_DIRECTION_MODE,
    PROP_WIND_GEAR,
    kelvin_to_percent,
    percent_to_kelvin,
)
from ..utils.coerce import coerce_boollike

_LOGGER = logging.getLogger(__name__)


class DeviceState:
    """State/attribute helper bound to one device property mapping."""

    def __init__(
        self,
        *,
        properties: Mapping[str, Any],
        min_color_temp_kelvin: int,
        max_color_temp_kelvin: int,
        max_fan_gear: int,
    ) -> None:
        """Store the runtime data required to resolve derived state."""
        self._properties = properties
        self._min_color_temp_kelvin = min_color_temp_kelvin
        self._max_color_temp_kelvin = max_color_temp_kelvin
        self._max_fan_gear = max_fan_gear

    def get_property(self, key: str, default: Any = None) -> Any:
        """Return one raw property value."""
        return self._properties.get(key, default)

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        """Convert one value to ``int`` when possible."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_float(value: Any) -> float | None:
        """Convert one value to ``float`` when possible."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def get_bool_property(self, key: str, default: bool = False) -> bool:
        """Return one boolean-like property value."""
        value = self._properties.get(key)
        if value is None:
            return default
        if isinstance(value, (bool, int, float, str)):
            return coerce_boollike(value, logger=_LOGGER, context="API")
        return bool(value)

    def get_int_property(self, key: str, default: int = 0) -> int:
        """Return one integer property value."""
        value = self._coerce_int(self._properties.get(key))
        return default if value is None else value

    def get_float_property(self, key: str, default: float = 0.0) -> float:
        """Return one float property value."""
        value = self._coerce_float(self._properties.get(key))
        return default if value is None else value

    def get_optional_int_property(self, key: str) -> int | None:
        """Return one optional integer property value."""
        return self._coerce_int(self._properties.get(key))

    def get_str_property(self, key: str) -> str | None:
        """Return one string property value when present."""
        value = self._properties.get(key)
        if value is None:
            return None
        return str(value)

    @property
    def supports_color_temp(self) -> bool:
        """Return whether color temperature adjustment is supported."""
        return self._max_color_temp_kelvin > 0 and self._min_color_temp_kelvin > 0

    @property
    def is_on(self) -> bool:
        """Return whether the device power state is on."""
        return self.get_bool_property(PROP_POWER_STATE)

    @property
    def is_connected(self) -> bool:
        """Return whether the device is connected."""
        return self.get_bool_property(PROP_CONNECT_STATE, True)

    @property
    def brightness(self) -> int:
        """Return brightness in the 0-100 API scale."""
        return self.get_int_property(PROP_BRIGHTNESS, 100)

    @property
    def color_temp(self) -> int:
        """Return color temperature in Kelvin."""
        percent = self.get_int_property(PROP_TEMPERATURE, DEFAULT_COLOR_TEMP_PERCENT)
        return self.percent_to_kelvin_for_device(percent)

    def percent_to_kelvin_for_device(self, percent: int) -> int:
        """Convert API percentage to Kelvin using device-specific bounds."""
        percent = max(0, min(100, percent))
        if self.supports_color_temp:
            temp_range = self._max_color_temp_kelvin - self._min_color_temp_kelvin
            if temp_range <= 0:
                return self._min_color_temp_kelvin
            return self._min_color_temp_kelvin + int(percent * temp_range / 100)
        return percent_to_kelvin(percent)

    def kelvin_to_percent_for_device(self, kelvin: int) -> int:
        """Convert Kelvin back to API percentage."""
        if self.supports_color_temp:
            min_temp = self._min_color_temp_kelvin
            max_temp = self._max_color_temp_kelvin
            temp_range = max_temp - min_temp
            if temp_range <= 0:
                return 50
            kelvin = max(min_temp, min(max_temp, kelvin))
            return max(0, min(100, round((kelvin - min_temp) * 100 / temp_range)))
        return kelvin_to_percent(kelvin)

    @property
    def fade_state(self) -> bool:
        """Return current fade/transition flag."""
        return self.get_bool_property(PROP_FADE_STATE)

    @property
    def sleep_aid_enabled(self) -> bool:
        """Return whether sleep-aid mode is enabled."""
        return self.get_bool_property(PROP_SLEEP_AID_ENABLE)

    @property
    def wake_up_enabled(self) -> bool:
        """Return whether wake-up mode is enabled."""
        return self.get_bool_property(PROP_WAKE_UP_ENABLE)

    @property
    def focus_mode_enabled(self) -> bool:
        """Return whether focus mode is enabled."""
        return self.get_bool_property(PROP_FOCUS_MODE)

    @property
    def body_reactive_enabled(self) -> bool:
        """Return whether body reactive mode is enabled."""
        return self.get_bool_property(PROP_BODY_REACTIVE)

    @property
    def panel_led_enabled(self) -> bool:
        """Return whether panel LED is enabled."""
        return self.get_bool_property(PROP_LED)

    @property
    def panel_memory_enabled(self) -> bool:
        """Return whether panel memory is enabled."""
        return self.get_bool_property(PROP_MEMORY)

    @property
    def panel_pair_key_full(self) -> bool:
        """Return whether panel bind slots are full."""
        return self.get_bool_property(PROP_PAIR_KEY_FULL)

    @property
    def ir_switch_enabled(self) -> bool:
        """Return current IR switch state."""
        return self.get_bool_property(PROP_IR_SWITCH)

    @property
    def battery_level(self) -> int | None:
        """Return battery level or ``None`` when absent."""
        if PROP_BATTERY not in self._properties:
            return None
        return self.get_int_property(PROP_BATTERY, 0)

    @property
    def is_charging(self) -> bool:
        """Return whether the device is charging."""
        return self.get_bool_property(PROP_CHARGING)

    @property
    def has_battery(self) -> bool:
        """Return whether battery telemetry exists."""
        return PROP_BATTERY in self._properties

    @property
    def position(self) -> int:
        """Return curtain position in the 0-100 range."""
        position = self.get_int_property(PROP_POSITION, 0)
        return max(0, min(100, position))

    @property
    def is_moving(self) -> bool:
        """Return whether the curtain is currently moving."""
        return self.get_bool_property(PROP_MOVING)

    @property
    def direction(self) -> str | None:
        """Return curtain direction in HA-friendly strings."""
        direction = self.get_property(PROP_DIRECTION)
        if direction == DIRECTION_OPENING:
            return "opening"
        if direction == DIRECTION_CLOSING:
            return "closing"
        return None

    @property
    def fan_is_on(self) -> bool:
        """Return whether the fan output is enabled."""
        return self.get_bool_property(PROP_FAN_ONOFF)

    @property
    def fan_gear(self) -> int:
        """Return fan gear clamped to the device range."""
        gear = self.get_int_property(PROP_FAN_GEAR, 1)
        return max(1, min(self._max_fan_gear, gear))

    @property
    def fan_mode(self) -> int:
        """Return the current fan mode."""
        return self.get_int_property(PROP_FAN_MODE, 0)

    @property
    def heater_is_on(self) -> bool:
        """Return whether heater output is enabled."""
        return self.get_bool_property(PROP_HEATER_SWITCH)

    @property
    def heater_mode(self) -> int:
        """Return heater mode."""
        return self.get_int_property(PROP_HEATER_MODE, 0)

    @property
    def wind_gear(self) -> int:
        """Return heater wind gear."""
        return self.get_int_property(PROP_WIND_GEAR, 0)

    @property
    def light_mode(self) -> int:
        """Return heater light mode."""
        return self.get_int_property(PROP_LIGHT_MODE, 0)

    @property
    def wind_direction_mode(self) -> int:
        """Return heater wind direction mode."""
        return self.get_int_property(PROP_WIND_DIRECTION_MODE, 1)

    @property
    def aeration_gear(self) -> int:
        """Return aeration gear."""
        return self.get_int_property(PROP_AERATION_GEAR, 0)

    @property
    def aeration_is_on(self) -> bool:
        """Return whether aeration is enabled."""
        return self.aeration_gear > 0

    @property
    def door_is_open(self) -> bool:
        """Return whether a door sensor reports open state."""
        return self.get_bool_property(PROP_DOOR_OPEN)

    @property
    def is_activated(self) -> bool:
        """Return whether a body sensor reports activation."""
        return self.get_bool_property(PROP_ACTIVATED)

    @property
    def is_dark(self) -> bool:
        """Return whether ambient darkness is reported."""
        return self.get_bool_property(PROP_DARK)

    @property
    def low_battery(self) -> bool:
        """Return whether low-battery state is reported."""
        return self.get_bool_property(PROP_LOW_BATTERY)


__all__ = ["DeviceState"]
