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
    MAX_BRIGHTNESS,
    MIN_BRIGHTNESS,
    PROP_BRIGHTNESS,
    PROP_POWER_STATE,
    PROP_TEMPERATURE,
)
from .core.utils.coerce import coerce_bool_option
from .entities.base import LiproEntity
from .entities.commands import PowerCommand
from .entities.descriptors import ConditionalAttr, DeviceAttr, ScaledBrightness
from .helpers.platform import (
    add_entry_entities,
    create_platform_entities,
    device_supports_platform,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.device import LiproDevice
    from .runtime_types import LiproRuntimeCoordinator

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

# Home Assistant uses 0-255 brightness scale
_HA_BRIGHTNESS_SCALE: Final = 255


def _light_is_on(entity: LiproEntity) -> object:
    """Read light power state from the formal device view."""
    return entity.device.state.is_on


def _light_brightness(entity: LiproEntity) -> object:
    """Read raw light brightness from the formal device view."""
    return entity.device.state.brightness


def _light_color_temp(entity: LiproEntity) -> object:
    """Read raw color temperature from the formal device view."""
    return entity.device.state.color_temp


def _supports_color_temp(entity: LiproEntity) -> object:
    """Return whether the current device supports color temperature."""
    return entity.capabilities.supports_color_temp


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro lights."""
    add_entry_entities(
        entry,
        async_add_entities,
        entity_builder=lambda coordinator: create_platform_entities(
            coordinator,
            device_filter=lambda d: device_supports_platform(d, "light"),
            entity_factory=LiproLight,
        ),
    )


class LiproLight(LiproEntity, LightEntity):
    """Representation of a Lipro light."""

    is_on = DeviceAttr[bool](_light_is_on)
    brightness = ScaledBrightness(_light_brightness)
    color_temp_kelvin = ConditionalAttr[int](
        _light_color_temp,
        capability=_supports_color_temp,
    )

    _power = PowerCommand()

    def __init__(
        self,
        coordinator: LiproRuntimeCoordinator,
        device: LiproDevice,
    ) -> None:
        """Initialize the light."""
        suffix = "light" if device.capabilities.is_fan_light else ""
        super().__init__(coordinator, device, suffix)

        if device.capabilities.is_fan_light:
            self._attr_translation_key = "light"
        else:
            self._attr_name = None

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        """Return supported color modes based on device capability."""
        if self.capabilities.supports_color_temp:
            return {ColorMode.COLOR_TEMP}
        return {ColorMode.BRIGHTNESS}

    @property
    def color_mode(self) -> ColorMode:
        """Return the current color mode."""
        if self.capabilities.supports_color_temp:
            return ColorMode.COLOR_TEMP
        return ColorMode.BRIGHTNESS

    @property
    def min_color_temp_kelvin(self) -> int:
        """Return the minimum color temperature in Kelvin."""
        return self.capabilities.min_color_temp_kelvin

    @property
    def max_color_temp_kelvin(self) -> int:
        """Return the maximum color temperature in Kelvin."""
        return self.capabilities.max_color_temp_kelvin

    def _ha_brightness_to_device(self, brightness: int) -> int:
        """Convert HA brightness (0-255) to clamped device value (1-100)."""
        value = round(brightness * 100 / _HA_BRIGHTNESS_SCALE)
        return max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, value))

    def _kelvin_to_device_temp_percent(self, kelvin: int) -> int:
        """Convert Kelvin to clamped device temperature percent."""
        clamped_kelvin = max(
            self.capabilities.min_color_temp_kelvin,
            min(self.capabilities.max_color_temp_kelvin, kelvin),
        )
        return self.device.state.kelvin_to_percent_for_device(clamped_kelvin)

    def _merge_slider_state(self, state_changes: dict[str, int]) -> dict[str, int]:
        """Merge brightness/temperature into one payload when both are known."""
        merged = dict(state_changes)
        has_brightness = PROP_BRIGHTNESS in merged
        has_temperature = PROP_TEMPERATURE in merged

        if (
            has_brightness
            and not has_temperature
            and self.capabilities.supports_color_temp
        ):
            temperature = self.device.state.get_optional_int_property(PROP_TEMPERATURE)
            if temperature is not None:
                merged[PROP_TEMPERATURE] = max(0, min(100, temperature))

        if has_temperature and not has_brightness:
            brightness = self.device.state.get_optional_int_property(PROP_BRIGHTNESS)
            if brightness is not None:
                merged[PROP_BRIGHTNESS] = max(
                    MIN_BRIGHTNESS,
                    min(MAX_BRIGHTNESS, brightness),
                )

        return merged

    def _turn_on_when_adjusting_while_off(self) -> bool:
        """Return whether slider adjust should power on when light is off."""
        config_entry = self.runtime_coordinator.config_entry
        options = config_entry.options if config_entry is not None else {}
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
        """Turn the light on."""
        state_changes: dict[str, int] = {}

        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            state_changes[PROP_BRIGHTNESS] = self._ha_brightness_to_device(brightness)
        if (kelvin := kwargs.get(ATTR_COLOR_TEMP_KELVIN)) is not None:
            state_changes[PROP_TEMPERATURE] = self._kelvin_to_device_temp_percent(kelvin)

        if not state_changes:
            await self._power.turn_on(self)
            return

        if not self.is_on and self._turn_on_when_adjusting_while_off():
            state_changes[PROP_POWER_STATE] = 1

        await self.async_change_state(
            self._merge_slider_state(state_changes),
            debounced=True,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        del kwargs
        await self._power.turn_off(self)

    async def async_set_brightness(self, brightness: int) -> None:
        """Set the light brightness."""
        state_changes = {PROP_BRIGHTNESS: self._ha_brightness_to_device(brightness)}
        if not self.is_on and self._turn_on_when_adjusting_while_off():
            state_changes[PROP_POWER_STATE] = 1
        await self.async_change_state(self._merge_slider_state(state_changes), debounced=True)

    async def async_set_color_temp_kelvin(self, color_temp_kelvin: int) -> None:
        """Set the light color temperature."""
        state_changes = {
            PROP_TEMPERATURE: self._kelvin_to_device_temp_percent(color_temp_kelvin)
        }
        if not self.is_on and self._turn_on_when_adjusting_while_off():
            state_changes[PROP_POWER_STATE] = 1
        await self.async_change_state(self._merge_slider_state(state_changes), debounced=True)
