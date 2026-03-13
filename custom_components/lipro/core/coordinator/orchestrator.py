"""Runtime orchestrator for aggressive refactor (Phase C).

This module replaces the scattered DI wiring in factory.py with a clean,
context-driven orchestration pattern.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ..command.confirmation_tracker import CommandConfirmationTracker
from ..device.identity_index import DeviceIdentityIndex
from ..utils.background_task_manager import BackgroundTaskManager
from .factory import (
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

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from .runtime.mqtt.connection import PollingIntervalUpdater

_LOGGER = logging.getLogger(__name__)


class RuntimeOrchestrator:
    """Orchestrates runtime component initialization with unified context."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        client,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int,
        logger: logging.Logger,
    ) -> None:
        """Initialize orchestrator with external dependencies."""
        self.hass = hass
        self.client = client
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
        tuning_runtime = TuningRuntime(
            initial_batch_size=32,
        )

        state_runtime = StateRuntime(
            devices=state.devices,
            device_identity_index=state.device_identity_index,
            entities=state.entities,
            entities_by_device=state.entities_by_device,
            normalize_device_key=normalize_device_key,
        )

        device_runtime = DeviceRuntime(
            client=self.client,
            auth_manager=self.auth_manager,
            device_identity_index=state.device_identity_index,
            filter_config_options=dict(self.config_entry.options),
        )

        async def _query_device_status_batch(
            device_ids: list[str],
        ) -> dict[str, dict[str, Any]]:
            """Query device status batch (extracted from factory.py)."""
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
            device: LiproDevice,
            properties: dict[str, Any],
            source: str,
        ) -> bool:
            """Apply properties update through the coordinator callback contract."""
            return await context.apply_properties_update(device, properties, source)

        status_runtime = StatusRuntime(
            power_query_interval=300,
            outlet_power_cycle_size=10,
            max_devices_per_query=50,
            initial_batch_size=32,
            query_device_status=_query_device_status_batch,
            apply_properties_update=_apply_properties_update,
            get_device_by_id=state_runtime.get_device_by_id,
        )

        mqtt_runtime = MqttRuntime(
            hass=self.hass,
            mqtt_client=None,
            base_scan_interval=self.update_interval,
            polling_updater=polling_updater,
            device_resolver=context.get_device_by_id,  # type: ignore[arg-type]
            property_applier=context.apply_properties_update,
            listener_notifier=context.schedule_listener_update,  # type: ignore[arg-type]
            connect_state_tracker=context.record_connect_state,  # type: ignore[arg-type]
            group_reconciler=context.request_group_reconciliation,  # type: ignore[arg-type]
            polling_multiplier=2,
            background_task_manager=state.background_task_manager,
        )

        command_builder = CommandBuilder(debug_mode=False)
        command_sender = CommandSender(client=self.client)
        retry_strategy = RetryStrategy()

        confirmation_manager = ConfirmationManager(
            confirmation_tracker=state.confirmation_tracker,
            pending_expectations={},
            device_state_latency_seconds={},
            post_command_refresh_tasks={},
            track_background_task=state.background_task_manager.create,
            request_refresh=context.request_refresh,
            mqtt_connected_provider=context.is_mqtt_connected,
        )

        command_runtime = CommandRuntime(
            builder=command_builder,
            sender=command_sender,
            retry=retry_strategy,
            confirmation=confirmation_manager,
            trigger_reauth=context.trigger_reauth,
            debug_mode=False,
        )

        return CoordinatorRuntimes(
            tuning=tuning_runtime,
            state=state_runtime,
            device=device_runtime,
            status=status_runtime,
            mqtt=mqtt_runtime,
            command=command_runtime,
        )
