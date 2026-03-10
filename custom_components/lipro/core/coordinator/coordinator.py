"""Native coordinator runtime for the Lipro integration.

This coordinator is being refactored to use pure composition with runtime components
instead of inheritance-based mixins.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from ..command.confirmation_tracker import CommandConfirmationTracker
from ..device.identity_index import DeviceIdentityIndex
from ..utils.background_task_manager import BackgroundTaskManager
from .runtime.command import (
    CommandBuilder,
    CommandSender,
    ConfirmationManager,
    RetryStrategy,
)
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

        # Initialize components in stages
        self._init_state_containers()
        self._init_runtime_components(update_interval)
        self._init_service_layer()

    def _init_state_containers(self) -> None:
        """Initialize core state containers and managers."""
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

        # Command runtime state (required by ConfirmationManager)
        self._pending_expectations: dict[str, Any] = {}
        self._device_state_latency_seconds: dict[str, float] = {}
        self._post_command_refresh_tasks: dict[str, asyncio.Task[Any]] = {}
        self._connect_status_priority_ids: set[str] = set()
        self._force_connect_status_refresh: bool = False

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

        # Initialize CommandRuntime with sub-components
        command_builder = CommandBuilder(debug_mode=False)
        command_sender = CommandSender(client=self.client)
        retry_strategy = RetryStrategy()
        confirmation_manager = ConfirmationManager(
            confirmation_tracker=self._confirmation_tracker,
            pending_expectations=self._pending_expectations,
            device_state_latency_seconds=self._device_state_latency_seconds,
            post_command_refresh_tasks=self._post_command_refresh_tasks,
            track_background_task=self._background_task_manager.create,
            request_refresh=self.async_request_refresh,
            mqtt_connected_provider=lambda: self._mqtt_runtime.is_connected,
        )

        self._command_runtime = CommandRuntime(
            builder=command_builder,
            sender=command_sender,
            retry=retry_strategy,
            confirmation=confirmation_manager,
            connect_status_priority_ids=self._connect_status_priority_ids,
            normalize_device_key=self._normalize_device_key,
            force_connect_status_refresh_setter=lambda v: setattr(
                self, "_force_connect_status_refresh", v
            ),
            trigger_reauth=self._async_trigger_reauth,
            debug_mode=False,
        )

    def _init_service_layer(self) -> None:
        """Initialize service layer that delegates to runtime components."""
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
        results = await self.client.status.query_device_status(device_ids)
        return {item.get("iotId", ""): item for item in results if "iotId" in item}

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

    async def _async_trigger_reauth(self, reason: str) -> None:
        """Trigger reauthentication flow.

        Args:
            reason: Reason for reauth (e.g., "auth_expired", "auth_error")
        """
        _LOGGER.warning("Triggering reauth: %s", reason)
        error_message = f"Authentication failed: {reason}"
        raise ConfigEntryAuthFailed(error_message)

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates.

        This method creates and initializes the MQTT client with credentials
        from the API, then starts the connection for current devices.

        Returns:
            True if setup succeeded, False otherwise
        """
        from ...const.config import CONF_PHONE_ID
        from ..mqtt.client import LiproMqttClient
        from ..mqtt.credentials import decrypt_mqtt_credential
        from ..mqtt.utils import resolve_mqtt_biz_id

        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False

        try:
            # Get encrypted MQTT credentials from API
            mqtt_config = await self.client.get_mqtt_config()
            if not mqtt_config:
                _LOGGER.warning("No MQTT config available")
                return False

            # Decrypt credentials
            access_key = decrypt_mqtt_credential(mqtt_config.get("accessKey", ""))
            secret_key = decrypt_mqtt_credential(mqtt_config.get("secretKey", ""))

            if not access_key or not secret_key:
                _LOGGER.warning("Failed to decrypt MQTT credentials")
                return False

            # Resolve biz_id
            biz_id = resolve_mqtt_biz_id(self.config_entry.data)
            if biz_id is None:
                _LOGGER.warning("No biz_id available for MQTT")
                return False

            self._biz_id = biz_id
            phone_id = self.config_entry.data.get(CONF_PHONE_ID, "")

            # Create MQTT client
            self._mqtt_client = LiproMqttClient(
                access_key=access_key,
                secret_key=secret_key,
                biz_id=biz_id,
                phone_id=phone_id,
            )

            # Update runtime with new client
            self._mqtt_runtime = MqttRuntime(
                hass=self.hass,
                mqtt_client=self._mqtt_client,
                base_scan_interval=int(self.update_interval.total_seconds()),
                polling_multiplier=2,
            )

            # Wire up dependencies
            self._mqtt_runtime.set_device_resolver(self._get_device_by_id)
            self._mqtt_runtime.set_property_applier(self._apply_properties_update)
            self._mqtt_runtime.set_listener_notifier(
                lambda: self.async_set_updated_data(self._devices)
            )

            # Start MQTT connection for current devices
            device_ids = [
                device.serial
                for device in self._devices.values()
                if device.is_group  # Prefer mesh groups
            ]
            if device_ids:
                await self._mqtt_runtime.connect(device_ids=device_ids, biz_id=biz_id)

            return True

        except Exception as err:
            _LOGGER.warning("Failed to setup MQTT: %s", err)
            return False

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API.

        This is called by Home Assistant's DataUpdateCoordinator on the
        configured update interval.

        Returns:
            Updated device dictionary

        Raises:
            UpdateFailed: If update fails
        """
        try:
            # Add total timeout protection (30 seconds)
            async with asyncio.timeout(30):
                # Ensure authentication is valid (no specific timeout, uses API timeout)
                await self.auth_manager.async_ensure_authenticated()

                # Refresh device list if needed (10 seconds timeout)
                if self._device_runtime.should_refresh_device_list():
                    async with asyncio.timeout(10):
                        snapshot = await self._device_runtime.refresh_devices(force=True)
                        # Update coordinator devices from snapshot
                        self._devices.clear()
                        self._devices.update(snapshot.devices)

                # Schedule MQTT setup if needed (5 seconds timeout)
                if self._mqtt_client is None and self._devices:
                    async with asyncio.timeout(5):
                        await self.async_setup_mqtt()

            return self._devices

        except TimeoutError:
            _LOGGER.error("Update data timeout after 30 seconds")
            raise UpdateFailed("Update timeout") from None

        except (
            LiproRefreshTokenExpiredError,
            LiproAuthError,
        ) as err:
            _LOGGER.error("Authentication failed: %s", err)
            error_message = f"Authentication failed: {err}"
            raise ConfigEntryAuthFailed(error_message) from err

        except (
            LiproConnectionError,
            LiproApiError,
        ) as err:
            _LOGGER.error("Update failed: %s", err)
            error_message = f"Update failed: {err}"
            raise UpdateFailed(error_message) from err

        except Exception as err:
            _LOGGER.exception("Unexpected update failure")
            raise UpdateFailed("Unexpected update failure") from err


LiproDataUpdateCoordinator = Coordinator

__all__ = ["Coordinator", "LiproDataUpdateCoordinator"]
