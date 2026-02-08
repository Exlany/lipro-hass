"""Select platform for Lipro integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .const import (
    CMD_CHANGE_STATE,
    HEATER_LIGHT_MAIN,
    HEATER_LIGHT_NIGHT,
    HEATER_LIGHT_OFF,
    PROP_BRIGHTNESS,
    PROP_LIGHT_MODE,
    PROP_TEMPERATURE,
    PROP_WIND_DIRECTION_MODE,
    WIND_DIRECTION_AUTO,
    WIND_DIRECTION_FIX,
    percent_to_kelvin,
)
from .entities.base import LiproEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

# Wind direction mode options
WIND_DIRECTION_OPTIONS = ["auto", "fixed"]
WIND_DIRECTION_TO_VALUE = {
    "auto": WIND_DIRECTION_AUTO,
    "fixed": WIND_DIRECTION_FIX,
}
VALUE_TO_WIND_DIRECTION = {v: k for k, v in WIND_DIRECTION_TO_VALUE.items()}

# Light mode options for heater
LIGHT_MODE_OPTIONS = ["off", "main", "night"]
LIGHT_MODE_TO_VALUE = {
    "off": HEATER_LIGHT_OFF,
    "main": HEATER_LIGHT_MAIN,
    "night": HEATER_LIGHT_NIGHT,
}
VALUE_TO_LIGHT_MODE = {v: k for k, v in LIGHT_MODE_TO_VALUE.items()}

# Light gear preset options
GEAR_OPTIONS = ["gear_1", "gear_2", "gear_3"]

# Tolerance for gear matching
GEAR_MATCH_BRIGHTNESS_TOLERANCE = 5  # 5% brightness tolerance
GEAR_MATCH_TEMP_TOLERANCE = 190  # ~190K temperature tolerance (~5% of 3800K range)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro select entities."""
    coordinator = entry.runtime_data
    entities: list[SelectEntity] = []

    for device in coordinator.devices.values():
        # Add select entities for heaters
        if device.is_heater:
            entities.append(LiproHeaterWindDirectionSelect(coordinator, device))
            entities.append(LiproHeaterLightModeSelect(coordinator, device))

        # Add gear preset select for lights with gear presets
        if device.is_light and device.has_gear_presets:
            entities.append(LiproLightGearSelect(coordinator, device))

    async_add_entities(entities)


class LiproSelect(LiproEntity, SelectEntity):
    """Base class for Lipro select entities."""


class LiproHeaterWindDirectionSelect(LiproSelect):
    """Select entity for heater wind direction mode."""

    _attr_options = WIND_DIRECTION_OPTIONS
    _attr_translation_key = "wind_direction"
    _entity_suffix = "wind_direction"

    @property
    def current_option(self) -> str | None:
        """Return the current wind direction mode."""
        mode = self.device.wind_direction_mode
        return VALUE_TO_WIND_DIRECTION.get(mode, "auto")

    @property
    def icon(self) -> str:
        """Return the icon based on wind direction."""
        if self.current_option == "auto":
            return "mdi:rotate-3d-variant"
        return "mdi:arrow-down"

    async def async_select_option(self, option: str) -> None:
        """Set the wind direction mode."""
        value = WIND_DIRECTION_TO_VALUE.get(option, WIND_DIRECTION_AUTO)
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_WIND_DIRECTION_MODE, "value": str(value)}],
            {PROP_WIND_DIRECTION_MODE: str(value)},
        )


class LiproHeaterLightModeSelect(LiproSelect):
    """Select entity for heater light mode."""

    _attr_options = LIGHT_MODE_OPTIONS
    _attr_translation_key = "heater_light"
    _entity_suffix = "light_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current light mode."""
        mode = self.device.light_mode
        return VALUE_TO_LIGHT_MODE.get(mode, "off")

    @property
    def icon(self) -> str:
        """Return the icon based on light mode."""
        mode = self.current_option
        if mode == "main":
            return "mdi:lightbulb"
        if mode == "night":
            return "mdi:lightbulb-night"
        return "mdi:lightbulb-off"

    async def async_select_option(self, option: str) -> None:
        """Set the light mode."""
        value = LIGHT_MODE_TO_VALUE.get(option, HEATER_LIGHT_OFF)
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_LIGHT_MODE, "value": str(value)}],
            {PROP_LIGHT_MODE: str(value)},
        )


