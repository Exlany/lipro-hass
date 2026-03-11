"""Switch platform for Lipro integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import EntityCategory

from .const.device_types import DEVICE_TYPE_OUTLET, DEVICE_TYPE_PANEL
from .const.properties import (
    CMD_PANEL_CHANGE_STATE,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    PROP_BODY_REACTIVE,
    PROP_FADE_STATE,
    PROP_FOCUS_MODE,
    PROP_LED,
    PROP_MEMORY,
    PROP_POWER_STATE,
    PROP_SLEEP_AID_ENABLE,
    PROP_WAKE_UP_ENABLE,
)
from .entities.base import LiproEntity
from .helpers.platform import create_device_entities, create_platform_entities

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.device import LiproDevice
    from .runtime_types import LiproCoordinator

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1


@dataclass
class PropertySwitchConfig:
    """Configuration for a property-based switch entity."""

    translation_key: str
    entity_suffix: str
    property_key: str
    device_property: str


# Light feature switches configuration
LIGHT_FEATURE_SWITCHES = [
    PropertySwitchConfig(
        translation_key="fade",
        entity_suffix="fade",
        property_key=PROP_FADE_STATE,
        device_property="fade_state",
    ),
    PropertySwitchConfig(
        translation_key="sleep_aid",
        entity_suffix="sleep_aid",
        property_key=PROP_SLEEP_AID_ENABLE,
        device_property="sleep_aid_enabled",
    ),
    PropertySwitchConfig(
        translation_key="wake_up",
        entity_suffix="wake_up",
        property_key=PROP_WAKE_UP_ENABLE,
        device_property="wake_up_enabled",
    ),
    PropertySwitchConfig(
        translation_key="focus_mode",
        entity_suffix="focus_mode",
        property_key=PROP_FOCUS_MODE,
        device_property="focus_mode_enabled",
    ),
    PropertySwitchConfig(
        translation_key="body_reactive",
        entity_suffix="body_reactive",
        property_key=PROP_BODY_REACTIVE,
        device_property="body_reactive_enabled",
    ),
]

# Panel feature switches configuration
PANEL_FEATURE_SWITCHES = [
    PropertySwitchConfig(
        translation_key="panel_led",
        entity_suffix="panel_led",
        property_key=PROP_LED,
        device_property="panel_led_enabled",
    ),
    PropertySwitchConfig(
        translation_key="panel_memory",
        entity_suffix="panel_memory",
        property_key=PROP_MEMORY,
        device_property="panel_memory_enabled",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lipro switches."""
    coordinator = entry.runtime_data
    entities: list[SwitchEntity] = []
    entities.extend(
        create_platform_entities(
            coordinator,
            device_filter=lambda d: d.is_switch,
            entity_factory=LiproSwitch,
        )
    )
    entities.extend(
        create_device_entities(
            coordinator,
            _build_light_feature_switches,
            device_filter=lambda d: d.is_light,
        )
    )
    entities.extend(
        create_device_entities(
            coordinator,
            _build_panel_feature_switches,
            device_filter=lambda d: d.device_type_hex == DEVICE_TYPE_PANEL,
        )
    )

    async_add_entities(entities)


def _build_light_feature_switches(
    coordinator: LiproCoordinator,
    device: LiproDevice,
) -> list[SwitchEntity]:
    """Build feature switches for one light device."""
    entities: list[SwitchEntity] = []
    for config in LIGHT_FEATURE_SWITCHES:
        if hasattr(device, config.device_property):
            entities.append(LiproPropertySwitch(coordinator, device, config))
    return entities


def _build_panel_feature_switches(
    coordinator: LiproCoordinator,
    device: LiproDevice,
) -> list[SwitchEntity]:
    """Build feature switches for one switch panel device."""
    entities: list[SwitchEntity] = []
    for config in PANEL_FEATURE_SWITCHES:
        if PROP_LED in device.properties or PROP_MEMORY in device.properties:
            if hasattr(device, config.device_property):
                entities.append(LiproPanelPropertySwitch(coordinator, device, config))
    return entities


class LiproSwitch(LiproEntity, SwitchEntity):
    """Representation of a Lipro switch or outlet."""

    _attr_name = None  # Use device name

    def __init__(
        self,
        coordinator: LiproCoordinator,
        device: LiproDevice,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, device)

        if device.device_type_hex == DEVICE_TYPE_OUTLET:
            self._attr_device_class = SwitchDeviceClass.OUTLET
            self._attr_translation_key = "outlet"
        else:
            self._attr_device_class = SwitchDeviceClass.SWITCH
            self._attr_translation_key = "switch"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.device.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self.async_send_command(CMD_POWER_ON, None, {PROP_POWER_STATE: "1"})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self.async_send_command(CMD_POWER_OFF, None, {PROP_POWER_STATE: "0"})


class LiproPropertySwitch(LiproEntity, SwitchEntity):
    """Generic property-based feature switch using configuration."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: LiproCoordinator,
        device: LiproDevice,
        config: PropertySwitchConfig,
    ) -> None:
        """Initialize the property switch."""
        super().__init__(coordinator, device, config.entity_suffix)
        self._config = config
        self._attr_translation_key = config.translation_key

    @property
    def is_on(self) -> bool:
        """Return true if the feature is enabled."""
        return bool(getattr(self.device, self._config.device_property, False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the feature."""
        await self.async_change_state({self._config.property_key: "1"})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the feature."""
        await self.async_change_state({self._config.property_key: "0"})


class LiproPanelPropertySwitch(LiproEntity, SwitchEntity):
    """Generic panel property switch using PANEL_CHANGE_STATE command."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: LiproCoordinator,
        device: LiproDevice,
        config: PropertySwitchConfig,
    ) -> None:
        """Initialize the panel property switch."""
        super().__init__(coordinator, device, config.entity_suffix)
        self._config = config
        self._attr_translation_key = config.translation_key

    @property
    def is_on(self) -> bool:
        """Return true if the feature is enabled."""
        return bool(getattr(self.device, self._config.device_property, False))

    async def _async_set_panel_state(self, enabled: bool) -> None:
        """Send one panel config update with the required panelType."""
        value = "1" if enabled else "0"
        payload, _ = self._normalize_property_map(
            {
                self._config.property_key: value,
                "panelType": self.device.panel_type,
            }
        )
        await self.async_send_command(
            CMD_PANEL_CHANGE_STATE,
            payload,
            {self._config.property_key: value},
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the panel feature."""
        await self._async_set_panel_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the panel feature."""
        await self._async_set_panel_state(False)

