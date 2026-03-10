"""Native coordinator runtime for the Lipro integration.

This coordinator is being refactored to use pure composition with runtime components
instead of inheritance-based mixins.
"""

from __future__ import annotations

import asyncio
from collections import deque
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..api import LiproClient
from ..command.confirmation_tracker import CommandConfirmationTracker
from ..device.identity_index import DeviceIdentityIndex
from ..utils.background_task_manager import BackgroundTaskManager
from .runtime.device_runtime import DeviceRuntime
from .runtime.mqtt_runtime import MqttRuntime
from .runtime.shared_state import CoordinatorSharedState
from .runtime.state_runtime import StateRuntime
from .runtime.status_runtime import StatusRuntime
from .runtime.tuning_runtime import TuningRuntime

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from ..mqtt.client import LiproMqttClient
    from .entity_protocol import LiproEntityProtocol

_LOGGER = logging.getLogger(__name__)


class Coordinator(DataUpdateCoordinator[dict[str, "LiproDevice"]]):
    """Coordinator runtime with runtime component composition.

    This coordinator is being refactored from mixin-based inheritance to
    pure composition with explicit runtime collaborators.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator runtime.

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
        self.client = client
        self.auth_manager = auth_manager
        self.config_entry = config_entry

        # Core state containers
        self._devices: dict[str, LiproDevice] = {}
        self._entities: dict[str, LiproEntityProtocol] = {}
        self._entities_by_device: dict[str, list[LiproEntityProtocol]] = {}
        self._device_identity_index = DeviceIdentityIndex()

        # MQTT state
        self._mqtt_client: LiproMqttClient | None = None
        self._biz_id: str | None = None

        # Background task management
        self._background_task_manager = BackgroundTaskManager(
            self.hass.async_create_task,
            _LOGGER,
        )
        self._background_tasks: set[asyncio.Task[Any]] = (
            self._background_task_manager.tasks
        )

        # Command confirmation tracking
        self._confirmation_tracker = CommandConfirmationTracker(
            default_post_command_refresh_delay_seconds=0.8,
            min_post_command_refresh_delay_seconds=0.3,
            max_post_command_refresh_delay_seconds=3.0,
            state_latency_margin_seconds=0.2,
            state_latency_ewma_alpha=0.3,
            state_confirm_timeout_seconds=5.0,
        )

        # Initialize runtime components and services
        self._init_runtime_components(update_interval)

    def _normalize_device_key(self, device_id: str) -> str:
        """Normalize device identifier for indexing.

        Args:
            device_id: Device serial or identifier

        Returns:
            Normalized key for consistent indexing
        """
        return device_id.lower().strip()

    def _init_runtime_components(self, update_interval: int) -> None:
        """Initialize all runtime components after state containers are ready."""

        # Initialize shared state
        self._shared_state = CoordinatorSharedState(
            devices=self._devices,
            mqtt_connected=False,
            biz_id=None,
            last_refresh_at=0.0,
            polling_interval=float(update_interval),
            command_confirmation_timeout=5.0,
            debug_mode=False,
        )

        # Initialize TuningRuntime (simplest, no dependencies)
        self._tuning_runtime = TuningRuntime(
            initial_batch_size=32,
            initial_mqtt_stale_window=180.0,
        )

        # Initialize StateRuntime
        self._state_runtime = StateRuntime(
            devices=self._devices,
            device_identity_index=self._device_identity_index,
            entities=self._entities,
            entities_by_device=self._entities_by_device,
            normalize_device_key=self._normalize_device_key,
        )

        # Initialize DeviceRuntime
        self._device_runtime = DeviceRuntime(
            client=self.client,
            auth_manager=self.auth_manager,
            device_identity_index=self._device_identity_index,
            filter_config_options=self.config_entry.options,
        )

        # Initialize StatusRuntime (requires helper methods)
        self._status_runtime = StatusRuntime(
            power_query_interval=300,
            outlet_power_cycle_size=10,
            max_devices_per_query=50,
            initial_batch_size=32,
            query_device_status=self._query_device_status_batch,
            apply_properties_update=self._apply_properties_update,
            get_device_by_id=self._get_device_by_id,
        )

        # Initialize MqttRuntime
        self._mqtt_runtime = MqttRuntime(
            hass=self.hass,
            mqtt_client=self._mqtt_client,
            base_scan_interval=update_interval,
            polling_multiplier=2,
        )

        # TODO: Initialize CommandRuntime (requires complex sub-components)
        # - CommandRuntime

        # Placeholder: Initialize services (these will delegate to runtimes)
        from .services import (
            CoordinatorCommandService,
            CoordinatorDeviceRefreshService,
            CoordinatorMqttService,
            CoordinatorStateService,
        )

        self.command_service = CoordinatorCommandService(self)
        self.device_refresh_service = CoordinatorDeviceRefreshService(self)
        self.mqtt_service = CoordinatorMqttService(self)
        self.state_service = CoordinatorStateService(self)

    # Helper methods for StatusRuntime
    async def _query_device_status_batch(
        self, device_ids: list[str]
    ) -> dict[str, dict[str, Any]]:
        """Query device status batch via API.

        Args:
            device_ids: List of device IDs to query

        Returns:
            Dictionary mapping device ID to status properties
        """
        # TODO: Implement actual API call
        return {}

    def _apply_properties_update(
        self, device: LiproDevice, properties: dict[str, Any], source: str
    ) -> bool:
        """Apply property updates to device.

        Args:
            device: Target device
            properties: Properties to update
            source: Update source identifier

        Returns:
            True if updates were applied
        """
        # Delegate to StateRuntime
        return self._state_runtime.apply_properties_update(
            device, properties, source=source
        )

    def _get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Get device by ID.

        Args:
            device_id: Device identifier

        Returns:
            Device if found, None otherwise
        """
        # Delegate to StateRuntime
        return self._state_runtime.get_device_by_id(device_id)

    async def _async_update_data(self) -> dict[str, "LiproDevice"]:
        """Fetch data from API.

        This is called by Home Assistant's DataUpdateCoordinator on the
        configured update interval.

        Returns:
            Updated device dictionary
        """
        # TODO: Delegate to status runtime for periodic updates
        return {}


LiproDataUpdateCoordinator = Coordinator

__all__ = ["Coordinator", "LiproDataUpdateCoordinator"]
