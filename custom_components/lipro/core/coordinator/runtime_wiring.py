"""Internal coordinator runtime-wiring helpers.

These helpers keep `Coordinator` as the single runtime root while moving
construction mechanics and service-layer bootstrapping into one support-only seam.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
import logging

from ..device import LiproDevice
from .factory import CoordinatorRuntimes, CoordinatorStateContainers
from .lifecycle import CoordinatorUpdateCycle
from .runtime_context import RuntimeContext
from .services import (
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorPollingService,
    CoordinatorStateService,
    CoordinatorTelemetryService,
)
from .services.protocol_service import CoordinatorProtocolService
from .services.telemetry_service import CoordinatorSignalService
from .types import PropertyDict


@dataclass(frozen=True, slots=True)
class CoordinatorServiceLayer:
    """Coordinator-owned runtime service surfaces created from runtime components."""

    command_service: CoordinatorCommandService
    mqtt_service: CoordinatorMqttService
    state_service: CoordinatorStateService
    polling_service: CoordinatorPollingService
    device_refresh_service: CoordinatorDeviceRefreshService
    telemetry_service: CoordinatorTelemetryService


def build_runtime_context(
    *,
    get_device_by_id: Callable[[str], LiproDevice | None],
    apply_properties_update: Callable[[LiproDevice, PropertyDict, str], Awaitable[bool]],
    schedule_listener_update: Callable[[], None],
    signal_service: CoordinatorSignalService,
    request_refresh: Callable[[], Awaitable[None]],
    trigger_reauth: Callable[[str], Awaitable[None]],
    is_mqtt_connected: Callable[[], bool],
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
    command_service = CoordinatorCommandService(
        command_runtime=runtimes.command,
        tuning_runtime=runtimes.tuning,
    )
    mqtt_service = CoordinatorMqttService(
        devices_getter=lambda: state.devices,
        mqtt_runtime_getter=lambda: runtimes.mqtt,
        setup_callback=async_setup_mqtt,
    )
    state_service = CoordinatorStateService(state_runtime=runtimes.state)
    polling_service = CoordinatorPollingService(
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
    device_refresh_service = CoordinatorDeviceRefreshService(
        device_runtime=runtimes.device,
        state_runtime=runtimes.state,
        refresh_callback=async_refresh_devices,
    )
    telemetry_service = CoordinatorTelemetryService(
        mqtt_service=mqtt_service,
        command_runtime=runtimes.command,
        status_runtime=runtimes.status,
        tuning_runtime=runtimes.tuning,
        mqtt_runtime_getter=lambda: runtimes.mqtt,
        device_count_getter=lambda: len(state.devices),
        polling_interval_seconds_getter=update_interval_seconds_getter,
    )
    return CoordinatorServiceLayer(
        command_service=command_service,
        mqtt_service=mqtt_service,
        state_service=state_service,
        polling_service=polling_service,
        device_refresh_service=device_refresh_service,
        telemetry_service=telemetry_service,
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
    devices_getter: Callable[[], Mapping[str, LiproDevice]],
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
    "build_runtime_context",
    "build_update_cycle",
    "initialize_service_layer",
]
