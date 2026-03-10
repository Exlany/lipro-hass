"""Coordinator runtime typing base.

This module provides a shared base class for coordinator runtime members so mypy can
type-check runtime methods that access coordinator state attributes.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, NoReturn

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..device import LiproDevice
from .entity_protocol import LiproEntityProtocol

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..anonymous_share import AnonymousShareManager
    from ..api import LiproClient
    from ..auth import LiproAuthManager
    from ..command.confirmation_tracker import CommandConfirmationTracker
    from ..command.expectation import PendingCommandExpectation
    from ..device.identity_index import DeviceIdentityIndex
    from ..mqtt import LiproMqttClient
    from ..mqtt.message import DedupCacheKey
    from ..mqtt.setup_backoff import MqttSetupBackoff
    from ..utils.background_task_manager import BackgroundTaskManager
    from .device_list_snapshot import DeviceFilterConfig
    from .mqtt.runtime import MqttRuntime
    from .protocols import (
        CommandServiceProtocol,
        DeviceRefreshServiceProtocol,
        MqttServiceProtocol,
        StateManagementProtocol,
    )


class _CoordinatorBase(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Shared base for coordinator runtime typing only."""

    hass: HomeAssistant
    config_entry: ConfigEntry | None

    client: LiproClient
    auth_manager: LiproAuthManager

    command_service: CommandServiceProtocol
    device_refresh_service: DeviceRefreshServiceProtocol
    mqtt_service: MqttServiceProtocol
    state_service: StateManagementProtocol

    # Runtime device caches
    _devices: dict[str, LiproDevice]
    _diagnostic_gateway_devices: dict[str, LiproDevice]
    _device_identity_index: DeviceIdentityIndex
    _iot_ids_to_query: list[str]
    _group_ids_to_query: list[str]
    _outlet_ids_to_query: list[str]
    _product_configs_by_id: dict[int, dict[str, Any]]
    _product_configs: dict[str, dict[str, Any]]
    _last_device_refresh_at: float
    _force_device_refresh: bool
    _missing_device_cycles: dict[str, int]
    _cloud_serials_last_seen: set[str]
    _entry_reload_handle: asyncio.TimerHandle | None
    _entry_reload_reasons: set[str]
    _last_entry_reload_at: float

    # Entity debounce protection index
    _entities: dict[str, LiproEntityProtocol]
    _entities_by_device: dict[str, list[LiproEntityProtocol]]

    # MQTT runtime state
    _mqtt_client: LiproMqttClient | None
    _mqtt_connected: bool
    _mqtt_setup_in_progress: bool
    _mqtt_setup_backoff: MqttSetupBackoff
    _mqtt_setup_backoff_gate_logged: bool
    _biz_id: str | None
    _mqtt_listener_update_handle: asyncio.TimerHandle | None
    _mqtt_message_cache: dict[DedupCacheKey, float]
    _mqtt_dedup_window: float
    _mqtt_disconnect_time: float | None
    _mqtt_disconnect_notified: bool
    _mqtt_runtime: MqttRuntime | None
    _mqtt_group_online_reconcile_task: asyncio.Task[Any] | None
    _mqtt_group_online_reconcile_last_at: float
    _last_mqtt_connect_state_at: dict[str, float]

    # Background tasks created by the coordinator.
    _background_task_manager: BackgroundTaskManager
    _background_tasks: set[asyncio.Task[Any]]

    # Command confirmation/adaptive reconciliation state
    _pending_command_expectations: dict[str, PendingCommandExpectation]
    _device_state_latency_seconds: dict[str, float]
    _command_confirmation_tracker: CommandConfirmationTracker
    _post_command_refresh_tasks: dict[str, asyncio.Task[Any]]
    _command_traces: deque[dict[str, Any]]
    _last_command_failure: dict[str, Any] | None

    # Options-derived flags
    _debug_mode: bool
    _mqtt_enabled: bool
    _power_monitoring_enabled: bool
    _power_query_interval: int
    _request_timeout: int
    _room_area_sync_force: bool
    _command_result_verify: bool
    _device_filter_config: DeviceFilterConfig
    _device_filter_enabled: bool

    # Connect-status polling + adaptive batch metrics
    _last_power_query_time: float
    _outlet_power_round_robin_index: int
    _last_connect_status_query_time: float
    _force_connect_status_refresh: bool
    _connect_status_priority_ids: set[str]
    _connect_status_mqtt_stale_seconds: float
    _connect_status_skip_history: deque[bool]
    _state_status_batch_size: int
    _state_batch_metrics: deque[tuple[int, float, int]]

    # Cross-runtime helpers implemented on the final coordinator class.
    def get_device_by_id(
        self, device_id: Any
    ) -> LiproDevice | None:  # pragma: no cover
        """Look up a device by any known identifier."""
        raise NotImplementedError

    def _resolve_direct_iot_query_ids(self) -> list[str]:  # pragma: no cover
        """Return IoT IDs that should still use individual status APIs."""
        raise NotImplementedError

    @staticmethod
    def _normalize_device_key(device_id: str) -> str:  # pragma: no cover
        """Normalize runtime device identifiers for per-device caches."""
        raise NotImplementedError

    def _apply_properties_update(  # pragma: no cover
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        apply_protection: bool = True,
    ) -> dict[str, Any]:
        """Apply property updates to a device with optional protection filters."""
        raise NotImplementedError

    def _track_background_task(  # pragma: no cover
        self, coro: Coroutine[Any, Any, Any]
    ) -> asyncio.Task[Any]:
        """Create and track a background task."""
        raise NotImplementedError

    def _on_mqtt_message(  # pragma: no cover
        self,
        device_id: str,
        properties: dict[str, Any],
    ) -> None:
        """Handle one MQTT message callback."""
        raise NotImplementedError

    def _get_anonymous_share_manager(self) -> AnonymousShareManager:  # pragma: no cover
        """Return the anonymous share manager."""
        raise NotImplementedError

    async def _trigger_reauth(
        self, key: str, **placeholders: str
    ) -> None:  # pragma: no cover
        """Trigger reauth flow with a repair issue."""
        raise NotImplementedError

    async def _async_ensure_authenticated(self) -> None:  # pragma: no cover
        """Ensure authentication state is valid."""
        raise NotImplementedError

    @property
    def devices(self) -> dict[str, LiproDevice]:  # pragma: no cover
        """Expose the current runtime device mapping."""
        raise NotImplementedError

    @property
    def last_command_failure(self) -> dict[str, Any] | None:  # pragma: no cover
        """Expose the latest command failure summary."""
        raise NotImplementedError

    def _should_refresh_device_list(self) -> bool:  # pragma: no cover
        """Return whether the next refresh should reload the device list."""
        raise NotImplementedError

    async def _fetch_devices(self) -> None:  # pragma: no cover
        """Fetch and reconcile the full device list."""
        raise NotImplementedError

    def _schedule_mqtt_setup_if_needed(self) -> None:  # pragma: no cover
        """Schedule MQTT setup when runtime state requires it."""
        raise NotImplementedError

    def _check_mqtt_disconnect_notification(self) -> None:  # pragma: no cover
        """Evaluate whether a MQTT disconnect notification should be raised."""
        raise NotImplementedError

    async def _raise_update_data_error(self, err: Exception) -> NoReturn:  # pragma: no cover
        """Map one update-time exception to the final raised error."""
        raise NotImplementedError

    def _resolve_connect_status_query_ids(self) -> list[str]:  # pragma: no cover
        """Resolve individual device IDs for connect-status polling."""
        raise NotImplementedError

    async def _query_connect_status(
        self,
        device_ids: list[str] | None = None,
    ) -> None:  # pragma: no cover
        """Query connect status for selected runtime devices."""
        raise NotImplementedError

    def _record_state_batch_metric(
        self,
        batch_size: int,
        duration_seconds: float,
        fallback_depth: int,
    ) -> None:  # pragma: no cover
        """Record one adaptive state-batch sample."""
        raise NotImplementedError

    def _adapt_state_batch_size(self) -> None:  # pragma: no cover
        """Adapt runtime batch size using recorded metrics."""
        raise NotImplementedError

    def _filter_pending_command_mismatches(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:  # pragma: no cover
        """Filter stale device properties while commands are pending."""
        raise NotImplementedError

    def _observe_command_confirmation(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> None:  # pragma: no cover
        """Observe one property update for command confirmation."""
        raise NotImplementedError

    async def _sync_mqtt_subscriptions(self) -> None:  # pragma: no cover
        """Synchronize MQTT subscriptions for current runtime devices."""
        raise NotImplementedError

    def _prune_runtime_state_for_devices(
        self,
        active_serials: set[str],
    ) -> None:  # pragma: no cover
        """Prune per-device runtime caches for removed devices."""
        raise NotImplementedError

    def _track_command_expectation(
        self,
        device_serial: str,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> None:  # pragma: no cover
        """Track expected device state after sending one command."""
        raise NotImplementedError

    def _get_adaptive_post_refresh_delay(
        self,
        device_serial: str | None,
    ) -> float:  # pragma: no cover
        """Return the adaptive post-command refresh delay."""
        raise NotImplementedError

    def _schedule_post_command_refresh(
        self,
        *,
        skip_immediate: bool = False,
        device_serial: str | None = None,
    ) -> None:  # pragma: no cover
        """Schedule immediate and delayed refresh work after a command."""
        raise NotImplementedError

    def _init_mqtt_state(self) -> None:  # pragma: no cover
        """Initialize MQTT-specific runtime state."""
        raise NotImplementedError

    def _reset_mqtt_state(self) -> None:  # pragma: no cover
        """Reset MQTT-specific runtime state."""
        raise NotImplementedError

    def _build_status_metrics_snapshot(self) -> dict[str, Any]:  # pragma: no cover
        """Build the runtime status metrics snapshot payload."""
        raise NotImplementedError

    async def async_stop_mqtt(self) -> None:  # pragma: no cover
        """Stop coordinator-managed MQTT runtime."""
        raise NotImplementedError

    def _reset_runtime_state(self) -> None:  # pragma: no cover
        """Reset coordinator runtime state during shutdown."""
        raise NotImplementedError
