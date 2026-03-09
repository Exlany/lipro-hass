"""Coordinator runtime state and options loading."""

from __future__ import annotations

import asyncio
from collections import deque
import hashlib
import logging
from typing import TYPE_CHECKING, Any

from ...const.api import MAX_DEVICES_PER_QUERY
from ...const.config import (
    CONF_ANONYMOUS_SHARE_ENABLED,
    CONF_ANONYMOUS_SHARE_ERRORS,
    CONF_COMMAND_RESULT_VERIFY,
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_MQTT_ENABLED,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_ROOM_AREA_SYNC_FORCE,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_COMMAND_RESULT_VERIFY,
    DEFAULT_DEBUG_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_ROOM_AREA_SYNC_FORCE,
    MAX_POWER_QUERY_INTERVAL,
    MAX_REQUEST_TIMEOUT,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
)
from ..anonymous_share import get_anonymous_share_manager
from ..command.confirmation_tracker import CommandConfirmationTracker
from ..command.expectation import (
    PendingCommandExpectation as _PendingCommandExpectation,
)
from ..device import LiproDevice
from ..device.identity_index import DeviceIdentityIndex
from ..utils.background_task_manager import BackgroundTaskManager
from ..utils.coerce import coerce_bool_option, coerce_int_option
from ..utils.developer_report import (
    build_developer_report as build_coordinator_developer_report,
)
from ..utils.redaction import redact_identifier as _redact_identifier
from .command_confirm import (
    _MAX_POST_COMMAND_REFRESH_DELAY_SECONDS,
    _MIN_POST_COMMAND_REFRESH_DELAY_SECONDS,
    _POST_COMMAND_REFRESH_DELAY_SECONDS,
    _STATE_CONFIRM_TIMEOUT_SECONDS,
    _STATE_LATENCY_EWMA_ALPHA,
    _STATE_LATENCY_MARGIN_SECONDS,
)
from .command_send import _MAX_DEVELOPER_COMMAND_TRACES
from .device_list_snapshot import (
    DeviceFilterConfig,
    build_device_filter_config,
    has_active_device_filter,
)
from .device_refresh import _DeviceRefreshMixin
from .entity_protocol import LiproEntityProtocol
from .tuning import (
    _CONNECT_STATUS_MQTT_STALE_SECONDS,
    _CONNECT_STATUS_SKIP_RATIO_WINDOW,
    _STATE_STATUS_BATCH_METRICS_WINDOW,
    _STATE_STATUS_BATCH_SIZE_MAX,
)

if TYPE_CHECKING:
    from ..anonymous_share import AnonymousShareManager

_LOGGER = logging.getLogger(__name__)

# HA version for anonymous share reporting
try:
    from homeassistant.const import __version__ as _ha_ver

    HA_VERSION: str | None = _ha_ver
except ImportError:
    HA_VERSION = None


