"""Select platform for Lipro integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from homeassistant.components.select import SelectEntity

from .const.properties import (
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
from .helpers.platform import (
    add_entry_entities,
    build_device_entities_from_rules,
    create_device_entities,
    should_expose_light_gear_select,
)
from .select_internal.gear import (
    GearPreset,
    available_gear_options,
    build_gear_attributes,
    coerce_int_like,
    extract_gear_preset,
    iter_valid_gear_presets,
    resolve_current_gear_option,
    resolve_gear_option_index,
)
from .select_internal.mapped_property import (
    MappedPropertySnapshot,
    build_mapped_property_snapshot,
    coerce_mapped_value,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.device import LiproDevice
    from .runtime_types import LiproRuntimeCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

WIND_DIRECTION_OPTIONS: Final = ["auto", "fixed"]
WIND_DIRECTION_TO_VALUE: Final = {
    "auto": WIND_DIRECTION_AUTO,
    "fixed": WIND_DIRECTION_FIX,
}
VALUE_TO_WIND_DIRECTION: Final = {v: k for k, v in WIND_DIRECTION_TO_VALUE.items()}

LIGHT_MODE_OPTIONS: Final = ["off", "main", "night"]
LIGHT_MODE_TO_VALUE: Final = {
    "off": HEATER_LIGHT_OFF,
    "main": HEATER_LIGHT_MAIN,
    "night": HEATER_LIGHT_NIGHT,
}
VALUE_TO_LIGHT_MODE: Final = {v: k for k, v in LIGHT_MODE_TO_VALUE.items()}

_MAX_GEAR_COUNT: Final = 3
GEAR_OPTIONS: Final = ["gear_1", "gear_2", "gear_3"]
_GEAR_PRESET_NAMES: Final[tuple[str, ...]] = ("warm", "neutral", "cool")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro select entities."""
    add_entry_entities(
        entry,
        async_add_entities,
        entity_builder=lambda coordinator: create_device_entities(
            coordinator,
            _build_device_select_entities,
        ),
    )


def _build_device_select_entities(
    coordinator: LiproRuntimeCoordinator,
    device: LiproDevice,
) -> list[SelectEntity]:
    """Build all select entities for one device."""
    return build_device_entities_from_rules(
        coordinator,
        device,
        rules=(
            (
                lambda d: d.capabilities.is_heater,
                (LiproHeaterWindDirectionSelect, LiproHeaterLightModeSelect),
            ),
            (should_expose_light_gear_select, (LiproLightGearSelect,)),
        ),
    )


class LiproSelect(LiproEntity, SelectEntity):
    """Base class for Lipro select entities."""