class LiproLightGearSelect(LiproSelect):
    """Select entity for light gear presets.

    Allows quick switching between predefined brightness/color temperature combinations.
    The gear presets are stored on the device and synced via gearList property.
    """

    _attr_options = GEAR_OPTIONS
    _attr_translation_key = "light_gear"
    _entity_suffix = "gear"

    @property
    def current_option(self) -> str | None:
        """Return the current gear based on brightness and temperature match."""
        gear_list = self.device.gear_list
        if not gear_list:
            return None

        # Try to match current brightness/temperature to a gear
        current_brightness = self.device.brightness
        current_temp = self.device.color_temp  # Kelvin

        # Find matching gear (with some tolerance)
        for i, gear in enumerate(gear_list[:3]):  # Max 3 gears
            if not isinstance(gear, dict):
                continue
            gear_brightness = gear.get("brightness", 0)
            gear_temp_pct = gear.get("temperature", 0)
            gear_temp_k = self._percent_to_kelvin(gear_temp_pct)

            # Allow tolerance for brightness and temperature matching
            brightness_diff = abs(current_brightness - gear_brightness)
            temp_diff = abs(current_temp - gear_temp_k)
            if (
                brightness_diff <= GEAR_MATCH_BRIGHTNESS_TOLERANCE
                and temp_diff <= GEAR_MATCH_TEMP_TOLERANCE
            ):
                return GEAR_OPTIONS[i]

        # Check lastGearIndex as fallback
        last_index = self.device.last_gear_index
        if 0 <= last_index < len(GEAR_OPTIONS):
            return GEAR_OPTIONS[last_index]

        return None

    def _percent_to_kelvin(self, percent: int) -> int:
        """Convert percentage to Kelvin using device-specific range."""
        # Clamp percent to valid range
        percent = max(0, min(100, percent))
        if self.device.supports_color_temp:
            min_temp = self.device.min_color_temp_kelvin
            max_temp = self.device.max_color_temp_kelvin
            temp_range = max_temp - min_temp
            # Ensure temp_range is non-negative
            if temp_range <= 0:
                return min_temp
            return min_temp + int(percent * temp_range / 100)
        return percent_to_kelvin(percent)

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:tune-variant"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return extra state attributes showing gear details."""
        attrs: dict[str, str] = {}
        gear_list = self.device.gear_list
        for i, gear in enumerate(gear_list[:3]):
            if not isinstance(gear, dict):
                continue
            brightness = gear.get("brightness", 0)
            temp_pct = gear.get("temperature", 0)
            temp_k = self._percent_to_kelvin(temp_pct)
            attrs[f"gear_{i + 1}"] = f"{brightness}%, {temp_k}K"
        return attrs

    async def async_select_option(self, option: str) -> None:
        """Apply the selected gear preset."""
        gear_list = self.device.gear_list
        if not gear_list:
            _LOGGER.warning("No gear presets available for %s", self.device.name)
            return

        # Get gear index from option
        try:
            gear_index = GEAR_OPTIONS.index(option)
        except ValueError:
            _LOGGER.warning("Invalid gear option: %s", option)
            return

        if gear_index >= len(gear_list):
            _LOGGER.warning("Gear index %d out of range", gear_index)
            return

        gear = gear_list[gear_index]
        brightness = gear.get("brightness", 100)
        temp_pct = gear.get("temperature", 50)

        _LOGGER.debug(
            "Applying gear %d to %s: brightness=%d%%, temperature=%d%%(%dK)",
            gear_index + 1,
            self.device.name,
            brightness,
            temp_pct,
            percent_to_kelvin(temp_pct),
        )

        # Send brightness and temperature (percentage) together
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [
                {"key": PROP_BRIGHTNESS, "value": str(brightness)},
                {"key": PROP_TEMPERATURE, "value": str(temp_pct)},
            ],
            {
                PROP_BRIGHTNESS: str(brightness),
                PROP_TEMPERATURE: str(temp_pct),
            },
        )
