"""Fan platform for Lipro integration."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    AERATION_OFF,
    AERATION_STRONG,
    AERATION_WEAK,
    FAN_MODE_NATURAL,
    FAN_MODE_NORMAL,
    FAN_MODE_SLEEP,
    PROP_AERATION_GEAR,
    PROP_FAN_GEAR,
    PROP_FAN_MODE,
    PROP_FAN_ONOFF,
)
from .entities.base import LiproEntity
from .helpers import create_platform_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

# Preset modes for fan light
PRESET_MODE_NATURAL: Final = "natural"
PRESET_MODE_SLEEP: Final = "sleep"
PRESET_MODE_NORMAL: Final = "normal"

PRESET_MODES: Final = [PRESET_MODE_NATURAL, PRESET_MODE_SLEEP, PRESET_MODE_NORMAL]

MODE_TO_PRESET: Final = {
    FAN_MODE_NATURAL: PRESET_MODE_NATURAL,
    FAN_MODE_SLEEP: PRESET_MODE_SLEEP,
    FAN_MODE_NORMAL: PRESET_MODE_NORMAL,
}

PRESET_TO_MODE: Final = {v: k for k, v in MODE_TO_PRESET.items()}

# Preset modes for heater ventilation fan
PRESET_VENT_OFF: Final = "off"
PRESET_VENT_STRONG: Final = "strong"
PRESET_VENT_WEAK: Final = "weak"

VENT_PRESET_MODES: Final = [PRESET_VENT_STRONG, PRESET_VENT_WEAK]

AERATION_TO_PRESET: Final = {
    AERATION_OFF: PRESET_VENT_OFF,
    AERATION_STRONG: PRESET_VENT_STRONG,
    AERATION_WEAK: PRESET_VENT_WEAK,
}

PRESET_TO_AERATION: Final = {v: k for k, v in AERATION_TO_PRESET.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro fans."""
    coordinator = entry.runtime_data
    entities: list[FanEntity] = []

    # Add fan entities for fan lights
    entities.extend(
        create_platform_entities(
            coordinator,
            device_filter=lambda d: d.is_fan_light,
            entity_factory=LiproFan,
        )
    )

    # Add ventilation fan entities for heaters (bathroom heaters)
    entities.extend(
        create_platform_entities(
            coordinator,
            device_filter=lambda d: d.is_heater,
            entity_factory=LiproHeaterVentFan,
        )
    )

    async_add_entities(entities)


class LiproFan(LiproEntity, FanEntity):
    """Representation of a Lipro fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_preset_modes = PRESET_MODES
    _attr_translation_key = "fan"
    _entity_suffix = "fan"

    def _percentage_to_gear(self, percentage: int) -> int:
        """Convert percentage to gear value, clamped to device range."""
        speed_range = self.device.fan_speed_range
        gear = math.ceil(percentage_to_ranged_value(speed_range, percentage))
        return max(speed_range[0], min(speed_range[1], gear))

    def _add_power_on_if_needed(
        self,
        properties: dict[str, int],
        optimistic: dict[str, int | str],
        *,
        optimistic_power: bool,
    ) -> None:
        """Ensure fan turns on when updating mode/speed while currently off."""
        if self.is_on:
            return
        properties[PROP_FAN_ONOFF] = 1
        if optimistic_power:
            optimistic[PROP_FAN_ONOFF] = "1"
        else:
            # Keep UI responsive for slider, but avoid debounce protection on power key.
            self.device.update_properties({PROP_FAN_ONOFF: "1"})

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return self.device.max_fan_gear

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.device.fan_is_on

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if not self.is_on:
            return 0
        return ranged_value_to_percentage(
            self.device.fan_speed_range, self.device.fan_gear
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        mode = self.device.fan_mode
        return MODE_TO_PRESET.get(mode, PRESET_MODE_NORMAL)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        properties: dict[str, int] = {PROP_FAN_ONOFF: 1}

        if percentage is not None:
            gear = self._percentage_to_gear(percentage)
            properties[PROP_FAN_GEAR] = gear

        if preset_mode is not None:
            mode = PRESET_TO_MODE.get(preset_mode, FAN_MODE_NORMAL)
            properties[PROP_FAN_MODE] = mode

        await self.async_change_state(properties)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.async_change_state({PROP_FAN_ONOFF: 0})

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return

        gear = self._percentage_to_gear(percentage)
        properties: dict[str, int] = {PROP_FAN_GEAR: gear}
        optimistic: dict[str, int | str] = {PROP_FAN_GEAR: str(gear)}
        self._add_power_on_if_needed(
            properties,
            optimistic,
            optimistic_power=False,
        )
        await self.async_change_state(
            properties,
            optimistic_state=optimistic,
            debounced=True,
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        mode = PRESET_TO_MODE.get(preset_mode, FAN_MODE_NORMAL)
        properties: dict[str, int] = {PROP_FAN_MODE: mode}
        optimistic: dict[str, int | str] = {PROP_FAN_MODE: str(mode)}
        self._add_power_on_if_needed(properties, optimistic, optimistic_power=True)
        await self.async_change_state(properties, optimistic_state=optimistic)


class LiproHeaterVentFan(LiproEntity, FanEntity):
    """Representation of a Lipro heater ventilation fan (换气扇).

    This entity controls the ventilation/exhaust fan in bathroom heaters.
    It has two speed presets: strong (强) and weak (弱).
    """

    _attr_supported_features = (
        FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_preset_modes = VENT_PRESET_MODES
    _attr_translation_key = "ventilation_fan"
    _entity_suffix = "vent_fan"

    @property
    def is_on(self) -> bool:
        """Return true if ventilation fan is on."""
        return self.device.aeration_is_on

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        return AERATION_TO_PRESET.get(self.device.aeration_gear, PRESET_VENT_OFF)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the ventilation fan."""
        # Default to strong if no preset specified
        if preset_mode is None:
            preset_mode = PRESET_VENT_STRONG

        aeration = PRESET_TO_AERATION.get(preset_mode, AERATION_STRONG)
        await self.async_change_state({PROP_AERATION_GEAR: aeration})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the ventilation fan."""
        await self.async_change_state({PROP_AERATION_GEAR: AERATION_OFF})

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the ventilation fan."""
        aeration = PRESET_TO_AERATION.get(preset_mode, AERATION_STRONG)
        await self.async_change_state({PROP_AERATION_GEAR: aeration})
