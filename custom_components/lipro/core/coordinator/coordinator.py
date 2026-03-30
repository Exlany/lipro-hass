"""Native coordinator runtime for the Lipro integration."""

from __future__ import annotations

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
from .services import CoordinatorCommandService

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..api.types import OtaInfoRow
    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from .entity_protocol import LiproEntityProtocol
    from .factory import CoordinatorBootstrapArtifact
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
        self._bind_runtime_dependencies(
            protocol=protocol,
            auth_manager=auth_manager,
            config_entry=config_entry,
            update_interval=update_interval,
        )
        self._bind_bootstrap_artifact(
            self._build_runtime_bootstrap(
                self._build_runtime_orchestrator(
                    hass=hass,
                    protocol=protocol,
                    auth_manager=auth_manager,
                    config_entry=config_entry,
                    update_interval=update_interval,
                )
            )
        )

    def _bind_runtime_dependencies(
        self,
        *,
        protocol: LiproProtocolFacade,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int,
    ) -> None:
        """Bind direct runtime dependencies owned by the coordinator root."""
        self.protocol = protocol
        self.auth_manager = auth_manager
        self.config_entry = config_entry
        self._config_entry = config_entry
        self._scan_interval_seconds = int(update_interval)

    def _build_runtime_orchestrator(
        self,
        *,
        hass: HomeAssistant,
        protocol: LiproProtocolFacade,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int,
    ) -> RuntimeOrchestrator:
        """Build the runtime orchestrator responsible for collaborator assembly."""
        return RuntimeOrchestrator(
            hass=hass,
            protocol=protocol,
            auth_manager=auth_manager,
            config_entry=config_entry,
            update_interval=update_interval,
            logger=_LOGGER,
        )

    def _build_runtime_bootstrap(
        self,
        orchestrator: RuntimeOrchestrator,
    ) -> CoordinatorBootstrapArtifact:
        """Build the coordinator bootstrap artifact using the stable runtime patch seam."""
        return orchestrator.build_bootstrap_artifact(
            get_device_by_id=self._get_device_by_id,
            apply_properties_update=self._apply_properties_update,
            schedule_listener_update=self._schedule_listener_update,
            request_refresh=self.async_request_refresh,
            is_mqtt_connected=self._is_mqtt_connected,
            async_setup_mqtt=self.async_setup_mqtt,
            replace_devices=self._replace_devices,
            publish_updated_data=self.async_set_updated_data,
            async_refresh_devices=self.async_refresh_devices,
            update_interval_seconds_getter=self._get_update_interval_seconds,
            run_status_polling=self._async_run_status_polling,
            refresh_device_snapshot=self._async_force_refresh_device_snapshot,
            polling_updater=self,
        )

    def _bind_bootstrap_artifact(self, bootstrap: CoordinatorBootstrapArtifact) -> None:
        """Bind the assembled runtime artifact onto the coordinator root."""
        self._state = bootstrap.state
        self._runtimes = bootstrap.runtimes
        self.auth_service = bootstrap.support_services.auth_service
        self.protocol_service = bootstrap.support_services.protocol_service
        self.signal_service = bootstrap.support_services.signal_service
        self.command_service = bootstrap.service_layer.command_service
        self.mqtt_service = bootstrap.service_layer.mqtt_service
        self.state_service = bootstrap.service_layer.state_service
        self._polling_service = bootstrap.service_layer.polling_service
        self.schedule_service = bootstrap.service_layer.schedule_service
        self.device_refresh_service = bootstrap.service_layer.device_refresh_service
        self.telemetry_service = bootstrap.service_layer.telemetry_service
        self._update_cycle = bootstrap.update_cycle

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

    def _get_update_interval_seconds(self) -> int | None:
        """Return the current polling interval in seconds for service consumers."""
        if self.update_interval is None:
            return None
        return int(self.update_interval.total_seconds())

    async def _async_force_refresh_device_snapshot(self) -> None:
        """Refresh the canonical device snapshot using coordinator root policy."""
        await self._async_refresh_device_snapshot(force=True, mqtt_timeout_seconds=5)

    @property
    def devices(self) -> Mapping[str, LiproDevice]:
        """Return the canonical runtime device registry view."""
        return MappingProxyType(self._state.devices)

    # Public methods for entity integration
    def iter_devices(self) -> tuple[LiproDevice, ...]:
        """Return a stable iterable of the current runtime devices."""
        return tuple(self.devices.values())

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

    async def async_apply_optimistic_state(
        self,
        device: LiproDevice,
        properties: Mapping[str, object],
    ) -> None:
        """Apply one optimistic property projection using runtime-owned locking."""
        if not properties:
            return

        device_lock = self.state_service.get_device_lock(device.serial)
        async with device_lock:
            device.update_properties(dict(properties))

    async def async_query_device_ota_info(
        self,
        device: LiproDevice,
        *,
        allow_rich_v2_fallback: bool | None = None,
    ) -> list[OtaInfoRow]:
        """Query OTA metadata for one device through the formal runtime verb."""
        return await self.protocol_service.async_query_ota_info(
            device_id=device.serial,
            device_type=device.device_type_hex,
            iot_name=device.iot_name or None,
            allow_rich_v2_fallback=(
                device.capabilities.is_light
                if allow_rich_v2_fallback is None
                else allow_rich_v2_fallback
            ),
        )

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
