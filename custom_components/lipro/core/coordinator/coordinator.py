"""Native coordinator runtime for the Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from contextlib import suppress
from datetime import timedelta
import logging
from types import MappingProxyType
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..protocol import LiproProtocolFacade
from .lifecycle import (
    async_refresh_snapshot_if_needed as coordinator_async_refresh_snapshot_if_needed,
    async_run_status_polling_if_needed as coordinator_async_run_status_polling_if_needed,
    async_run_update_cycle as coordinator_async_run_update_cycle,
    async_setup_mqtt as coordinator_async_setup_mqtt,
    async_setup_mqtt_if_needed as coordinator_async_setup_mqtt_if_needed,
    async_shutdown as coordinator_async_shutdown,
    async_update_data as coordinator_async_update_data,
)
from .orchestrator import RuntimeOrchestrator
from .runtime_context import RuntimeContext
from .services import (
    CoordinatorAuthService,
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorPollingService,
    CoordinatorProtocolService,
    CoordinatorSignalService,
    CoordinatorStateService,
    CoordinatorTelemetryService,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from .entity_protocol import LiproEntityProtocol
    from .types import PropertyDict

_LOGGER = logging.getLogger(__name__)


class Coordinator(DataUpdateCoordinator[dict[str, "LiproDevice"]]):
    """Coordinator runtime built from explicit runtime context and owned services."""

    def __init__(
        self,
        hass: HomeAssistant,
        protocol: LiproProtocolFacade,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator runtime.

        Args:
            hass: Home Assistant instance
            protocol: Formal protocol facade
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
        self.protocol = protocol
        self.auth_manager = auth_manager
        self.config_entry = config_entry
        self._config_entry = config_entry
        self._scan_interval_seconds = int(update_interval)

        # Build runtime components via orchestrator
        orchestrator = RuntimeOrchestrator(
            hass=hass,
            protocol=protocol,
            auth_manager=auth_manager,
            config_entry=config_entry,
            update_interval=update_interval,
            logger=_LOGGER,
        )

        # Build state containers
        self._state = orchestrator.build_state_containers()

        # Formal runtime service surfaces
        self.auth_service = CoordinatorAuthService(
            hass=hass,
            auth_manager=auth_manager,
            config_entry=config_entry,
        )
        self.protocol_service = CoordinatorProtocolService(
            protocol_getter=lambda: self.protocol,
        )

        self.signal_service = CoordinatorSignalService(
            telemetry_service_getter=lambda: self.telemetry_service,
            device_refresh_service_getter=lambda: self.device_refresh_service,
        )

        # Build runtime context (unified dependency injection)
        context = RuntimeContext(
            get_device_by_id=self._get_device_by_id,
            apply_properties_update=self._apply_properties_update,
            schedule_listener_update=self._schedule_listener_update,
            record_connect_state=self.signal_service,
            request_group_reconciliation=self.signal_service,
            request_refresh=self.async_request_refresh,
            trigger_reauth=self.auth_service.async_trigger_reauth,
            is_mqtt_connected=self._is_mqtt_connected,
        )

        # Build runtime components
        self._runtimes = orchestrator.build_runtimes(
            context=context,
            state=self._state,
            polling_updater=self,
        )

        # Initialize service layer
        self._init_service_layer()

    # RuntimeContext callback methods (injected into all runtimes)
    def _get_device_by_id(self, device_id: str) -> LiproDevice | None:
        """Get device by any known identifier (RuntimeContext callback)."""
        if hasattr(self, "_runtimes"):
            return self._runtimes.state.get_device_by_id(device_id)
        return self._state.device_identity_index.get(device_id)

    async def _apply_properties_update(
        self,
        device: LiproDevice,
        properties: PropertyDict,
        source: str,
    ) -> bool:
        """Apply properties update after reconciling pending command expectations."""
        filtered_properties = self._runtimes.command.filter_pending_state_properties(
            device_serial=device.serial,
            properties=properties,
        )
        if not filtered_properties:
            return False

        self._runtimes.command.observe_state_confirmation(
            device_serial=device.serial,
            properties=filtered_properties,
        )
        return await self._runtimes.state.apply_properties_update(
            device,
            filtered_properties,
            source=source,
        )

    def _schedule_listener_update(self) -> None:
        """Schedule listener update (RuntimeContext callback)."""
        self.async_set_updated_data(dict(self._state.devices))

    def _is_mqtt_connected(self) -> bool:
        """Check MQTT connection status (RuntimeContext callback)."""
        return self._runtimes.mqtt.is_connected

    def update_polling_interval(self, interval: timedelta) -> None:
        """Apply one coordinator polling interval update requested by MQTT runtime."""
        self.update_interval = interval

    def _replace_devices(self, devices: dict[str, LiproDevice]) -> None:
        """Replace the canonical device registry in place to preserve shared references."""
        self._state.devices.clear()
        self._state.devices.update(devices)

    def _init_service_layer(self) -> None:
        """Initialize formal runtime service surfaces."""
        self.command_service = CoordinatorCommandService(
            command_runtime=self._runtimes.command,
            tuning_runtime=self._runtimes.tuning,
        )
        self.mqtt_service = CoordinatorMqttService(
            devices_getter=lambda: self._state.devices,
            mqtt_runtime_getter=lambda: self._runtimes.mqtt,
            setup_callback=self.async_setup_mqtt,
        )
        self.state_service = CoordinatorStateService(state_runtime=self._runtimes.state)
        self._polling_service = CoordinatorPollingService(
            device_runtime=self._runtimes.device,
            status_runtime=self._runtimes.status,
            tuning_runtime=self._runtimes.tuning,
            protocol_service=self.protocol_service,
            mqtt_service=self.mqtt_service,
            devices_getter=lambda: self._state.devices,
            replace_devices=self._replace_devices,
            publish_updated_data=lambda devices: self.async_set_updated_data(devices),
            get_device_by_id=self.get_device_by_id,
            has_mqtt_transport_getter=lambda: self._runtimes.mqtt.has_transport,
            logger=_LOGGER,
        )
        self.device_refresh_service = CoordinatorDeviceRefreshService(
            device_runtime=self._runtimes.device,
            state_runtime=self._runtimes.state,
            refresh_callback=self.async_refresh_devices,
        )
        self.telemetry_service = CoordinatorTelemetryService(
            mqtt_service=self.mqtt_service,
            command_runtime=self._runtimes.command,
            status_runtime=self._runtimes.status,
            tuning_runtime=self._runtimes.tuning,
            mqtt_runtime_getter=lambda: self._runtimes.mqtt,
            device_count_getter=lambda: len(self._state.devices),
            polling_interval_seconds_getter=lambda: (
                int(self.update_interval.total_seconds())
                if self.update_interval is not None
                else None
            ),
        )

    @property
    def devices(self) -> Mapping[str, LiproDevice]:
        """Return the canonical runtime device registry view."""
        return MappingProxyType(self._state.devices)

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

    def register_entity(self, entity: LiproEntityProtocol) -> None:
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

    def unregister_entity(self, entity: LiproEntityProtocol) -> None:
        """Unregister entity from debounce protection tracking.

        Args:
            entity: Entity to unregister
        """
        # Skip entities without entity_id
        if not entity.entity_id:
            return

        # Only unregister through the shared runtime if this is still
        # the active entity instance for the entity_id.
        should_unregister_from_runtime = (
            self._state.entities.get(entity.entity_id) is entity
        )
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
        success = await self.command_service.async_send_command(
            device, command, properties
        )
        if success:
            return True

        last_failure = self.command_service.last_failure
        if isinstance(last_failure, dict):
            error_type = last_failure.get("error")
            if error_type == "LiproRefreshTokenExpiredError":
                raise ConfigEntryAuthFailed("auth_expired")
            if error_type == "LiproAuthError":
                raise ConfigEntryAuthFailed("auth_error")

        return False

    async def async_refresh_devices(self) -> dict[str, LiproDevice]:
        """Force a full device snapshot refresh and publish the latest state."""
        return await self._polling_service.async_refresh_devices()

    def _get_outlet_ids_for_power_polling(self) -> list[str]:
        """Resolve the current outlet IDs participating in power polling."""
        return self._polling_service.get_outlet_ids_for_power_polling()

    async def _async_run_outlet_power_polling(self) -> None:
        """Refresh outlet power info on the coordinator's scheduled main path."""
        await self._polling_service.async_run_outlet_power_polling()

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates."""
        return await coordinator_async_setup_mqtt(
            protocol=self.protocol,
            config_entry=self.config_entry,
            devices=self._state.devices,
            background_task_manager=self._state.background_task_manager,
            mqtt_runtime=self._runtimes.mqtt,
        )

    async def async_shutdown(self) -> None:
        """Release coordinator-owned MQTT and background resources."""
        await coordinator_async_shutdown(
            protocol=self.protocol,
            mqtt_runtime=self._runtimes.mqtt,
            device_runtime=self._runtimes.device,
            background_task_manager=self._state.background_task_manager,
            shutdown_command_service=self.command_service.async_shutdown,
        )
        await super().async_shutdown()

    async def _async_refresh_device_snapshot(
        self,
        *,
        force: bool,
        mqtt_timeout_seconds: float | None = None,
    ) -> None:
        """Refresh device snapshot, synchronize coordinator state, and sync MQTT."""
        await self._polling_service.async_refresh_device_snapshot(
            force=force,
            mqtt_timeout_seconds=mqtt_timeout_seconds,
        )

    async def _async_run_status_polling(self) -> None:
        """Run adaptive REST status polling via StatusRuntime."""
        await self._polling_service.async_run_status_polling()

    async def _async_refresh_snapshot_if_needed(self) -> None:
        """Refresh the canonical device snapshot when runtime policy requests it."""
        await coordinator_async_refresh_snapshot_if_needed(
            should_refresh_device_list=self._runtimes.device.should_refresh_device_list,
            refresh_device_snapshot=lambda: self._async_refresh_device_snapshot(
                force=True,
                mqtt_timeout_seconds=5,
            ),
        )

    async def _async_setup_mqtt_if_needed(self) -> None:
        """Attach MQTT transport when devices exist and no transport is bound yet."""
        await coordinator_async_setup_mqtt_if_needed(
            has_transport=self._runtimes.mqtt.has_transport,
            has_devices=bool(self._state.devices),
            setup_mqtt=self.async_setup_mqtt,
        )

    async def _async_run_status_polling_if_needed(self) -> None:
        """Run adaptive status polling only when devices are currently tracked."""
        await coordinator_async_run_status_polling_if_needed(
            has_devices=bool(self._state.devices),
            run_status_polling=self._async_run_status_polling,
        )

    async def _async_run_update_cycle(self) -> None:
        """Run the coordinator's scheduled update stages inside the global timeout."""
        await coordinator_async_run_update_cycle(
            ensure_authenticated=self.auth_service.async_ensure_authenticated,
            refresh_snapshot_if_needed=self._async_refresh_snapshot_if_needed,
            setup_mqtt_if_needed=self._async_setup_mqtt_if_needed,
            run_status_polling_if_needed=self._async_run_status_polling_if_needed,
        )

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API for one scheduled update cycle."""
        return await coordinator_async_update_data(
            run_update_cycle=self._async_run_update_cycle,
            telemetry_service=self.telemetry_service,
            devices=self._state.devices,
        )


__all__ = ["Coordinator"]
