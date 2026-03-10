"""Pure composition coordinator for the Lipro integration.

This coordinator uses explicit runtime collaborators instead of inheritance-based
mixins, following the composition-over-inheritance principle for better testability
and maintainability.
"""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..api import LiproClient
from ..device import LiproDevice
from .runtime.command_runtime import CommandRuntime
from .runtime.device_runtime import DeviceRuntime
from .runtime.mqtt_runtime import MqttRuntime
from .runtime.shared_state import CoordinatorSharedState
from .runtime.state_runtime import StateRuntime
from .runtime.status_runtime import StatusRuntime
from .runtime.tuning_runtime import TuningRuntime
from .services import (
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorStateService,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)


class Coordinator(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Pure composition coordinator with explicit runtime collaborators.

    This coordinator delegates all functionality to specialized runtime components
    instead of inheriting from multiple mixin classes. This approach provides:

    - Clear separation of concerns
    - Easier testing through dependency injection
    - Reduced coupling between components
    - Explicit collaboration boundaries
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize coordinator with runtime collaborators.

        Args:
            hass: Home Assistant instance
            client: Lipro API client
            auth_manager: Authentication manager
            config_entry: Configuration entry
            update_interval: Polling interval in seconds
        """
        super().__init__(
            hass,
            _LOGGER,
            name="Lipro",
            update_interval=timedelta(seconds=update_interval),
            config_entry=config_entry,
            always_update=True,
        )

        # Core dependencies
        self.client = client
        self.auth_manager = auth_manager

        # Initialize shared state
        self._shared_state = CoordinatorSharedState()

        # TODO: Initialize runtime components with proper dependencies
        # This is a skeleton implementation that needs to be completed
        # with actual component initialization based on the old mixin logic

        # Placeholder runtime instances (will be properly initialized)
        self._command_runtime: CommandRuntime | None = None
        self._device_runtime: DeviceRuntime | None = None
        self._mqtt_runtime: MqttRuntime | None = None
        self._state_runtime: StateRuntime | None = None
        self._status_runtime: StatusRuntime | None = None
        self._tuning_runtime: TuningRuntime | None = None

        # Initialize legacy state (temporary bridge during migration)
        self._init_legacy_state()

        # Public service boundaries (delegate to runtime)
        self.command_service = CoordinatorCommandService(self)
        self.device_refresh_service = CoordinatorDeviceRefreshService(self)
        self.mqtt_service = CoordinatorMqttService(self)
        self.state_service = CoordinatorStateService(self)

    def _init_legacy_state(self) -> None:
        """Initialize legacy state containers for backward compatibility.

        This method bridges the gap between old mixin-based state and new
        runtime-based state. It will be removed once full migration is complete.
        """
        # TODO: Move this logic into proper runtime initialization
        pass

    # -------------------------------------------------------------------------
    # Public API - Delegate to runtime components
    # -------------------------------------------------------------------------

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return current device snapshot."""
        return self._shared_state.devices

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Look up device by any known identifier.

        Args:
            device_id: Device serial or identifier

        Returns:
            Device if found, None otherwise
        """
        if self._state_runtime:
            return self._state_runtime.get_device_by_id(device_id)
        return self._shared_state.get_device(device_id)

    async def async_refresh_devices_runtime(self) -> None:
        """Trigger forced device refresh.

        Delegates to device runtime for full snapshot refresh.
        """
        if self._device_runtime:
            await self._device_runtime.refresh_devices(force=True)

    @property
    def mqtt_connected(self) -> bool:
        """Return MQTT connection status."""
        if self._mqtt_runtime:
            return self._mqtt_runtime.is_connected
        return self._shared_state.mqtt_connected

    async def async_setup_mqtt_runtime(self) -> bool:
        """Set up MQTT runtime.

        Returns:
            True if setup succeeded
        """
        if self._mqtt_runtime:
            return await self._mqtt_runtime.setup()
        return False

    async def async_stop_mqtt_runtime(self) -> None:
        """Stop MQTT runtime."""
        if self._mqtt_runtime:
            await self._mqtt_runtime.stop()

    async def async_sync_mqtt_subscriptions_runtime(self) -> None:
        """Sync MQTT subscriptions."""
        if self._mqtt_runtime:
            await self._mqtt_runtime.sync_subscriptions()

    # -------------------------------------------------------------------------
    # Legacy compatibility methods (temporary bridge)
    # -------------------------------------------------------------------------

    def get_device(self, serial: str) -> LiproDevice | None:
        """Get device by serial number.

        Args:
            serial: Device serial number

        Returns:
            Device if found, None otherwise
        """
        return self._shared_state.get_device(serial)

    @property
    def last_command_failure(self) -> dict[str, Any] | None:
        """Get last command failure trace."""
        if self._command_runtime:
            return self._command_runtime.last_command_failure
        return None

    async def async_ensure_authenticated(self) -> None:
        """Ensure authentication is valid."""
        # Delegate to auth manager
        await self.auth_manager.async_ensure_authenticated()

    async def async_execute_command_flow(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: dict[str, Any],
    ) -> tuple[bool, str]:
        """Execute command flow.

        Args:
            device: Target device
            command: Command name
            properties: Command properties
            fallback_device_id: Fallback device ID
            trace: Command trace

        Returns:
            Tuple of (success, route)
        """
        if self._command_runtime:
            return await self._command_runtime.send_device_command(
                device=device,
                command=command,
                properties=properties,
                fallback_device_id=fallback_device_id,
            )
        return False, "no_runtime"

    async def async_handle_command_api_error(
        self,
        device: LiproDevice,
        trace: dict[str, Any],
        route: str,
        err: Exception,
    ) -> bool:
        """Handle command API error.

        Args:
            device: Target device
            trace: Command trace
            route: Command route
            err: Exception that occurred

        Returns:
            False (command failed)
        """
        _LOGGER.error(
            "Command failed for device %s via %s: %s",
            device.serial,
            route,
            err,
        )
        return False

    # -------------------------------------------------------------------------
    # DataUpdateCoordinator lifecycle
    # -------------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API.

        This is called by Home Assistant's DataUpdateCoordinator on the
        configured update interval.

        Returns:
            Updated device dictionary
        """
        # TODO: Implement full update logic using runtime components
        # For now, return current state
        return self._shared_state.devices


LiproDataUpdateCoordinator = Coordinator

__all__ = ["Coordinator", "LiproDataUpdateCoordinator"]
