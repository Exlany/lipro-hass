"""Coordinator mixin typing base.

This module provides a shared base class for coordinator mixins so mypy can
type-check mixin methods that access coordinator runtime attributes.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any

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


class _CoordinatorBase(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Shared base for coordinator mixins (typing only)."""

    hass: HomeAssistant
    config_entry: ConfigEntry | None

    client: LiproClient
    auth_manager: LiproAuthManager

    # Runtime device caches
    _devices: dict[str, LiproDevice]
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

    # Cross-mixin helpers implemented on the final coordinator class.
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
