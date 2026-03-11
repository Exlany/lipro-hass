"""Coordinator wiring factory (Phase H).

This module extracts dependency-injection wiring out of
`core/coordinator/coordinator.py`.

Goals:
- Keep `Coordinator` focused on HA integration + orchestration.
- Make runtime wiring explicit and testable.
- Reduce coordinator file size (towards < 300 LOC).

Note:
This is *not* a full IoC container. It is a pragmatic factory that builds the
current set of runtime components with injected callbacks.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed

from ...const.config import CONF_PHONE_ID
from ..api import LiproClient
from ..command.confirmation_tracker import CommandConfirmationTracker
from ..device.identity_index import DeviceIdentityIndex
from ..mqtt.credentials import decrypt_mqtt_credential
from ..mqtt.mqtt_client import LiproMqttClient
from ..utils.background_task_manager import BackgroundTaskManager
from .mqtt.setup import resolve_mqtt_biz_id
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

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..auth import LiproAuthManager
    from ..device import LiproDevice
    from .entity_protocol import LiproEntityProtocol

_LOGGER = logging.getLogger(__name__)


def normalize_device_key(device_id: str) -> str:
    """Normalize device identifier for indexing."""
    return device_id.lower().strip()


@dataclass(slots=True)
class CoordinatorStateContainers:
    """Mutable state containers owned by the coordinator."""

    devices: dict[str, LiproDevice]
    entities: dict[str, LiproEntityProtocol]
    entities_by_device: dict[str, list[LiproEntityProtocol]]
    device_identity_index: DeviceIdentityIndex
    background_task_manager: BackgroundTaskManager
    confirmation_tracker: CommandConfirmationTracker
    mqtt_client: LiproMqttClient | None = None
    biz_id: str | None = None


@dataclass(frozen=True, slots=True)
class CoordinatorRuntimes:
    """Runtime component registry."""

    tuning: TuningRuntime
    state: StateRuntime
    device: DeviceRuntime
    status: StatusRuntime
    mqtt: MqttRuntime
    command: CommandRuntime


def build_state_containers(
    *,
    hass: HomeAssistant,
    logger: logging.Logger,
) -> CoordinatorStateContainers:
    """Build the coordinator's core mutable containers."""
    background_task_manager = BackgroundTaskManager(hass.async_create_task, logger)

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
        mqtt_client=None,
        biz_id=None,
    )


