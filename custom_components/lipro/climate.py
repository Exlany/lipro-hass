"""Climate platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature

from .const import (
    CMD_CHANGE_STATE,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    HEATER_MODE_DEFAULT,
    HEATER_MODE_DEMIST,
    HEATER_MODE_DRY,
    HEATER_MODE_GENTLE_WIND,
    PROP_HEATER_MODE,
    PROP_HEATER_SWITCH,
)
from .entities.base import LiproEntity
from .helpers import create_platform_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1

# Preset modes
PRESET_DEFAULT = "default"
PRESET_DEMIST = "demist"
PRESET_DRY = "dry"
PRESET_GENTLE_WIND = "gentle_wind"

PRESET_MODES = [PRESET_DEFAULT, PRESET_DEMIST, PRESET_DRY, PRESET_GENTLE_WIND]

MODE_TO_PRESET = {
    HEATER_MODE_DEFAULT: PRESET_DEFAULT,
    HEATER_MODE_DEMIST: PRESET_DEMIST,
    HEATER_MODE_DRY: PRESET_DRY,
    HEATER_MODE_GENTLE_WIND: PRESET_GENTLE_WIND,
}

PRESET_TO_MODE = {v: k for k, v in MODE_TO_PRESET.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro climate entities."""
    entities = create_platform_entities(
        entry.runtime_data,
        device_filter=lambda d: d.is_heater,
        entity_factory=LiproHeater,
    )
    async_add_entities(entities)


class LiproHeater(LiproEntity, ClimateEntity):
    """Representation of a Lipro heater."""

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_preset_modes = PRESET_MODES
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_translation_key = "heater"
    _attr_name = None  # Use device name (heater is the primary entity)
    _enable_turn_on_off_backwards_compatibility = False

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if self.device.heater_is_on:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        mode = self.device.heater_mode
        return MODE_TO_PRESET.get(mode, PRESET_DEFAULT)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.HEAT:
            await self.async_send_command(CMD_POWER_ON, None, {PROP_HEATER_SWITCH: "1"})
        else:
            await self.async_send_command(
                CMD_POWER_OFF,
                None,
                {PROP_HEATER_SWITCH: "0"},
            )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        mode = PRESET_TO_MODE.get(preset_mode, HEATER_MODE_DEFAULT)
        await self.async_send_command(
            CMD_CHANGE_STATE,
            [{"key": PROP_HEATER_MODE, "value": str(mode)}],
            {PROP_HEATER_MODE: str(mode)},
        )

    async def async_turn_on(self) -> None:
        """Turn on the heater."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn off the heater."""
        await self.async_set_hvac_mode(HVACMode.OFF)
