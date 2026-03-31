"""Runtime orchestrator for coordinator collaborators."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import TYPE_CHECKING

from .factory import (
    CoordinatorBootstrapArtifact,
    CoordinatorRuntimes,
    CoordinatorStateContainers,
)
from .lifecycle import CoordinatorUpdateCycle
from .orchestrator_runtime_builders import (
    BootstrapAssembly,
    BootstrapCallbacks,
    RuntimeCollaboratorBuilder,
)
from .runtime_context import RuntimeContext
from .runtime_wiring import (
    CoordinatorServiceLayer,
    CoordinatorSupportServices,
    build_runtime_context,
    build_update_cycle,
    initialize_service_layer,
    initialize_support_services,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from ..protocol import LiproProtocolFacade
    from .runtime.mqtt.connection import PollingIntervalUpdater
    from .types import PropertyDict


class RuntimeOrchestrator:
    """Orchestrates runtime component initialization with unified context."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        protocol: LiproProtocolFacade,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int,
        logger: logging.Logger,
    ) -> None:
        """Initialize orchestrator with external dependencies."""
        self.hass = hass
        self.protocol = protocol
        self.auth_manager = auth_manager
        self.config_entry = config_entry
        self.logger = logger
        self._builders = RuntimeCollaboratorBuilder(
            hass=hass,
            protocol=protocol,
            auth_manager=auth_manager,
            config_entry=config_entry,
            update_interval=update_interval,
            logger=logger,
        )

    def _build_support_services(
        self,
        *,
        service_layer_ref: dict[str, CoordinatorServiceLayer],
    ) -> CoordinatorSupportServices:
        support_services = initialize_support_services(
            hass=self.hass,
            protocol=self.protocol,
            auth_manager=self.auth_manager,
            config_entry=self.config_entry,
            telemetry_service_getter=lambda: (
                service_layer_ref["value"].telemetry_service
            ),
            device_refresh_service_getter=lambda: (
                service_layer_ref["value"].device_refresh_service
            ),
        )
        _ = support_services.signal_service
        return support_services

    def _build_runtime_context(
        self,
        *,
        get_device_by_id: Callable[[str], LiproDevice | None],
        apply_properties_update: Callable[
            [LiproDevice, PropertyDict, str], Awaitable[bool]
        ],
        schedule_listener_update: Callable[[], None],
        request_refresh: Callable[[], Awaitable[None]],
        is_mqtt_connected: Callable[[], bool],
        support_services: CoordinatorSupportServices,
    ) -> RuntimeContext:
        return build_runtime_context(
            get_device_by_id=get_device_by_id,
            apply_properties_update=apply_properties_update,
            schedule_listener_update=schedule_listener_update,
            signal_service=support_services.signal_service,
            request_refresh=request_refresh,
            trigger_reauth=support_services.auth_service.async_trigger_reauth,
            is_mqtt_connected=is_mqtt_connected,
        )

    def _build_update_cycle_artifact(
        self,
        *,
        support_services: CoordinatorSupportServices,
        runtimes: CoordinatorRuntimes,
        state: CoordinatorStateContainers,
        service_layer: CoordinatorServiceLayer,
        async_setup_mqtt: Callable[[], Awaitable[bool]],
        run_status_polling: Callable[[], Awaitable[None]],
        refresh_device_snapshot: Callable[[], Awaitable[None]],
    ) -> CoordinatorUpdateCycle:
        return build_update_cycle(
            ensure_authenticated=support_services.auth_service.async_ensure_authenticated,
            should_refresh_device_list=runtimes.device.should_refresh_device_list,
            refresh_device_snapshot=refresh_device_snapshot,
            has_mqtt_transport=lambda: runtimes.mqtt.has_transport,
            has_devices=lambda: bool(state.devices),
            setup_mqtt=async_setup_mqtt,
            run_status_polling=run_status_polling,
            telemetry_service=service_layer.telemetry_service,
            devices_getter=lambda: state.devices,
        )

    def _build_service_layer(
        self,
        *,
        runtimes: CoordinatorRuntimes,
        state: CoordinatorStateContainers,
        support_services: CoordinatorSupportServices,
        async_setup_mqtt: Callable[[], Awaitable[bool]],
        replace_devices: Callable[[dict[str, LiproDevice]], None],
        publish_updated_data: Callable[[dict[str, LiproDevice]], None],
        get_device_by_id: Callable[[str], LiproDevice | None],
        async_refresh_devices: Callable[[], Awaitable[dict[str, LiproDevice]]],
        update_interval_seconds_getter: Callable[[], int | None],
    ) -> CoordinatorServiceLayer:
        return initialize_service_layer(
            runtimes=runtimes,
            state=state,
            protocol_service=support_services.protocol_service,
            async_setup_mqtt=async_setup_mqtt,
            replace_devices=replace_devices,
            publish_updated_data=publish_updated_data,
            get_device_by_id=get_device_by_id,
            async_refresh_devices=async_refresh_devices,
            update_interval_seconds_getter=update_interval_seconds_getter,
            logger=self.logger,
        )

    def _build_bootstrap_callbacks(
        self,
        *,
        get_device_by_id: Callable[[str], LiproDevice | None],
        apply_properties_update: Callable[
            [LiproDevice, PropertyDict, str], Awaitable[bool]
        ],
        schedule_listener_update: Callable[[], None],
        request_refresh: Callable[[], Awaitable[None]],
        is_mqtt_connected: Callable[[], bool],
        async_setup_mqtt: Callable[[], Awaitable[bool]],
        replace_devices: Callable[[dict[str, LiproDevice]], None],
        publish_updated_data: Callable[[dict[str, LiproDevice]], None],
        async_refresh_devices: Callable[[], Awaitable[dict[str, LiproDevice]]],
        update_interval_seconds_getter: Callable[[], int | None],
        run_status_polling: Callable[[], Awaitable[None]],
        refresh_device_snapshot: Callable[[], Awaitable[None]],
        polling_updater: PollingIntervalUpdater,
    ) -> BootstrapCallbacks:
        return BootstrapCallbacks(
            get_device_by_id=get_device_by_id,
            apply_properties_update=apply_properties_update,
            schedule_listener_update=schedule_listener_update,
            request_refresh=request_refresh,
            is_mqtt_connected=is_mqtt_connected,
            async_setup_mqtt=async_setup_mqtt,
            replace_devices=replace_devices,
            publish_updated_data=publish_updated_data,
            async_refresh_devices=async_refresh_devices,
            update_interval_seconds_getter=update_interval_seconds_getter,
            run_status_polling=run_status_polling,
            refresh_device_snapshot=refresh_device_snapshot,
            polling_updater=polling_updater,
        )

    def _assemble_bootstrap(
        self,
        *,
        callbacks: BootstrapCallbacks,
    ) -> BootstrapAssembly:
        state = self._builders.build_state_containers()
        service_layer_ref: dict[str, CoordinatorServiceLayer] = {}
        support_services = self._build_support_services(
            service_layer_ref=service_layer_ref
        )
        runtimes = self._builders.build_runtimes(
            context=self._build_runtime_context(
                get_device_by_id=callbacks.get_device_by_id,
                apply_properties_update=callbacks.apply_properties_update,
                schedule_listener_update=callbacks.schedule_listener_update,
                request_refresh=callbacks.request_refresh,
                is_mqtt_connected=callbacks.is_mqtt_connected,
                support_services=support_services,
            ),
            state=state,
            polling_updater=callbacks.polling_updater,
        )
        service_layer = self._build_service_layer(
            runtimes=runtimes,
            state=state,
            support_services=support_services,
            async_setup_mqtt=callbacks.async_setup_mqtt,
            replace_devices=callbacks.replace_devices,
            publish_updated_data=callbacks.publish_updated_data,
            get_device_by_id=callbacks.get_device_by_id,
            async_refresh_devices=callbacks.async_refresh_devices,
            update_interval_seconds_getter=callbacks.update_interval_seconds_getter,
        )
        service_layer_ref["value"] = service_layer
        return BootstrapAssembly(
            state=state,
            support_services=support_services,
            runtimes=runtimes,
            service_layer=service_layer,
        )

    def _build_bootstrap_artifact_from_assembly(
        self,
        *,
        assembly: BootstrapAssembly,
        callbacks: BootstrapCallbacks,
    ) -> CoordinatorBootstrapArtifact:
        return CoordinatorBootstrapArtifact(
            state=assembly.state,
            runtimes=assembly.runtimes,
            support_services=assembly.support_services,
            service_layer=assembly.service_layer,
            update_cycle=self._build_update_cycle_artifact(
                support_services=assembly.support_services,
                runtimes=assembly.runtimes,
                state=assembly.state,
                service_layer=assembly.service_layer,
                async_setup_mqtt=callbacks.async_setup_mqtt,
                run_status_polling=callbacks.run_status_polling,
                refresh_device_snapshot=callbacks.refresh_device_snapshot,
            ),
        )

    def build_bootstrap_artifact(
        self,
        *,
        get_device_by_id: Callable[[str], LiproDevice | None],
        apply_properties_update: Callable[
            [LiproDevice, PropertyDict, str], Awaitable[bool]
        ],
        schedule_listener_update: Callable[[], None],
        request_refresh: Callable[[], Awaitable[None]],
        is_mqtt_connected: Callable[[], bool],
        async_setup_mqtt: Callable[[], Awaitable[bool]],
        replace_devices: Callable[[dict[str, LiproDevice]], None],
        publish_updated_data: Callable[[dict[str, LiproDevice]], None],
        async_refresh_devices: Callable[[], Awaitable[dict[str, LiproDevice]]],
        update_interval_seconds_getter: Callable[[], int | None],
        run_status_polling: Callable[[], Awaitable[None]],
        refresh_device_snapshot: Callable[[], Awaitable[None]],
        polling_updater: PollingIntervalUpdater,
    ) -> CoordinatorBootstrapArtifact:
        """Assemble the complete coordinator bootstrap artifact from formal collaborators."""
        callbacks = self._build_bootstrap_callbacks(
            get_device_by_id=get_device_by_id,
            apply_properties_update=apply_properties_update,
            schedule_listener_update=schedule_listener_update,
            request_refresh=request_refresh,
            is_mqtt_connected=is_mqtt_connected,
            async_setup_mqtt=async_setup_mqtt,
            replace_devices=replace_devices,
            publish_updated_data=publish_updated_data,
            async_refresh_devices=async_refresh_devices,
            update_interval_seconds_getter=update_interval_seconds_getter,
            run_status_polling=run_status_polling,
            refresh_device_snapshot=refresh_device_snapshot,
            polling_updater=polling_updater,
        )
        assembly = self._assemble_bootstrap(callbacks=callbacks)
        return self._build_bootstrap_artifact_from_assembly(
            assembly=assembly,
            callbacks=callbacks,
        )
