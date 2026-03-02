"""Data update coordinator for Lipro integration."""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Coroutine, Mapping
from datetime import timedelta
import hashlib
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Final, NoReturn

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import area_registry as ar, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..const import (
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_MQTT_ENABLED,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_ROOM_AREA_SYNC_FORCE,
    CONF_SCAN_INTERVAL,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_DEBUG_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_ROOM_AREA_SYNC_FORCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_POWER_QUERY_INTERVAL,
    MAX_REQUEST_TIMEOUT,
    MAX_SCAN_INTERVAL,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
    PROP_BRIGHTNESS,
    PROP_CONNECT_STATE,
    PROP_FAN_GEAR,
    PROP_POSITION,
    PROP_TEMPERATURE,
)
from ..const.api import MAX_DEVICES_PER_QUERY, MAX_MQTT_CACHE_SIZE
from ..const.config import CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY
from ..helpers.coerce import coerce_bool_option, coerce_int_option
from .anonymous_share import get_anonymous_share_manager
from .api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .command.command_confirmation_tracker import CommandConfirmationTracker
from .command.command_dispatch import execute_command_plan_with_trace
from .command.command_expectation import (
    PendingCommandExpectation as _PendingCommandExpectation,
)
from .command.command_result import (
    apply_missing_msg_sn_failure,
    apply_push_failure,
    apply_successful_command_trace,
    build_command_api_error_failure,
    classify_command_result_payload,
    extract_msg_sn,
    is_command_push_failed,
    poll_command_result_state,
    query_command_result_once,
    resolve_polled_command_result,
    run_delayed_refresh,
    should_skip_immediate_post_refresh,
)
from .command.command_trace import build_command_trace, update_trace_with_exception
from .command.post_command_refresh import schedule_post_command_refresh
from .device import LiproDevice, parse_properties_list
from .device.device_identity_index import DeviceIdentityIndex
from .device.device_refresh import (
    DeviceFilterConfig,
    FetchedDeviceSnapshot,
    build_device_filter_config,
    build_fetched_device_snapshot,
    has_active_device_filter,
    is_device_included_by_filter,
    plan_stale_device_reconciliation,
)
from .device.group_status import resolve_mesh_group_lookup_ids
from .device.outlet_power import (
    apply_outlet_power_info,
    should_reraise_outlet_power_error,
)
from .mqtt import LiproMqttClient, decrypt_mqtt_credential
from .mqtt.mqtt_message import (
    DedupCacheKey,
    build_dedup_cache_key,
    cleanup_dedup_cache,
    compute_properties_hash,
    is_duplicate_within_window,
    is_online_connect_state,
)
from .mqtt.mqtt_polling import resolve_base_scan_interval_seconds
from .mqtt.mqtt_runtime import MqttRuntime
from .mqtt.mqtt_setup import (
    build_mqtt_subscription_device_ids,
    extract_mqtt_encrypted_credentials,
    iter_mesh_group_serials,
    resolve_mqtt_biz_id,
)
from .mqtt.mqtt_setup_backoff import MqttSetupBackoff
from .runtime.connect_status_runtime import (
    adapt_connect_status_stale_window as adapt_connect_status_stale_window_runtime,
    resolve_connect_status_query_interval_seconds as resolve_connect_status_query_interval_seconds_runtime,
)
from .runtime.coordinator_runtime import (
    should_refresh_device_list as should_refresh_device_list_runtime,
    should_schedule_mqtt_setup,
)
from .runtime.group_lookup_runtime import compute_group_lookup_mapping_decision
from .runtime.outlet_power_runtime import (
    query_outlet_power as query_outlet_power_runtime,
    query_single_outlet_power as query_single_outlet_power_runtime,
    resolve_outlet_power_cycle_size as resolve_outlet_power_cycle_size_runtime,
)
from .runtime.product_config_runtime import (
    apply_product_config as apply_product_config_runtime,
    index_product_configs as index_product_configs_runtime,
    match_product_config as match_product_config_runtime,
)
from .runtime.room_sync_runtime import (
    normalize_room_name as normalize_room_name_runtime,
    resolve_room_area_target_name as resolve_room_area_target_name_runtime,
)
from .runtime.state_batch_runtime import (
    normalize_state_batch_metric,
    summarize_recent_state_batch_metrics,
)
from .runtime.status_strategy import (
    ConnectStatusQueryDecision,
    compute_adaptive_state_batch_size,
    resolve_connect_status_query_candidates,
)
from .utils.background_task_manager import BackgroundTaskManager
from .utils.developer_report import (
    build_developer_report as build_coordinator_developer_report,
)
from .utils.log_safety import safe_error_placeholder, summarize_properties_for_log
from .utils.redaction import redact_identifier as _redact_identifier

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..entities.base import LiproEntity
    from .auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)

# Polling interval multiplier when MQTT provides real-time updates.
# Use 2x (not higher) to still catch sub-device state drift in mesh groups.
_MQTT_POLLING_MULTIPLIER: Final[int] = 2

# Coalesce MQTT-driven listener updates to reduce event-loop churn under bursts.
_MQTT_LISTENER_UPDATE_DEBOUNCE_SECONDS: Final[float] = 0.05

# Time threshold (seconds) for cleaning stale MQTT dedup cache entries
_MQTT_CACHE_STALE_SECONDS: Final[float] = 5.0

# Cap concurrent per-outlet power-info requests to avoid API rate limiting.
_OUTLET_POWER_QUERY_CONCURRENCY: Final[int] = 5

# When many outlets exist, query power info in rotating slices to avoid large
# bursts on each power interval tick.
_OUTLET_POWER_QUERY_MAX_DEVICES_PER_CYCLE: Final[int] = 10
_OUTLET_POWER_TARGET_FULL_CYCLE_COUNT: Final[int] = 4

# Query connect status less frequently than full status polling to reduce load.
_CONNECT_STATUS_QUERY_INTERVAL_SECONDS: Final[float] = 60.0
# When MQTT is unstable/disconnected, degrade to a shorter connect-status interval.
_CONNECT_STATUS_QUERY_INTERVAL_DEGRADED_SECONDS: Final[float] = 20.0
# When MQTT recently provided connectState, skip redundant REST connect-status.
_CONNECT_STATUS_MQTT_STALE_SECONDS: Final[float] = 180.0
_CONNECT_STATUS_MQTT_STALE_MIN_SECONDS: Final[float] = 90.0
_CONNECT_STATUS_MQTT_STALE_MAX_SECONDS: Final[float] = 300.0
_CONNECT_STATUS_STALE_ADJUST_STEP_SECONDS: Final[float] = 15.0
_CONNECT_STATUS_SKIP_RATIO_WINDOW: Final[int] = 20
_CONNECT_STATUS_SKIP_RATIO_LOW: Final[float] = 0.20
_CONNECT_STATUS_SKIP_RATIO_HIGH: Final[float] = 0.85

# Runtime adaptive state-batch tuning.
_STATE_STATUS_BATCH_SIZE_MIN: Final[int] = 16
_STATE_STATUS_BATCH_SIZE_MAX: Final[int] = 64
_STATE_STATUS_BATCH_ADJUST_STEP: Final[int] = 8
_STATE_STATUS_BATCH_METRICS_WINDOW: Final[int] = 24
_STATE_STATUS_BATCH_METRICS_SAMPLE_SIZE: Final[int] = 6
_STATE_STATUS_BATCH_LATENCY_LOW_SECONDS: Final[float] = 1.2
_STATE_STATUS_BATCH_LATENCY_HIGH_SECONDS: Final[float] = 3.5

# Number of consecutive full-device-list fetches a device can be missing
# before being removed from HA device registry.
_STALE_DEVICE_REMOVE_THRESHOLD: Final[int] = 3

# Periodic full device-list refresh to discover newly paired devices.
_DEVICE_LIST_REFRESH_INTERVAL_SECONDS: Final[int] = 600

# Defensive cap for malformed pagination responses that never terminate.
_MAX_DEVICE_LIST_PAGES: Final[int] = 50

# Optional command-result verification tuning.
_COMMAND_RESULT_VERIFY_ATTEMPTS: Final[int] = 3
_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS: Final[float] = 0.35

# API status may lag after command push; schedule one delayed refresh fallback.
_POST_COMMAND_REFRESH_DELAY_SECONDS: Final[float] = 3.0

# Adaptive post-command reconciliation tuning.
_MIN_POST_COMMAND_REFRESH_DELAY_SECONDS: Final[float] = 1.5
_MAX_POST_COMMAND_REFRESH_DELAY_SECONDS: Final[float] = 8.0
_STATE_LATENCY_MARGIN_SECONDS: Final[float] = 0.6
_STATE_LATENCY_EWMA_ALPHA: Final[float] = 0.35
_STATE_CONFIRM_TIMEOUT_SECONDS: Final[float] = 20.0

# Keep the latest command traces in memory for debug diagnostics.
_MAX_DEVELOPER_COMMAND_TRACES: Final[int] = 100

# Cooldown for MQTT group online reconciliation refresh to avoid refresh storms
# when connectState flaps or multiple sub-devices reconnect in bursts.
_MQTT_GROUP_ONLINE_RECONCILE_COOLDOWN_SECONDS: Final[float] = 5.0

_SLIDER_LIKE_PROPERTIES: Final[frozenset[str]] = frozenset(
    {
        PROP_BRIGHTNESS,
        PROP_TEMPERATURE,
        PROP_FAN_GEAR,
        PROP_POSITION,
    }
)


# HA version for anonymous share reporting
try:
    from homeassistant.const import __version__ as _ha_ver

    HA_VERSION: str | None = _ha_ver
except ImportError:
    HA_VERSION = None


