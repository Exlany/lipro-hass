"""Light platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    LightEntity,
)
from homeassistant.components.light.const import ColorMode

from .const.config import CONF_LIGHT_TURN_ON_ON_ADJUST, DEFAULT_LIGHT_TURN_ON_ON_ADJUST
from .const.properties import (
    CMD_POWER_OFF,
    CMD_POWER_ON,
    MAX_BRIGHTNESS,
    MIN_BRIGHTNESS,
    PROP_BRIGHTNESS,
    PROP_POWER_STATE,
    PROP_TEMPERATURE,
)
from .core.utils.coerce import coerce_bool_option
from .entities.base import LiproEntity
from .helpers.platform import create_platform_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.coordinator import LiproDataUpdateCoordinator
    from .core.device import LiproDevice

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

# Home Assistant uses 0-255 brightness scale
_HA_BRIGHTNESS_SCALE: Final = 255


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

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Return supported color modes based on device capability.

        Dynamic property so it reflects product config changes after init.
        """
        if self.device.supports_color_temp:
            return {ColorMode.COLOR_TEMP}
        return {ColorMode.BRIGHTNESS}

    @property
    def color_mode(self) -> ColorMode:
        """Return the current color mode.

        Dynamic property matching supported_color_modes.
        """
        if self.device.supports_color_temp:
            return ColorMode.COLOR_TEMP
        return ColorMode.BRIGHTNESS

    @property
    def min_color_temp_kelvin(self) -> int:
        """Return the minimum color temperature in Kelvin.

        Uses device-specific range from product config.
        """
        return self.device.min_color_temp_kelvin

    @property
    def max_color_temp_kelvin(self) -> int:
        """Return the maximum color temperature in Kelvin.

        Uses device-specific range from product config.
        """
        return self.device.max_color_temp_kelvin

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self.device.is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light (0-255)."""
        # Convert from 0-100 to 0-255
        brightness_pct = max(0, min(100, self.device.brightness))
        return round(brightness_pct * _HA_BRIGHTNESS_SCALE / 100)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature in Kelvin."""
        if not self.device.supports_color_temp:
            return None
        return self.device.color_temp

    def _ha_brightness_to_device(self, brightness: int) -> int:
        """Convert HA brightness (0-255) to clamped device value (1-100)."""
        value = round(brightness * 100 / _HA_BRIGHTNESS_SCALE)
        return max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, value))

    def _kelvin_to_device_temp_percent(self, kelvin: int) -> int:
        """Convert Kelvin to clamped device temperature percent."""
        clamped_kelvin = max(
            self.device.min_color_temp_kelvin,
            min(self.device.max_color_temp_kelvin, kelvin),
        )
        return self.device.kelvin_to_percent_for_device(clamped_kelvin)

    def _merge_slider_state(self, state_changes: dict[str, int]) -> dict[str, int]:
        """Merge brightness/temperature into one payload when both are known.

        Keeps brightness + color temperature paired for debounced light updates,
        so rapid cross-slider operations do not drop the previous value.
        """
        merged = dict(state_changes)
        has_brightness = PROP_BRIGHTNESS in merged
        has_temperature = PROP_TEMPERATURE in merged

        if has_brightness and not has_temperature and self.device.supports_color_temp:
            temperature = self.device.get_optional_int_property(PROP_TEMPERATURE)
            if temperature is not None:
                merged[PROP_TEMPERATURE] = max(0, min(100, temperature))

        if has_temperature and not has_brightness:
            brightness = self.device.get_optional_int_property(PROP_BRIGHTNESS)
            if brightness is not None:
                merged[PROP_BRIGHTNESS] = max(
                    MIN_BRIGHTNESS,
                    min(MAX_BRIGHTNESS, brightness),
                )

        return merged

    def _turn_on_when_adjusting_while_off(self) -> bool:
        """Return whether slider adjust should power on when light is off."""
        config_entry = getattr(self.coordinator, "config_entry", None)
        options = getattr(config_entry, "options", {})
        raw_value = options.get(
            CONF_LIGHT_TURN_ON_ON_ADJUST,
            DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
        )
        return coerce_bool_option(
            raw_value,
            option_name=CONF_LIGHT_TURN_ON_ON_ADJUST,
            default=DEFAULT_LIGHT_TURN_ON_ON_ADJUST,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        state_changes: dict[str, int] = {}

        # Handle brightness
        if ATTR_BRIGHTNESS in kwargs:
            brightness = self._ha_brightness_to_device(kwargs[ATTR_BRIGHTNESS])
            state_changes[PROP_BRIGHTNESS] = brightness

        # Handle color temperature (only if device supports it)
        if ATTR_COLOR_TEMP_KELVIN in kwargs and self.device.supports_color_temp:
            temp_percent = self._kelvin_to_device_temp_percent(
                int(kwargs[ATTR_COLOR_TEMP_KELVIN])
            )
            state_changes[PROP_TEMPERATURE] = temp_percent

        # Use debounce for slider controls (brightness, color_temp)
        # to avoid flooding API when user drags the slider.
        if state_changes:
            state_changes = self._merge_slider_state(state_changes)
            if not self.is_on and self._turn_on_when_adjusting_while_off():
                state_changes[PROP_POWER_STATE] = 1
            await self.async_change_state(state_changes, debounced=True)
        else:
            # Just turn on (no debounce needed for simple on/off)
            await self.async_send_command(CMD_POWER_ON, None, {PROP_POWER_STATE: "1"})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.async_send_command(CMD_POWER_OFF, None, {PROP_POWER_STATE: "0"})
