"""Base entity for Lipro integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Final, cast

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const.base import DOMAIN, MANUFACTURER
from ..const.properties import CMD_CHANGE_STATE
from ..core.utils.debounce import Debouncer
from ..runtime_types import LiproCoordinator

if TYPE_CHECKING:
    from ..core.device import LiproDevice

_LOGGER = logging.getLogger(__name__)

# Time window (seconds) after debounced command during which
# coordinator updates should not overwrite optimistic state
DEBOUNCE_PROTECTION_WINDOW: Final = 2.0

# Small buffer (seconds) after command is sent before clearing protection,
# allowing the cloud response to arrive
_POST_COMMAND_PROTECTION_BUFFER: Final = 1.0


class LiproEntity(CoordinatorEntity[Any]):
    """Base class for Lipro entities."""

    coordinator: LiproCoordinator

    _attr_has_entity_name = True
    _attr_attribution = "Data provided by Lipro Smart Home"

    def __init__(
        self,
        coordinator: LiproCoordinator,
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
        super().__init__(cast(Any, coordinator))
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

        # Cache device_info (static per device, built once)
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial)},
            name=device.name,
            manufacturer=MANUFACTURER,
            model=device.physical_model or device.iot_name,
            suggested_area=device.room_name,
        )
        if not device.is_group and device.serial:
            device_info["serial_number"] = device.serial
        if device.firmware_version:
            device_info["sw_version"] = device.firmware_version
        if device.iot_name:
            device_info["hw_version"] = device.iot_name
        self._attr_device_info = device_info

    @property
    def device(self) -> LiproDevice:
        """Return the device."""
        # Get fresh device data from coordinator
        return self.coordinator.get_device(self._device.serial) or self._device

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.device.available

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
        return monotonic() < self._debounce_protected_until

    def get_protected_keys(self) -> set[str]:
        """Get the set of property keys currently protected by debounce.

        Returns:
            Set of property keys that should not be overwritten by coordinator.

        """
        if self.is_debouncing:
            return self._debounce_protected_keys
        if self._debounce_protected_keys:
            self._debounce_protected_keys.clear()
        return set()

    def _get_debouncer(self) -> Debouncer:
        """Get or create debouncer for this entity."""
        if self._debouncer is None:
            self._debouncer = Debouncer()
        return self._debouncer

    @staticmethod
    def _normalize_property_map(
        properties: Mapping[str, Any],
    ) -> tuple[list[dict[str, str]], dict[str, str]]:
        """Convert a property mapping to API payload and optimistic state."""
        property_dict = {key: str(value) for key, value in properties.items()}
        payload = [{"key": key, "value": value} for key, value in property_dict.items()]
        return payload, property_dict

    async def async_change_state(
        self,
        properties: Mapping[str, Any],
        *,
        optimistic_state: Mapping[str, Any] | None = None,
        debounced: bool = False,
    ) -> bool | None:
        """Send a CHANGE_STATE command with normalized property payload.

        Args:
            properties: Properties to send as key-value pairs.
            optimistic_state: Optional optimistic state override.
            debounced: Whether to debounce the command send.

        Returns:
            For non-debounced sends, True/False command result.
            For debounced sends, None (send is scheduled by debouncer).

        """
        payload, default_optimistic = self._normalize_property_map(properties)
        if optimistic_state is None:
            optimistic = default_optimistic
        else:
            optimistic = {key: str(value) for key, value in optimistic_state.items()}

        if debounced:
            await self.async_send_command_debounced(
                CMD_CHANGE_STATE,
                payload,
                optimistic,
            )
            return None

        return await self.async_send_command(
            CMD_CHANGE_STATE,
            payload,
            optimistic,
        )

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
        if not self.available:
            _LOGGER.debug(
                "Skipping command %s: %s unavailable", command, self.entity_id
            )
            return False

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
        if not self.available:
            _LOGGER.debug(
                "Skipping debounced command %s: %s unavailable",
                command,
                self.entity_id,
            )
            return

        # Apply optimistic state update immediately (no debounce for UI feedback)
        if optimistic_state:
            self.device.update_properties(optimistic_state)
            self.async_write_ha_state()

            # Set protection window to prevent coordinator from overwriting
            # these properties during slider drag
            self._debounce_protected_until = monotonic() + DEBOUNCE_PROTECTION_WINDOW
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
        self._debounce_protected_until = monotonic() + _POST_COMMAND_PROTECTION_BUFFER

        # If command failed, request refresh to restore actual state
        if not success and optimistic_state:
            self._debounce_protected_keys.clear()
            self._debounce_protected_until = 0
            await self.coordinator.async_request_refresh()
