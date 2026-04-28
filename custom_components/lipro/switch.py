"""Switch platform for Lipro integration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import EntityCategory

from .const.properties import (
    PROP_BODY_REACTIVE,
    PROP_FADE_STATE,
    PROP_FOCUS_MODE,
    PROP_LED,
    PROP_MEMORY,
    PROP_SLEEP_AID_ENABLE,
    PROP_WAKE_UP_ENABLE,
)
from .entities.base import LiproEntity
from .entities.commands import (
    PanelPropertyToggleCommand,
    PowerCommand,
    PropertyToggleCommand,
)
from .helpers.platform import (
    add_entry_entities,
    build_device_entities_from_rules,
    create_device_entities,
    device_supports_platform,
    should_expose_light_property_switch,
    should_expose_panel_property_switch,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.device import LiproDevice
    from .runtime_types import LiproRuntimeCoordinator

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1


@dataclass
class PropertySwitchConfig:
    """Configuration for a property-based switch entity."""

    translation_key: str
    entity_suffix: str
    property_key: str


# ── Entity classes ──────────────────────────────────────────────────


class LiproSwitch(LiproEntity, SwitchEntity):
    """Representation of a Lipro switch or outlet."""

    _attr_name = None  # Use device name

    _power = PowerCommand()

    def __init__(
        self,
        coordinator: LiproRuntimeCoordinator,
        device: LiproDevice,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device)

        if device.capabilities.is_outlet:
            self._attr_device_class = SwitchDeviceClass.OUTLET
            self._attr_translation_key = "outlet"
        else:
            self._attr_device_class = SwitchDeviceClass.SWITCH
            self._attr_translation_key = "switch"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.device.state.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self._power.turn_on(self)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self._power.turn_off(self)


class LiproPropertySwitch(LiproEntity, SwitchEntity):
    """Generic property-based feature switch using configuration."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: LiproRuntimeCoordinator,
        device: LiproDevice,
        config: PropertySwitchConfig,
    ) -> None:
        """Initialize the property switch."""
        super().__init__(coordinator, device, config.entity_suffix)
        self._config = config
        self._toggle = PropertyToggleCommand(config.property_key)
        self._attr_translation_key = config.translation_key

    @property
    def is_on(self) -> bool:
        """Return true if the feature is enabled."""
        return self.device.state.get_bool_property(self._config.property_key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the feature."""
        await self._toggle.turn_on(self)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the feature."""
        await self._toggle.turn_off(self)


class LiproPanelPropertySwitch(LiproEntity, SwitchEntity):
    """Generic panel property switch using PANEL_CHANGE_STATE command."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: LiproRuntimeCoordinator,
        device: LiproDevice,
        config: PropertySwitchConfig,
    ) -> None:
        """Initialize the panel property switch."""
        super().__init__(coordinator, device, config.entity_suffix)
        self._config = config
        self._toggle = PanelPropertyToggleCommand(config.property_key)
        self._attr_translation_key = config.translation_key

    @property
    def is_on(self) -> bool:
        """Return true if the feature is enabled."""
        return self.device.state.get_bool_property(self._config.property_key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the panel feature."""
        await self._toggle.turn_on(self)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the panel feature."""
        await self._toggle.turn_off(self)


# ── Declarative config & rules ──────────────────────────────────────

# Light feature switches configuration
LIGHT_FEATURE_SWITCHES = [
    PropertySwitchConfig(
        translation_key="fade",
        entity_suffix="fade",
        property_key=PROP_FADE_STATE,
    ),
    PropertySwitchConfig(
        translation_key="sleep_aid",
        entity_suffix="sleep_aid",
        property_key=PROP_SLEEP_AID_ENABLE,
    ),
    PropertySwitchConfig(
        translation_key="wake_up",
        entity_suffix="wake_up",
        property_key=PROP_WAKE_UP_ENABLE,
    ),
    PropertySwitchConfig(
        translation_key="focus_mode",
        entity_suffix="focus_mode",
        property_key=PROP_FOCUS_MODE,
    ),
    PropertySwitchConfig(
        translation_key="body_reactive",
        entity_suffix="body_reactive",
        property_key=PROP_BODY_REACTIVE,
    ),
]

# Panel feature switches configuration
PANEL_FEATURE_SWITCHES = [
    PropertySwitchConfig(
        translation_key="panel_led",
        entity_suffix="panel_led",
        property_key=PROP_LED,
    ),
    PropertySwitchConfig(
        translation_key="panel_memory",
        entity_suffix="panel_memory",
        property_key=PROP_MEMORY,
    ),
]

# Declarative rules for switch entity creation.
# Each (predicate, factories) pair follows the same pattern as fan.py/sensor.py.
# Per-config conditions are expressed as individual rules with compound predicates.
_SWITCH_RULES: list[
    tuple[
        Callable[[LiproDevice], bool],
        Sequence[Callable[[LiproRuntimeCoordinator, LiproDevice], SwitchEntity]],
    ]
] = [
    # Main switch entity (outlet or panel)
    (lambda d: device_supports_platform(d, "switch"), [LiproSwitch]),
    *[
        (
            lambda d, property_key=cfg.property_key: (
                should_expose_light_property_switch(
                    d,
                    property_key=property_key,
                )
            ),
            [lambda c, d, cfg=cfg: LiproPropertySwitch(c, d, cfg)],
        )
        for cfg in LIGHT_FEATURE_SWITCHES
    ],
    *[
        (
            lambda d, property_key=cfg.property_key: (
                should_expose_panel_property_switch(
                    d,
                    property_key=property_key,
                )
            ),
            [lambda c, d, cfg=cfg: LiproPanelPropertySwitch(c, d, cfg)],
        )
        for cfg in PANEL_FEATURE_SWITCHES
    ],
]


# ── Platform setup ──────────────────────────────────────────────────


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro switches."""
    add_entry_entities(
        entry,
        async_add_entities,
        entity_builder=lambda coordinator: create_device_entities(
            coordinator,
            _build_device_switches,
        ),
    )


def _build_device_switches(
    coordinator: LiproRuntimeCoordinator,
    device: LiproDevice,
) -> list[SwitchEntity]:
    """Build switch entities for one device using declarative rules."""
    return build_device_entities_from_rules(coordinator, device, rules=_SWITCH_RULES)