class LiproMappedPropertySelect(LiproSelect):
    """Base select for option<->value mapped device properties."""

    _option_to_value: dict[str, int]
    _value_to_option: dict[int, str]
    _property_key: str
    _last_unknown_value: object | None = None

    @staticmethod
    def _coerce_mapped_value(raw_value: object) -> int | None:
        """Convert one raw property value into an integer enum value."""
        return coerce_mapped_value(raw_value)

    def _get_raw_property_value(self) -> object:
        """Return the raw normalized property value for this select."""
        return self.device.properties.get(self._property_key)

    def _mapped_snapshot(self) -> MappedPropertySnapshot:
        """Return the normalized mapped-property snapshot for this select."""
        return build_mapped_property_snapshot(
            self.device.properties,
            property_key=self._property_key,
            value_to_option=self._value_to_option,
        )

    def _log_unknown_mapped_value(self, raw_value: object) -> None:
        """Log one unknown enum value once per distinct raw value."""
        if raw_value == self._last_unknown_value:
            return
        self._last_unknown_value = raw_value
        _LOGGER.warning(
            "Unknown %s value %r for %s",
            self._property_key,
            raw_value,
            self.device.name,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current option from the raw property mapping."""
        snapshot = self._mapped_snapshot()
        if snapshot.raw_value is None:
            self._last_unknown_value = None
            return None

        if snapshot.option is None:
            self._log_unknown_mapped_value(snapshot.raw_value)
            return None

        self._last_unknown_value = None
        return snapshot.option

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose raw enum state when the device reports an unknown value."""
        return self._mapped_snapshot().build_unknown_attributes(
            property_key=self._property_key,
        )

    async def async_select_option(self, option: str) -> None:
        """Set the option by mapped property value."""
        value = self._option_to_value.get(option)
        if value is None:
            _LOGGER.warning(
                "Ignoring unsupported %s option %r for %s",
                self._property_key,
                option,
                self.device.name,
            )
            return
        await self.async_change_state({self._property_key: value})


class LiproHeaterWindDirectionSelect(LiproMappedPropertySelect):
    """Select entity for heater wind direction mode."""

    _attr_options = WIND_DIRECTION_OPTIONS
    _attr_translation_key = "wind_direction"
    _entity_suffix = "wind_direction"
    _option_to_value = WIND_DIRECTION_TO_VALUE
    _value_to_option = VALUE_TO_WIND_DIRECTION
    _property_key = PROP_WIND_DIRECTION_MODE


class LiproHeaterLightModeSelect(LiproMappedPropertySelect):
    """Select entity for heater light mode."""

    _attr_options = LIGHT_MODE_OPTIONS
    _attr_translation_key = "heater_light"
    _entity_suffix = "light_mode"
    _option_to_value = LIGHT_MODE_TO_VALUE
    _value_to_option = VALUE_TO_LIGHT_MODE
    _property_key = PROP_LIGHT_MODE


class LiproLightGearSelect(LiproSelect):
    """Select entity for light gear presets."""

    _attr_translation_key = "light_gear"
    _entity_suffix = "gear"

    @staticmethod
    def _coerce_int_like(value: object) -> int | None:
        """Convert one int-like gear field value safely."""
        return coerce_int_like(value)

    @classmethod
    def _extract_gear_values(cls, gear: object) -> tuple[int, int] | None:
        """Extract (brightness, temperature_percent) from one gear payload."""
        preset = extract_gear_preset(0, gear)
        if preset is None:
            return None
        return preset.brightness, preset.temperature_percent

    def _iter_valid_gear_presets(self) -> list[GearPreset]:
        """Return valid gear presets while preserving the original gear index."""
        return iter_valid_gear_presets(
            self.device.extras.gear_list,
            max_count=_MAX_GEAR_COUNT,
        )

    def _resolve_current_gear_option(self) -> str | None:
        """Resolve the current option by exact brightness/temperature match."""
        return resolve_current_gear_option(
            self.device.extras.gear_list,
            current_brightness=self.device.state.brightness,
            current_temperature_percent=self.device.state.get_int_property(
                PROP_TEMPERATURE,
                -1,
            ),
            max_count=_MAX_GEAR_COUNT,
            options=GEAR_OPTIONS,
        )

    def _build_gear_attributes(self) -> dict[str, object]:
        """Build extra-state attributes describing available gear presets."""
        color_temp_range: tuple[int, int] | None = None
        if self.capabilities.supports_color_temp:
            color_temp_range = (
                self.capabilities.min_color_temp_kelvin,
                self.capabilities.max_color_temp_kelvin,
            )
        return build_gear_attributes(
            self.device.extras.gear_list,
            max_count=_MAX_GEAR_COUNT,
            preset_names=_GEAR_PRESET_NAMES,
            percent_to_kelvin=self.device.state.percent_to_kelvin_for_device,
            color_temp_range=color_temp_range,
        )

    def _resolve_selected_gear(self, option: str) -> GearPreset | None:
        """Resolve one selected option into the raw preset payload and values."""
        gear_index = resolve_gear_option_index(option, option_names=GEAR_OPTIONS)
        if gear_index is None:
            _LOGGER.warning("Invalid gear option: %s", option)
            return None

        gear_list = self.device.extras.gear_list
        if gear_index >= len(gear_list):
            _LOGGER.warning("Gear index %d out of range", gear_index)
            return None

        preset = extract_gear_preset(gear_index, gear_list[gear_index])
        if preset is None:
            _LOGGER.warning(
                "Invalid gear preset at index %d for %s: %r",
                gear_index,
                self.device.name,
                gear_list[gear_index],
            )
            return None
        return preset

    @property
    def options(self) -> list[str]:
        """Return gear options based on actual device gear count."""
        return available_gear_options(
            len(self.device.extras.gear_list),
            max_count=_MAX_GEAR_COUNT,
            option_names=GEAR_OPTIONS,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current gear based on exact brightness and temperature match."""
        if not self.device.extras.gear_list:
            return None
        return self._resolve_current_gear_option()

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes showing gear details."""
        return self._build_gear_attributes()

    async def async_select_option(self, option: str) -> None:
        """Apply the selected gear preset."""
        if not self.device.extras.gear_list:
            _LOGGER.warning("No gear presets available for %s", self.device.name)
            return

        preset = self._resolve_selected_gear(option)
        if preset is None:
            return

        _LOGGER.debug(
            "Applying gear %d to %s: brightness=%d%%, temperature=%d%%(%dK)",
            preset.gear_index + 1,
            self.device.name,
            preset.brightness,
            preset.temperature_percent,
            self.device.state.percent_to_kelvin_for_device(
                preset.temperature_percent,
            ),
        )

        success = await self.async_change_state(
            {
                PROP_BRIGHTNESS: preset.brightness,
                PROP_TEMPERATURE: preset.temperature_percent,
            }
        )
        if success:
            await self.coordinator.async_request_refresh()
