"""Select platform for Lipro integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final, Protocol, cast

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
from .helpers.platform import (
    add_entry_entities,
    build_device_entities_from_rules,
    create_device_entities,
    should_expose_light_gear_select,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import (
        CoordinatorEntity,
        DataUpdateCoordinator,
    )

    from . import LiproConfigEntry
    from .core.capability import CapabilitySnapshot
    from .core.device import LiproDevice
    from .runtime_types import LiproRuntimeCoordinator

    class _LiproEntityBase(CoordinatorEntity[DataUpdateCoordinator[dict[str, object]]]):
        def __init__(
            self,
            coordinator: LiproRuntimeCoordinator,
            device: LiproDevice,
            entity_suffix: str = "",
        ) -> None: ...

        @property
        def device(self) -> LiproDevice: ...

        @property
        def capabilities(self) -> CapabilitySnapshot: ...

        async def async_change_state(
            self,
            properties: Mapping[str, object],
            *,
            optimistic_state: Mapping[str, object] | None = None,
            debounced: bool = False,
        ) -> bool | None: ...

else:
    class _EntityBaseModule(Protocol):
        LiproEntity: type[object]

    _entity_base_module = cast(
        _EntityBaseModule,
        __import__(
            "custom_components.lipro.entities.base",
            fromlist=["LiproEntity"],
        ),
    )
    _LiproEntityBase = _entity_base_module.LiproEntity

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

# Wind direction mode options
WIND_DIRECTION_OPTIONS: Final = ["auto", "fixed"]
WIND_DIRECTION_TO_VALUE: Final = {
    "auto": WIND_DIRECTION_AUTO,
    "fixed": WIND_DIRECTION_FIX,
}
VALUE_TO_WIND_DIRECTION: Final = {v: k for k, v in WIND_DIRECTION_TO_VALUE.items()}

# Light mode options for heater
LIGHT_MODE_OPTIONS: Final = ["off", "main", "night"]
LIGHT_MODE_TO_VALUE: Final = {
    "off": HEATER_LIGHT_OFF,
    "main": HEATER_LIGHT_MAIN,
    "night": HEATER_LIGHT_NIGHT,
}
VALUE_TO_LIGHT_MODE: Final = {v: k for k, v in LIGHT_MODE_TO_VALUE.items()}

# Light gear preset options (max 3)
_MAX_GEAR_COUNT: Final = 3
GEAR_OPTIONS: Final = ["gear_1", "gear_2", "gear_3"]

# Descriptive names for gear presets (used in extra_state_attributes)
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


class LiproSelect(_LiproEntityBase, SelectEntity):
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
        if raw_value is None:
            return None
        if isinstance(raw_value, bool):
            return int(raw_value)
        if isinstance(raw_value, int):
            return raw_value
        if isinstance(raw_value, float):
            return int(raw_value) if raw_value.is_integer() else None
        if isinstance(raw_value, str):
            normalized = raw_value.strip()
            if not normalized:
                return None
            try:
                return int(normalized)
            except ValueError:
                return None
        return None

    def _get_raw_property_value(self) -> object:
        """Return the raw normalized property value for this select."""
        return self.device.properties.get(self._property_key)

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
        raw_value = self._get_raw_property_value()
        if raw_value is None:
            self._last_unknown_value = None
            return None

        value = self._coerce_mapped_value(raw_value)
        if value is None:
            self._log_unknown_mapped_value(raw_value)
            return None

        option = self._value_to_option.get(value)
        if option is None:
            self._log_unknown_mapped_value(raw_value)
            return None

        self._last_unknown_value = None
        return option

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose raw enum state when the device reports an unknown value."""
        raw_value = self._get_raw_property_value()
        if raw_value is None:
            return {}

        value = self._coerce_mapped_value(raw_value)
        if value is not None and value in self._value_to_option:
            return {}

        return {
            "property_key": self._property_key,
            "raw_value": raw_value,
        }

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
    """Select entity for light gear presets.

    Allows quick switching between predefined brightness/color temperature combinations.
    The gear presets are stored on the device and synced via gearList property.

    Note: The API does not return lastGearIndex, so we use exact matching of
    brightness and temperature percentage values to determine the current gear.
    """

    _attr_translation_key = "light_gear"
    _entity_suffix = "gear"

    @staticmethod
    def _coerce_gear_int(value: object) -> int | None:
        """Convert one gear field value to int safely."""
        if value is None:
            return None
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value) if value.is_integer() else None
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return None
            try:
                return int(normalized)
            except ValueError:
                return None
        return None

    @classmethod
    def _extract_gear_values(cls, gear: object) -> tuple[int, int] | None:
        """Extract (brightness, temperature_percent) from one gear payload."""
        if not isinstance(gear, dict):
            return None

        brightness = cls._coerce_gear_int(gear.get("brightness"))
        temp_pct = cls._coerce_gear_int(gear.get("temperature"))
        if brightness is None or temp_pct is None:
            return None
        return brightness, temp_pct

    @property
    def options(self) -> list[str]:
        """Return gear options based on actual device gear count."""
        count = len(self.device.extras.gear_list)
        if not count:
            return []
        if count < len(GEAR_OPTIONS):
            return GEAR_OPTIONS[:count]
        return GEAR_OPTIONS

    @property
    def current_option(self) -> str | None:
        """Return the current gear based on exact brightness and temperature match.

        Uses exact matching of brightness and temperature percentage values.
        Returns None if current values don't match any preset (custom state).
        """
        gear_list = self.device.extras.gear_list
        if not gear_list:
            return None

        current_brightness = self.device.state.brightness
        current_temp_pct = self.device.state.get_int_property(PROP_TEMPERATURE, -1)

        for i, gear in enumerate(gear_list[:_MAX_GEAR_COUNT]):
            values = self._extract_gear_values(gear)
            if values is None:
                continue
            gear_brightness, gear_temp_pct = values

            if (
                current_brightness == gear_brightness
                and current_temp_pct == gear_temp_pct
            ):
                return GEAR_OPTIONS[i]

        return None

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return extra state attributes showing gear details."""
        attrs: dict[str, object] = {}
        gear_list = self.device.extras.gear_list

        for i, gear in enumerate(gear_list[:_MAX_GEAR_COUNT]):
            values = self._extract_gear_values(gear)
            if values is None:
                continue
            brightness, temp_pct = values
            temp_k = self.device.state.percent_to_kelvin_for_device(temp_pct)
            attrs[f"preset_{_GEAR_PRESET_NAMES[i]}"] = f"{brightness}% / {temp_k}K"

        if self.capabilities.supports_color_temp:
            min_k = self.capabilities.min_color_temp_kelvin
            max_k = self.capabilities.max_color_temp_kelvin
            attrs["color_temp_range"] = f"{min_k}K - {max_k}K"

        return attrs

    async def async_select_option(self, option: str) -> None:
        """Apply the selected gear preset."""
        gear_list = self.device.extras.gear_list
        if not gear_list:
            _LOGGER.warning("No gear presets available for %s", self.device.name)
            return

        try:
            gear_index = GEAR_OPTIONS.index(option)
        except ValueError:
            _LOGGER.warning("Invalid gear option: %s", option)
            return

        if gear_index >= len(gear_list):
            _LOGGER.warning("Gear index %d out of range", gear_index)
            return

        gear = gear_list[gear_index]
        values = self._extract_gear_values(gear)
        if values is None:
            _LOGGER.warning(
                "Invalid gear preset at index %d for %s: %r",
                gear_index,
                self.device.name,
                gear,
            )
            return

        brightness, temp_pct = values

        _LOGGER.debug(
            "Applying gear %d to %s: brightness=%d%%, temperature=%d%%(%dK)",
            gear_index + 1,
            self.device.name,
            brightness,
            temp_pct,
            self.device.state.percent_to_kelvin_for_device(temp_pct),
        )

        success = await self.async_change_state(
            {
                PROP_BRIGHTNESS: brightness,
                PROP_TEMPERATURE: temp_pct,
            }
        )
        if success:
            await self.coordinator.async_request_refresh()
