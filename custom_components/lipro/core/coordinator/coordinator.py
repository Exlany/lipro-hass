"""Native coordinator runtime for the Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import timedelta
import logging
from types import MappingProxyType
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..protocol import LiproProtocolFacade
from .lifecycle import (
    async_setup_mqtt as coordinator_async_setup_mqtt,
    async_shutdown as coordinator_async_shutdown,
)
from .orchestrator import RuntimeOrchestrator
from .runtime_wiring import (
    build_runtime_context,
    build_update_cycle,
    initialize_service_layer,
)
from .services import (
    CoordinatorAuthService,
    CoordinatorCommandService,
    CoordinatorProtocolService,
    CoordinatorSignalService,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from .entity_protocol import LiproEntityProtocol
    from .types import PropertyDict

_LOGGER = logging.getLogger(__name__)

# Preserve the historical patch seam for focused runtime-root tests.
_PATCHABLE_RUNTIME_SERVICE_TYPES = (CoordinatorCommandService,)


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

        # Build runtime components
        self._runtimes = orchestrator.build_runtimes(
            context=build_runtime_context(
                get_device_by_id=self._get_device_by_id,
                apply_properties_update=self._apply_properties_update,
                schedule_listener_update=self._schedule_listener_update,
                signal_service=self.signal_service,
                request_refresh=self.async_request_refresh,
                trigger_reauth=self.auth_service.async_trigger_reauth,
                is_mqtt_connected=self._is_mqtt_connected,
            ),
            state=self._state,
            polling_updater=self,
        )

        service_layer = initialize_service_layer(
            runtimes=self._runtimes,
            state=self._state,
            protocol_service=self.protocol_service,
            async_setup_mqtt=self.async_setup_mqtt,
            replace_devices=self._replace_devices,
            publish_updated_data=lambda devices: self.async_set_updated_data(devices),
            get_device_by_id=self.get_device_by_id,
            async_refresh_devices=self.async_refresh_devices,
            update_interval_seconds_getter=lambda: (
                int(self.update_interval.total_seconds())
                if self.update_interval is not None
                else None
            ),
            logger=_LOGGER,
        )
        self.command_service = service_layer.command_service
        self.mqtt_service = service_layer.mqtt_service
        self.state_service = service_layer.state_service
        self._polling_service = service_layer.polling_service
        self.device_refresh_service = service_layer.device_refresh_service
        self.telemetry_service = service_layer.telemetry_service
        self._update_cycle = build_update_cycle(
            ensure_authenticated=self.auth_service.async_ensure_authenticated,
            should_refresh_device_list=self._runtimes.device.should_refresh_device_list,
            refresh_device_snapshot=lambda: self._async_refresh_device_snapshot(
                force=True,
                mqtt_timeout_seconds=5,
            ),
            has_mqtt_transport=lambda: self._runtimes.mqtt.has_transport,
            has_devices=lambda: bool(self._state.devices),
            setup_mqtt=self.async_setup_mqtt,
            run_status_polling=self._async_run_status_polling,
            telemetry_service=self.telemetry_service,
            devices_getter=lambda: self._state.devices,
        )

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
        """Register entity for debounce protection tracking."""
        if not entity.entity_id:
            return

        self._runtimes.state.register_entity(
            entity=entity,
            device_serial=entity.device.serial,
        )

    def unregister_entity(self, entity: LiproEntityProtocol) -> None:
        """Unregister entity from debounce protection tracking."""
        if not entity.entity_id:
            return

        self._runtimes.state.unregister_entity_instance(entity)

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

        failure_summary = self.command_service.last_failure
        reauth_reason = (
            failure_summary.get("reauth_reason")
            if isinstance(failure_summary, dict)
            else None
        )
        if isinstance(reauth_reason, str) and reauth_reason:
            raise ConfigEntryAuthFailed(reauth_reason)

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

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API for one scheduled update cycle."""
        return await self._update_cycle.async_update_data()


__all__ = ["Coordinator"]
