"""Native coordinator runtime for the Lipro integration."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from contextlib import suppress
from datetime import timedelta
import logging
from types import MappingProxyType
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ...const.config import DEFAULT_SCAN_INTERVAL
from ..api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from ..protocol import LiproProtocolFacade
from .mqtt.setup import build_mqtt_subscription_device_ids
from .mqtt_lifecycle import async_setup_mqtt as setup_mqtt_lifecycle
from .orchestrator import RuntimeOrchestrator
from .outlet_power import apply_outlet_power_info, should_reraise_outlet_power_error
from .runtime.device.snapshot import RuntimeSnapshotRefreshRejectedError
from .runtime.outlet_power_runtime import query_outlet_power
from .runtime_context import RuntimeContext
from .services import (
    CoordinatorAuthService,
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
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
    from .types import PropertyDict, StatusQueryMetrics

_LOGGER = logging.getLogger(__name__)


async def _async_run_best_effort_shutdown_step(
    *,
    label: str,
    operation: Callable[[], Awaitable[object]],
) -> None:
    """Run one shutdown step with explicit best-effort semantics."""
    try:
        await operation()
    except asyncio.CancelledError:
        raise
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning(
            "%s failed during best-effort shutdown (%s)",
            label,
            type(err).__name__,
        )


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

    def _init_service_layer(self) -> None:
        """Initialize formal runtime service surfaces."""
        self.command_service = CoordinatorCommandService(
            command_runtime=self._runtimes.command,
            tuning_runtime=self._runtimes.tuning,
        )
        self.device_refresh_service = CoordinatorDeviceRefreshService(
            device_runtime=self._runtimes.device,
            state_runtime=self._runtimes.state,
            refresh_callback=self.async_refresh_devices,
        )
        self.mqtt_service = CoordinatorMqttService(
            devices_getter=lambda: self._state.devices,
            mqtt_runtime_getter=lambda: self._runtimes.mqtt,
            setup_callback=self.async_setup_mqtt,
        )
        self.state_service = CoordinatorStateService(state_runtime=self._runtimes.state)
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
        """Return one read-only view of the runtime device registry."""
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
        return await self.command_service.async_send_command(
            device, command, properties
        )

    async def async_refresh_devices(self) -> dict[str, LiproDevice]:
        """Force a full device snapshot refresh and publish the latest state."""
        await self._async_refresh_device_snapshot(force=True, mqtt_timeout_seconds=5)
        refreshed_devices = dict(self._state.devices)
        self.async_set_updated_data(refreshed_devices)
        return refreshed_devices


    def _get_outlet_ids_for_power_polling(self) -> list[str]:
        """Resolve the current outlet IDs participating in power polling."""
        snapshot = self._runtimes.device.get_last_snapshot()
        if snapshot is not None and snapshot.outlet_ids:
            return list(snapshot.outlet_ids)
        return [
            device.iot_device_id
            for device in self._state.devices.values()
            if device.capabilities.is_outlet and device.iot_device_id
        ]

    async def _async_run_outlet_power_polling(self) -> None:
        """Refresh outlet power info on the coordinator's scheduled main path."""
        status_runtime = self._runtimes.status
        if not status_runtime.should_query_power():
            return

        outlet_ids = self._get_outlet_ids_for_power_polling()
        if not outlet_ids:
            return

        outlet_ids_to_query = status_runtime.get_outlet_power_query_slice(outlet_ids)
        if not outlet_ids_to_query:
            return

        await query_outlet_power(
            outlet_ids_to_query=outlet_ids_to_query,
            round_robin_index=0,
            resolve_cycle_size=lambda total_devices: total_devices,
            fetch_outlet_power_info=self.protocol_service.async_fetch_outlet_power_info,
            get_device_by_id=lambda device_id: (
                self.get_device_by_id(device_id) if isinstance(device_id, str) else None
            ),
            apply_outlet_power_info=apply_outlet_power_info,
            should_reraise_outlet_power_error=should_reraise_outlet_power_error,
            logger=_LOGGER,
            concurrency=max(1, min(3, len(outlet_ids_to_query))),
        )
        status_runtime.mark_power_query_complete()
        status_runtime.advance_outlet_power_cycle(outlet_ids)

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates.

        This method delegates to the mqtt_lifecycle module for setup.

        Returns:
            True if setup succeeded, False otherwise
        """
        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False

        device_ids = build_mqtt_subscription_device_ids(self._state.devices)
        if not device_ids:
            return False

        mqtt_runtime = self._runtimes.mqtt
        if mqtt_runtime.has_transport:
            if mqtt_runtime.is_connected:
                await mqtt_runtime.sync_subscriptions(device_ids)
                return True
            return await mqtt_runtime.connect(device_ids=device_ids)

        result = await setup_mqtt_lifecycle(
            protocol=self.protocol,
            config_entry=self.config_entry,
            background_task_manager=self._state.background_task_manager,
            devices=self._state.devices,
            mqtt_runtime=mqtt_runtime,
        )
        return result is not None

    async def async_shutdown(self) -> None:
        """Release coordinator-owned MQTT and background resources."""
        await _async_run_best_effort_shutdown_step(
            label="MQTT disconnect notification cleanup",
            operation=self._runtimes.mqtt.clear_disconnect_notification,
        )
        await _async_run_best_effort_shutdown_step(
            label="Command service shutdown",
            operation=self.command_service.async_shutdown,
        )
        await _async_run_best_effort_shutdown_step(
            label="MQTT runtime shutdown",
            operation=self._runtimes.mqtt.disconnect,
        )
        await _async_run_best_effort_shutdown_step(
            label="Background task shutdown",
            operation=self._state.background_task_manager.cancel_all,
        )

        self.protocol.attach_mqtt_facade(None)
        self._runtimes.mqtt.detach_transport()
        self._runtimes.mqtt.reset()
        self._runtimes.device.reset()
        await super().async_shutdown()

    async def _async_refresh_device_snapshot(
        self,
        *,
        force: bool,
        mqtt_timeout_seconds: float | None = None,
    ) -> None:
        """Refresh device snapshot, synchronize coordinator state, and sync MQTT."""
        snapshot = await self._runtimes.device.refresh_devices(force=force)
        self._state.devices.clear()
        self._state.devices.update(snapshot.devices)

        if not self._runtimes.mqtt.has_transport:
            return

        if mqtt_timeout_seconds is None:
            await self.mqtt_service.async_sync_subscriptions()
            return

        async with asyncio.timeout(mqtt_timeout_seconds):
            await self.mqtt_service.async_sync_subscriptions()

    async def _async_run_status_polling(self) -> None:
        """Run adaptive REST status polling via StatusRuntime.

        This supplements MQTT push with periodic REST polling to:
        - Catch state drift when MQTT messages are missed
        - Query devices that lack MQTT support
        - Monitor outlet power consumption on a scheduled cycle

        The StatusRuntime handles candidate filtering, batching, and parallel
        execution. TuningRuntime receives batch metrics for adaptive tuning.
        """
        status_runtime = self._runtimes.status
        mqtt_connected = self._is_mqtt_connected()
        device_ids = list(self._state.devices.keys())

        # Filter to devices needing REST query (respects MQTT freshness)
        candidates = status_runtime.filter_query_candidates(
            self._state.devices,
            device_ids,
            mqtt_connected=mqtt_connected,
        )

        results: list[StatusQueryMetrics] = []
        if candidates:
            # Split into optimally-sized batches
            batches = status_runtime.compute_query_batches(candidates)

            if batches:
                # Execute queries in parallel
                results = await status_runtime.execute_parallel_queries(batches)

        # Feed metrics to TuningRuntime for adaptive batch sizing
        tuning = self._runtimes.tuning
        for metrics in results:
            device_count = metrics.get("device_count", 0)
            duration = metrics.get("duration", 0.0)
            if device_count > 0 and duration > 0:
                tuning.record_batch_metric(
                    batch_size=device_count,
                    duration=duration,
                    device_count=device_count,
                )

        # Apply adaptive batch size from TuningRuntime
        new_batch_size = tuning.compute_adaptive_batch_size()
        if new_batch_size is not None:
            status_runtime.update_batch_size(new_batch_size)

        await self._async_run_outlet_power_polling()

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
                await self.auth_service.async_ensure_authenticated()

                # Refresh device list if needed (10 seconds timeout)
                if self._runtimes.device.should_refresh_device_list():
                    async with asyncio.timeout(10):
                        await self._async_refresh_device_snapshot(
                            force=True,
                            mqtt_timeout_seconds=5,
                        )

                # Schedule MQTT setup if needed (5 seconds timeout)
                if not self._runtimes.mqtt.has_transport and self._state.devices:
                    async with asyncio.timeout(5):
                        await self.async_setup_mqtt()

                # Run adaptive status polling.
                if self._state.devices:
                    async with asyncio.timeout(10):
                        await self._async_run_status_polling()

            self.telemetry_service.record_update_success()
            return self._state.devices

        except asyncio.CancelledError:
            raise
        except TimeoutError:
            self.telemetry_service.record_update_failure(
                TimeoutError("Update timeout"),
                stage="timeout",
            )
            _LOGGER.error("Update data timeout after 30 seconds")
            raise UpdateFailed("Update timeout") from None

        except (
            LiproRefreshTokenExpiredError,
            LiproAuthError,
        ) as err:
            self.telemetry_service.record_update_failure(err, stage="auth")
            _LOGGER.error("Authentication failed: %s", err)
            error_message = f"Authentication failed: {err}"
            raise ConfigEntryAuthFailed(error_message) from err

        except (
            LiproConnectionError,
            LiproApiError,
        ) as err:
            self.telemetry_service.record_update_failure(err, stage="protocol")
            _LOGGER.error("Update failed: %s", err)
            error_message = f"Update failed: {err}"
            raise UpdateFailed(error_message) from err

        except RuntimeSnapshotRefreshRejectedError as err:
            self.telemetry_service.record_update_failure(err, stage="runtime")
            _LOGGER.warning("Device snapshot refresh rejected: %s", err)
            raise UpdateFailed(str(err)) from err

        except Exception as err:
            self.telemetry_service.record_update_failure(err, stage="unexpected")
            _LOGGER.exception("Unexpected update failure")
            raise UpdateFailed("Unexpected update failure") from err


__all__ = ["Coordinator"]