def build_runtimes(
    *,
    hass: HomeAssistant,
    client: LiproClient,
    auth_manager: LiproAuthManager,
    config_entry: ConfigEntry,
    update_interval: int,
    state: CoordinatorStateContainers,
    request_refresh: Callable[[], Coroutine[Any, Any, None]],
    force_connect_status_refresh_setter: Callable[[bool], None],
    trigger_reauth: Callable[[str], Coroutine[Any, Any, None]],
) -> CoordinatorRuntimes:
    """Build all runtime components and complete dependency injection."""

    tuning_runtime = TuningRuntime(
        initial_batch_size=32,
        initial_mqtt_stale_window=180.0,
    )

    state_runtime = StateRuntime(
        devices=state.devices,
        device_identity_index=state.device_identity_index,
        entities=state.entities,
        entities_by_device=state.entities_by_device,
        normalize_device_key=normalize_device_key,
    )

    device_runtime = DeviceRuntime(
        client=client,
        auth_manager=auth_manager,
        device_identity_index=state.device_identity_index,
        filter_config_options=dict(config_entry.options),
    )

    async def _query_device_status_batch(device_ids: list[str]) -> dict[str, dict[str, Any]]:
        status_endpoint = getattr(client, "status", None)
        query_device_status = getattr(status_endpoint, "query_device_status", None)
        if query_device_status is None:
            rows = await client.query_device_status(device_ids)
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
        device: LiproDevice, properties: dict[str, Any], source: str
    ) -> bool:
        return await state_runtime.apply_properties_update(
            device, properties, source=source
        )

    status_runtime = StatusRuntime(
        power_query_interval=300,
        outlet_power_cycle_size=10,
        max_devices_per_query=50,
        initial_batch_size=32,
        query_device_status=_query_device_status_batch,
        apply_properties_update=_apply_properties_update,
        get_device_by_id=state_runtime.get_device_by_id,
    )

    # Create placeholder MQTT runtime (will be replaced by async_setup_mqtt)
    class _NoopDeviceResolver:
        def get_device_by_id(self, device_id: str) -> Any:
            return None

    class _NoopPropertyApplier:
        async def __call__(self, device: Any, properties: Any, source: Any) -> bool:
            return False

    class _NoopListenerNotifier:
        def schedule_listener_update(self) -> None:
            pass

    class _NoopConnectStateTracker:
        def record_connect_state(
            self, device_serial: str, timestamp: float, is_online: bool
        ) -> None:
            pass

    class _NoopGroupReconciler:
        def schedule_group_reconciliation(
            self, device_name: str, timestamp: float
        ) -> None:
            pass

    mqtt_runtime = MqttRuntime(
        hass=hass,
        mqtt_client=state.mqtt_client,
        base_scan_interval=update_interval,
        device_resolver=_NoopDeviceResolver(),
        property_applier=_NoopPropertyApplier(),
        listener_notifier=_NoopListenerNotifier(),
        connect_state_tracker=_NoopConnectStateTracker(),
        group_reconciler=_NoopGroupReconciler(),
        polling_multiplier=2,
        background_task_manager=state.background_task_manager,
    )

    pending_expectations: dict[str, Any] = {}
    device_state_latency_seconds: dict[str, float] = {}
    post_command_refresh_tasks: dict[str, asyncio.Task[Any]] = {}
    connect_status_priority_ids: set[str] = set()

    command_builder = CommandBuilder(debug_mode=False)
    command_sender = CommandSender(client=client)
    retry_strategy = RetryStrategy()

    confirmation_manager = ConfirmationManager(
        confirmation_tracker=state.confirmation_tracker,
        pending_expectations=pending_expectations,
        device_state_latency_seconds=device_state_latency_seconds,
        post_command_refresh_tasks=post_command_refresh_tasks,
        track_background_task=state.background_task_manager.create,
        request_refresh=request_refresh,
        mqtt_connected_provider=lambda: mqtt_runtime.is_connected,
    )

    command_runtime = CommandRuntime(
        builder=command_builder,
        sender=command_sender,
        retry=retry_strategy,
        confirmation=confirmation_manager,
        connect_status_priority_ids=connect_status_priority_ids,
        normalize_device_key=normalize_device_key,
        force_connect_status_refresh_setter=force_connect_status_refresh_setter,
        trigger_reauth=trigger_reauth,
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


async def async_create_mqtt_client(
    *,
    client: LiproClient,
    config_entry: ConfigEntry,
) -> tuple[LiproMqttClient, str] | None:
    """Create an MQTT client from API credentials.

    Returns:
        Tuple of (mqtt_client, biz_id) on success.
    """
    mqtt_config = await client.get_mqtt_config()
    if not mqtt_config:
        _LOGGER.warning("No MQTT config available")
        return None

    access_key = decrypt_mqtt_credential(mqtt_config.get("accessKey", ""))
    secret_key = decrypt_mqtt_credential(mqtt_config.get("secretKey", ""))

    if not access_key or not secret_key:
        _LOGGER.warning("Failed to decrypt MQTT credentials")
        return None

    biz_id = resolve_mqtt_biz_id(config_entry.data)
    if biz_id is None:
        _LOGGER.warning("No biz_id available for MQTT")
        return None

    phone_id = config_entry.data.get(CONF_PHONE_ID, "")

    return (
        LiproMqttClient(
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=phone_id,
        ),
        biz_id,
    )


def raise_reauth(reason: str) -> None:
    """Raise ConfigEntryAuthFailed with a stable message."""
    error_message = f"Authentication failed: {reason}"
    raise ConfigEntryAuthFailed(error_message)
