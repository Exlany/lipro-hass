"""Light platform for Lipro integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)

from .const import (
    CMD_CHANGE_STATE,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    MAX_BRIGHTNESS,
    MIN_BRIGHTNESS,
    PROP_BRIGHTNESS,
    PROP_POWER_STATE,
    PROP_TEMPERATURE,
)
from .entities.base import LiproEntity
from .helpers import create_platform_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.coordinator import LiproDataUpdateCoordinator
    from .core.device import LiproDevice

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro lights."""
    entities = create_platform_entities(
        entry.runtime_data,
        device_filter=lambda d: d.is_light or d.is_fan_light,
        entity_factory=LiproLight,
    )
    async_add_entities(entities)


class LiproLight(LiproEntity, LightEntity):
    """Representation of a Lipro light."""

    def __init__(
        self,
        coordinator: LiproDataUpdateCoordinator,
        device: LiproDevice,
    ) -> None:
        """Initialize the light."""
        # Use suffix for fan lights to distinguish from fan entity
        suffix = "light" if device.is_fan_light else ""
        super().__init__(coordinator, device, suffix)

        if device.is_fan_light:
            self._attr_translation_key = "light"
        else:
            self._attr_name = None  # Use device name

        # Set color mode based on device capability
        if device.supports_color_temp:
            self._attr_supported_color_modes = {ColorMode.COLOR_TEMP}
            self._attr_color_mode = ColorMode.COLOR_TEMP
            # Use device-specific color temp range
            self._attr_min_color_temp_kelvin = device.min_color_temp_kelvin
            self._attr_max_color_temp_kelvin = device.max_color_temp_kelvin
        else:
            # Single color temperature - brightness only mode
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
            self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.device.is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light (0-255)."""
        # Convert from 0-100 to 0-255
        brightness_pct = self.device.brightness
        return round(brightness_pct * 255 / 100)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature in Kelvin."""
        if not self.device.supports_color_temp:
            return None
        return self.device.color_temp

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        properties: list[dict[str, str]] = []
        optimistic: dict[str, Any] = {PROP_POWER_STATE: "1"}
        use_debounce = False

        # Handle brightness
        if ATTR_BRIGHTNESS in kwargs:
            # Convert from 0-255 to 1-100
            brightness = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
            brightness = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, brightness))
            properties.append({"key": PROP_BRIGHTNESS, "value": str(brightness)})
            optimistic[PROP_BRIGHTNESS] = str(brightness)
            use_debounce = True

        # Handle color temperature (only if device supports it)
        if ATTR_COLOR_TEMP_KELVIN in kwargs and self.device.supports_color_temp:
            color_temp = int(kwargs[ATTR_COLOR_TEMP_KELVIN])
            # Clamp to device-specific range
            color_temp = max(
                self.device.min_color_temp_kelvin,
                min(self.device.max_color_temp_kelvin, color_temp),
            )
            # Convert to percentage using device-specific range
            min_temp = self.device.min_color_temp_kelvin
            max_temp = self.device.max_color_temp_kelvin
            temp_range = max_temp - min_temp
            if temp_range > 0:
                temp_percent = round((color_temp - min_temp) * 100 / temp_range)
                # Clamp to valid percentage range
                temp_percent = max(0, min(100, temp_percent))
            else:
                temp_percent = 50  # Default to middle if range is 0 or negative
            properties.append({"key": PROP_TEMPERATURE, "value": str(temp_percent)})
            optimistic[PROP_TEMPERATURE] = str(temp_percent)
            use_debounce = True

        # Use debounce for slider controls (brightness, color_temp)
        # to avoid flooding API when user drags the slider
        if properties and use_debounce:
            await self.async_send_command_debounced(
                CMD_CHANGE_STATE,
                properties,
                optimistic,
            )
        elif properties:
            await self.async_send_command(CMD_CHANGE_STATE, properties, optimistic)
        else:
            # Just turn on (no debounce needed for simple on/off)
            await self.async_send_command(CMD_POWER_ON, None, optimistic)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.async_send_command(CMD_POWER_OFF, None, {PROP_POWER_STATE: "0"})
