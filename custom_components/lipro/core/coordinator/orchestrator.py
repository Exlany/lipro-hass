"""Runtime orchestrator for coordinator collaborators."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from typing import TYPE_CHECKING, Any

from ..command.confirmation_tracker import CommandConfirmationTracker
from ..device.identity_index import DeviceIdentityIndex
from ..utils.background_task_manager import BackgroundTaskManager
from .factory import (
    CoordinatorBootstrapArtifact,
    CoordinatorRuntimes,
    CoordinatorStateContainers,
    normalize_device_key,
)
from .runtime.command import (
    CommandBuilder,
    CommandSender,
    ConfirmationManager,
    RetryStrategy,
)
from .runtime.command_runtime import CommandRuntime
from .runtime.device_runtime import DeviceRuntime
from .runtime.mqtt_runtime import MqttRuntime
from .runtime.state_runtime import StateRuntime
from .runtime.status_runtime import StatusRuntime
from .runtime.tuning_runtime import TuningRuntime
from .runtime_context import RuntimeContext
from .runtime_wiring import (
    build_runtime_context,
    build_update_cycle,
    initialize_service_layer,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from ..protocol import LiproProtocolFacade
    from .runtime.mqtt.connection import PollingIntervalUpdater
    from .services.protocol_service import CoordinatorProtocolService
    from .services.telemetry_service import CoordinatorSignalService
    from .types import PropertyDict

_LOGGER = logging.getLogger(__name__)


class _DeviceResolverPort:
    def __init__(self, context: RuntimeContext) -> None:
        self._context = context

    def get_device_by_id(self, device_id: str) -> LiproDevice | None:
        return self._context.get_device_by_id(device_id)


class _ListenerNotifierPort:
    def __init__(self, context: RuntimeContext) -> None:
        self._context = context

    def schedule_listener_update(self) -> None:
        self._context.schedule_listener_update()


class _ConnectStateTrackerPort:
    def __init__(self, context: RuntimeContext) -> None:
        self._context = context

    def record_connect_state(
        self,
        device_serial: str,
        timestamp: float,
        is_online: bool,
    ) -> None:
        self._context.record_connect_state.record_connect_state(
            device_serial,
            timestamp,
            is_online,
        )


class _GroupReconcilerPort:
    def __init__(self, context: RuntimeContext) -> None:
        self._context = context

    def schedule_group_reconciliation(
        self,
        device_name: str,
        timestamp: float,
    ) -> None:
        self._context.request_group_reconciliation.schedule_group_reconciliation(
            device_name,
            timestamp,
        )


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
        self.update_interval = update_interval
        self.logger = logger

    def build_state_containers(self) -> CoordinatorStateContainers:
        """Build mutable state containers."""
        background_task_manager = BackgroundTaskManager(
            self.hass.async_create_task, self.logger
        )

        confirmation_tracker = CommandConfirmationTracker(
            default_post_command_refresh_delay_seconds=0.8,
            min_post_command_refresh_delay_seconds=0.3,
            max_post_command_refresh_delay_seconds=3.0,
            state_latency_margin_seconds=0.2,
            state_latency_ewma_alpha=0.3,
            state_confirm_timeout_seconds=5.0,
        )

        return CoordinatorStateContainers(
            devices={},
            entities={},
            entities_by_device={},
            device_identity_index=DeviceIdentityIndex(),
            background_task_manager=background_task_manager,
            confirmation_tracker=confirmation_tracker,
        )

    def build_runtimes(
        self,
        *,
        context: RuntimeContext,
        state: CoordinatorStateContainers,
        polling_updater: PollingIntervalUpdater,
    ) -> CoordinatorRuntimes:
        """Build all runtime components with unified context injection."""
        state_runtime = self._build_state_runtime(state)
        return CoordinatorRuntimes(
            tuning=self._build_tuning_runtime(),
            state=state_runtime,
            device=self._build_device_runtime(state),
            status=self._build_status_runtime(context, state_runtime),
            mqtt=self._build_mqtt_runtime(context, state, polling_updater),
            command=self._build_command_runtime(context, state),
        )

    def build_bootstrap_artifact(
        self,
        *,
        signal_service: CoordinatorSignalService,
        protocol_service: CoordinatorProtocolService,
        get_device_by_id: Callable[[str], LiproDevice | None],
        apply_properties_update: Callable[
            [LiproDevice, PropertyDict, str],
            Awaitable[bool],
        ],
        schedule_listener_update: Callable[[], None],
        request_refresh: Callable[[], Awaitable[None]],
        trigger_reauth: Callable[[str], Awaitable[None]],
        is_mqtt_connected: Callable[[], bool],
        ensure_authenticated: Callable[[], Awaitable[None]],
        async_setup_mqtt: Callable[[], Awaitable[bool]],
        replace_devices: Callable[[dict[str, LiproDevice]], None],
        publish_updated_data: Callable[[dict[str, LiproDevice]], None],
        async_refresh_devices: Callable[[], Awaitable[dict[str, LiproDevice]]],
        update_interval_seconds_getter: Callable[[], int | None],
        run_status_polling: Callable[[], Awaitable[None]],
        refresh_device_snapshot: Callable[[], Awaitable[None]],
        polling_updater: PollingIntervalUpdater,
    ) -> CoordinatorBootstrapArtifact:
        """Build the named bootstrap contract consumed by `Coordinator`."""
        state = self.build_state_containers()
        runtimes = self.build_runtimes(
            context=build_runtime_context(
                get_device_by_id=get_device_by_id,
                apply_properties_update=apply_properties_update,
                schedule_listener_update=schedule_listener_update,
                signal_service=signal_service,
                request_refresh=request_refresh,
                trigger_reauth=trigger_reauth,
                is_mqtt_connected=is_mqtt_connected,
            ),
            state=state,
            polling_updater=polling_updater,
        )
        service_layer = initialize_service_layer(
            runtimes=runtimes,
            state=state,
            protocol_service=protocol_service,
            async_setup_mqtt=async_setup_mqtt,
            replace_devices=replace_devices,
            publish_updated_data=publish_updated_data,
            get_device_by_id=get_device_by_id,
            async_refresh_devices=async_refresh_devices,
            update_interval_seconds_getter=update_interval_seconds_getter,
            logger=self.logger,
        )
        return CoordinatorBootstrapArtifact(
            state=state,
            runtimes=runtimes,
            service_layer=service_layer,
            update_cycle=build_update_cycle(
                ensure_authenticated=ensure_authenticated,
                should_refresh_device_list=runtimes.device.should_refresh_device_list,
                refresh_device_snapshot=refresh_device_snapshot,
                has_mqtt_transport=lambda: runtimes.mqtt.has_transport,
                has_devices=lambda: bool(state.devices),
                setup_mqtt=async_setup_mqtt,
                run_status_polling=run_status_polling,
                telemetry_service=service_layer.telemetry_service,
                devices_getter=lambda: state.devices,
            ),
        )

    def _build_tuning_runtime(self) -> TuningRuntime:
        return TuningRuntime(initial_batch_size=32)

    def _build_state_runtime(
        self,
        state: CoordinatorStateContainers,
    ) -> StateRuntime:
        return StateRuntime(
            devices=state.devices,
            device_identity_index=state.device_identity_index,
            entities=state.entities,
            entities_by_device=state.entities_by_device,
            normalize_device_key=normalize_device_key,
        )

    def _build_device_runtime(
        self,
        state: CoordinatorStateContainers,
    ) -> DeviceRuntime:
        return DeviceRuntime(
            protocol=self.protocol,
            auth_manager=self.auth_manager,
            device_identity_index=state.device_identity_index,
            filter_config_options=dict(self.config_entry.options),
        )

    def _build_status_runtime(
        self,
        context: RuntimeContext,
        state_runtime: StateRuntime,
    ) -> StatusRuntime:
        async def _query_device_status_batch(
            device_ids: list[str],
        ) -> dict[str, dict[str, Any]]:
            rows = await self.protocol.query_device_status(device_ids)
            return self.protocol.contracts.build_device_status_map(rows)

        async def _apply_properties_update(
            device: LiproDevice,
            properties: dict[str, Any],
            source: str,
        ) -> bool:
            return await context.apply_properties_update(device, properties, source)

        return StatusRuntime(
            power_query_interval=300,
            outlet_power_cycle_size=10,
            max_devices_per_query=50,
            initial_batch_size=32,
            query_device_status=_query_device_status_batch,
            apply_properties_update=_apply_properties_update,
            get_device_by_id=state_runtime.get_device_by_id,
        )

    def _build_mqtt_runtime(
        self,
        context: RuntimeContext,
        state: CoordinatorStateContainers,
        polling_updater: PollingIntervalUpdater,
    ) -> MqttRuntime:
        return MqttRuntime(
            hass=self.hass,
            mqtt_transport=None,
            base_scan_interval=self.update_interval,
            polling_updater=polling_updater,
            device_resolver=_DeviceResolverPort(context),
            property_applier=context.apply_properties_update,
            listener_notifier=_ListenerNotifierPort(context),
            connect_state_tracker=_ConnectStateTrackerPort(context),
            group_reconciler=_GroupReconcilerPort(context),
            polling_multiplier=2,
            background_task_manager=state.background_task_manager,
        )

    def _build_command_runtime(
        self,
        context: RuntimeContext,
        state: CoordinatorStateContainers,
    ) -> CommandRuntime:
        confirmation_manager = ConfirmationManager(
            confirmation_tracker=state.confirmation_tracker,
            pending_expectations={},
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=state.background_task_manager.create,
            request_refresh=context.request_refresh,
            mqtt_connected_provider=context.is_mqtt_connected,
        )
        return CommandRuntime(
            builder=CommandBuilder(debug_mode=False),
            sender=CommandSender(protocol=self.protocol),
            retry=RetryStrategy(),
            confirmation=confirmation_manager,
            trigger_reauth=context.trigger_reauth,
            debug_mode=False,
        )
