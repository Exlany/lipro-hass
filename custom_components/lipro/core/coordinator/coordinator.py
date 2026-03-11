"""Native coordinator runtime for the Lipro integration.

Refactored to use RuntimeContext + Orchestrator pattern (Phase C - Aggressive Refactor).
"""

from __future__ import annotations

import asyncio
from contextlib import suppress
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
from ..mqtt.mqtt_client import LiproMqttClient
from .mqtt_lifecycle import async_setup_mqtt as setup_mqtt_lifecycle
from .orchestrator import RuntimeOrchestrator
from .runtime_context import RuntimeContext
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
    from .entity_protocol import LiproEntityProtocol

_LOGGER = logging.getLogger(__name__)


class Coordinator(DataUpdateCoordinator[dict[str, "LiproDevice"]]):
    """Coordinator runtime with RuntimeContext + Orchestrator pattern.

    Refactored to use:
    - RuntimeContext: Unified dependency injection
    - RuntimeOrchestrator: Centralized component wiring
    - Thin facade: < 250 LOC, pure HA adapter
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
        self._config_entry = config_entry
        self._scan_interval_seconds = int(update_interval)
        self._force_connect_status_refresh: bool = False

        # Build runtime components via orchestrator
        orchestrator = RuntimeOrchestrator(
            hass=hass,
            client=client,
            auth_manager=auth_manager,
            config_entry=config_entry,
            update_interval=update_interval,
            logger=_LOGGER,
        )

        # Build state containers
        self._state = orchestrator.build_state_containers()

        # Build runtime context (unified dependency injection)
        context = RuntimeContext(
            get_device_by_id=self._get_device_by_id,
            apply_properties_update=self._apply_properties_update,
            schedule_listener_update=self._schedule_listener_update,
            request_refresh=self.async_request_refresh,
            trigger_reauth=self._trigger_reauth,
            is_mqtt_connected=self._is_mqtt_connected,
        )

        # Build runtime components
        self._runtimes = orchestrator.build_runtimes(
            context=context,
            state=self._state,
            force_connect_status_refresh_setter=self._set_force_connect_status_refresh,
        )

        # Initialize service layer
        self._init_service_layer()

    # RuntimeContext callback methods (injected into all runtimes)
    def _get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Get device by ID (RuntimeContext callback)."""
        return self._state.devices.get(device_id)

    async def _apply_properties_update(
        self, device: LiproDevice, properties: dict[str, Any], *, source: str
    ) -> None:
        """Apply properties update (RuntimeContext callback)."""
        await self._runtimes.state.apply_properties_update(device, properties, source=source)

    def _schedule_listener_update(self) -> None:
        """Schedule listener update (RuntimeContext callback)."""
        self.async_set_updated_data(self._state.devices)

    async def _trigger_reauth(self, reason: str) -> None:
        """Trigger re-authentication (RuntimeContext callback)."""
        _LOGGER.warning("Re-authentication required: %s", reason)
        self.config_entry.async_start_reauth(self.hass)

    def _is_mqtt_connected(self) -> bool:
        """Check MQTT connection status (RuntimeContext callback)."""
        return self._runtimes.mqtt.is_connected if self._runtimes.mqtt else False

    def _set_force_connect_status_refresh(self, value: bool) -> None:
        """Set force connect status refresh flag."""
        self._force_connect_status_refresh = value
    def _init_service_layer(self) -> None:
        """Initialize service layer that delegates to runtime components."""
        self.command_service = CoordinatorCommandService(self)
        self.device_refresh_service = CoordinatorDeviceRefreshService(self)
        self.mqtt_service = CoordinatorMqttService(self)
        self.state_service = CoordinatorStateService(self)

    # Public accessors for runtime components (used by service layer)
    @property
    def command_runtime(self):
        """Access command runtime (public API for services)."""
        return self._runtimes.command

    @property
    def device_runtime(self):
        """Access device runtime (public API for services)."""
        return self._runtimes.device

    @property
    def mqtt_runtime(self):
        """Access MQTT runtime (public API for services)."""
        return self._runtimes.mqtt

    @property
    def state_runtime(self):
        """Access state runtime (public API for services)."""
        return self._runtimes.state

    @property
    def status_runtime(self):
        """Access status runtime (public API for services)."""
        return self._runtimes.status

    @property
    def mqtt_client(self) -> LiproMqttClient | None:
        """Access MQTT client (public API for services)."""
        return self._state.mqtt_client

    @property
    def biz_id(self) -> str | None:
        """Access MQTT biz_id (public API for services)."""
        return self._state.biz_id

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Access device dictionary (public API for services)."""
        return self._state.devices

    # Public methods for entity integration
    def get_device(self, serial: str) -> LiproDevice | None:
        """Get device by serial number.

        Args:
            serial: Device serial number

        Returns:
            Device if found, None otherwise
        """
        return self.state_service.get_device(serial)

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Get device by any identifier (serial, iot_id, gateway_id, etc).

        Args:
            device_id: Device identifier

        Returns:
            Device if found, None otherwise
        """
        return self.state_service.get_device_by_id(device_id)

    def register_entity(self, entity: Any) -> None:
        """Register entity for debounce protection tracking.

        Args:
            entity: Entity to register
        """
        # Skip entities without entity_id
        if not entity.entity_id:
            return

        # Register in state runtime for debounce protection
        self._runtimes.state.register_entity(
            entity=entity,
            device_serial=entity.device.serial,
        )

        # Keep the entity index in sync with runtime state
        self._state.entities[entity.entity_id] = entity
        device_serial = entity.device.serial
        if device_serial not in self._state.entities_by_device:
            self._state.entities_by_device[device_serial] = []
        if entity not in self._state.entities_by_device[device_serial]:
            self._state.entities_by_device[device_serial].append(entity)

    def unregister_entity(self, entity: Any) -> None:
        """Unregister entity from debounce protection tracking.

        Args:
            entity: Entity to unregister
        """
        # Skip entities without entity_id
        if not entity.entity_id:
            return

        # Only unregister through the shared runtime if this is still
        # the active entity instance for the entity_id.
        should_unregister_from_runtime = self._state.entities.get(entity.entity_id) is entity
        if should_unregister_from_runtime:
            self._runtimes.state.unregister_entity(entity.entity_id)

        device_serial = entity.device.serial
        if device_serial in self._state.entities_by_device:
            with suppress(ValueError):
                self._state.entities_by_device[device_serial].remove(entity)
            if not self._state.entities_by_device[device_serial]:
                del self._state.entities_by_device[device_serial]

    def get_device_lock(self, device_serial: str) -> asyncio.Lock:
        """Get the lock for a specific device.

        This allows entities to use the same lock as the coordinator
        for device property updates, preventing race conditions.

        Args:
            device_serial: Device serial number

        Returns:
            Lock for the device
        """
        return self.state_service.get_device_lock(device_serial)

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
    ) -> bool:
        """Send command to device.

        Args:
            device: Target device
            command: Command name
            properties: Command properties

        Returns:
            True if command succeeded
        """
        return await self.command_service.async_send_command(
            device, command, properties
        )

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
        status_endpoint = getattr(self.client, "status", None)
        query_device_status = getattr(status_endpoint, "query_device_status", None)
        if query_device_status is None:
            rows = await self.client.query_device_status(device_ids)
        else:
            rows = await query_device_status(device_ids)

        status: dict[str, dict[str, Any]] = {}
        for row in rows:
            device_id: str | None = None
            for key in ("iotId", "deviceId", "id"):
                candidate = row.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    device_id = candidate
                    break
            if device_id is None:
                continue

            properties = row.get("properties")
            if isinstance(properties, dict):
                status[device_id] = dict(properties)
                continue

            status[device_id] = {
                key: value
                for key, value in row.items()
                if key not in {"iotId", "deviceId", "id"}
            }
        return status

    async def _apply_properties_update(
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
        return await self._runtimes.state.apply_properties_update(
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
        return self._runtimes.state.get_device_by_id(device_id)

    async def _async_ensure_authenticated(self) -> None:
        """Ensure coordinator authentication is valid."""
        await self.auth_manager.async_ensure_authenticated()

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

        This method delegates to the mqtt_lifecycle module for setup.

        Returns:
            True if setup succeeded, False otherwise
        """
        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False

        result = await setup_mqtt_lifecycle(
            hass=self.hass,
            client=self.client,
            config_entry=self.config_entry,
            state_runtime=self._runtimes.state,
            background_task_manager=self._state.background_task_manager,
            devices=self._state.devices,
            scan_interval_seconds=self._scan_interval_seconds,
            apply_properties_update=self._apply_properties_update,
            set_updated_data=self.async_set_updated_data,
        )

        if result is None:
            return False

        mqtt_runtime, mqtt_client, biz_id = result
        self._state.mqtt_client = mqtt_client
        self._state.biz_id = biz_id
        self._runtimes.mqtt = mqtt_runtime

        return True

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
                await self._async_ensure_authenticated()

                # Refresh device list if needed (10 seconds timeout)
                if self._runtimes.device.should_refresh_device_list():
                    async with asyncio.timeout(10):
                        snapshot = await self._runtimes.device.refresh_devices(force=True)
                        # Update coordinator devices from snapshot
                        self._state.devices.clear()
                        self._state.devices.update(snapshot.devices)

                # Schedule MQTT setup if needed (5 seconds timeout)
                if self._state.mqtt_client is None and self._state.devices:
                    async with asyncio.timeout(5):
                        await self.async_setup_mqtt()

            return self._state.devices

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


__all__ = ["Coordinator"]
