"""Internal coordinator runtime-wiring helpers.

These helpers keep `Coordinator` as the single runtime root while moving
construction mechanics and service-layer bootstrapping into one support-only seam.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from ..device import LiproDevice
from .factory import CoordinatorRuntimes, CoordinatorStateContainers
from .lifecycle import CoordinatorUpdateCycle
from .runtime_context import (
    DeviceResolverProtocol,
    ListenerNotifierProtocol,
    MqttConnectedProviderProtocol,
    PropertyApplierProtocol,
    ReauthTriggerProtocol,
    RefreshRequestProtocol,
    RuntimeContext,
)
from .services import (
    CoordinatorAuthService,
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorPollingService,
    CoordinatorProtocolService,
    CoordinatorScheduleService,
    CoordinatorSignalService,
    CoordinatorStateService,
    CoordinatorTelemetryService,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..protocol import LiproProtocolFacade


@dataclass(frozen=True, slots=True)
class CoordinatorSupportServices:
    """Coordinator-owned support services bound through one bootstrap artifact."""

    auth_service: CoordinatorAuthService
    protocol_service: CoordinatorProtocolService
    signal_service: CoordinatorSignalService


@dataclass(frozen=True, slots=True)
class CoordinatorServiceLayer:
    """Coordinator-owned runtime service surfaces created from runtime components."""

    command_service: CoordinatorCommandService
    mqtt_service: CoordinatorMqttService
    state_service: CoordinatorStateService
    polling_service: CoordinatorPollingService
    schedule_service: CoordinatorScheduleService
    device_refresh_service: CoordinatorDeviceRefreshService
    telemetry_service: CoordinatorTelemetryService


def build_runtime_context(
    *,
    get_device_by_id: DeviceResolverProtocol,
    apply_properties_update: PropertyApplierProtocol,
    schedule_listener_update: ListenerNotifierProtocol,
    signal_service: CoordinatorSignalService,
    request_refresh: RefreshRequestProtocol,
    trigger_reauth: ReauthTriggerProtocol,
    is_mqtt_connected: MqttConnectedProviderProtocol,
) -> RuntimeContext:
    """Build the unified runtime context consumed by coordinator runtimes."""
    return RuntimeContext(
        get_device_by_id=get_device_by_id,
        apply_properties_update=apply_properties_update,
        schedule_listener_update=schedule_listener_update,
        record_connect_state=signal_service,
        request_group_reconciliation=signal_service,
        request_refresh=request_refresh,
        trigger_reauth=trigger_reauth,
        is_mqtt_connected=is_mqtt_connected,
    )


def initialize_support_services(
    *,
    hass: HomeAssistant,
    protocol: LiproProtocolFacade,
    auth_manager: LiproAuthManager,
    config_entry: ConfigEntry,
    telemetry_service_getter: Callable[[], CoordinatorTelemetryService],
    device_refresh_service_getter: Callable[[], CoordinatorDeviceRefreshService],
) -> CoordinatorSupportServices:
    """Build the coordinator-owned support services for one bootstrap artifact."""
    return CoordinatorSupportServices(
        auth_service=CoordinatorAuthService(
            hass=hass,
            auth_manager=auth_manager,
            config_entry=config_entry,
        ),
        protocol_service=CoordinatorProtocolService(
            protocol_getter=lambda: protocol,
        ),
        signal_service=CoordinatorSignalService(
            telemetry_service_getter=telemetry_service_getter,
            device_refresh_service_getter=device_refresh_service_getter,
        ),
    )


def _build_command_service(
    *,
    runtimes: CoordinatorRuntimes,
) -> CoordinatorCommandService:
    """Build the coordinator command service from owned runtimes."""
    return CoordinatorCommandService(
        command_runtime=runtimes.command,
        tuning_runtime=runtimes.tuning,
    )



def _build_mqtt_service(
    *,
    state: CoordinatorStateContainers,
    runtimes: CoordinatorRuntimes,
    async_setup_mqtt: Callable[[], Awaitable[bool]],
) -> CoordinatorMqttService:
    """Build the coordinator MQTT service from runtime-owned dependencies."""
    return CoordinatorMqttService(
        devices_getter=lambda: state.devices,
        mqtt_runtime_getter=lambda: runtimes.mqtt,
        setup_callback=async_setup_mqtt,
    )



def _build_polling_service(
    *,
    runtimes: CoordinatorRuntimes,
    state: CoordinatorStateContainers,
    protocol_service: CoordinatorProtocolService,
    mqtt_service: CoordinatorMqttService,
    replace_devices: Callable[[dict[str, LiproDevice]], None],
    publish_updated_data: Callable[[dict[str, LiproDevice]], None],
    get_device_by_id: Callable[[str], LiproDevice | None],
    logger: logging.Logger,
) -> CoordinatorPollingService:
    """Build the coordinator polling service from runtime-owned dependencies."""
    return CoordinatorPollingService(
        device_runtime=runtimes.device,
        status_runtime=runtimes.status,
        tuning_runtime=runtimes.tuning,
        protocol_service=protocol_service,
        mqtt_service=mqtt_service,
        devices_getter=lambda: state.devices,
        replace_devices=replace_devices,
        publish_updated_data=publish_updated_data,
        get_device_by_id=get_device_by_id,
        has_mqtt_transport_getter=lambda: runtimes.mqtt.has_transport,
        logger=logger,
    )



def _build_device_refresh_service(
    *,
    runtimes: CoordinatorRuntimes,
    async_refresh_devices: Callable[[], Awaitable[dict[str, LiproDevice]]],
) -> CoordinatorDeviceRefreshService:
    """Build the coordinator device-refresh service from runtime-owned dependencies."""
    return CoordinatorDeviceRefreshService(
        device_runtime=runtimes.device,
        state_runtime=runtimes.state,
        refresh_callback=async_refresh_devices,
    )



def _build_telemetry_service(
    *,
    runtimes: CoordinatorRuntimes,
    state: CoordinatorStateContainers,
    mqtt_service: CoordinatorMqttService,
    update_interval_seconds_getter: Callable[[], int | None],
) -> CoordinatorTelemetryService:
    """Build the coordinator telemetry service from runtime-owned dependencies."""
    return CoordinatorTelemetryService(
        mqtt_service=mqtt_service,
        command_runtime=runtimes.command,
        status_runtime=runtimes.status,
        tuning_runtime=runtimes.tuning,
        mqtt_runtime_getter=lambda: runtimes.mqtt,
        device_count_getter=lambda: len(state.devices),
        polling_interval_seconds_getter=update_interval_seconds_getter,
    )


def initialize_service_layer(
    *,
    runtimes: CoordinatorRuntimes,
    state: CoordinatorStateContainers,
    protocol_service: CoordinatorProtocolService,
    async_setup_mqtt: Callable[[], Awaitable[bool]],
    replace_devices: Callable[[dict[str, LiproDevice]], None],
    publish_updated_data: Callable[[dict[str, LiproDevice]], None],
    get_device_by_id: Callable[[str], LiproDevice | None],
    async_refresh_devices: Callable[[], Awaitable[dict[str, LiproDevice]]],
    update_interval_seconds_getter: Callable[[], int | None],
    logger: logging.Logger,
) -> CoordinatorServiceLayer:
    """Build the formal runtime service surfaces owned by `Coordinator`."""
    mqtt_service = _build_mqtt_service(
        state=state,
        runtimes=runtimes,
        async_setup_mqtt=async_setup_mqtt,
    )
    return CoordinatorServiceLayer(
        command_service=_build_command_service(runtimes=runtimes),
        mqtt_service=mqtt_service,
        state_service=CoordinatorStateService(state_runtime=runtimes.state),
        polling_service=_build_polling_service(
            runtimes=runtimes,
            state=state,
            protocol_service=protocol_service,
            mqtt_service=mqtt_service,
            replace_devices=replace_devices,
            publish_updated_data=publish_updated_data,
            get_device_by_id=get_device_by_id,
            logger=logger,
        ),
        schedule_service=CoordinatorScheduleService(protocol_service=protocol_service),
        device_refresh_service=_build_device_refresh_service(
            runtimes=runtimes,
            async_refresh_devices=async_refresh_devices,
        ),
        telemetry_service=_build_telemetry_service(
            runtimes=runtimes,
            state=state,
            mqtt_service=mqtt_service,
            update_interval_seconds_getter=update_interval_seconds_getter,
        ),
    )


def build_update_cycle(
    *,
    ensure_authenticated: Callable[[], Awaitable[None]],
    should_refresh_device_list: Callable[[], bool],
    refresh_device_snapshot: Callable[[], Awaitable[None]],
    has_mqtt_transport: Callable[[], bool],
    has_devices: Callable[[], bool],
    setup_mqtt: Callable[[], Awaitable[bool]],
    run_status_polling: Callable[[], Awaitable[None]],
    telemetry_service: CoordinatorTelemetryService,
    devices_getter: Callable[[], dict[str, LiproDevice]],
) -> CoordinatorUpdateCycle:
    """Build the coordinator update-cycle collaborator from explicit callbacks."""
    return CoordinatorUpdateCycle(
        ensure_authenticated=ensure_authenticated,
        should_refresh_device_list=should_refresh_device_list,
        refresh_device_snapshot=refresh_device_snapshot,
        has_mqtt_transport=has_mqtt_transport,
        has_devices=has_devices,
        setup_mqtt=setup_mqtt,
        run_status_polling=run_status_polling,
        telemetry_service=telemetry_service,
        devices_getter=devices_getter,
    )


__all__ = [
    "CoordinatorServiceLayer",
    "CoordinatorSupportServices",
    "build_runtime_context",
    "build_update_cycle",
    "initialize_service_layer",
    "initialize_support_services",
]
