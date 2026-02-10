"""Base entity for Lipro integration."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..core.coordinator import LiproDataUpdateCoordinator
from ..helpers.debounce import Debouncer

if TYPE_CHECKING:
    from ..core.device import LiproDevice

# Time window (seconds) after debounced command during which
# coordinator updates should not overwrite optimistic state
DEBOUNCE_PROTECTION_WINDOW = 2.0


class LiproEntity(CoordinatorEntity[LiproDataUpdateCoordinator]):
    """Base class for Lipro entities."""

    _attr_has_entity_name = True
    _attr_attribution = "Data provided by Lipro Smart Home"

    def __init__(
        self,
        coordinator: LiproDataUpdateCoordinator,
        device: LiproDevice,
        entity_suffix: str = "",
    ) -> None:
        """Initialize the entity.

        Args:
            coordinator: Data update coordinator.
            device: The Lipro device.
            entity_suffix: Optional suffix for entity unique ID.
                Falls back to class attribute _entity_suffix if not provided.

        """
        super().__init__(coordinator)
        self._device = device
        self._entity_suffix = entity_suffix or getattr(type(self), "_entity_suffix", "")
        self._debouncer: Debouncer | None = None
        # Track when debounced properties were last set (for protection window)
        self._debounce_protected_until: float = 0
        self._debounce_protected_keys: set[str] = set()

        # Set unique ID
        if self._entity_suffix:
            self._attr_unique_id = f"{device.unique_id}_{self._entity_suffix}"
        else:
            self._attr_unique_id = device.unique_id

    @property
    def device(self) -> LiproDevice:
        """Return the device."""
        # Get fresh device data from coordinator
        return self.coordinator.get_device(self._device.serial) or self._device

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.device.available

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        info = DeviceInfo(
            identifiers={(DOMAIN, self._device.serial)},
            name=self._device.name,
            manufacturer="Lipro",
            model=self._device.physical_model or self._device.iot_name,
            suggested_area=self._device.room_name,
        )

        # Add serial number for non-group devices
        if not self._device.is_group and self._device.serial:
            info["serial_number"] = self._device.serial

        # Add firmware version if available from device
        if self._device.firmware_version:
            info["sw_version"] = self._device.firmware_version

        # Add hardware model info if available (iot_name is the internal model code)
        if self._device.iot_name:
            info["hw_version"] = self._device.iot_name

        return info

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # Register with coordinator for debounce protection tracking
        self.coordinator.register_entity(self)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        # Cancel any pending debounce tasks
        if self._debouncer is not None:
            self._debouncer.cancel()
            self._debouncer = None
        # Unregister from coordinator
        self.coordinator.unregister_entity(self)
        await super().async_will_remove_from_hass()

    @property
    def is_debouncing(self) -> bool:
        """Check if entity is currently in debounce protection window."""
        return time.time() < self._debounce_protected_until

    def get_protected_keys(self) -> set[str]:
        """Get the set of property keys currently protected by debounce.

        Returns:
            Set of property keys that should not be overwritten by coordinator.

        """
        if self.is_debouncing:
            return self._debounce_protected_keys
        return set()

    def _get_debouncer(self) -> Debouncer:
        """Get or create debouncer for this entity."""
        if self._debouncer is None:
            self._debouncer = Debouncer()
        return self._debouncer

    async def async_send_command(
        self,
        command: str,
        properties: list[dict[str, str]] | None = None,
        optimistic_state: dict[str, Any] | None = None,
    ) -> bool:
        """Send a command to the device with optimistic state update.

        Args:
            command: Command name.
            properties: Optional properties to send.
            optimistic_state: Optional dict of property key-value pairs to
                              optimistically update before cloud confirmation.

        Returns:
            True if successful.

        """
        # Apply optimistic state update immediately
        if optimistic_state:
            self.device.update_properties(optimistic_state)
            self.async_write_ha_state()

        success = await self.coordinator.async_send_command(
            self.device,
            command,
            properties,
        )

        # If command failed, request refresh to restore actual state
        if not success and optimistic_state:
            await self.coordinator.async_request_refresh()

        return success

    async def async_send_command_debounced(
        self,
        command: str,
        properties: list[dict[str, str]] | None = None,
        optimistic_state: dict[str, Any] | None = None,
    ) -> None:
        """Send a command with debouncing for slider controls.

        Use this for continuous value changes (brightness, color_temp, position)
        to avoid flooding the API with requests.

        Args:
            command: Command name.
            properties: Optional properties to send.
            optimistic_state: Optional dict of property key-value pairs to
                              optimistically update before cloud confirmation.

        """
        # Apply optimistic state update immediately (no debounce for UI feedback)
        if optimistic_state:
            self.device.update_properties(optimistic_state)
            self.async_write_ha_state()

            # Set protection window to prevent coordinator from overwriting
            # these properties during slider drag
            self._debounce_protected_until = time.time() + DEBOUNCE_PROTECTION_WINDOW
            self._debounce_protected_keys = set(optimistic_state.keys())

        # Debounce the actual API call
        debouncer = self._get_debouncer()
        await debouncer.async_call(
            self._send_command_internal,
            command,
            properties,
            optimistic_state,
        )

    async def _send_command_internal(
        self,
        command: str,
        properties: list[dict[str, str]] | None,
        optimistic_state: dict[str, Any] | None,
    ) -> None:
        """Internal method to send command (called by debouncer).

        Args:
            command: Command name.
            properties: Optional properties to send.
            optimistic_state: State that was optimistically set.

        """
        success = await self.coordinator.async_send_command(
            self.device,
            command,
            properties,
        )

        # Clear protection after command is sent (with small buffer for response)
        self._debounce_protected_until = time.time() + 1.0

        # If command failed, request refresh to restore actual state
        if not success and optimistic_state:
            self._debounce_protected_keys.clear()
            self._debounce_protected_until = 0
            await self.coordinator.async_request_refresh()