class _CoordinatorStateMixin(_DeviceRefreshMixin):
    """Mixin: runtime state init/reset, options loading, developer report."""

    # ---------------------------------------------------------------------
    # Construction helpers
    # ---------------------------------------------------------------------

    def _init_runtime_state(self) -> None:
        """Initialize coordinator runtime state containers and caches."""
        self._devices: dict[str, LiproDevice] = {}
        self._device_identity_index = DeviceIdentityIndex()
        self._diagnostic_gateway_devices: dict[str, LiproDevice] = {}
        self._iot_ids_to_query: list[str] = []
        self._group_ids_to_query: list[str] = []
        self._outlet_ids_to_query: list[str] = []  # Outlet device IDs for power query

        # Track entities for debounce protection (indexed by device serial)
        self._entities: dict[str, LiproEntityProtocol] = {}
        self._entities_by_device: dict[str, list[LiproEntityProtocol]] = {}

        # Product configs cache (productId/iotName -> config)
        self._product_configs_by_id: dict[int, dict[str, Any]] = {}
        self._product_configs: dict[str, dict[str, Any]] = {}

        # Last successful full device-list refresh timestamp.
        self._last_device_refresh_at: float = 0.0

        # Power query tracking
        self._last_power_query_time: float = 0.0
        self._outlet_power_round_robin_index: int = 0

        # Connect-status polling tracking
        self._last_connect_status_query_time: float = 0.0
        self._force_connect_status_refresh: bool = True
        self._init_mqtt_state()
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

        # Track per-device delayed refresh tasks for post-command consistency.
        self._post_command_refresh_tasks: dict[str, asyncio.Task[Any]] = {}

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

        # Raw (unfiltered) cloud serial snapshot from last full device fetch.
        self._cloud_serials_last_seen: set[str] = set()

        # Debounced config-entry reload scheduling for device-list changes.
        self._entry_reload_handle: asyncio.TimerHandle | None = None
        self._entry_reload_reasons: set[str] = set()
        self._last_entry_reload_at: float = 0.0

        # Debug mode command traces (opt-in)
        self._command_traces: deque[dict[str, Any]] = deque(
            maxlen=_MAX_DEVELOPER_COMMAND_TRACES
        )

        # Last command failure summary for service-layer error mapping.
        self._last_command_failure: dict[str, Any] | None = None

    def _reset_runtime_state(self) -> None:
        """Clear runtime state to break circular references on shutdown."""
        self._entities.clear()
        self._entities_by_device.clear()
        self._devices.clear()
        self._diagnostic_gateway_devices.clear()
        self._device_identity_index.clear()
        self._product_configs_by_id.clear()
        self._product_configs.clear()
        self._command_traces.clear()
        self._reset_mqtt_state()
        self._missing_device_cycles.clear()
        self._cloud_serials_last_seen.clear()
        self._entry_reload_reasons.clear()
        self._entry_reload_handle = None
        self._last_entry_reload_at = 0.0
        self._pending_command_expectations.clear()
        self._device_state_latency_seconds.clear()
        self._last_device_refresh_at = 0.0

    # ---------------------------------------------------------------------
    # Options loading + anonymous share
    # ---------------------------------------------------------------------

    def _load_options(self) -> None:
        """Load options from config entry."""
        options = self.config_entry.options if self.config_entry else {}

        self._mqtt_enabled = coerce_bool_option(
            options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
            option_name=CONF_MQTT_ENABLED,
            default=DEFAULT_MQTT_ENABLED,
            logger=_LOGGER,
        )

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

        self._request_timeout = coerce_int_option(
            options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT),
            option_name=CONF_REQUEST_TIMEOUT,
            default=DEFAULT_REQUEST_TIMEOUT,
            min_value=MIN_REQUEST_TIMEOUT,
            max_value=MAX_REQUEST_TIMEOUT,
            logger=_LOGGER,
        )

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

        installation_id = None
        storage_path = None
        if self.config_entry:
            installation_id = hashlib.sha256(
                self.config_entry.entry_id.encode()
            ).hexdigest()[:16]
            storage_path = self.hass.config.config_dir

        share_manager = self._get_anonymous_share_manager()
        share_manager.set_enabled(
            enabled, errors, installation_id, storage_path, ha_version=HA_VERSION
        )
        _LOGGER.debug(
            "Anonymous share: enabled=%s, errors=%s",
            enabled,
            errors,
        )

    def _get_anonymous_share_manager(self) -> AnonymousShareManager:
        """Return the anonymous share manager (patched in tests via this module)."""
        return get_anonymous_share_manager(
            self.hass,
            entry_id=self.config_entry.entry_id if self.config_entry else None,
        )

    # ---------------------------------------------------------------------
    # Basic accessors
    # ---------------------------------------------------------------------

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return all devices."""
        return self._devices

    def get_device(self, serial: str) -> LiproDevice | None:
        """Get a device by serial number."""
        return self._devices.get(serial)

    def get_device_by_id(self, device_id: Any) -> LiproDevice | None:
        """Look up a device by any known identifier."""
        return self._device_identity_index.get(device_id)

    # ---------------------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------------------

    def build_developer_report(self) -> dict[str, Any]:
        """Build a sanitized runtime report for real-world troubleshooting."""
        share_manager = self._get_anonymous_share_manager()
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
            diagnostic_gateway_devices=self._diagnostic_gateway_devices,
            group_count=len(self._group_ids_to_query),
            individual_count=len(self._iot_ids_to_query),
            outlet_count=len(self._outlet_ids_to_query),
            pending_devices=pending_devices,
            pending_errors=pending_errors,
            command_traces=list(self._command_traces),
            last_command_failure=self.last_command_failure,
            redact_identifier=_redact_identifier,
        )
        report["runtime"]["status_metrics"] = self._build_status_metrics_snapshot()
        return report


__all__ = ["_CoordinatorStateMixin"]
