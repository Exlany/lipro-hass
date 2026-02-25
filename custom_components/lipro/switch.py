"""Switch platform for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import EntityCategory

from .const import (
    CMD_POWER_OFF,
    CMD_POWER_ON,
    DEVICE_TYPE_OUTLET,
    PROP_BODY_REACTIVE,
    PROP_FADE_STATE,
    PROP_FOCUS_MODE,
    PROP_POWER_STATE,
    PROP_SLEEP_AID_ENABLE,
    PROP_WAKE_UP_ENABLE,
)
from .entities.base import LiproEntity
from .helpers import create_device_entities, create_platform_entities

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

    # Add feature switches for lights.
    entities.extend(
        create_device_entities(
            coordinator,
            _build_light_feature_switches,
            device_filter=lambda d: d.is_light,
        )
    )

    async_add_entities(entities)


def _build_light_feature_switches(
    coordinator: LiproDataUpdateCoordinator,
    device: LiproDevice,
) -> list[SwitchEntity]:
    """Build feature switches for one light device."""
    entities: list[SwitchEntity] = [LiproFadeSwitch(coordinator, device)]

    # Natural Light features (自然光灯)
    if device.has_sleep_wake_features:
        entities.extend(
            [
                LiproSleepAidSwitch(coordinator, device),
                LiproWakeUpSwitch(coordinator, device),
            ]
        )

    # Floor Lamp features (落地灯)
    if device.has_floor_lamp_features:
        entities.extend(
            [
                LiproFocusModeSwitch(coordinator, device),
                LiproBodyReactiveSwitch(coordinator, device),
            ]
        )

    return entities


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

        # Set device class and translation key based on device type
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
    """Base class for property-based feature switches.

    Subclasses only need to define:
    - _entity_suffix: Unique ID suffix for the entity
    - _property_key: The property key to control
    - _device_property: The device property name to read state from
    - _attr_translation_key: Translation key for i18n

    Icons are managed declaratively via icons.json (HA best practice).
    """

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


class LiproFadeSwitch(LiproPropertySwitch):
    """Switch entity for light fade/transition effect.

    When enabled, the light will smoothly transition between brightness levels.
    When disabled, brightness changes are instant.
    """

    _attr_translation_key = "fade"
    _entity_suffix = "fade"
    _property_key = PROP_FADE_STATE
    _device_property = "fade_state"


class LiproSleepAidSwitch(LiproPropertySwitch):
    """Switch entity for Natural Light sleep aid mode.

    When enabled, the light will gradually dim to help you fall asleep.
    Only available on Natural Light (自然光灯) devices.
    """

    _attr_translation_key = "sleep_aid"
    _entity_suffix = "sleep_aid"
    _property_key = PROP_SLEEP_AID_ENABLE
    _device_property = "sleep_aid_enabled"


class LiproWakeUpSwitch(LiproPropertySwitch):
    """Switch entity for Natural Light wake up mode.

    When enabled, the light will gradually brighten to help you wake up.
    Only available on Natural Light (自然光灯) devices.
    """

    _attr_translation_key = "wake_up"
    _entity_suffix = "wake_up"
    _property_key = PROP_WAKE_UP_ENABLE
    _device_property = "wake_up_enabled"


class LiproFocusModeSwitch(LiproPropertySwitch):
    """Switch entity for Floor Lamp focus mode.

    When enabled, the light enters focus/reading mode.
    Only available on Floor Lamp (落地灯) devices.
    """

    _attr_translation_key = "focus_mode"
    _entity_suffix = "focus_mode"
    _property_key = PROP_FOCUS_MODE
    _device_property = "focus_mode_enabled"


class LiproBodyReactiveSwitch(LiproPropertySwitch):
    """Switch entity for Floor Lamp body reactive (motion sensing) mode.

    When enabled, the light responds to body/motion detection.
    Only available on Floor Lamp (落地灯) devices.
    """

    _attr_translation_key = "body_reactive"
    _entity_suffix = "body_reactive"
    _property_key = PROP_BODY_REACTIVE
    _device_property = "body_reactive_enabled"
