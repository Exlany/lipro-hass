"""Climate platform for Lipro integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature

from .const.properties import (
    HEATER_MODE_DEFAULT,
    HEATER_MODE_DEMIST,
    HEATER_MODE_DRY,
    HEATER_MODE_GENTLE_WIND,
    PROP_HEATER_MODE,
    PROP_HEATER_SWITCH,
)
from .entities.base import LiproEntity
from .entities.commands import PowerCommand
from .helpers.platform import (
    add_entry_entities,
    create_platform_entities,
    device_supports_platform,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)

# Preset modes
PRESET_DEFAULT: Final = "default"
PRESET_DEMIST: Final = "demist"
PRESET_DRY: Final = "dry"
PRESET_GENTLE_WIND: Final = "gentle_wind"

PRESET_MODES: Final = [PRESET_DEFAULT, PRESET_DEMIST, PRESET_DRY, PRESET_GENTLE_WIND]

MODE_TO_PRESET: Final = {
    HEATER_MODE_DEFAULT: PRESET_DEFAULT,
    HEATER_MODE_DEMIST: PRESET_DEMIST,
    HEATER_MODE_DRY: PRESET_DRY,
    HEATER_MODE_GENTLE_WIND: PRESET_GENTLE_WIND,
}

PRESET_TO_MODE: Final = {v: k for k, v in MODE_TO_PRESET.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro climate entities."""
    add_entry_entities(
        entry,
        async_add_entities,
        entity_builder=lambda coordinator: create_platform_entities(
            coordinator,
            device_filter=lambda d: device_supports_platform(d, "climate"),
            entity_factory=LiproHeater,
        ),
    )


class LiproHeater(LiproEntity, ClimateEntity):
    """Representation of a Lipro heater."""

    _power = PowerCommand(state_key=PROP_HEATER_SWITCH)

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]  # noqa: RUF012
    _attr_supported_features = (
        ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_preset_modes = PRESET_MODES
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_translation_key = "heater"
    _attr_name = None  # Use device name (heater is the primary entity)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if self.device.state.heater_is_on:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        mode = self.device.state.heater_mode
        return MODE_TO_PRESET.get(mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.HEAT:
            await self._power.turn_on(self)
        else:
            await self._power.turn_off(self)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        mode = PRESET_TO_MODE.get(preset_mode)
        if mode is None:
            _LOGGER.debug(
                "Ignoring unsupported preset mode '%s' for %s",
                preset_mode,
                self.device.name,
            )
            return
        await self.async_change_state({PROP_HEATER_MODE: mode})

    async def async_turn_on(self) -> None:
        """Turn on the heater."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn off the heater."""
        await self.async_set_hvac_mode(HVACMode.OFF)
