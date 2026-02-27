"""Data update coordinator for Lipro integration."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import timedelta
import hashlib
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Final

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
    MIN_COLOR_TEMP_KELVIN,
    MIN_POWER_QUERY_INTERVAL,
    MIN_REQUEST_TIMEOUT,
    MIN_SCAN_INTERVAL,
    PROP_BRIGHTNESS,
    PROP_CONNECT_STATE,
    PROP_FAN_GEAR,
    PROP_POSITION,
    PROP_TEMPERATURE,
)
from ..const.api import (
    MAX_DEVICES_PER_QUERY,
    MAX_MQTT_CACHE_SIZE,
    MQTT_DISCONNECT_NOTIFY_THRESHOLD,
)
from ..const.config import CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY
from .anonymous_share import get_anonymous_share_manager
from .api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .command_dispatch import (
    CommandDispatchPlan,
    execute_command_dispatch,
    plan_command_dispatch,
)
from .command_trace import (
    build_command_trace,
    update_trace_with_exception,
    update_trace_with_resolved_request,
    update_trace_with_response,
)
from .coordinator_runtime import (
    should_refresh_device_list as should_refresh_device_list_runtime,
    should_schedule_mqtt_setup,
)
from .developer_report import (
    build_developer_report as build_coordinator_developer_report,
)
from .device import LiproDevice, parse_properties_list
from .device_refresh import (
    FetchedDeviceSnapshot,
    build_fetched_device_snapshot,
    plan_stale_device_reconciliation,
    register_lookup_id,
)
from .group_status import resolve_mesh_group_lookup_ids
from .mqtt import LiproMqttClient, decrypt_mqtt_credential
from .mqtt_lifecycle import (
    compute_relaxed_polling_seconds,
    resolve_disconnect_notification_minutes,
    resolve_disconnect_started_at,
)
from .mqtt_message import (
    build_dedup_cache_key,
    cleanup_dedup_cache,
    compute_properties_hash,
    is_duplicate_within_window,
    is_online_connect_state,
)
from .mqtt_setup import (
    build_mqtt_subscription_device_ids,
    extract_mqtt_encrypted_credentials,
    iter_mesh_group_serials,
    resolve_mqtt_biz_id,
)
from .outlet_power import apply_outlet_power_info, should_reraise_outlet_power_error

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from ..entities.base import LiproEntity
    from .auth import LiproAuthManager

_LOGGER = logging.getLogger(__name__)

# Polling interval multiplier when MQTT provides real-time updates.
# Use 2x (not higher) to still catch sub-device state drift in mesh groups.
_MQTT_POLLING_MULTIPLIER: Final[int] = 2

# Time threshold (seconds) for cleaning stale MQTT dedup cache entries
_MQTT_CACHE_STALE_SECONDS: Final[float] = 5.0

# Number of consecutive full-device-list fetches a device can be missing
# before being removed from HA device registry.
_STALE_DEVICE_REMOVE_THRESHOLD: Final[int] = 3

# Periodic full device-list refresh to discover newly paired devices.
_DEVICE_LIST_REFRESH_INTERVAL_SECONDS: Final[int] = 600

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


@dataclass
class _PendingCommandExpectation:
    """Track pending command values until observed in status updates."""

    sent_at: float
    expected: dict[str, str]

    def is_expired(self, now: float, timeout_seconds: float) -> bool:
        """Return True when pending expectation exceeded timeout."""
        return now - self.sent_at > timeout_seconds

    def stale_keys(self, properties: dict[str, Any]) -> set[str]:
        """Return keys that still conflict with expected values."""
        return {
            key
            for key, value in properties.items()
            if key in self.expected and str(value) != self.expected[key]
        }

    def observe(self, properties: dict[str, Any]) -> bool:
        """Consume matching keys from an observed property update.

        Returns True when all expected keys are confirmed.
        """
        for key in list(self.expected):
            value = properties.get(key)
            if value is not None and str(value) == self.expected[key]:
                self.expected.pop(key, None)
        return not self.expected


_SLIDER_LIKE_PROPERTIES: Final[frozenset[str]] = frozenset(
    {
        PROP_BRIGHTNESS,
        PROP_TEMPERATURE,
        PROP_FAN_GEAR,
        PROP_POSITION,
    }
)


def _should_skip_immediate_post_refresh(
    command: str,
    properties: list[dict[str, str]] | None,
) -> bool:
    """Decide whether immediate refresh can be skipped for slider-like updates.

    For brightness/color-temperature slider updates, optimistic state already
    keeps the UI responsive and delayed refresh is enough to reconcile eventual
    backend consistency. Skipping immediate refresh reduces API pressure and
    helps avoid command congestion under rapid slider interactions.
    """
    if command.upper() != "CHANGE_STATE" or not properties:
        return False

    property_keys = {
        item.get("key")
        for item in properties
        if isinstance(item, dict) and isinstance(item.get("key"), str)
    }
    if not property_keys:
        return False

    return property_keys.issubset(_SLIDER_LIKE_PROPERTIES)


def _redact_identifier(identifier: str | None) -> str | None:
    """Redact identifiers for share-friendly developer reports."""
    if not isinstance(identifier, str):
        return None

    normalized = identifier.strip()
    if not normalized:
        return None

    if len(normalized) <= 8:
        return "***"
    return f"{normalized[:4]}***{normalized[-4:]}"


def _coerce_option_int(
    value: Any,
    *,
    option_name: str,
    default: int,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Coerce option value to int with fallback and clamp."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        _LOGGER.warning(
            "Invalid option %s=%r, using default %d",
            option_name,
            value,
            default,
        )
        parsed = default

    if min_value is not None:
        parsed = max(min_value, parsed)
    if max_value is not None:
        parsed = min(max_value, parsed)
    return parsed


def _coerce_option_bool(
    value: Any,
    *,
    option_name: str,
    default: bool,
) -> bool:
    """Coerce option value to bool with fallback."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False

    _LOGGER.warning(
        "Invalid option %s=%r, using default %s",
        option_name,
        value,
        default,
    )
    return default


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
        self._devices: dict[str, LiproDevice] = {}
        self._device_by_id: dict[str, LiproDevice] = {}  # Any known ID -> Device
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
        self._biz_id: str | None = None
        # Product configs cache (iotName -> config)
        self._product_configs: dict[str, dict[str, Any]] = {}
        # MQTT message deduplication cache: "device_id:hash" -> timestamp
        self._mqtt_message_cache: dict[str, float] = {}
        # Deduplication window in seconds (ignore duplicate messages within this window)
        self._mqtt_dedup_window: float = 0.5
        # Last successful full device-list refresh timestamp.
        self._last_device_refresh_at: float = 0.0
        # Power query tracking
        self._last_power_query_time: float = 0.0
        # Flag to force device list re-fetch on next update
        self._force_device_refresh: bool = False
        # MQTT disconnect tracking for user notification
        self._mqtt_disconnect_time: float | None = None
        self._mqtt_disconnect_notified: bool = False
        # Track delayed refresh task for post-command eventual consistency.
        self._post_command_refresh_task: asyncio.Task | None = None
        # Pending CHANGE_STATE expectations per device for stale-update filtering.
        self._pending_command_expectations: dict[str, _PendingCommandExpectation] = {}
        # Learned command->state confirmation latency (EWMA) per device.
        self._device_state_latency_seconds: dict[str, float] = {}
        # Track consecutive missing counts for safe stale-device cleanup
        self._missing_device_cycles: dict[str, int] = {}
        # Debug mode command traces (opt-in)
        self._command_traces: deque[dict[str, Any]] = deque(
            maxlen=_MAX_DEVELOPER_COMMAND_TRACES
        )
        # Last command failure summary for service-layer error mapping.
        self._last_command_failure: dict[str, Any] | None = None

        # Load options from config entry
        self._load_options()

        # Initialize anonymous share system based on config
        self._setup_anonymous_share()

    def _load_options(self) -> None:
        """Load options from config entry."""
        options = self.config_entry.options if self.config_entry else {}

        # MQTT enabled
        self._mqtt_enabled = _coerce_option_bool(
            options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
            option_name=CONF_MQTT_ENABLED,
            default=DEFAULT_MQTT_ENABLED,
        )

        # Power monitoring
        self._power_monitoring_enabled = _coerce_option_bool(
            options.get(CONF_ENABLE_POWER_MONITORING, DEFAULT_ENABLE_POWER_MONITORING),
            option_name=CONF_ENABLE_POWER_MONITORING,
            default=DEFAULT_ENABLE_POWER_MONITORING,
        )
        self._power_query_interval = _coerce_option_int(
            options.get(CONF_POWER_QUERY_INTERVAL, DEFAULT_POWER_QUERY_INTERVAL),
            option_name=CONF_POWER_QUERY_INTERVAL,
            default=DEFAULT_POWER_QUERY_INTERVAL,
            min_value=MIN_POWER_QUERY_INTERVAL,
            max_value=MAX_POWER_QUERY_INTERVAL,
        )

        # Request timeout
        self._request_timeout = _coerce_option_int(
            options.get(CONF_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT),
            option_name=CONF_REQUEST_TIMEOUT,
            default=DEFAULT_REQUEST_TIMEOUT,
            min_value=MIN_REQUEST_TIMEOUT,
            max_value=MAX_REQUEST_TIMEOUT,
        )

        # Debug mode includes verbose logging and runtime command traces.
        self._debug_mode = _coerce_option_bool(
            options.get(CONF_DEBUG_MODE, DEFAULT_DEBUG_MODE),
            option_name=CONF_DEBUG_MODE,
            default=DEFAULT_DEBUG_MODE,
        )
        self._room_area_sync_force = _coerce_option_bool(
            options.get(CONF_ROOM_AREA_SYNC_FORCE, DEFAULT_ROOM_AREA_SYNC_FORCE),
            option_name=CONF_ROOM_AREA_SYNC_FORCE,
            default=DEFAULT_ROOM_AREA_SYNC_FORCE,
        )
        self._command_result_verify = _coerce_option_bool(
            options.get(CONF_COMMAND_RESULT_VERIFY, DEFAULT_COMMAND_RESULT_VERIFY),
            option_name=CONF_COMMAND_RESULT_VERIFY,
            default=DEFAULT_COMMAND_RESULT_VERIFY,
        )

        # Apply debug mode to all lipro loggers
        lipro_logger = logging.getLogger("custom_components.lipro")
        if self._debug_mode:
            lipro_logger.setLevel(logging.DEBUG)
            _LOGGER.debug("Debug mode enabled for all Lipro modules")
        else:
            lipro_logger.setLevel(logging.NOTSET)

    def _setup_anonymous_share(self) -> None:
        """Set up the anonymous share system based on config options."""
        options = self.config_entry.options if self.config_entry else {}
        enabled = _coerce_option_bool(
            options.get(CONF_ANONYMOUS_SHARE_ENABLED, DEFAULT_ANONYMOUS_SHARE_ENABLED),
            option_name=CONF_ANONYMOUS_SHARE_ENABLED,
            default=DEFAULT_ANONYMOUS_SHARE_ENABLED,
        )
        errors = _coerce_option_bool(
            options.get(CONF_ANONYMOUS_SHARE_ERRORS, DEFAULT_ANONYMOUS_SHARE_ERRORS),
            option_name=CONF_ANONYMOUS_SHARE_ERRORS,
            default=DEFAULT_ANONYMOUS_SHARE_ERRORS,
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

    def _record_command_trace(self, trace: dict[str, Any]) -> None:
        """Record one command trace when debug mode is enabled."""
        if not self._debug_mode:
            return

        self._command_traces.append(trace)

    def build_developer_report(self) -> dict[str, Any]:
        """Build a sanitized runtime report for real-world troubleshooting."""
        share_manager = get_anonymous_share_manager(self.hass)
        pending_devices, pending_errors = share_manager.pending_count
        polling_interval_seconds = (
            int(self.update_interval.total_seconds())
            if self.update_interval is not None
            else None
        )
        return build_coordinator_developer_report(
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
            if entity not in entities:
                entities.append(entity)

    def unregister_entity(self, entity: LiproEntity) -> None:
        """Unregister an entity.

        Args:
            entity: The entity to unregister.

        """
        if entity.unique_id and entity.unique_id in self._entities:
            del self._entities[entity.unique_id]
            # Remove from device index
            device_serial = entity.device.serial
            if device_serial in self._entities_by_device:
                entities = self._entities_by_device[device_serial]
                self._entities_by_device[device_serial] = [
                    e for e in entities if e.unique_id != entity.unique_id
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
        pending = self._pending_command_expectations.get(device_serial)
        if not pending:
            return properties

        now = monotonic()
        if pending.is_expired(now, _STATE_CONFIRM_TIMEOUT_SECONDS):
            self._pending_command_expectations.pop(device_serial, None)
            return properties

        blocked_keys = pending.stale_keys(properties)
        if not blocked_keys:
            return properties

        filtered = {k: v for k, v in properties.items() if k not in blocked_keys}
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
        if command.upper() != "CHANGE_STATE" or not properties:
            self._pending_command_expectations.pop(device_serial, None)
            return

        expected: dict[str, str] = {}
        for item in properties:
            key = item.get("key")
            value = item.get("value")
            if isinstance(key, str):
                expected[key] = str(value)

        if not expected:
            self._pending_command_expectations.pop(device_serial, None)
            return

        self._pending_command_expectations[device_serial] = _PendingCommandExpectation(
            sent_at=monotonic(),
            expected=expected,
        )

    def _update_state_latency(
        self,
        device_serial: str,
        observed_latency: float,
    ) -> None:
        """Update per-device command->state latency EWMA."""
        bounded = max(
            _MIN_POST_COMMAND_REFRESH_DELAY_SECONDS,
            min(_MAX_POST_COMMAND_REFRESH_DELAY_SECONDS, observed_latency),
        )
        previous = self._device_state_latency_seconds.get(device_serial)
        if previous is None:
            self._device_state_latency_seconds[device_serial] = bounded
            return

        alpha = _STATE_LATENCY_EWMA_ALPHA
        self._device_state_latency_seconds[device_serial] = (
            previous * (1 - alpha) + bounded * alpha
        )

    def _observe_command_confirmation(
        self,
        device_serial: str,
        properties: dict[str, Any],
    ) -> None:
        """Observe property updates and confirm pending command expectations."""
        pending = self._pending_command_expectations.get(device_serial)
        if not pending:
            return

        now = monotonic()
        if pending.is_expired(now, _STATE_CONFIRM_TIMEOUT_SECONDS):
            self._pending_command_expectations.pop(device_serial, None)
            return

        if not pending.observe(properties):
            return

        latency = now - pending.sent_at
        self._update_state_latency(device_serial, latency)
        self._pending_command_expectations.pop(device_serial, None)
        _LOGGER.debug(
            "Device %s: confirmed command state in %.2fs (adaptive delay=%.2fs)",
            device_serial[:8] + "...",
            latency,
            self._get_adaptive_post_refresh_delay(device_serial),
        )

    def _get_adaptive_post_refresh_delay(self, device_serial: str | None) -> float:
        """Get adaptive delayed-refresh value for a device."""
        learned = (
            self._device_state_latency_seconds.get(device_serial)
            if isinstance(device_serial, str)
            else None
        )
        delay = (
            learned + _STATE_LATENCY_MARGIN_SECONDS
            if learned is not None
            else _POST_COMMAND_REFRESH_DELAY_SECONDS
        )
        return max(
            _MIN_POST_COMMAND_REFRESH_DELAY_SECONDS,
            min(_MAX_POST_COMMAND_REFRESH_DELAY_SECONDS, delay),
        )

    def _prune_runtime_state_for_devices(self, active_serials: set[str]) -> None:
        """Prune per-device runtime caches for removed devices."""
        stale_pending = set(self._pending_command_expectations) - active_serials
        for serial in stale_pending:
            self._pending_command_expectations.pop(serial, None)

        stale_latency = set(self._device_state_latency_seconds) - active_serials
        for serial in stale_latency:
            self._device_state_latency_seconds.pop(serial, None)

    def _apply_properties_update(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
        *,
        apply_protection: bool = True,
    ) -> None:
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

        if properties:
            self._adapt_fan_gear_range(device, properties)
            device.update_properties(properties)
            self._observe_command_confirmation(device.serial, properties)
            _LOGGER.debug(
                "Updated %s: %s",
                device.name,
                properties,
            )

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
        await self._async_show_auth_notification(key, **placeholders)
        if self.config_entry:
            self.config_entry.async_start_reauth(self.hass)

    @property
    def devices(self) -> dict[str, LiproDevice]:
        """Return all devices."""
        return self._devices

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
        if not isinstance(device_id, str):
            return None

        normalized = device_id.strip()
        if not normalized:
            return None

        device = self._device_by_id.get(normalized)
        if device:
            return device

        return self._device_by_id.get(normalized.lower())

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
        try:
            await self.async_setup_mqtt()
        finally:
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

        # Cancel pending delayed refresh task.
        if (
            self._post_command_refresh_task
            and not self._post_command_refresh_task.done()
        ):
            self._post_command_refresh_task.cancel()
            self._post_command_refresh_task = None

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
        self._entities.clear()
        self._entities_by_device.clear()
        self._devices.clear()
        self._device_by_id.clear()
        self._product_configs.clear()
        self._command_traces.clear()
        self._mqtt_message_cache.clear()
        self._missing_device_cycles.clear()
        self._pending_command_expectations.clear()
        self._device_state_latency_seconds.clear()
        self._last_device_refresh_at = 0.0

        _LOGGER.debug("Coordinator shutdown complete")

    def _on_mqtt_connect(self) -> None:
        """Handle MQTT connection."""
        self._mqtt_connected = True
        self._mqtt_disconnect_time = None
        self._mqtt_disconnect_notified = False
        # Dismiss any previous disconnect issue
        async_delete_issue(self.hass, DOMAIN, "mqtt_disconnected")
        # Reduce polling frequency when MQTT provides real-time updates
        base = self._base_scan_interval
        relaxed = compute_relaxed_polling_seconds(base, _MQTT_POLLING_MULTIPLIER)
        self.update_interval = timedelta(seconds=relaxed)
        _LOGGER.info("MQTT connected, polling interval relaxed to %ds", relaxed)

    def _on_mqtt_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._mqtt_connected = False
        self._mqtt_disconnect_time = resolve_disconnect_started_at(
            self._mqtt_disconnect_time,
            now=monotonic(),
        )
        # Restore normal polling frequency
        base = self._base_scan_interval
        self.update_interval = timedelta(seconds=base)
        _LOGGER.warning("MQTT disconnected, polling interval restored to %ds", base)

    def _check_mqtt_disconnect_notification(self) -> None:
        """Send persistent notification if MQTT has been disconnected too long."""
        minutes = resolve_disconnect_notification_minutes(
            mqtt_enabled=self._mqtt_enabled,
            mqtt_connected=self._mqtt_connected,
            disconnect_started_at=self._mqtt_disconnect_time,
            disconnect_notified=self._mqtt_disconnect_notified,
            now=monotonic(),
            threshold_seconds=MQTT_DISCONNECT_NOTIFY_THRESHOLD,
        )
        if minutes is None:
            return

        self._mqtt_disconnect_notified = True
        self.hass.async_create_task(
            self._async_show_mqtt_disconnect_notification(minutes)
        )

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
        if self.config_entry:
            return _coerce_option_int(
                self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
                option_name=CONF_SCAN_INTERVAL,
                default=DEFAULT_SCAN_INTERVAL,
                min_value=MIN_SCAN_INTERVAL,
                max_value=MAX_SCAN_INTERVAL,
            )
        return DEFAULT_SCAN_INTERVAL

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

        self._apply_properties_update(device, properties)
        self._after_mqtt_properties_applied(device, properties)

    def _resolve_mqtt_message_device(self, device_id: str) -> LiproDevice | None:
        """Resolve MQTT message target device by known identifier mappings."""
        device = self.get_device_by_id(device_id)
        if device is not None:
            return device

        _LOGGER.debug("MQTT message for unknown device: %s...", device_id[:8])
        return None

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

    def _after_mqtt_properties_applied(
        self,
        device: LiproDevice,
        properties: dict[str, Any],
    ) -> None:
        """Run post-update notifications and reconciliation scheduling hooks."""
        if not properties:
            return

        # Force notify all listeners of the update
        # Note: async_set_updated_data won't trigger updates when always_update=False
        # and the same dict object is passed, so we use async_update_listeners directly
        self.async_update_listeners()

        # Fallback: when a device comes back online, schedule an immediate
        # REST API refresh to reconcile state. In mesh groups, sub-devices
        # may reconnect with a different state than the group reports.
        connect_state = properties.get(PROP_CONNECT_STATE)
        if device.is_group and is_online_connect_state(connect_state):
            _LOGGER.debug(
                "MQTT: device %s online, scheduling REST API reconciliation",
                device.name,
            )
            self.hass.async_create_task(self.async_request_refresh())

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

        self._mqtt_setup_in_progress = True
        self.hass.async_create_task(self._async_setup_mqtt_safe())

    async def _async_update_data(self) -> dict[str, LiproDevice]:
        """Fetch data from API.

        Returns:
            Dictionary of devices keyed by serial.

        Raises:
            UpdateFailed: If update fails.

        """
        try:
            # Ensure we have a valid token
            await self.auth_manager.ensure_valid_token()
            self._clear_auth_issues()

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

        except LiproRefreshTokenExpiredError as err:
            # Refresh token expired, trigger reauth flow
            await self._trigger_reauth("auth_expired")
            msg = f"Refresh token expired, re-authentication required: {err}"
            raise ConfigEntryAuthFailed(msg) from err
        except LiproAuthError as err:
            # Trigger reauth flow when authentication fails
            await self._trigger_reauth("auth_error", error=str(err))
            msg = f"Authentication error: {err}"
            raise ConfigEntryAuthFailed(msg) from err
        except LiproConnectionError as err:
            msg = f"Connection error: {err}"
            raise UpdateFailed(msg) from err
        except LiproApiError as err:
            msg = f"API error: {err}"
            raise UpdateFailed(msg) from err

    async def _fetch_devices(self) -> None:
        """Fetch all devices from API with pagination."""
        _LOGGER.debug("Fetching device list")

        previous_devices = dict(self._devices)
        previous_serials = set(self._devices)
        devices_data = await self._fetch_all_device_pages()
        snapshot = build_fetched_device_snapshot(devices_data)
        self._apply_fetched_device_snapshot(snapshot)
        self._sync_device_room_assignments(previous_devices)
        self._last_device_refresh_at = monotonic()
        self._schedule_reload_for_added_devices(previous_serials)
        await self._record_devices_for_anonymous_share()
        await self._reconcile_stale_devices(previous_serials)

        if self._mqtt_client and self._mqtt_connected:
            await self._sync_mqtt_subscriptions()

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
        self.hass.async_create_task(
            self.hass.config_entries.async_reload(self.config_entry.entry_id)
        )

    async def _fetch_all_device_pages(self) -> list[dict[str, Any]]:
        """Fetch full device list from paginated API responses."""
        devices_data: list[dict[str, Any]] = []
        offset = 0

        while True:
            result: Any = await self.client.get_devices(
                offset=offset,
                limit=MAX_DEVICES_PER_QUERY,
            )

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
                _LOGGER.debug(
                    "Skipping %d malformed device rows from API payload",
                    len(raw_page) - len(page),
                )

            devices_data.extend(page)
            if len(raw_page) < MAX_DEVICES_PER_QUERY:
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
        if not isinstance(room_name, str):
            return None
        normalized = room_name.strip()
        return normalized or None

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

        for serial, device in self._devices.items():
            previous = previous_devices.get(serial)
            if previous is None:
                continue

            old_room_name = self._normalize_room_name(previous.room_name)
            new_room_name = self._normalize_room_name(device.room_name)
            if old_room_name == new_room_name:
                continue

            device_entry = device_registry.async_get_device(identifiers={(DOMAIN, serial)})
            if device_entry is None:
                continue

            update_kwargs: dict[str, Any] = {"suggested_area": new_room_name}
            current_area_id = device_entry.area_id
            if self._room_area_sync_force:
                if new_room_name is None:
                    update_kwargs["area_id"] = None
                else:
                    update_kwargs["area_id"] = area_registry.async_get_or_create(
                        new_room_name
                    ).id
            elif current_area_id is None:
                if new_room_name is not None:
                    update_kwargs["area_id"] = area_registry.async_get_or_create(
                        new_room_name
                    ).id
            else:
                current_area = area_registry.async_get_area(current_area_id)
                current_area_name = (
                    self._normalize_room_name(current_area.name)
                    if current_area is not None
                    else None
                )
                if current_area_name == old_room_name:
                    if new_room_name is None:
                        update_kwargs["area_id"] = None
                    else:
                        update_kwargs["area_id"] = area_registry.async_get_or_create(
                            new_room_name
                        ).id

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
        if self._product_configs:
            # Already loaded
            return

        try:
            configs = await self.client.get_product_configs()
            _LOGGER.debug("Loaded %d product configurations", len(configs))

            configs_by_id, configs_by_iot_name = self._index_product_configs(configs)
            self._product_configs = configs_by_iot_name

            for device in self._devices.values():
                matched_config = self._match_product_config(
                    device,
                    configs_by_id,
                    configs_by_iot_name,
                )
                if matched_config:
                    self._apply_product_config(device, matched_config)

        except LiproApiError as err:
            _LOGGER.warning("Failed to load product configs: %s", err)
            # Continue with default values

    @staticmethod
    def _coerce_int_or_zero(value: Any) -> int:
        """Coerce mixed numeric payloads into int with safe fallback."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _index_product_configs(
        self,
        configs: list[dict[str, Any]],
    ) -> tuple[dict[int, dict[str, Any]], dict[str, dict[str, Any]]]:
        """Create lookup maps by product ID and fwIotName."""
        configs_by_id: dict[int, dict[str, Any]] = {}
        configs_by_iot_name: dict[str, dict[str, Any]] = {}

        for config in configs:
            config_id = self._coerce_int_or_zero(config.get("id"))
            if config_id > 0:
                configs_by_id[config_id] = config

            fw_iot_name = config.get("fwIotName")
            if isinstance(fw_iot_name, str) and fw_iot_name:
                configs_by_iot_name[fw_iot_name.lower()] = config

        return configs_by_id, configs_by_iot_name

    def _match_product_config(
        self,
        device: LiproDevice,
        configs_by_id: dict[int, dict[str, Any]],
        configs_by_iot_name: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Match one device to its best product config."""
        if device.product_id:
            matched = configs_by_id.get(device.product_id)
            if matched:
                _LOGGER.debug(
                    "Device %s: matched config by productId=%d -> %s",
                    device.name,
                    device.product_id,
                    matched.get("name"),
                )
                return matched

        if device.iot_name:
            matched = configs_by_iot_name.get(device.iot_name.lower())
            if matched:
                _LOGGER.debug(
                    "Device %s: matched config by iotName=%s -> %s",
                    device.name,
                    device.iot_name,
                    matched.get("name"),
                )
                return matched

        return None

    def _apply_product_config(
        self,
        device: LiproDevice,
        config: dict[str, Any],
    ) -> None:
        """Apply matched product-config overrides to runtime device model."""
        min_temp = self._coerce_int_or_zero(config.get("minTemperature", 0))
        max_temp = self._coerce_int_or_zero(config.get("maxTemperature", 0))
        max_fan_gear = self._coerce_int_or_zero(config.get("maxFanGear", 0))

        if max_temp > 0:
            device.min_color_temp_kelvin = min_temp or MIN_COLOR_TEMP_KELVIN
            device.max_color_temp_kelvin = max_temp
            _LOGGER.debug(
                "Device %s: color temp range %d-%d K",
                device.name,
                device.min_color_temp_kelvin,
                device.max_color_temp_kelvin,
            )
        elif max_temp == 0 and min_temp == 0:
            device.min_color_temp_kelvin = 0
            device.max_color_temp_kelvin = 0
            _LOGGER.debug(
                "Device %s: single color temperature (no adjustment)",
                device.name,
            )

        if max_fan_gear > 0:
            device.default_max_fan_gear_in_model = max_fan_gear
            device.max_fan_gear = max(device.max_fan_gear, max_fan_gear)
            _LOGGER.debug(
                "Device %s: fan gear baseline 1-%d, effective 1-%d",
                device.name,
                device.default_max_fan_gear_in_model,
                device.max_fan_gear,
            )

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
        if self._iot_ids_to_query:
            await self._query_connect_status()

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
        )

        for status_data in status_list:
            device_id = status_data.get("deviceId")
            if not device_id:
                continue

            # Find device using IoT ID mapping
            device = self.get_device_by_id(device_id)

            if device:
                properties = parse_properties_list(
                    status_data.get("properties", []),
                )
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
        properties = parse_properties_list(status_data.get("properties", []))
        self._apply_properties_update(device, properties)

    def _apply_group_lookup_mappings(
        self,
        device: LiproDevice,
        status_data: dict[str, Any],
    ) -> None:
        """Update lookup IDs and group-member metadata for a mesh group device."""
        lookup_ids = resolve_mesh_group_lookup_ids(status_data)

        # Save gateway device ID for API-level lookups
        # Note: MQTT messages use mesh_group_xxx topics, not gateway IDs
        if lookup_ids.gateway_id:
            device.extra_data["gateway_device_id"] = lookup_ids.gateway_id
            # Map gateway ID -> device for API responses that reference it
            register_lookup_id(self._device_by_id, lookup_ids.gateway_id, device)

        # Map group member IDs -> group device. Real API control often accepts
        # group-level commands only, so member IDs should resolve to the group.
        for member_lookup_id in lookup_ids.member_lookup_ids:
            register_lookup_id(self._device_by_id, member_lookup_id, device)
        device.extra_data["group_member_ids"] = lookup_ids.member_ids
        device.extra_data["group_member_count"] = len(lookup_ids.member_ids)

    async def _query_outlet_power(self) -> None:
        """Query power information for outlet devices.

        The API returns aggregated data (single nowPower + energyList) for all
        requested devices, so we query each outlet individually to get accurate
        per-device power data. Queries run concurrently for better performance.
        """
        if not self._outlet_ids_to_query:
            return

        await asyncio.gather(
            *(
                self._query_single_outlet_power(did)
                for did in self._outlet_ids_to_query
            ),
        )

    async def _query_single_outlet_power(self, device_id: str) -> None:
        """Query and apply power info for one outlet device."""
        try:
            power_data = await self.client.fetch_outlet_power_info([device_id])
            if not power_data:
                return
            device = self.get_device_by_id(device_id)
            if device is not None and apply_outlet_power_info(device, power_data):
                _LOGGER.debug(
                    "Updated power info for %s: nowPower=%s",
                    device.name,
                    power_data.get("nowPower"),
                )
        except LiproApiError as err:
            # Auth/connection errors must bubble up so _async_update_data can
            # trigger reauth or mark update failed.
            if should_reraise_outlet_power_error(err):
                raise
            _LOGGER.debug("Failed to query power for %s: %s", device_id, err)

    async def _query_connect_status(self) -> None:
        """Query real-time connection status for devices.

        This provides more accurate online/offline status than the cached
        connectState property from device status queries.
        """
        if not self._iot_ids_to_query:
            return

        connect_status = await self.client.query_connect_status(
            self._iot_ids_to_query,
        )

        if not connect_status:
            return

        for device_id, is_online in connect_status.items():
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
        self._product_configs.clear()
        await self.async_refresh()

    def _record_push_failure_trace(
        self,
        trace: dict[str, Any],
        route: str,
        command: str,
        device: LiproDevice,
    ) -> None:
        """Record failed command push result as a trace event."""
        trace["route"] = route
        trace["success"] = False
        trace["error"] = "PushFailed"
        trace["error_message"] = "pushSuccess=false"
        self._record_command_trace(trace)
        _LOGGER.warning(
            "Command push failed (command=%s, device=%s, route=%s, device_id=%s)",
            command,
            device.name,
            route,
            device.serial,
        )
        self._last_command_failure = {
            "reason": "push_failed",
            "code": "push_failed",
            "route": route,
            "device_id": device.serial,
            "command": command,
        }

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
        skip_immediate_refresh = _should_skip_immediate_post_refresh(
            command, properties
        )
        self._track_command_expectation(device.serial, command, properties)
        adaptive_delay = self._get_adaptive_post_refresh_delay(device.serial)
        self._schedule_post_command_refresh(
            skip_immediate=skip_immediate_refresh,
            device_serial=device.serial,
        )
        trace["post_refresh_mode"] = (
            "delayed_only" if skip_immediate_refresh else "immediate_and_delayed"
        )
        trace["adaptive_post_refresh_delay_seconds"] = round(adaptive_delay, 3)
        trace["route"] = route
        trace["success"] = True
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
        update_trace_with_exception(trace, route=route, err=err)
        self._record_command_trace(trace)
        self._last_command_failure = {
            "reason": "api_error",
            "code": err.code,
            "message": str(err),
            "route": route,
            "device_id": device.serial,
        }
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

    @staticmethod
    def _is_command_push_failed(result: Any) -> bool:
        """Return True when command dispatch explicitly reports push failure."""
        return isinstance(result, dict) and result.get("pushSuccess") is False

    @staticmethod
    def _extract_msg_sn(result: Any) -> str | None:
        """Extract command serial number from command response payload."""
        if not isinstance(result, dict):
            return None
        for key in ("msgSn", "msg_sn", "messageSn", "message_sn"):
            value = result.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    @staticmethod
    def _classify_command_result_payload(payload: dict[str, Any]) -> str:
        """Classify query_command_result payload as confirmed/failed/pending/unknown."""
        success_value = payload.get("success")
        if success_value is True:
            return "confirmed"
        if success_value is False:
            return "failed"

        push_success = payload.get("pushSuccess")
        if push_success is True:
            return "confirmed"
        if push_success is False:
            return "failed"

        result_value = payload.get("result")
        if result_value in (True, 1, "1", "success", "SUCCESS"):
            return "confirmed"
        if result_value in (False, 0, "0", "failed", "FAIL", "FAILURE"):
            return "failed"
        if result_value in ("pending", "PENDING", "processing", "PROCESSING"):
            return "pending"

        status_value = payload.get("status")
        if status_value in (1, "1", "success", "SUCCESS", "done", "DONE"):
            return "confirmed"
        if status_value in (0, "0", "failed", "FAIL", "failure", "FAILURE"):
            return "failed"
        if status_value in (2, "2", "pending", "PENDING", "processing", "PROCESSING"):
            return "pending"

        return "unknown"

    def _record_command_result_rejected(
        self,
        *,
        route: str,
        msg_sn: str,
        trace: dict[str, Any],
        device: LiproDevice,
        attempt: int,
        verify_started_at: float,
    ) -> None:
        """Record rejected command-result verification state."""
        trace["route"] = route
        trace["success"] = False
        trace["error"] = "CommandResultRejected"
        trace["error_message"] = "command_result_failed"
        trace["command_result_verify"] = {
            "enabled": True,
            "verified": False,
            "attempts": attempt,
            "msg_sn": msg_sn,
            "state": "failed",
        }
        self._record_command_trace(trace)
        self._last_command_failure = {
            "reason": "command_result_failed",
            "code": "command_result_failed",
            "route": route,
            "msg_sn": msg_sn,
            "device_id": device.serial,
        }
        _LOGGER.warning(
            "query_command_result rejected command (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs, route=%s)",
            device.serial,
            msg_sn,
            attempt,
            monotonic() - verify_started_at,
            route,
        )

    def _record_command_result_unconfirmed(
        self,
        *,
        route: str,
        msg_sn: str,
        trace: dict[str, Any],
        device: LiproDevice,
        verify_started_at: float,
        last_payload: dict[str, Any] | None,
    ) -> None:
        """Record unconfirmed command-result verification state."""
        trace["route"] = route
        trace["success"] = False
        trace["error"] = "CommandResultUnconfirmed"
        trace["error_message"] = "command_result_unconfirmed"
        trace["command_result_verify"] = {
            "enabled": True,
            "verified": False,
            "attempts": _COMMAND_RESULT_VERIFY_ATTEMPTS,
            "msg_sn": msg_sn,
            "last_state": (
                self._classify_command_result_payload(last_payload)
                if isinstance(last_payload, dict)
                else "query_error"
            ),
        }
        self._record_command_trace(trace)
        self._last_command_failure = {
            "reason": "command_result_unconfirmed",
            "code": "command_result_unconfirmed",
            "route": route,
            "msg_sn": msg_sn,
            "device_id": device.serial,
        }
        _LOGGER.warning(
            "query_command_result not confirmed (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs, route=%s, last_state=%s)",
            device.serial,
            msg_sn,
            _COMMAND_RESULT_VERIFY_ATTEMPTS,
            monotonic() - verify_started_at,
            route,
            trace["command_result_verify"]["last_state"],
        )

    def _record_command_result_confirmed(
        self,
        *,
        trace: dict[str, Any],
        msg_sn: str,
        attempt: int,
        device: LiproDevice,
        verify_started_at: float,
    ) -> None:
        """Record confirmed command-result verification state."""
        trace["command_result_verify"] = {
            "enabled": True,
            "verified": True,
            "attempts": attempt,
            "msg_sn": msg_sn,
        }
        _LOGGER.debug(
            "query_command_result confirmed (device=%s, msgSn=%s, attempts=%s, elapsed=%.3fs)",
            device.serial,
            msg_sn,
            attempt,
            monotonic() - verify_started_at,
        )

    async def _query_command_result_once(
        self,
        *,
        device: LiproDevice,
        msg_sn: str,
        attempt: int,
    ) -> dict[str, Any] | None:
        """Query command result once and return payload when available."""
        try:
            payload = await self.client.query_command_result(
                msg_sn=msg_sn,
                device_id=device.serial,
                device_type=device.device_type_hex,
            )
        except LiproApiError as err:
            _LOGGER.debug(
                "query_command_result failed (device=%s, msgSn=%s, attempt=%s/%s, code=%s): %s",
                device.name,
                msg_sn,
                attempt,
                _COMMAND_RESULT_VERIFY_ATTEMPTS,
                err.code,
                err,
            )
            return None
        return payload

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
        last_payload: dict[str, Any] | None = None
        for attempt in range(1, _COMMAND_RESULT_VERIFY_ATTEMPTS + 1):
            payload = await self._query_command_result_once(
                device=device,
                msg_sn=msg_sn,
                attempt=attempt,
            )
            if payload is None:
                if attempt < _COMMAND_RESULT_VERIFY_ATTEMPTS:
                    await asyncio.sleep(_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS)
                continue

            last_payload = payload
            state = self._classify_command_result_payload(payload)
            _LOGGER.debug(
                "query_command_result attempt=%s/%s (device=%s, msgSn=%s, route=%s) state=%s",
                attempt,
                _COMMAND_RESULT_VERIFY_ATTEMPTS,
                device.serial,
                msg_sn,
                route,
                state,
            )
            if state == "confirmed":
                self._record_command_result_confirmed(
                    trace=trace,
                    msg_sn=msg_sn,
                    attempt=attempt,
                    device=device,
                    verify_started_at=verify_started_at,
                )
                return True
            if state == "failed":
                self._record_command_result_rejected(
                    route=route,
                    msg_sn=msg_sn,
                    trace=trace,
                    device=device,
                    attempt=attempt,
                    verify_started_at=verify_started_at,
                )
                return False

            if attempt < _COMMAND_RESULT_VERIFY_ATTEMPTS:
                await asyncio.sleep(_COMMAND_RESULT_VERIFY_INTERVAL_SECONDS)

        self._record_command_result_unconfirmed(
            route=route,
            msg_sn=msg_sn,
            trace=trace,
            device=device,
            verify_started_at=verify_started_at,
            last_payload=last_payload,
        )
        return False

    async def _execute_command_plan_with_trace(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
        trace: dict[str, Any],
    ) -> tuple[CommandDispatchPlan, Any, str]:
        """Plan, dispatch, and trace one command request."""
        plan: CommandDispatchPlan = plan_command_dispatch(
            device,
            command,
            properties,
            fallback_device_id,
        )
        route = plan.route
        update_trace_with_resolved_request(
            trace,
            command=plan.command,
            properties=plan.properties,
            fallback_device_id=plan.member_fallback_id,
            redact_identifier=_redact_identifier,
        )

        result, route = await execute_command_dispatch(
            self.client,
            device=device,
            plan=plan,
        )
        update_trace_with_response(trace, result)
        return plan, result, route

    def _record_missing_msg_sn_failure(
        self,
        *,
        trace: dict[str, Any],
        route: str,
        command: str,
        device: LiproDevice,
    ) -> None:
        """Record verification failure when command response has no msgSn."""
        trace["route"] = route
        trace["success"] = False
        trace["error"] = "CommandResultMissingMsgSn"
        trace["error_message"] = "command_result_missing_msgsn"
        trace["command_result_verify"] = {
            "enabled": True,
            "verified": False,
            "attempts": 0,
        }
        self._record_command_trace(trace)
        self._last_command_failure = {
            "reason": "command_result_unconfirmed",
            "code": "command_result_missing_msgsn",
            "route": route,
            "device_id": device.serial,
            "command": command,
        }
        _LOGGER.warning(
            "Command sent but msgSn missing for verification (command=%s, device=%s, route=%s, device_id=%s)",
            command,
            device.name,
            route,
            device.serial,
        )

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

        msg_sn = self._extract_msg_sn(result)
        if msg_sn is None:
            self._record_missing_msg_sn_failure(
                trace=trace,
                route=route,
                command=command,
                device=device,
            )
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
            await self.auth_manager.ensure_valid_token()
            self._clear_auth_issues()

            plan, result, route = await self._execute_command_plan_with_trace(
                device=device,
                command=command,
                properties=properties,
                fallback_device_id=fallback_device_id,
                trace=trace,
            )
            if self._is_command_push_failed(result):
                self._record_push_failure_trace(
                    trace=trace,
                    route=route,
                    command=command,
                    device=device,
                )
                return False

            if not await self._verify_delivery_if_enabled(
                trace=trace,
                route=route,
                command=command,
                device=device,
                result=result,
            ):
                return False

            self._finalize_successful_command(
                device=device,
                command=plan.command,
                properties=plan.properties,
                route=route,
                trace=trace,
            )

            return True

        except LiproApiError as err:
            return await self._handle_command_api_error(
                device=device,
                trace=trace,
                route=route,
                err=err,
            )

    def _schedule_post_command_refresh(
        self,
        *,
        skip_immediate: bool = False,
        device_serial: str | None = None,
    ) -> None:
        """Schedule command-result refreshes with optional delayed fallback.

        Immediate refresh updates state quickly when backend is already consistent.
        Delayed refresh covers eventual-consistency lag for REST polling setups.
        """
        if not skip_immediate:
            self.hass.async_create_task(self.async_request_refresh())

        should_schedule_delayed = not self._mqtt_connected
        if (
            not should_schedule_delayed
            and isinstance(device_serial, str)
            and device_serial in self._pending_command_expectations
        ):
            # Even with MQTT, keep one delayed fallback when command confirmation
            # is pending. Real environments may have variable push delays/loss.
            should_schedule_delayed = True

        if not should_schedule_delayed:
            return

        delay_seconds = self._get_adaptive_post_refresh_delay(device_serial)
        if (
            self._post_command_refresh_task
            and not self._post_command_refresh_task.done()
        ):
            self._post_command_refresh_task.cancel()

        self._post_command_refresh_task = self.hass.async_create_task(
            self._async_delayed_command_refresh(delay_seconds),
        )

    async def _async_delayed_command_refresh(self, delay_seconds: float) -> None:
        """Run one delayed refresh after command to absorb API status lag."""
        try:
            await asyncio.sleep(delay_seconds)
            await self.async_request_refresh()
        except asyncio.CancelledError:
            return
