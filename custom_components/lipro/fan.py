"""Fan platform for Lipro integration."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    AERATION_OFF,
    AERATION_STRONG,
    AERATION_WEAK,
    CMD_CHANGE_STATE,
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
PRESET_MODE_NATURAL = "natural"
PRESET_MODE_SLEEP = "sleep"
PRESET_MODE_NORMAL = "normal"

PRESET_MODES = [PRESET_MODE_NATURAL, PRESET_MODE_SLEEP, PRESET_MODE_NORMAL]

MODE_TO_PRESET = {
    FAN_MODE_NATURAL: PRESET_MODE_NATURAL,
    FAN_MODE_SLEEP: PRESET_MODE_SLEEP,
    FAN_MODE_NORMAL: PRESET_MODE_NORMAL,
}

PRESET_TO_MODE = {v: k for k, v in MODE_TO_PRESET.items()}

# Preset modes for heater ventilation fan
PRESET_VENT_OFF = "off"
PRESET_VENT_STRONG = "strong"
PRESET_VENT_WEAK = "weak"

VENT_PRESET_MODES = [PRESET_VENT_STRONG, PRESET_VENT_WEAK]

AERATION_TO_PRESET = {
    AERATION_OFF: PRESET_VENT_OFF,
    AERATION_STRONG: PRESET_VENT_STRONG,
    AERATION_WEAK: PRESET_VENT_WEAK,
}

PRESET_TO_AERATION = {v: k for k, v in AERATION_TO_PRESET.items()}


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
        properties: list[dict[str, str]] = [{"key": PROP_FAN_ONOFF, "value": "1"}]
        optimistic: dict[str, Any] = {PROP_FAN_ONOFF: "1"}

        if percentage is not None:
            speed_range = self.device.fan_speed_range
            gear = math.ceil(percentage_to_ranged_value(speed_range, percentage))
            gear = max(speed_range[0], min(speed_range[1], gear))
            properties.append({"key": PROP_FAN_GEAR, "value": str(gear)})
            optimistic[PROP_FAN_GEAR] = str(gear)

        if preset_mode is not None:
            mode = PRESET_TO_MODE.get(preset_mode, FAN_MODE_NORMAL)
            properties.append({"key": PROP_FAN_MODE, "value": str(mode)})
            optimistic[PROP_FAN_MODE] = str(mode)

        await self.async_send_command(CMD_CHANGE_STATE, properties, optimistic)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_FAN_ONOFF, "value": "0"}],
            {PROP_FAN_ONOFF: "0"},
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return

        speed_range = self.device.fan_speed_range
        gear = math.ceil(percentage_to_ranged_value(speed_range, percentage))
        gear = max(speed_range[0], min(speed_range[1], gear))
        properties = [{"key": PROP_FAN_GEAR, "value": str(gear)}]
        optimistic: dict[str, Any] = {PROP_FAN_GEAR: str(gear)}

        # Turn on if not already on — send fanOnOff in properties but NOT in
        # optimistic, so it won't be debounce-protected (same pattern as light powerState)
        if not self.is_on:
            properties.insert(0, {"key": PROP_FAN_ONOFF, "value": "1"})
            self.device.update_properties({PROP_FAN_ONOFF: "1"})

        # Use debounce for speed slider to avoid flooding API
        await self.async_send_command_debounced(
            CMD_CHANGE_STATE,
            properties,
            optimistic,
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        mode = PRESET_TO_MODE.get(preset_mode, FAN_MODE_NORMAL)
        properties = [{"key": PROP_FAN_MODE, "value": str(mode)}]
        optimistic: dict[str, Any] = {PROP_FAN_MODE: str(mode)}

        # Turn on if not already on
        if not self.is_on:
            properties.insert(0, {"key": PROP_FAN_ONOFF, "value": "1"})
            optimistic[PROP_FAN_ONOFF] = "1"

        await self.async_send_command(CMD_CHANGE_STATE, properties, optimistic)


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
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_AERATION_GEAR, "value": str(aeration)}],
            {PROP_AERATION_GEAR: str(aeration)},
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the ventilation fan."""
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_AERATION_GEAR, "value": str(AERATION_OFF)}],
            {PROP_AERATION_GEAR: str(AERATION_OFF)},
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the ventilation fan."""
        aeration = PRESET_TO_AERATION.get(preset_mode, AERATION_STRONG)
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_AERATION_GEAR, "value": str(aeration)}],
            {PROP_AERATION_GEAR: str(aeration)},
        )
