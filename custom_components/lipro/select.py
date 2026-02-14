"""Select platform for Lipro integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

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

# Light gear preset options (max 3)
GEAR_OPTIONS = ["gear_1", "gear_2", "gear_3"]


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

    Note: The API does not return lastGearIndex, so we use exact matching of
    brightness and temperature percentage values to determine the current gear.
    """

    _attr_translation_key = "light_gear"
    _entity_suffix = "gear"

    @property
    def options(self) -> list[str]:
        """Return gear options based on actual device gear count."""
        count = len(self.device.gear_list)
        if 0 < count < len(GEAR_OPTIONS):
            return GEAR_OPTIONS[:count]
        return GEAR_OPTIONS

    @property
    def current_option(self) -> str | None:
        """Return the current gear based on exact brightness and temperature match.

        Uses exact matching of brightness and temperature percentage values.
        Returns None if current values don't match any preset (custom state).
        """
        gear_list = self.device.gear_list
        if not gear_list:
            return None

        # Get current values as percentages (same format as gearList)
        current_brightness = self.device.brightness
        current_temp_pct = self.device.get_int_property(PROP_TEMPERATURE, -1)

        # Exact match: brightness and temperature percentage must match exactly
        for i, gear in enumerate(gear_list[:3]):  # Max 3 gears
            if not isinstance(gear, dict):
                continue  # type: ignore[unreachable]
            gear_brightness = gear.get("brightness", 0)
            gear_temp_pct = gear.get("temperature", 0)

            # Exact match (no tolerance - API test confirmed this is correct)
            if (
                current_brightness == gear_brightness
                and current_temp_pct == gear_temp_pct
            ):
                return GEAR_OPTIONS[i]

        # No match - return None to indicate custom/unknown state
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes showing gear details.

        Shows brightness and color temperature (in Kelvin) for each preset.
        """
        attrs: dict[str, Any] = {}
        gear_list = self.device.gear_list

        for i, gear in enumerate(gear_list[:3]):
            if not isinstance(gear, dict):
                continue  # type: ignore[unreachable]
            brightness = gear.get("brightness", 0)
            temp_pct = gear.get("temperature", 0)

            # Convert percentage to Kelvin using centralized device method
            temp_k = self.device.percent_to_kelvin_for_device(temp_pct)

            # Use descriptive names matching the translations
            names = ["warm", "neutral", "cool"]
            attrs[f"preset_{names[i]}"] = f"{brightness}% / {temp_k}K"

        # Also show the device's color temp range
        if self.device.supports_color_temp:
            min_k = self.device.min_color_temp_kelvin
            max_k = self.device.max_color_temp_kelvin
            attrs["color_temp_range"] = f"{min_k}K - {max_k}K"

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
            self.device.percent_to_kelvin_for_device(temp_pct),
        )

        optimistic = {
            PROP_BRIGHTNESS: str(brightness),
            PROP_TEMPERATURE: str(temp_pct),
        }

        # Use async_send_command for consistent optimistic update + error recovery.
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [
                {"key": PROP_BRIGHTNESS, "value": str(brightness)},
                {"key": PROP_TEMPERATURE, "value": str(temp_pct)},
            ],
            optimistic,
        )

        # Notify other entities (e.g., light) sharing this device about the
        # brightness/temperature change applied by optimistic state above.
        self.coordinator.async_update_listeners()
