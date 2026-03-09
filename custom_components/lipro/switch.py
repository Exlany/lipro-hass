"""Switch platform for Lipro integration."""

from __future__ import annotations

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
from .helpers.platform import (
    build_device_entities_from_rules,
    create_device_entities,
    create_platform_entities,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import LiproConfigEntry
    from .core.coordinator import LiproDataUpdateCoordinator
    from .core.device import LiproDevice

# Limit parallel updates to avoid overwhelming the API
PARALLEL_UPDATES = 1


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
    coordinator: LiproDataUpdateCoordinator,
    device: LiproDevice,
) -> list[SwitchEntity]:
    """Build feature switches for one light device."""
    return build_device_entities_from_rules(
        coordinator,
        device,
        always_factories=(LiproFadeSwitch,),
        rules=(
            (
                lambda d: d.has_sleep_wake_features,
                (LiproSleepAidSwitch, LiproWakeUpSwitch),
            ),
            (
                lambda d: d.has_floor_lamp_features,
                (LiproFocusModeSwitch, LiproBodyReactiveSwitch),
            ),
        ),
    )


def _build_panel_feature_switches(
    coordinator: LiproDataUpdateCoordinator,
    device: LiproDevice,
) -> list[SwitchEntity]:
    """Build feature switches for one switch panel device."""
    return build_device_entities_from_rules(
        coordinator,
        device,
        rules=(
            (
                lambda d: PROP_LED in d.properties,
                (LiproPanelLedSwitch,),
            ),
            (
                lambda d: PROP_MEMORY in d.properties,
                (LiproPanelMemorySwitch,),
            ),
        ),
    )


class LiproSwitch(LiproEntity, SwitchEntity):
    """Representation of a Lipro switch or outlet."""

    _attr_name = None  # Use device name

    def __init__(
        self,
        coordinator: LiproDataUpdateCoordinator,
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
    """Base class for property-based feature switches."""

    _attr_entity_category = EntityCategory.CONFIG
    _property_key: str
    _device_property: str

    @property
    def is_on(self) -> bool:
        """Return true if the feature is enabled."""
        return bool(getattr(self.device, self._device_property, False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the feature."""
        await self.async_change_state({self._property_key: "1"})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the feature."""
        await self.async_change_state({self._property_key: "0"})


class LiproPanelPropertySwitch(LiproPropertySwitch):
    """Base class for switch-panel config entities using PANEL_CHANGE_STATE."""

    async def _async_set_panel_state(self, enabled: bool) -> None:
        """Send one panel config update with the required panelType."""
        value = "1" if enabled else "0"
        payload, _ = self._normalize_property_map(
            {
                self._property_key: value,
                "panelType": self.device.panel_type,
            }
        )
        await self.async_send_command(
            CMD_PANEL_CHANGE_STATE,
            payload,
            {self._property_key: value},
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable the panel feature."""
        await self._async_set_panel_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable the panel feature."""
        await self._async_set_panel_state(False)


class LiproFadeSwitch(LiproPropertySwitch):
    """Switch entity for light fade/transition effect."""

    _attr_translation_key = "fade"
    _entity_suffix = "fade"
    _property_key = PROP_FADE_STATE
    _device_property = "fade_state"


class LiproSleepAidSwitch(LiproPropertySwitch):
    """Switch entity for Natural Light sleep aid mode."""

    _attr_translation_key = "sleep_aid"
    _entity_suffix = "sleep_aid"
    _property_key = PROP_SLEEP_AID_ENABLE
    _device_property = "sleep_aid_enabled"


class LiproWakeUpSwitch(LiproPropertySwitch):
    """Switch entity for Natural Light wake up mode."""

    _attr_translation_key = "wake_up"
    _entity_suffix = "wake_up"
    _property_key = PROP_WAKE_UP_ENABLE
    _device_property = "wake_up_enabled"


class LiproFocusModeSwitch(LiproPropertySwitch):
    """Switch entity for Floor Lamp focus mode."""

    _attr_translation_key = "focus_mode"
    _entity_suffix = "focus_mode"
    _property_key = PROP_FOCUS_MODE
    _device_property = "focus_mode_enabled"


class LiproBodyReactiveSwitch(LiproPropertySwitch):
    """Switch entity for Floor Lamp motion reactive mode."""

    _attr_translation_key = "body_reactive"
    _entity_suffix = "body_reactive"
    _property_key = PROP_BODY_REACTIVE
    _device_property = "body_reactive_enabled"


class LiproPanelLedSwitch(LiproPanelPropertySwitch):
    """Switch entity for a panel's indicator LED."""

    _attr_translation_key = "panel_led"
    _entity_suffix = "panel_led"
    _property_key = PROP_LED
    _device_property = "panel_led_enabled"


class LiproPanelMemorySwitch(LiproPanelPropertySwitch):
    """Switch entity for a panel's power-loss memory."""

    _attr_translation_key = "panel_memory"
    _entity_suffix = "panel_memory"
    _property_key = PROP_MEMORY
    _device_property = "panel_memory_enabled"