class LiproDataUpdateCoordinator(DataUpdateCoordinator[dict[str, LiproDevice]]):
    """Coordinator to manage fetching Lipro data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LiproClient,
        auth_manager: LiproAuthManager,
        config_entry: ConfigEntry,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance.
            client: Lipro API client.
            auth_manager: Authentication manager.
            config_entry: The config entry for this coordinator.
            update_interval: Update interval in seconds.

        """
        super().__init__(
            hass,
            _LOGGER,
            name="Lipro",
            update_interval=timedelta(seconds=update_interval),
            config_entry=config_entry,
            # Lipro devices are updated in-place (mutable LiproDevice objects).
            # With always_update=False, HA's default equality check may treat
            # self.data as "unchanged" and skip listener callbacks, preventing
            # entities from refreshing. Always notify on each refresh tick.
            always_update=True,
        )
        self.client = client
        self.auth_manager = auth_manager
        self._init_runtime_state()

        # Load options from config entry
        self._load_options()

        # Initialize anonymous share system based on config
        self._setup_anonymous_share()

    def _init_runtime_state(self) -> None:
        """Initialize coordinator runtime state containers and caches."""
        self._devices: dict[str, LiproDevice] = {}
        self._device_identity_index = DeviceIdentityIndex()
        self._device_by_id = {}  # Any known ID -> Device
        self._iot_ids_to_query: list[str] = []
        self._group_ids_to_query: list[str] = []
        self._outlet_ids_to_query: list[str] = []  # Outlet device IDs for power query
        # Track entities for debounce protection (indexed by device serial)
        self._entities: dict[str, LiproEntity] = {}
        self._entities_by_device: dict[str, list[LiproEntity]] = {}
        # MQTT client for real-time updates
        self._mqtt_client: LiproMqttClient | None = None
        self._mqtt_connected = False
        self._mqtt_setup_in_progress = False
        self._mqtt_setup_backoff = MqttSetupBackoff()
        self._mqtt_setup_backoff_gate_logged = False
        self._biz_id: str | None = None
        self._mqtt_listener_update_handle: asyncio.TimerHandle | None = None
        # Product configs cache (productId/iotName -> config)
        self._product_configs_by_id: dict[int, dict[str, Any]] = {}
        self._product_configs: dict[str, dict[str, Any]] = {}
        # MQTT message deduplication cache: "device_id:hash" -> timestamp
        self._mqtt_message_cache: dict[DedupCacheKey, float] = {}
        # Deduplication window in seconds (ignore duplicate messages within this window)
        self._mqtt_dedup_window: float = 0.5
        # Last successful full device-list refresh timestamp.
        self._last_device_refresh_at: float = 0.0
        # Power query tracking
        self._last_power_query_time: float = 0.0
        self._outlet_power_round_robin_index: int = 0
        # Connect-status polling tracking
        self._last_connect_status_query_time: float = 0.0
        self._force_connect_status_refresh: bool = True
        self._last_mqtt_connect_state_at: dict[str, float] = {}
        self._connect_status_priority_ids: set[str] = set()
        self._connect_status_mqtt_stale_seconds: float = (
            _CONNECT_STATUS_MQTT_STALE_SECONDS
        )
        self._connect_status_skip_history: deque[bool] = deque(
            maxlen=_CONNECT_STATUS_SKIP_RATIO_WINDOW
        )
        self._state_status_batch_size: int = min(
            MAX_DEVICES_PER_QUERY,
            _STATE_STATUS_BATCH_SIZE_MAX,
        )
        self._state_batch_metrics: deque[tuple[int, float, int]] = deque(
            maxlen=_STATE_STATUS_BATCH_METRICS_WINDOW
        )
        # Flag to force device list re-fetch on next update
        self._force_device_refresh: bool = False
        self._device_filter_config: DeviceFilterConfig = build_device_filter_config({})
        self._device_filter_enabled: bool = False
        # MQTT disconnect tracking for user notification
        self._mqtt_disconnect_time: float | None = None
        self._mqtt_disconnect_notified: bool = False
        self._mqtt_runtime: MqttRuntime | None = MqttRuntime(
            self,
            polling_multiplier=_MQTT_POLLING_MULTIPLIER,
            connect_status_mqtt_stale_seconds=_CONNECT_STATUS_MQTT_STALE_SECONDS,
            logger=_LOGGER,
        )
        # Track per-device delayed refresh tasks for post-command consistency.
        self._post_command_refresh_tasks: dict[str, asyncio.Task[Any]] = {}
        # Single-flight + cooldown for group-online MQTT reconciliation refresh.
        self._mqtt_group_online_reconcile_task: asyncio.Task[Any] | None = None
        self._mqtt_group_online_reconcile_last_at: float = 0.0
        # Background tasks created by coordinator; cancelled on shutdown.
        self._background_task_manager = BackgroundTaskManager(
            self.hass.async_create_task,
            _LOGGER,
        )
        self._background_tasks: set[asyncio.Task[Any]] = (
            self._background_task_manager.tasks
        )
        # Pending CHANGE_STATE expectations per device for stale-update filtering.
        self._pending_command_expectations: dict[str, _PendingCommandExpectation] = {}
        # Learned command->state confirmation latency (EWMA) per device.
        self._device_state_latency_seconds: dict[str, float] = {}
        self._command_confirmation_tracker = CommandConfirmationTracker(
            default_post_command_refresh_delay_seconds=_POST_COMMAND_REFRESH_DELAY_SECONDS,
            min_post_command_refresh_delay_seconds=_MIN_POST_COMMAND_REFRESH_DELAY_SECONDS,
            max_post_command_refresh_delay_seconds=_MAX_POST_COMMAND_REFRESH_DELAY_SECONDS,
            state_latency_margin_seconds=_STATE_LATENCY_MARGIN_SECONDS,
            state_latency_ewma_alpha=_STATE_LATENCY_EWMA_ALPHA,
            state_confirm_timeout_seconds=_STATE_CONFIRM_TIMEOUT_SECONDS,
        )
        # Track consecutive missing counts for safe stale-device cleanup
        self._missing_device_cycles: dict[str, int] = {}
        # Debug mode command traces (opt-in)
        self._command_traces: deque[dict[str, Any]] = deque(
            maxlen=_MAX_DEVELOPER_COMMAND_TRACES
        )
        # Last command failure summary for service-layer error mapping.
        self._last_command_failure: dict[str, Any] | None = None

    def _load_options(self) -> None:
        """Load options from config entry."""
        options = self.config_entry.options if self.config_entry else {}

        # MQTT enabled
        self._mqtt_enabled = coerce_bool_option(
            options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
            option_name=CONF_MQTT_ENABLED,
            default=DEFAULT_MQTT_ENABLED,
            logger=_LOGGER,
        )

        # Power monitoring
        self._power_monitoring_enabled = coerce_bool_option(
            options.get(CONF_ENABLE_POWER_MONITORING, DEFAULT_ENABLE_POWER_MONITORING),
            option_name=CONF_ENABLE_POWER_MONITORING,
            default=DEFAULT_ENABLE_POWER_MONITORING,
            logger=_LOGGER,
        )
        self._power_query_interval = coerce_int_option(
            options.get(CONF_POWER_QUERY_INTERVAL, DEFAULT_POWER_QUERY_INTERVAL),
            option_name=CONF_POWER_QUERY_INTERVAL,
            default=DEFAULT_POWER_QUERY_INTERVAL,
            min_value=MIN_POWER_QUERY_INTERVAL,
            max_value=MAX_POWER_QUERY_INTERVAL,
            logger=_LOGGER,
        )

        # Request timeout
        self._request_timeout = coerce_int_option(
            options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT),
            option_name=CONF_REQUEST_TIMEOUT,
            default=DEFAULT_REQUEST_TIMEOUT,
            min_value=MIN_REQUEST_TIMEOUT,
            max_value=MAX_REQUEST_TIMEOUT,
            logger=_LOGGER,
        )

        # Debug mode includes verbose logging and runtime command traces.
        self._debug_mode = coerce_bool_option(
            options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE),
            option_name=CONF_DEBUG_MODE,
            default=DEFAULT_DEBUG_MODE,
            logger=_LOGGER,
        )
        self._room_area_sync_force = coerce_bool_option(
            options.get(CONF_ROOM_AREA_SYNC_FORCE, DEFAULT_ROOM_AREA_SYNC_FORCE),
            option_name=CONF_ROOM_AREA_SYNC_FORCE,
            default=DEFAULT_ROOM_AREA_SYNC_FORCE,
            logger=_LOGGER,
        )
        self._command_result_verify = coerce_bool_option(
            options.get(CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY),
            option_name=CONF_COMMAND_RESULT_VERIFY,
            default=DEFAULT_COMMAND_RESULT_VERIFY,
            logger=_LOGGER,
        )
        self._device_filter_config = build_device_filter_config(options)
        self._device_filter_enabled = has_active_device_filter(
            self._device_filter_config
        )
        if self._device_filter_enabled:
            _LOGGER.debug("Device filter enabled in options")

        if self._debug_mode:
            _LOGGER.debug("Debug mode enabled")

    def _setup_anonymous_share(self) -> None:
        """Set up the anonymous share system based on config options."""
        options = self.config_entry.options if self.config_entry else {}
        enabled = coerce_bool_option(
            options.get(CONF_ANONYMOUS_SHARE_ENABLED, DEFAULT_ANONYMOUS_SHARE_ENABLED),
            option_name=CONF_ANONYMOUS_SHARE_ENABLED,
            default=DEFAULT_ANONYMOUS_SHARE_ENABLED,
            logger=_LOGGER,
        )
        errors = coerce_bool_option(
            options.get(CONF_ANONYMOUS_SHARE_ERRORS, DEFAULT_ANONYMOUS_SHARE_ERRORS),
            option_name=CONF_ANONYMOUS_SHARE_ERRORS,
            default=DEFAULT_ANONYMOUS_SHARE_ERRORS,
            logger=_LOGGER,
        )

        # Generate anonymous installation ID from config entry ID
        installation_id = None
        storage_path = None
        if self.config_entry:
            installation_id = hashlib.sha256(
                self.config_entry.entry_id.encode()
            ).hexdigest()[:16]
            # Use HA config directory for storage
            storage_path = self.hass.config.config_dir

        share_manager = get_anonymous_share_manager(self.hass)
        share_manager.set_enabled(
            enabled, errors, installation_id, storage_path, ha_version=HA_VERSION
        )
        _LOGGER.debug(
            "Anonymous share: enabled=%s, errors=%s",
            enabled,
            errors,
        )

    def _reset_runtime_state(self) -> None:
        """Clear runtime state to break circular references on shutdown."""
        self._entities.clear()
        self._entities_by_device.clear()
        self._devices.clear()
        self._device_by_id.clear()
        self._product_configs_by_id.clear()
        self._product_configs.clear()
        self._command_traces.clear()
        self._mqtt_message_cache.clear()
        self._missing_device_cycles.clear()
        self._pending_command_expectations.clear()
        self._device_state_latency_seconds.clear()
        self._last_device_refresh_at = 0.0
        self._mqtt_group_online_reconcile_task = None
        self._mqtt_group_online_reconcile_last_at = 0.0
        self._mqtt_runtime = None

    def _ensure_mqtt_runtime(self) -> MqttRuntime:
        """Ensure extracted MQTT runtime helper is available."""
        if self._mqtt_runtime is None:
            self._mqtt_runtime = MqttRuntime(
                self,
                polling_multiplier=_MQTT_POLLING_MULTIPLIER,
                connect_status_mqtt_stale_seconds=_CONNECT_STATUS_MQTT_STALE_SECONDS,
                logger=_LOGGER,
            )
        return self._mqtt_runtime

    def _record_command_trace(self, trace: dict[str, Any]) -> None:
        """Record one command trace when debug mode is enabled."""
        if not self._debug_mode:
            return

        self._command_traces.append(trace)

    def _build_status_metrics_snapshot(self) -> dict[str, Any]:
        """Build current runtime status-query metrics snapshot."""
        sample_count = len(self._state_batch_metrics)
        avg_batch_size: float | None = None
        avg_duration_seconds: float | None = None
        avg_fallback_depth: float | None = None
        if sample_count:
            batch_size_sum = 0
            duration_sum = 0.0
            fallback_sum = 0
            for (
                batch_size,
                duration_seconds,
                fallback_depth,
            ) in self._state_batch_metrics:
                batch_size_sum += max(0, int(batch_size))
                duration_sum += max(0.0, float(duration_seconds))
                fallback_sum += max(0, int(fallback_depth))
            avg_batch_size = batch_size_sum / sample_count
            avg_duration_seconds = duration_sum / sample_count
            avg_fallback_depth = fallback_sum / sample_count

        connect_decisions = len(self._connect_status_skip_history)
        connect_skip_ratio = (
            sum(self._connect_status_skip_history) / connect_decisions
            if connect_decisions
            else None
        )
        return {
            "state_batch_size_current": self._state_status_batch_size,
            "state_batch_size_avg": avg_batch_size,
            "state_batch_duration_avg_seconds": avg_duration_seconds,
            "state_fallback_depth_avg": avg_fallback_depth,
            "state_metrics_samples": sample_count,
            "connect_skip_ratio": connect_skip_ratio,
            "connect_skip_samples": connect_decisions,
            "connect_mqtt_stale_window_seconds": self._connect_status_mqtt_stale_seconds,
        }

    def build_developer_report(self) -> dict[str, Any]:
        """Build a sanitized runtime report for real-world troubleshooting."""
        share_manager = get_anonymous_share_manager(self.hass)
        pending_devices, pending_errors = share_manager.pending_count
        polling_interval_seconds = (
            int(self.update_interval.total_seconds())
            if self.update_interval is not None
            else None
        )
        report = build_coordinator_developer_report(
            config_entry=self.config_entry,
            debug_mode=self._debug_mode,
            mqtt_enabled=self._mqtt_enabled,
            mqtt_connected=self._mqtt_connected,
            polling_interval_seconds=polling_interval_seconds,
            last_update_success=self.last_update_success,
            devices=self._devices,
            group_count=len(self._group_ids_to_query),
            individual_count=len(self._iot_ids_to_query),
            outlet_count=len(self._outlet_ids_to_query),
            pending_devices=pending_devices,
            pending_errors=pending_errors,
            command_traces=list(self._command_traces),
            redact_identifier=_redact_identifier,
        )
        report["runtime"]["status_metrics"] = self._build_status_metrics_snapshot()
        return report

    def register_entity(self, entity: LiproEntity) -> None:
        """Register an entity for debounce protection tracking.

        Args:
            entity: The entity to register.

        """
        if entity.unique_id:
            self._entities[entity.unique_id] = entity
            # Index by device serial for efficient lookup
            device_serial = entity.device.serial
            entities = self._entities_by_device.setdefault(device_serial, [])
            # Guard against duplicate registration (e.g., during reload race)
            # using unique_id as the stable identity. If we see the same unique_id
            # again, replace the instance in-place so unregister of the old object
            # cannot remove the new one from the device index.
            for idx, existing in enumerate(entities):
                if existing.unique_id == entity.unique_id:
                    entities[idx] = entity
                    break
            else:
                entities.append(entity)

    def unregister_entity(self, entity: LiproEntity) -> None:
        """Unregister an entity.

        Args:
            entity: The entity to unregister.

        """
        if not entity.unique_id:
            return

        if self._entities.get(entity.unique_id) is entity:
            del self._entities[entity.unique_id]

        # Remove from device index using object identity to avoid unregistering
        # a stale entity instance removing a new instance with the same unique_id.
        device_serial = entity.device.serial
        if device_serial in self._entities_by_device:
            entities = self._entities_by_device[device_serial]
            self._entities_by_device[device_serial] = [
                e for e in entities if e is not entity
            ]
            if not self._entities_by_device[device_serial]:
                del self._entities_by_device[device_serial]

    def _get_protected_keys_for_device(self, device_serial: str) -> set[str]:
        """Get all protected property keys for a device.

        When entities are debouncing (user dragging slider), we should not
        overwrite their optimistic state with stale data from the cloud.

        Args:
            device_serial: The device serial number.

        Returns:
            Set of property keys that should not be overwritten.

        """
        protected_keys: set[str] = set()
        # Use indexed lookup for O(1) access instead of O(n) iteration
        for entity in self._entities_by_device.get(device_serial, []):
            protected_keys.update(entity.get_protected_keys())
        return protected_keys

    def _filter_protected_properties(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Filter out debounce-protected properties.

        Args:
            device_serial: The device serial number.
            properties: Properties to filter.

        Returns:
            Filtered properties dict.

        """
        protected_keys = self._get_protected_keys_for_device(device_serial)
        if not protected_keys:
            return properties

        filtered = {k: v for k, v in properties.items() if k not in protected_keys}

        if filtered != properties:
            _LOGGER.debug(
                "Skipping protected keys for device %s: %s",
                device_serial[:8] + "...",  # Redact for privacy
                protected_keys & properties.keys(),
            )

        return filtered

    def _filter_pending_command_mismatches(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """Filter stale values while waiting for command confirmation.

        If we recently sent CHANGE_STATE to a device, transient polls may still
        return old values. Keep optimistic keys stable by dropping mismatched
        values for pending keys until confirmed or timeout.
        """
        filtered, blocked_keys = (
            self._command_confirmation_tracker.filter_pending_command_mismatches(
                pending_expectations=self._pending_command_expectations,
                device_serial=device_serial,
                properties=properties,
            )
        )
        if not blocked_keys:
            return filtered

        _LOGGER.debug(
            "Skipping stale keys for device %s while command pending: %s",
            device_serial[:8] + "...",
            blocked_keys,
        )
        return filtered

    def _track_command_expectation(
        self,
        device_serial: str,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> None:
        """Track expected CHANGE_STATE values for adaptive confirmation."""
        self._command_confirmation_tracker.track_command_expectation(
            pending_expectations=self._pending_command_expectations,
            device_serial=device_serial,
            command=command,
            properties=properties,
        )

    def _update_state_latency(
        self,
        device_serial: str,
        observed_latency: float,
    ) -> None:
        """Update per-device command->state latency EWMA."""
        self._command_confirmation_tracker.update_state_latency(
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
            observed_latency=observed_latency,
        )

    def _observe_command_confirmation(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> None:
        """Observe property updates and confirm pending command expectations."""
        latency = self._command_confirmation_tracker.observe_command_confirmation(
            pending_expectations=self._pending_command_expectations,
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
            properties=properties,
        )
        if latency is None:
            return

        _LOGGER.debug(
            "Device %s: confirmed command state in %.2fs (adaptive delay=%.2fs)",
            device_serial[:8] + "...",
            latency,
            self._get_adaptive_post_refresh_delay(device_serial),
        )

    def _get_adaptive_post_refresh_delay(self, device_serial: str | None) -> float:
        """Get adaptive delayed-refresh value for a device."""
        return self._command_confirmation_tracker.get_adaptive_post_refresh_delay(
            device_state_latency_seconds=self._device_state_latency_seconds,
            device_serial=device_serial,
        )

    def _prune_runtime_state_for_devices(self, active_serials: set[str]) -> None:
        """Prune per-device runtime caches for removed devices."""
        self._command_confirmation_tracker.prune_runtime_state_for_devices(
            pending_expectations=self._pending_command_expectations,
            device_state_latency_seconds=self._device_state_latency_seconds,
            active_serials=active_serials,
        )

        active_normalized = {
            self._normalize_device_key(serial)
            for serial in active_serials
            if isinstance(serial, str) and serial.strip()
        }
        stale_mqtt_connect = set(self._last_mqtt_connect_state_at) - active_normalized
        for serial in stale_mqtt_connect:
            self._last_mqtt_connect_state_at.pop(serial, None)

        stale_connect_priority = (
            set(self._connect_status_priority_ids) - active_normalized
        )
        for serial in stale_connect_priority:
            self._connect_status_priority_ids.discard(serial)

    def _apply_properties_update(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        apply_protection: bool = True,
    ) -> dict[str, Any]:
        """Apply property updates to a device with optional debounce protection.

        Args:
            device: Target device.
            properties: Properties to update.
            apply_protection: Whether to filter debounce-protected keys.

        """
        if apply_protection:
            properties = self._filter_protected_properties(device.serial, properties)
            properties = self._filter_pending_command_mismatches(
                device.serial, properties
            )

        if not properties:
            return {}

        self._adapt_fan_gear_range(device, properties)
        device.update_properties(properties)
        self._observe_command_confirmation(device.serial, properties)
        if _LOGGER.isEnabledFor(logging.DEBUG):
            properties_summary = summarize_properties_for_log(properties)
            _LOGGER.debug(
                "Updated %s: count=%d keys=%s",
                device.name,
                properties_summary["count"],
                properties_summary["keys"],
            )
        return properties

    @staticmethod
    def _adapt_fan_gear_range(
        device: LiproDevice,
        properties: dict[str, Any],
    ) -> None:
        """Adapt fan speed upper-bound from observed runtime status.

        Some products do not expose ``maxFanGear`` in product config. For those
        devices, infer the real upper-bound from authoritative state payloads
        (REST/MQTT) so HA percentage mapping stays accurate.
        """
        if not device.is_fan_light:
            return

        raw_gear = properties.get(PROP_FAN_GEAR)
        if raw_gear is None:
            return

        try:
            observed_gear = int(str(raw_gear).strip())
        except (TypeError, ValueError):
            return

        # Ignore invalid/placeholder values; clamp abnormal outliers.
        if observed_gear <= 0:
            return
        observed_gear = min(observed_gear, 100)

        baseline_max = max(1, device.default_max_fan_gear_in_model)
        device.max_fan_gear = max(device.max_fan_gear, baseline_max)

        if observed_gear <= device.max_fan_gear:
            return

        old_max = device.max_fan_gear
        device.max_fan_gear = observed_gear
        _LOGGER.debug(
            "Device %s: inferred fan gear range 1-%d from runtime status (was 1-%d)",
            device.name,
            device.max_fan_gear,
            old_max,
        )

    async def _trigger_reauth(self, key: str, **placeholders: str) -> None:
        """Show auth notification and trigger reauth flow.

        Args:
            key: Translation key for the notification.
            **placeholders: Placeholder values for the notification message.

        """
        sanitized_placeholders = self._sanitize_auth_placeholders(placeholders)
        await self._async_show_auth_notification(key, **sanitized_placeholders)
        if self.config_entry:
            self.config_entry.async_start_reauth(self.hass)

    @staticmethod
    def _sanitize_auth_placeholders(placeholders: Mapping[str, Any]) -> dict[str, str]:
        """Sanitize auth placeholders to avoid raw error message leakage."""
        sanitized: dict[str, str] = {}
        for key, value in placeholders.items():
            if isinstance(value, BaseException):
                sanitized[key] = safe_error_placeholder(value)
                continue

            text = str(value).strip()
            if not text:
                continue

            if key == "error":
                # Only allow safe, structured markers (e.g. "401" or "LiproAuthError(code=401)").
                if (
                    text.isdigit() and len(text) <= 6
                ) or LiproDataUpdateCoordinator._is_safe_error_marker(text):
                    sanitized[key] = text
                else:
                    sanitized[key] = "AuthError"
                continue

            sanitized[key] = text
        return sanitized

    @staticmethod
    def _is_safe_error_marker(text: str) -> bool:
        """Return True when marker matches safe_error_placeholder() structure."""
        candidate = str(text).strip()
        if not candidate:
            return False
        if any(ch.isspace() for ch in candidate):
            return False
        if not candidate[:1].isalpha():
            return False

        # Accept "SomeError(code=401)" style (no raw message content).
        if "(" not in candidate or not candidate.endswith(")"):
            return False
        name, rest = candidate.split("(", 1)
        if not name or not name.replace("_", "").isalnum():
            return False
        inner = rest[:-1]
        if not inner.startswith("code="):
            return False
        code = inner.removeprefix("code=").strip()
        if not code or len(code) > 32:
            return False
        allowed = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:"
        )
        return all(ch in allowed for ch in code)

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return all devices."""
        return self._devices

    @property
    def _device_by_id(self) -> dict[str, LiproDevice]:
        """Compatibility alias for tests that access the raw identity dict."""
        return self._device_identity_index.mapping

    @_device_by_id.setter
    def _device_by_id(self, mapping: Any) -> None:
        """Replace device identity mapping while preserving index semantics."""
        if isinstance(mapping, Mapping):
            self._device_identity_index.replace(mapping)
            return
        self._device_identity_index.replace({})

    def get_device(self, serial: str) -> LiproDevice | None:
        """Get a device by serial number.

        Args:
            serial: Device serial number.

        Returns:
            Device or None if not found.

        """
        return self._devices.get(serial)

    def get_device_by_id(self, device_id: Any) -> LiproDevice | None:
        """Look up a device by any known identifier.

        Supports:
        - serial / iot_device_id: "03ab5ccd7cxxxxxx"
        - mesh group serial: "mesh_group_xxxxx"
        - gateway device ID (mapped via _query_group_status)

        Args:
            device_id: Any known device identifier.

        Returns:
            Device or None if not found.

        """
        return self._device_identity_index.get(device_id)

    @property
    def mqtt_connected(self) -> bool:
        """Return True if MQTT is connected."""
        return self._mqtt_connected

    async def _resolve_mqtt_decrypted_credentials(self) -> tuple[str, str] | None:
        """Fetch MQTT config and decrypt access credentials."""
        mqtt_config = await self.client.get_mqtt_config()
        credentials = extract_mqtt_encrypted_credentials(mqtt_config)
        if credentials is None:
            _LOGGER.warning("MQTT config missing accessKey or secretKey")
            return None

        encrypted_access_key, encrypted_secret_key = credentials
        access_key = await asyncio.to_thread(
            decrypt_mqtt_credential, encrypted_access_key
        )
        secret_key = await asyncio.to_thread(
            decrypt_mqtt_credential, encrypted_secret_key
        )
        return access_key, secret_key

    def _create_mqtt_client(
        self,
        *,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
    ) -> LiproMqttClient:
        """Create configured MQTT client instance."""
        return LiproMqttClient(
            access_key=access_key,
            secret_key=secret_key,
            biz_id=biz_id,
            phone_id=phone_id,
            on_message=self._on_mqtt_message,
            on_connect=self._on_mqtt_connect,
            on_disconnect=self._on_mqtt_disconnect,
        )

    async def _start_mqtt_for_current_devices(
        self, mqtt_client: LiproMqttClient
    ) -> None:
        """Start MQTT client with subscriptions for current devices."""
        # For mesh groups: use their serial (mesh_group_xxx) as the topic
        # For non-group devices: use their serial directly
        # Note: iot_device_id is an alias for serial, so we always use serial
        device_ids = build_mqtt_subscription_device_ids(self._devices)
        for mesh_group_serial in iter_mesh_group_serials(self._devices):
            _LOGGER.debug("MQTT: subscribing to mesh group %s", mesh_group_serial)

        await mqtt_client.start(device_ids)
        _LOGGER.info(
            "MQTT client setup complete, subscribing to %d devices",
            len(device_ids),
        )

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates.

        Returns:
            True if MQTT setup was successful.

        """
        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False
        try:
            credentials = await self._resolve_mqtt_decrypted_credentials()
            if credentials is None:
                return False
            access_key, secret_key = credentials

            biz_id = resolve_mqtt_biz_id(self.config_entry.data)
            if biz_id is None:
                _LOGGER.warning("No biz_id available for MQTT")
                return False
            self._biz_id = biz_id
            phone_id = self.config_entry.data.get(CONF_PHONE_ID, "")

            self._mqtt_client = self._create_mqtt_client(
                access_key=access_key,
                secret_key=secret_key,
                biz_id=biz_id,
                phone_id=phone_id,
            )
            await self._start_mqtt_for_current_devices(self._mqtt_client)
            return True

        except (LiproApiError, ValueError) as err:
            _LOGGER.warning("Failed to setup MQTT: %s", err)
            return False

    async def _async_setup_mqtt_safe(self) -> None:
        """Safely set up MQTT client, resetting flag on completion."""
        setup_succeeded = False
        cancelled = False
        try:
            setup_succeeded = await self.async_setup_mqtt()
        except asyncio.CancelledError:
            cancelled = True
            raise
        finally:
            if not cancelled:
                if setup_succeeded:
                    self._mqtt_setup_backoff.on_success()
                else:
                    self._mqtt_setup_backoff.on_failure(monotonic())
                    self._mqtt_setup_backoff_gate_logged = False
            self._mqtt_setup_in_progress = False

    async def async_stop_mqtt(self) -> None:
        """Stop MQTT client."""
        if self._mqtt_client:
            await self._mqtt_client.stop()
            self._mqtt_client = None
            self._mqtt_connected = False
            _LOGGER.info("MQTT client stopped")

    async def _sync_mqtt_subscriptions(self) -> None:
        """Sync MQTT subscriptions with current device list."""
        if not self._mqtt_client:
            return

        # serial works for both: mesh_group_xxx (groups) and iot_device_id (non-groups)
        expected = {dev.serial for dev in self._devices.values()}
        await self._mqtt_client.sync_subscriptions(expected)

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and release all resources."""
        # Cancel update timer FIRST to prevent polls during cleanup.
        # Without this, a scheduled poll could fire after _devices is cleared,
        # triggering _fetch_devices() and unnecessary API calls during shutdown.
        await super().async_shutdown()

        if self._mqtt_listener_update_handle is not None:
            self._mqtt_listener_update_handle.cancel()
            self._mqtt_listener_update_handle = None

        # Cancel pending delayed refresh tasks.
        delayed_tasks = list(self._post_command_refresh_tasks.values())
        self._post_command_refresh_tasks.clear()
        for task in delayed_tasks:
            if not task.done():
                task.cancel()

        await self._async_cancel_background_tasks()

        # Submit anonymous share report before shutdown (if enabled)
        try:
            share_manager = get_anonymous_share_manager(self.hass)
            if share_manager.is_enabled:
                session = async_get_clientsession(self.hass)
                await share_manager.submit_report(session)
        except (OSError, TimeoutError):
            _LOGGER.warning("Failed to submit anonymous share report on shutdown")

        # Stop MQTT client
        try:
            await self.async_stop_mqtt()
        except (OSError, TimeoutError):
            _LOGGER.warning("Failed to stop MQTT client on shutdown")

        # Close API client session
        try:
            await self.client.close()
        except (OSError, TimeoutError):
            _LOGGER.warning("Failed to close API client on shutdown")

        # Clear all data structures to break circular references
        self._reset_runtime_state()

        _LOGGER.debug("Coordinator shutdown complete")

    def _track_background_task(
        self, coro: Coroutine[Any, Any, Any]
    ) -> asyncio.Task[Any]:
        """Create and track a background task for centralized shutdown cleanup."""
        return self._background_task_manager.create(
            coro,
            create_task=self.hass.async_create_task,
        )

    def _on_background_task_done(self, task: asyncio.Task[Any]) -> None:
        """Finalize tracked background task and consume terminal exceptions."""
        self._background_task_manager.on_done(task)

    async def _async_cancel_background_tasks(self) -> None:
        """Cancel and await tracked background tasks."""
        await self._background_task_manager.cancel_all()

    def _on_mqtt_connect(self) -> None:
        """Handle MQTT connection."""
        # Dismiss any previous disconnect issue
        async_delete_issue(self.hass, DOMAIN, "mqtt_disconnected")
        self._ensure_mqtt_runtime().on_connect()

    def _on_mqtt_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._ensure_mqtt_runtime().on_disconnect()

    def _check_mqtt_disconnect_notification(self) -> None:
        """Send persistent notification if MQTT has been disconnected too long."""
        self._ensure_mqtt_runtime().check_disconnect_notification()

    async def _async_show_mqtt_disconnect_notification(self, minutes: int) -> None:
        """Create a repair issue for MQTT disconnect."""
        async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id="mqtt_disconnected",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="mqtt_disconnected",
            translation_placeholders={"minutes": str(minutes)},
        )

    @property
    def _base_scan_interval(self) -> int:
        """Get the configured base scan interval in seconds."""
        options = self.config_entry.options if self.config_entry else None
        return resolve_base_scan_interval_seconds(
            options=options,
            option_name=CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
            min_value=MIN_SCAN_INTERVAL,
            max_value=MAX_SCAN_INTERVAL,
            logger=_LOGGER,
        )

    def _on_mqtt_message(self, device_id: str, properties: dict[str, Any]) -> None:
        """Handle MQTT message with device status update.

        This callback is invoked from aiomqtt's async message iterator,
        which runs on the event loop, so no thread-safety wrapper is needed.

        Implements deduplication to handle duplicate MQTT messages that may
        arrive in quick succession (common with Lipro devices).

        Args:
            device_id: IoT device ID.
            properties: Flattened device properties.

        """
        device = self._resolve_mqtt_message_device(device_id)
        if not device:
            return

        current_time = monotonic()
        if self._is_duplicate_mqtt_payload(
            device_id=device_id,
            device_name=device.name,
            properties=properties,
            current_time=current_time,
        ):
            return

        applied = self._apply_properties_update(device, properties)
        self._after_mqtt_properties_applied(device, applied, current_time=current_time)

    def _schedule_mqtt_listener_update(self) -> None:
        """Coalesce listener updates triggered by MQTT bursts."""
        if not self.hass.loop.is_running():
            self.async_update_listeners()
            return

        if self._mqtt_listener_update_handle is not None:
            return

        self._mqtt_listener_update_handle = self.hass.loop.call_later(
            _MQTT_LISTENER_UPDATE_DEBOUNCE_SECONDS,
            self._flush_mqtt_listener_update,
        )

    def _flush_mqtt_listener_update(self) -> None:
        """Flush one coalesced MQTT listener update."""
        self._mqtt_listener_update_handle = None
        self.async_update_listeners()

    def _resolve_mqtt_message_device(self, device_id: str) -> LiproDevice | None:
        """Resolve MQTT message target device by known identifier mappings."""
        device = self.get_device_by_id(device_id)
        if device is not None:
            return device

        _LOGGER.debug("MQTT message for unknown device: %s...", device_id[:8])
        return None

    @staticmethod
    def _normalize_device_key(device_id: str) -> str:
        """Normalize runtime device identifiers for per-device caches."""
        return device_id.strip().lower()

    def _is_duplicate_mqtt_payload(
        self,
        *,
        device_id: str,
        device_name: str,
        properties: dict[str, Any],
        current_time: float,
    ) -> bool:
        """Return True when payload duplicates a recent MQTT message for the device."""
        props_hash = compute_properties_hash(properties)
        if props_hash is None:
            _LOGGER.debug(
                "MQTT: cannot hash properties for %s, skipping dedup", device_name
            )
            return False

        cache_key = build_dedup_cache_key(device_id, props_hash)
        if is_duplicate_within_window(
            self._mqtt_message_cache,
            cache_key=cache_key,
            current_time=current_time,
            dedup_window=self._mqtt_dedup_window,
        ):
            if self._debug_mode:
                last_time = self._mqtt_message_cache.get(cache_key)
                if last_time is not None:
                    _LOGGER.debug(
                        "MQTT: skipping duplicate message for %s (%.2fs ago)",
                        device_name,
                        current_time - last_time,
                    )
            return True

        self._mqtt_message_cache[cache_key] = current_time
        if len(self._mqtt_message_cache) > MAX_MQTT_CACHE_SIZE:
            self._cleanup_mqtt_cache(current_time)
        return False

    def _schedule_mqtt_group_online_reconciliation(
        self, *, device_name: str, now: float
    ) -> None:
        """Schedule one REST refresh for group-online MQTT reconnect bursts."""
        task = self._mqtt_group_online_reconcile_task
        if task is not None and not task.done():
            return

        if (
            self._mqtt_group_online_reconcile_last_at > 0
            and now - self._mqtt_group_online_reconcile_last_at
            < _MQTT_GROUP_ONLINE_RECONCILE_COOLDOWN_SECONDS
        ):
            return

        self._mqtt_group_online_reconcile_last_at = now
        _LOGGER.debug(
            "MQTT: device %s online, scheduling REST API reconciliation",
            device_name,
        )
        task = self._track_background_task(self.async_request_refresh())
        self._mqtt_group_online_reconcile_task = task
        task.add_done_callback(self._clear_mqtt_group_online_reconcile_task)

    def _clear_mqtt_group_online_reconcile_task(self, task: asyncio.Task[Any]) -> None:
        """Clear single-flight task handle once reconciliation completes."""
        if task is self._mqtt_group_online_reconcile_task:
            self._mqtt_group_online_reconcile_task = None

    def _after_mqtt_properties_applied(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        current_time: float | None = None,
    ) -> None:
        """Run post-update notifications and reconciliation scheduling hooks."""
        if not properties:
            return

        # Notify listeners (coalesced) for MQTT update bursts.
        # Note: async_set_updated_data won't trigger updates when always_update=False
        # and the same dict object is passed, so we use async_update_listeners.
        self._schedule_mqtt_listener_update()

        # Fallback: when a device comes back online, schedule an immediate
        # REST API refresh to reconcile state. In mesh groups, sub-devices
        # may reconnect with a different state than the group reports.
        connect_state = properties.get(PROP_CONNECT_STATE)
        now = monotonic() if current_time is None else current_time
        if connect_state is not None:
            normalized = self._normalize_device_key(device.serial)
            self._last_mqtt_connect_state_at[normalized] = now
            self._connect_status_priority_ids.discard(normalized)
        if device.is_group and is_online_connect_state(connect_state):
            self._schedule_mqtt_group_online_reconciliation(
                device_name=device.name,
                now=now,
            )

    def _cleanup_mqtt_cache(self, current_time: float) -> None:
        """Clean up stale MQTT dedup cache entries.

        Removes entries older than 5 seconds. If cache still exceeds limit,
        keeps the newest half.

        Args:
            current_time: Current monotonic time.

        """
        self._mqtt_message_cache = cleanup_dedup_cache(
            self._mqtt_message_cache,
            current_time=current_time,
            stale_seconds=_MQTT_CACHE_STALE_SECONDS,
            max_entries=MAX_MQTT_CACHE_SIZE,
        )

    async def _async_show_auth_notification(
        self,
        key: str,
        **placeholders: str,
    ) -> None:
        """Create a repair issue for authentication errors.

        Args:
            key: The translation key (e.g., "auth_expired", "auth_error").
            **placeholders: Placeholder values for the translation string.

        """
        async_create_issue(
            self.hass,
            domain=DOMAIN,
            issue_id=key,
            is_fixable=True,
            severity=IssueSeverity.ERROR,
            translation_key=key,
            translation_placeholders=placeholders or None,
        )

    def _clear_auth_issues(self) -> None:
        """Clear auth-related repair issues once authentication is healthy."""
        async_delete_issue(self.hass, DOMAIN, "auth_expired")
        async_delete_issue(self.hass, DOMAIN, "auth_error")

    async def _async_ensure_authenticated(self) -> None:
        """Ensure a valid access token and clear stale auth issues."""
        await self.auth_manager.ensure_valid_token()
        self._clear_auth_issues()

    def _should_refresh_device_list(self) -> bool:
        """Return True when a full device-list refresh should run."""
        return should_refresh_device_list_runtime(
            has_devices=bool(self._devices),
            force_device_refresh=self._force_device_refresh,
            last_device_refresh_at=self._last_device_refresh_at,
            now=monotonic(),
            refresh_interval_seconds=_DEVICE_LIST_REFRESH_INTERVAL_SECONDS,
        )

    def _schedule_mqtt_setup_if_needed(self) -> None:
        """Ensure MQTT setup task is scheduled when runtime conditions match."""
        if not should_schedule_mqtt_setup(
            mqtt_enabled=self._mqtt_enabled,
            has_mqtt_client=self._mqtt_client is not None,
            mqtt_setup_in_progress=self._mqtt_setup_in_progress,
            has_devices=bool(self._devices),
        ):
            return

        now = monotonic()
        if not self._mqtt_setup_backoff.should_attempt(now):
            if not self._mqtt_setup_backoff_gate_logged:
                _LOGGER.debug("Skipping MQTT setup attempt due to retry backoff gate")
                self._mqtt_setup_backoff_gate_logged = True
            return

        self._mqtt_setup_backoff_gate_logged = False

        self._mqtt_setup_in_progress = True
        self._track_background_task(self._async_setup_mqtt_safe())

    async def _raise_update_data_error(self, err: Exception) -> NoReturn:
        """Map API/auth exceptions to Home Assistant update errors."""
        error_marker = safe_error_placeholder(err)
        if isinstance(err, LiproRefreshTokenExpiredError):
            await self._trigger_reauth("auth_expired")
            msg = f"Refresh token expired, re-authentication required ({error_marker})"
            raise ConfigEntryAuthFailed(msg) from err
        if isinstance(err, LiproAuthError):
            await self._trigger_reauth("auth_error", error=error_marker)
            msg = f"Authentication error ({error_marker})"
            raise ConfigEntryAuthFailed(msg) from err
        if isinstance(err, LiproConnectionError):
            msg = f"Connection error ({error_marker})"
            raise UpdateFailed(msg) from err
        if isinstance(err, LiproApiError):
            msg = f"API error ({error_marker})"
            raise UpdateFailed(msg) from err

        raise err

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API.

        Returns:
            Dictionary of devices keyed by serial.

        Raises:
            UpdateFailed: If update fails.

        """
        try:
            await self._async_ensure_authenticated()

            # Periodically refresh the full device list to discover newly paired devices.
            if self._should_refresh_device_list():
                self._force_device_refresh = False
                await self._fetch_devices()
                # Load product configs and apply color temp ranges
                await self._load_product_configs()

            # Query device status
            await self._update_device_status()

            # Ensure MQTT client is running (retry if previous setup failed).
            self._schedule_mqtt_setup_if_needed()

            # Notify user if MQTT has been disconnected for too long
            self._check_mqtt_disconnect_notification()

            return self._devices

        except (
            LiproRefreshTokenExpiredError,
            LiproAuthError,
            LiproConnectionError,
            LiproApiError,
        ) as err:
            await self._raise_update_data_error(err)

    async def _fetch_devices(self) -> None:
        """Fetch all devices from API with pagination."""
        _LOGGER.debug("Fetching device list")

        previous_devices = self._devices
        previous_serials = set(previous_devices)
        devices_data = await self._fetch_all_device_pages()
        snapshot = build_fetched_device_snapshot(
            devices_data,
            device_filter=self._device_row_passes_filter
            if self._device_filter_enabled
            else None,
        )
        self._apply_fetched_device_snapshot(snapshot)
        self._sync_device_room_assignments(previous_devices)
        self._last_device_refresh_at = monotonic()
        self._force_connect_status_refresh = True
        self._schedule_reload_for_added_devices(previous_serials)
        await self._record_devices_for_anonymous_share()
        await self._reconcile_stale_devices(previous_serials)

        if self._mqtt_client and self._mqtt_connected:
            await self._sync_mqtt_subscriptions()

    def _device_row_passes_filter(self, device_data: dict[str, Any]) -> bool:
        """Return True when one raw device row passes configured filters."""
        return is_device_included_by_filter(device_data, self._device_filter_config)

    def _schedule_reload_for_added_devices(self, previous_serials: set[str]) -> None:
        """Reload config entry when new devices are discovered after initial setup."""
        if not previous_serials or self.config_entry is None:
            return

        current_serials = set(self._devices)
        added_serials = current_serials - previous_serials
        if not added_serials:
            return

        _LOGGER.info(
            "Discovered %d new Lipro device(s), scheduling entry reload",
            len(added_serials),
        )
        self._track_background_task(
            self.hass.config_entries.async_reload(self.config_entry.entry_id)
        )

    @staticmethod
    def _parse_device_list_page(
        result: Any,
        *,
        limit: int,
        logger: logging.Logger = _LOGGER,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Parse one devices page payload from API.

        Returns:
            (devices, has_more)
        """
        if not isinstance(result, dict):
            msg = (
                "Malformed device list response: expected object, "
                f"got {type(result).__name__}"
            )
            raise LiproApiError(msg)

        raw_page = result.get("devices", [])
        if raw_page is None:
            raw_page = []
        if not isinstance(raw_page, list):
            msg = (
                "Malformed device list payload: expected devices list, "
                f"got {type(raw_page).__name__}"
            )
            raise LiproApiError(msg)

        page = [item for item in raw_page if isinstance(item, dict)]
        if len(page) != len(raw_page):
            logger.debug(
                "Skipping %d malformed device rows from API payload",
                len(raw_page) - len(page),
            )

        has_more = len(raw_page) >= limit
        return page, has_more

    async def _fetch_all_device_pages(self) -> list[dict[str, Any]]:
        """Fetch full device list from paginated API responses."""
        devices_data: list[dict[str, Any]] = []
        offset = 0
        page_count = 0

        while True:
            if page_count >= _MAX_DEVICE_LIST_PAGES:
                msg = (
                    "Malformed device list response: pagination exceeded "
                    f"{_MAX_DEVICE_LIST_PAGES} pages"
                )
                raise LiproApiError(msg)

            result: Any = await self.client.get_devices(
                offset=offset,
                limit=MAX_DEVICES_PER_QUERY,
            )
            page_count += 1

            page, has_more = self._parse_device_list_page(
                result,
                limit=MAX_DEVICES_PER_QUERY,
            )
            devices_data.extend(page)
            if not has_more:
                return devices_data
            offset += MAX_DEVICES_PER_QUERY

    def _apply_fetched_device_snapshot(self, snapshot: FetchedDeviceSnapshot) -> None:
        """Apply refreshed device snapshot atomically."""
        self._devices = snapshot.devices
        self._device_by_id = snapshot.device_by_id
        self._iot_ids_to_query = snapshot.iot_ids
        self._group_ids_to_query = snapshot.group_ids
        self._outlet_ids_to_query = snapshot.outlet_ids

        _LOGGER.info(
            "Fetched %d devices (%d groups, %d individual, %d outlets)",
            len(self._devices),
            len(self._group_ids_to_query),
            len(self._iot_ids_to_query),
            len(self._outlet_ids_to_query),
        )

    @staticmethod
    def _normalize_room_name(room_name: str | None) -> str | None:
        """Normalize room names from cloud payloads to comparable values."""
        return normalize_room_name_runtime(room_name)

    def _sync_device_room_assignments(
        self, previous_devices: dict[str, LiproDevice]
    ) -> None:
        """Best-effort sync of cloud room changes into HA device registry areas.

        Sync policy:
        1. Always update suggested_area when room changes.
        2. Update area_id only when safe:
           - no current area assigned, or
           - current area name matches previous cloud room (cloud-managed).
        3. Preserve user-customized areas.
        """
        if not previous_devices:
            return

        device_registry = dr.async_get(self.hass)
        area_registry = ar.async_get(self.hass)
        area_id_cache: dict[str, str] = {}

        def _get_area_id(room_name: str) -> str:
            cached = area_id_cache.get(room_name)
            if cached is not None:
                return cached
            area_id = area_registry.async_get_or_create(room_name).id
            area_id_cache[room_name] = area_id
            return area_id

        for serial, device in self._devices.items():
            previous = previous_devices.get(serial)
            if previous is None:
                continue

            old_room_name = self._normalize_room_name(previous.room_name)
            new_room_name = self._normalize_room_name(device.room_name)
            if old_room_name == new_room_name:
                continue

            device_entry = device_registry.async_get_device(
                identifiers={(DOMAIN, serial)}
            )
            if device_entry is None:
                continue

            update_kwargs: dict[str, Any] = {"suggested_area": new_room_name}
            current_area_id = device_entry.area_id
            current_area_name: str | None = None
            if not self._room_area_sync_force and current_area_id is not None:
                current_area = area_registry.async_get_area(current_area_id)
                if current_area is not None:
                    current_area_name = self._normalize_room_name(current_area.name)

            update_area, target_area_name = resolve_room_area_target_name_runtime(
                room_area_sync_force=self._room_area_sync_force,
                old_room_name=old_room_name,
                new_room_name=new_room_name,
                current_area_id=current_area_id,
                current_area_name=current_area_name,
            )
            if update_area:
                if target_area_name is None:
                    update_kwargs["area_id"] = None
                else:
                    update_kwargs["area_id"] = _get_area_id(target_area_name)

            device_registry.async_update_device(device_entry.id, **update_kwargs)
            _LOGGER.debug(
                "Synced room mapping for %s: %s -> %s (area_updated=%s)",
                serial,
                old_room_name,
                new_room_name,
                "area_id" in update_kwargs,
            )

    async def _record_devices_for_anonymous_share(self) -> None:
        """Record fetched devices for anonymous diagnostics sharing."""
        share_manager = get_anonymous_share_manager(self.hass)
        if not share_manager.is_enabled:
            return

        await share_manager.async_ensure_loaded()
        share_manager.record_devices(list(self._devices.values()))

    async def _reconcile_stale_devices(self, previous_serials: set[str]) -> None:
        """Remove devices missing for consecutive full refresh cycles."""
        current_serials = set(self._devices)
        self._prune_runtime_state_for_devices(current_serials)

        reconcile_plan = plan_stale_device_reconciliation(
            previous_serials=previous_serials,
            current_serials=current_serials,
            missing_cycles=self._missing_device_cycles,
            remove_threshold=_STALE_DEVICE_REMOVE_THRESHOLD,
        )
        self._missing_device_cycles = reconcile_plan.missing_cycles

        if not reconcile_plan.removable_serials:
            return

        await self._async_remove_stale_devices(reconcile_plan.removable_serials)
        for serial in reconcile_plan.removable_serials:
            self._missing_device_cycles.pop(serial, None)

    async def _async_remove_stale_devices(self, stale_serials: set[str]) -> None:
        """Remove devices that no longer exist in the cloud.

        Args:
            stale_serials: Set of device serial numbers that are no longer present.

        """
        if not self.config_entry:
            return

        device_registry = dr.async_get(self.hass)

        for serial in stale_serials:
            # Find device in registry by identifier
            device_entry = device_registry.async_get_device(
                identifiers={(DOMAIN, serial)},
            )
            if device_entry:
                _LOGGER.info(
                    "Removing stale device: %s (serial: %s)",
                    device_entry.name,
                    serial,
                )
                device_registry.async_remove_device(device_entry.id)

    async def _load_product_configs(self) -> None:
        """Load product configurations and apply color temp ranges to devices.

        Product configs contain minTemperature and maxTemperature values
        which define the color temperature range for each product type.

        Matching priority (same as Lipro App):
        1. Match by productId -> config.id (most accurate)
        2. Match by iotName -> config.fwIotName (fallback)
        """
        if self._product_configs_by_id or self._product_configs:
            # Already loaded; re-apply for latest fetched snapshot.
            self._apply_product_configs_to_devices(
                self._product_configs_by_id,
                self._product_configs,
            )
            return

        try:
            configs = await self.client.get_product_configs()
            _LOGGER.debug("Loaded %d product configurations", len(configs))

            configs_by_id, configs_by_iot_name = index_product_configs_runtime(configs)
            self._product_configs_by_id = configs_by_id
            self._product_configs = configs_by_iot_name
            self._apply_product_configs_to_devices(configs_by_id, configs_by_iot_name)

        except LiproApiError as err:
            _LOGGER.warning("Failed to load product configs: %s", err)
            # Continue with default values

    def _apply_product_configs_to_devices(
        self,
        configs_by_id: dict[int, dict[str, Any]],
        configs_by_iot_name: dict[str, dict[str, Any]],
    ) -> None:
        """Match and apply cached product-config overrides to all devices."""
        for device in self._devices.values():
            matched_config = self._match_product_config(
                device,
                configs_by_id,
                configs_by_iot_name,
            )
            if matched_config:
                self._apply_product_config(device, matched_config)

    def _match_product_config(
        self,
        device: LiproDevice,
        configs_by_id: dict[int, dict[str, Any]],
        configs_by_iot_name: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Match one device to its best product config."""
        return match_product_config_runtime(
            device,
            configs_by_id=configs_by_id,
            configs_by_iot_name=configs_by_iot_name,
            logger=_LOGGER,
        )

    def _apply_product_config(
        self,
        device: LiproDevice,
        config: dict[str, Any],
    ) -> None:
        """Apply matched product-config overrides to runtime device model."""
        apply_product_config_runtime(device, config, logger=_LOGGER)

    async def _update_device_status(self) -> None:
        """Update status for all devices."""
        status_tasks = []

        # Query individual devices
        if self._iot_ids_to_query:
            status_tasks.append(self._query_device_status())

        # Query mesh groups
        if self._group_ids_to_query:
            status_tasks.append(self._query_group_status())

        # Query outlet power info (if enabled and interval has passed)
        if (
            self._power_monitoring_enabled
            and self._outlet_ids_to_query
            and self._should_query_power()
        ):
            status_tasks.append(self._query_outlet_power())

        if status_tasks:
            await asyncio.gather(*status_tasks)

        # Query real-time connection status LAST so it deterministically
        # overrides potentially stale connectState values from status APIs.
        connect_ids = self._resolve_connect_status_query_ids()
        if connect_ids:
            await self._query_connect_status(connect_ids)

    def _resolve_connect_status_query_ids(self) -> list[str]:
        """Resolve the connect-status query candidate IDs for this refresh cycle."""
        iot_ids = list(self._iot_ids_to_query)
        if not iot_ids:
            return []

        force_refresh = self._force_connect_status_refresh
        now = monotonic()
        decision = self._compute_connect_status_query_decision(
            iot_ids=iot_ids,
            force_refresh=force_refresh,
            now=now,
        )
        self._apply_connect_status_query_decision(
            decision,
            force_refresh=force_refresh,
            iot_ids=iot_ids,
        )

        return decision.query_ids

    def _compute_connect_status_query_decision(
        self,
        *,
        iot_ids: list[str],
        force_refresh: bool,
        now: float,
    ) -> ConnectStatusQueryDecision:
        """Compute connect-status query decision for the refresh tick."""
        query_interval_seconds = self._resolve_connect_status_query_interval_seconds(
            now,
        )
        return resolve_connect_status_query_candidates(
            iot_ids=iot_ids,
            force_refresh=force_refresh,
            mqtt_enabled=self._mqtt_enabled,
            mqtt_connected=self._mqtt_connected,
            last_query_time=self._last_connect_status_query_time,
            now=now,
            priority_ids=self._connect_status_priority_ids,
            mqtt_recent_time_by_id=self._last_mqtt_connect_state_at,
            stale_window_seconds=self._connect_status_mqtt_stale_seconds,
            query_interval_seconds=query_interval_seconds,
            normalize=self._normalize_device_key,
        )

    def _apply_connect_status_query_decision(
        self,
        decision: ConnectStatusQueryDecision,
        *,
        force_refresh: bool,
        iot_ids: list[str],
    ) -> None:
        """Apply connect-status decision side effects to coordinator state."""
        self._last_connect_status_query_time = decision.next_last_query_time

        # Force-refresh flag should be consumed once candidates are evaluated.
        if force_refresh:
            self._force_connect_status_refresh = False

        if decision.record_skip is not None:
            self._record_connect_status_decision(skipped=decision.record_skip)
        if decision.record_skip:
            skip_ratio = (
                sum(self._connect_status_skip_history)
                / len(self._connect_status_skip_history)
                if self._connect_status_skip_history
                else 0.0
            )
            _LOGGER.debug(
                "Skipping connect-status query: MQTT connectState is fresh for all %d devices "
                "(stale_window=%.1fs, skip_ratio=%.2f)",
                len(iot_ids),
                self._connect_status_mqtt_stale_seconds,
                skip_ratio,
            )

    def _resolve_connect_status_query_interval_seconds(self, now: float) -> float:
        """Resolve connect-status polling interval with MQTT degradation fallback."""
        return resolve_connect_status_query_interval_seconds_runtime(
            mqtt_enabled=self._mqtt_enabled,
            mqtt_connected=self._mqtt_connected,
            mqtt_disconnect_time=self._mqtt_disconnect_time,
            backoff_allows_attempt=self._mqtt_setup_backoff.should_attempt(now),
            normal_interval_seconds=_CONNECT_STATUS_QUERY_INTERVAL_SECONDS,
            degraded_interval_seconds=_CONNECT_STATUS_QUERY_INTERVAL_DEGRADED_SECONDS,
        )

    def _record_connect_status_decision(self, *, skipped: bool) -> None:
        """Record one connect-status skip decision and tune stale window."""
        self._connect_status_skip_history.append(skipped)
        self._adapt_connect_status_stale_window()

    def _adapt_connect_status_stale_window(self) -> None:
        """Adapt MQTT stale window based on recent connect skip ratio."""
        history = self._connect_status_skip_history
        current = self._connect_status_mqtt_stale_seconds
        updated = adapt_connect_status_stale_window_runtime(
            history=history,
            current_stale_seconds=current,
            window_size=_CONNECT_STATUS_SKIP_RATIO_WINDOW,
            skip_ratio_low=_CONNECT_STATUS_SKIP_RATIO_LOW,
            skip_ratio_high=_CONNECT_STATUS_SKIP_RATIO_HIGH,
            adjust_step_seconds=_CONNECT_STATUS_STALE_ADJUST_STEP_SECONDS,
            min_stale_seconds=_CONNECT_STATUS_MQTT_STALE_MIN_SECONDS,
            max_stale_seconds=_CONNECT_STATUS_MQTT_STALE_MAX_SECONDS,
        )
        if updated == current:
            return

        self._connect_status_mqtt_stale_seconds = updated
        skip_ratio = sum(history) / len(history) if history else 0.0
        _LOGGER.debug(
            "Adaptive connect stale window changed: %.1fs -> %.1fs (skip_ratio=%.2f, window=%d)",
            current,
            updated,
            skip_ratio,
            len(history),
        )

    def _should_query_power(self) -> bool:
        """Check if power query should be executed based on interval.

        Returns:
            True if power query should be executed.

        """
        current_time = monotonic()
        if current_time - self._last_power_query_time >= self._power_query_interval:
            self._last_power_query_time = current_time
            return True
        return False

    async def _query_device_status(self) -> None:
        """Query status for individual devices."""
        status_list = await self.client.query_device_status(
            self._iot_ids_to_query,
            max_devices_per_query=self._state_status_batch_size,
            on_batch_metric=self._record_state_batch_metric,
        )
        self._adapt_state_batch_size()

        for status_data in status_list:
            self._apply_device_status_row(status_data)

    def _record_state_batch_metric(
        self,
        batch_size: int,
        duration_seconds: float,
        fallback_depth: int,
    ) -> None:
        """Record one state-batch metric sample for runtime adaptation."""
        sample = normalize_state_batch_metric(
            batch_size,
            duration_seconds,
            fallback_depth,
        )
        self._state_batch_metrics.append(sample)
        _LOGGER.debug(
            "State batch metric: size=%d duration=%.3fs fallback_depth=%d current_batch=%d",
            sample[0],
            sample[1],
            sample[2],
            self._state_status_batch_size,
        )

    def _adapt_state_batch_size(self) -> None:
        """Adapt state batch size using recent latency/fallback metrics."""
        if not self._state_batch_metrics:
            return

        current = self._state_status_batch_size
        upper = min(MAX_DEVICES_PER_QUERY, _STATE_STATUS_BATCH_SIZE_MAX)
        updated = compute_adaptive_state_batch_size(
            current_batch_size=current,
            recent_metrics=self._state_batch_metrics,
            batch_size_min=_STATE_STATUS_BATCH_SIZE_MIN,
            batch_size_max=upper,
            batch_adjust_step=_STATE_STATUS_BATCH_ADJUST_STEP,
            metrics_sample_size=_STATE_STATUS_BATCH_METRICS_SAMPLE_SIZE,
            latency_low_seconds=_STATE_STATUS_BATCH_LATENCY_LOW_SECONDS,
            latency_high_seconds=_STATE_STATUS_BATCH_LATENCY_HIGH_SECONDS,
        )
        if updated == current:
            return

        avg_latency, max_depth, sample_count = summarize_recent_state_batch_metrics(
            list(self._state_batch_metrics),
            sample_size=_STATE_STATUS_BATCH_METRICS_SAMPLE_SIZE,
        )

        self._state_status_batch_size = updated
        _LOGGER.debug(
            "Adaptive state batch size changed: %d -> %d (avg_latency=%.3fs, max_fallback_depth=%d, samples=%d)",
            current,
            updated,
            avg_latency,
            max_depth,
            sample_count,
        )

    def _apply_device_status_row(self, status_data: dict[str, Any]) -> None:
        """Apply one device-status row to a mapped device."""
        device_id = status_data.get("deviceId")
        if not device_id:
            return

        device = self.get_device_by_id(device_id)
        if not device:
            return

        raw_properties = status_data.get("properties")
        if raw_properties:
            properties = parse_properties_list(raw_properties)
            self._apply_properties_update(device, properties)

    async def _query_group_status(self) -> None:
        """Query status for mesh groups.

        API Response structure:
        {
            "data": [
                {
                    "groupId": "mesh_group_10001",
                    "devices": [...],
                    "properties": [...],
                    "hasBindGateway": true,
                    "gatewayDeviceId": "03ab..."
                }
            ]
        }
        """
        status_list = await self.client.query_mesh_group_status(
            self._group_ids_to_query,
        )

        for status_data in status_list:
            self._apply_group_status_row(status_data)

    def _apply_group_status_row(self, status_data: dict[str, Any]) -> None:
        """Apply one mesh group status row to device mappings and properties."""
        group_id = status_data.get("groupId")
        if not group_id:
            _LOGGER.warning(
                "Missing groupId in mesh group status response: %s",
                list(status_data.keys()),
            )
            return

        device = self._devices.get(group_id)
        if not device:
            _LOGGER.debug(
                "Unknown group in status response: %s",
                group_id,
            )
            return

        self._apply_group_lookup_mappings(device, status_data)

        # Parse group-level properties (powerState, brightness, etc.)
        raw_properties = status_data.get("properties")
        if raw_properties:
            properties = parse_properties_list(raw_properties)
            self._apply_properties_update(device, properties)

    def _apply_group_lookup_mappings(
        self,
        device: LiproDevice,
        status_data: dict[str, Any],
    ) -> None:
        """Update lookup IDs and group-member metadata for a mesh group device."""
        lookup_ids = resolve_mesh_group_lookup_ids(status_data)
        decision = compute_group_lookup_mapping_decision(
            previous_gateway_id=device.extra_data.get("gateway_device_id"),
            current_gateway_id=lookup_ids.gateway_id,
            previous_member_lookup_ids=device.extra_data.get("group_member_lookup_ids", []),
            current_member_lookup_ids=lookup_ids.member_lookup_ids,
            member_ids=lookup_ids.member_ids,
        )
        if decision.gateway_unregister_id:
            self._device_identity_index.unregister(
                decision.gateway_unregister_id,
                device=device,
            )

        # Save gateway device ID for API-level lookups
        # Note: MQTT messages use mesh_group_xxx topics, not gateway IDs
        if decision.gateway_extra_data_value:
            device.extra_data["gateway_device_id"] = decision.gateway_extra_data_value
            # Map gateway ID -> device for API responses that reference it
            self._device_identity_index.register(decision.gateway_extra_data_value, device)
        else:
            device.extra_data.pop("gateway_device_id", None)

        for stale_lookup_id in decision.member_unregister_ids:
            self._device_identity_index.unregister(
                stale_lookup_id,
                device=device,
            )

        # Map group member IDs -> group device. Real API control often accepts
        # group-level commands only, so member IDs should resolve to the group.
        for member_lookup_id in decision.member_register_ids:
            self._device_identity_index.register(member_lookup_id, device)
        device.extra_data["group_member_ids"] = decision.member_ids_extra_data
        device.extra_data["group_member_lookup_ids"] = decision.member_lookup_ids_extra_data
        device.extra_data["group_member_count"] = decision.member_count

    async def _query_outlet_power(self) -> None:
        """Query power information for outlet devices.

        The API returns aggregated data (single nowPower + energyList) for all
        requested devices, so we query each outlet individually to get accurate
        per-device power data. Queries run with bounded concurrency to reduce
        rate-limit pressure and avoid event-loop spikes with many outlets.
        """
        self._outlet_power_round_robin_index = await query_outlet_power_runtime(
            outlet_ids_to_query=self._outlet_ids_to_query,
            round_robin_index=self._outlet_power_round_robin_index,
            resolve_cycle_size=self._resolve_outlet_power_cycle_size,
            query_single_outlet_power=self._query_single_outlet_power,
            concurrency=_OUTLET_POWER_QUERY_CONCURRENCY,
        )

    @staticmethod
    def _resolve_outlet_power_cycle_size(total_devices: int) -> int:
        """Resolve per-cycle outlet power query size with bounded dynamic scaling."""
        return resolve_outlet_power_cycle_size_runtime(
            total_devices,
            max_devices_per_cycle=_OUTLET_POWER_QUERY_MAX_DEVICES_PER_CYCLE,
            target_full_cycle_count=_OUTLET_POWER_TARGET_FULL_CYCLE_COUNT,
        )

    async def _query_single_outlet_power(self, device_id: str) -> None:
        """Query and apply power info for one outlet device."""
        await query_single_outlet_power_runtime(
            device_id=device_id,
            fetch_outlet_power_info=self.client.fetch_outlet_power_info,
            get_device_by_id=self.get_device_by_id,
            apply_outlet_power_info=apply_outlet_power_info,
            should_reraise_outlet_power_error=should_reraise_outlet_power_error,
            logger=_LOGGER,
        )

    async def _query_connect_status(self, device_ids: list[str] | None = None) -> None:
        """Query real-time connection status for devices.

        This provides more accurate online/offline status than the cached
        connectState property from device status queries.
        """
        query_ids = (
            list(device_ids) if device_ids is not None else self._iot_ids_to_query
        )
        if not query_ids:
            return

        connect_status = await self.client.query_connect_status(
            query_ids,
        )

        if not connect_status:
            return

        for device_id, is_online in connect_status.items():
            self._connect_status_priority_ids.discard(
                self._normalize_device_key(device_id)
            )
            device = self.get_device_by_id(device_id)
            if device:
                # Update connectState property (via _apply_properties_update
                # for consistent debounce protection handling)
                self._apply_properties_update(
                    device,
                    {PROP_CONNECT_STATE: "1" if is_online else "0"},
                )
                _LOGGER.debug(
                    "Updated connect status for %s: %s",
                    device.name,
                    "online" if is_online else "offline",
                )

    async def async_refresh_devices(self) -> None:
        """Force refresh of device list.

        Sets a flag so the next _async_update_data call re-fetches devices.
        Uses atomic swap in _fetch_devices, so the old device list remains
        intact if the refresh fails.
        """
        self._force_device_refresh = True
        # Clear product configs so new device types can be matched
        self._product_configs_by_id.clear()
        self._product_configs.clear()
        await self.async_refresh()

    def _finalize_successful_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        route: str,
        trace: dict[str, Any],
    ) -> None:
        """Finalize post-send refresh strategy and success trace fields."""
        skip_immediate_refresh = should_skip_immediate_post_refresh(
            command=command,
            properties=properties,
            slider_like_properties=_SLIDER_LIKE_PROPERTIES,
        )
        self._track_command_expectation(device.serial, command, properties)
        if not device.is_group:
            self._connect_status_priority_ids.add(
                self._normalize_device_key(device.serial)
            )
        self._force_connect_status_refresh = True
        adaptive_delay = self._get_adaptive_post_refresh_delay(device.serial)
        self._schedule_post_command_refresh(
            skip_immediate=skip_immediate_refresh,
            device_serial=device.serial,
        )
        apply_successful_command_trace(
            trace=trace,
            route=route,
            adaptive_delay_seconds=adaptive_delay,
            skip_immediate_refresh=skip_immediate_refresh,
        )
        self._record_command_trace(trace)
        self._last_command_failure = None

    async def _handle_command_api_error(
        self,
        *,
        device: LiproDevice,
        trace: dict[str, Any],
        route: str,
        err: LiproApiError,
    ) -> bool:
        """Handle command-send API errors with consistent trace and reauth flows."""
        self._last_command_failure = build_command_api_error_failure(
            trace=trace,
            route=route,
            device_serial=device.serial,
            err=err,
            update_trace_with_exception=update_trace_with_exception,
        )
        self._record_command_trace(trace)
        if isinstance(err, LiproRefreshTokenExpiredError):
            _LOGGER.warning(
                "Refresh token expired while sending command to %s",
                device.name,
            )
            await self._trigger_reauth("auth_expired")
            return False
        if isinstance(err, LiproAuthError):
            _LOGGER.warning(
                "Auth error sending command to %s, triggering reauth",
                device.name,
            )
            await self._trigger_reauth("auth_error")
            return False

        _LOGGER.warning("Failed to send command to %s: %s", device.name, err)
        return False

    @property
    def last_command_failure(self) -> dict[str, Any] | None:
        """Return the latest command failure summary for service-layer mapping."""
        if self._last_command_failure is None:
            return None
        return dict(self._last_command_failure)

    async def _verify_command_result_delivery(
        self,
        *,
        device: LiproDevice,
        msg_sn: str,
        route: str,
        trace: dict[str, Any],
    ) -> bool:
        """Verify command delivery result by polling query_command_result."""
        verify_started_at = monotonic()

        async def _query_once(attempt: int) -> dict[str, Any] | None:
            return await query_command_result_once(
                query_command_result=self.client.query_command_result,
                lipro_api_error=LiproApiError,
                device_name=device.name,
                device_serial=device.serial,
                device_type_hex=device.device_type_hex,
                msg_sn=msg_sn,
                attempt=attempt,
                attempt_limit=_COMMAND_RESULT_VERIFY_ATTEMPTS,
                logger=_LOGGER,
            )

        def _log_attempt(attempt: int, state: str) -> None:
            _LOGGER.debug(
                "query_command_result attempt=%s/%s (device=%s, msgSn=%s, route=%s) state=%s",
                attempt,
                _COMMAND_RESULT_VERIFY_ATTEMPTS,
                device.serial,
                msg_sn,
                route,
                state,
            )

        state, attempt, last_payload = await poll_command_result_state(
            query_once=_query_once,
            classify_payload=classify_command_result_payload,
            attempt_limit=_COMMAND_RESULT_VERIFY_ATTEMPTS,
            interval_seconds=_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS,
            on_attempt=_log_attempt,
        )

        verified, failure = resolve_polled_command_result(
            state=state,
            trace=trace,
            route=route,
            msg_sn=msg_sn,
            device_serial=device.serial,
            attempt=attempt,
            attempt_limit=_COMMAND_RESULT_VERIFY_ATTEMPTS,
            last_payload=last_payload,
            elapsed_seconds=monotonic() - verify_started_at,
            logger=_LOGGER,
        )
        if verified:
            return True

        self._last_command_failure = failure
        self._record_command_trace(trace)
        return False

    async def _verify_delivery_if_enabled(
        self,
        *,
        trace: dict[str, Any],
        route: str,
        command: str,
        device: LiproDevice,
        result: Any,
    ) -> bool:
        """Run command-result verification when enabled."""
        if not self._command_result_verify:
            return True

        msg_sn = extract_msg_sn(result)
        if msg_sn is None:
            self._last_command_failure = apply_missing_msg_sn_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_command_trace(trace)
            return False

        verified = await self._verify_command_result_delivery(
            device=device,
            msg_sn=msg_sn,
            route=route,
            trace=trace,
        )
        if verified:
            return True

        _LOGGER.warning(
            "Command delivery not confirmed (command=%s, device=%s, route=%s, msgSn=%s, failure=%s)",
            command,
            device.name,
            route,
            msg_sn,
            self._last_command_failure,
        )
        return False

    async def async_send_command(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None = None,
        fallback_device_id: str | None = None,
    ) -> bool:
        """Send a command to a device.

        Args:
            device: Target device.
            command: Command name.
            properties: Optional properties.
            fallback_device_id: Optional member IoT ID fallback when target is group.

        Returns:
            True if command was sent successfully.

        """
        trace = build_command_trace(
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            redact_identifier=_redact_identifier,
        )
        route = "device_direct"

        try:
            await self._async_ensure_authenticated()

            success, route = await self._execute_command_flow(
                device=device,
                command=command,
                properties=properties,
                fallback_device_id=fallback_device_id,
                trace=trace,
            )
            return success

        except LiproApiError as err:
            return await self._handle_command_api_error(
                device=device,
                trace=trace,
                route=route,
                err=err,
            )

    async def _execute_command_flow(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: dict[str, Any],
    ) -> tuple[bool, str]:
        """Execute command dispatch/verification/finalization flow."""
        plan, result, route = await execute_command_plan_with_trace(
            self.client,
            device=device,
            command=command,
            properties=properties,
            fallback_device_id=fallback_device_id,
            trace=trace,
            redact_identifier=_redact_identifier,
        )
        if is_command_push_failed(result):
            self._last_command_failure = apply_push_failure(
                trace=trace,
                route=route,
                command=command,
                device_name=device.name,
                device_serial=device.serial,
                logger=_LOGGER,
            )
            self._record_command_trace(trace)
            return False, route

        if not await self._verify_delivery_if_enabled(
            trace=trace,
            route=route,
            command=command,
            device=device,
            result=result,
        ):
            return False, route

        self._finalize_successful_command(
            device=device,
            command=plan.command,
            properties=plan.properties,
            route=route,
            trace=trace,
        )
        return True, route

    def _schedule_post_command_refresh(
        self,
        *,
        skip_immediate: bool = False,
        device_serial: str | None = None,
    ) -> None:
        """Schedule immediate refresh and optional delayed refresh after a command."""
        schedule_post_command_refresh(
            track_background_task=self._track_background_task,
            request_refresh=self.async_request_refresh,
            post_command_refresh_tasks=self._post_command_refresh_tasks,
            mqtt_connected=self._mqtt_connected,
            device_serial=device_serial,
            pending_expectations=self._pending_command_expectations,
            get_adaptive_post_refresh_delay=self._get_adaptive_post_refresh_delay,
            skip_immediate=skip_immediate,
        )

    async def _async_delayed_command_refresh(self, delay_seconds: float) -> None:
        """Run one delayed refresh after command to absorb API status lag."""
        await run_delayed_refresh(
            delay_seconds=delay_seconds,
            request_refresh=self.async_request_refresh,
        )
