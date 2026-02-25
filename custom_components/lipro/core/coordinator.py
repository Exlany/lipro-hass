"""Data update coordinator for Lipro integration."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import logging
from time import monotonic
from typing import TYPE_CHECKING, Any, Final

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
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
    CONF_BIZ_ID,
    CONF_DEBUG_MODE,
    CONF_ENABLE_POWER_MONITORING,
    CONF_MQTT_ENABLED,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_POWER_QUERY_INTERVAL,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_ANONYMOUS_SHARE_ENABLED,
    DEFAULT_ANONYMOUS_SHARE_ERRORS,
    DEFAULT_DEBUG_MODE,
    DEFAULT_ENABLE_POWER_MONITORING,
    DEFAULT_MQTT_ENABLED,
    DEFAULT_POWER_QUERY_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
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
from ..const.categories import DeviceCategory
from .anonymous_share import get_anonymous_share_manager
from .api import (
    LiproApiError,
    LiproAuthError,
    LiproClient,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from .device import LiproDevice, is_valid_iot_device_id, parse_properties_list
from .mqtt import LiproMqttClient, decrypt_mqtt_credential

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


@dataclass
class _FetchedDeviceSnapshot:
    """Atomic container for refreshed device indexes."""

    devices: dict[str, LiproDevice]
    device_by_id: dict[str, LiproDevice]
    iot_ids: list[str]
    group_ids: list[str]
    outlet_ids: list[str]


def _register_lookup_id(
    mapping: dict[str, LiproDevice],
    device_id: Any,
    device: LiproDevice,
) -> None:
    """Register a device lookup alias with case-insensitive compatibility."""
    if not isinstance(device_id, str):
        return
    normalized = device_id.strip()
    if not normalized:
        return
    mapping[normalized] = device
    mapping[normalized.lower()] = device


def _normalize_group_power_command(
    command: str,
    properties: list[dict[str, str]] | None,
) -> tuple[str, list[dict[str, str]] | None]:
    """Normalize group power CHANGE_STATE to POWER_ON/OFF for backend compatibility."""
    if command.upper() != "CHANGE_STATE" or not properties:
        return command, properties

    power_value: str | None = None
    has_non_power_properties = False
    for prop in properties:
        key = prop.get("key")
        if not isinstance(key, str):
            has_non_power_properties = True
            continue
        if key != "powerState":
            has_non_power_properties = True
            continue
        value = prop.get("value")
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "on"}:
                power_value = "1"
            elif normalized in {"0", "false", "off"}:
                power_value = "0"

    # Only collapse into POWER_ON/OFF when the payload is power-only.
    # Mixed updates (e.g., power + brightness/colorTemp) must preserve
    # CHANGE_STATE properties to avoid dropping non-power settings.
    if has_non_power_properties:
        return command, properties

    if power_value == "1":
        return "POWER_ON", None
    if power_value == "0":
        return "POWER_OFF", None
    return command, properties


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


def _resolve_group_fallback_member_id(
    device: LiproDevice,
    fallback_device_id: str | None,
) -> str | None:
    """Resolve fallback target for single-member mesh groups only."""
    if not device.is_group or not isinstance(fallback_device_id, str):
        return None

    candidate = fallback_device_id.strip().lower()
    if (
        not candidate
        or candidate == device.serial.lower()
        or not is_valid_iot_device_id(candidate)
    ):
        return None

    member_ids = device.extra_data.get("group_member_ids")
    if not isinstance(member_ids, list) or len(member_ids) != 1:
        return None

    only_member = member_ids[0]
    if not isinstance(only_member, str):
        return None

    member_id = only_member.strip().lower()
    if not member_id or not is_valid_iot_device_id(member_id):
        return None

    if candidate != member_id:
        return None

    return candidate


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


def _is_online_connect_state(value: Any) -> bool:
    """Normalize connect-state payload variants to an online/offline boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


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
        options = self.config_entry.options if self.config_entry else {}
        share_manager = get_anonymous_share_manager(self.hass)
        pending_devices, pending_errors = share_manager.pending_count

        mesh_groups: list[dict[str, Any]] = []
        for dev in self._devices.values():
            if not dev.is_group:
                continue

            member_ids = dev.extra_data.get("group_member_ids")
            safe_member_ids = (
                [_redact_identifier(mid) for mid in member_ids if isinstance(mid, str)]
                if isinstance(member_ids, list)
                else []
            )
            member_count = dev.extra_data.get("group_member_count")
            if not isinstance(member_count, int):
                member_count = len(safe_member_ids)

            mesh_groups.append(
                {
                    "group_id": _redact_identifier(dev.serial),
                    "iot_name": dev.iot_name,
                    "device_type": dev.device_type,
                    "physical_model": dev.physical_model,
                    "member_count": member_count,
                    "gateway_device_id": _redact_identifier(
                        dev.extra_data.get("gateway_device_id")
                    ),
                    "member_ids": safe_member_ids,
                }
            )

        report: dict[str, Any] = {
            "entry_id": _redact_identifier(
                self.config_entry.entry_id if self.config_entry else None
            ),
            "unique_id": _redact_identifier(
                self.config_entry.unique_id if self.config_entry else None
            ),
            "phone": _redact_identifier(
                self.config_entry.data.get(CONF_PHONE) if self.config_entry else None
            ),
            "debug_mode_enabled": self._debug_mode,
            "runtime": {
                "mqtt_enabled": self._mqtt_enabled,
                "mqtt_connected": self._mqtt_connected,
                "polling_interval_seconds": (
                    int(self.update_interval.total_seconds())
                    if self.update_interval is not None
                    else None
                ),
                "last_update_success": self.last_update_success,
            },
            "options": {
                "scan_interval": options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                "mqtt_enabled": options.get(CONF_MQTT_ENABLED, DEFAULT_MQTT_ENABLED),
                "power_monitoring_enabled": options.get(
                    CONF_ENABLE_POWER_MONITORING,
                    DEFAULT_ENABLE_POWER_MONITORING,
                ),
                "power_query_interval": options.get(
                    CONF_POWER_QUERY_INTERVAL,
                    DEFAULT_POWER_QUERY_INTERVAL,
                ),
                "request_timeout": options.get(
                    CONF_REQUEST_TIMEOUT,
                    DEFAULT_REQUEST_TIMEOUT,
                ),
                "debug_mode": options.get(
                    CONF_DEBUG_MODE,
                    DEFAULT_DEBUG_MODE,
                ),
            },
            "devices": {
                "total": len(self._devices),
                "group_count": len(self._group_ids_to_query),
                "individual_count": len(self._iot_ids_to_query),
                "outlet_count": len(self._outlet_ids_to_query),
            },
            "mesh_groups": mesh_groups,
            "anonymous_share_pending": {
                "devices": pending_devices,
                "errors": pending_errors,
            },
            "recent_commands": list(self._command_traces),
        }

        if not self._debug_mode:
            report["note"] = (
                "Debug mode is disabled. Enable it in advanced options "
                "to capture command traces."
            )

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
        self._device_state_latency_seconds[device_serial] = previous * (
            1 - alpha
        ) + bounded * alpha

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

    async def async_setup_mqtt(self) -> bool:
        """Set up MQTT client for real-time updates.

        Returns:
            True if MQTT setup was successful.

        """
        if self.config_entry is None:
            _LOGGER.error("Cannot setup MQTT: config_entry is None")
            return False
        try:
            # Get MQTT config from API
            mqtt_config = await self.client.get_mqtt_config()

            encrypted_access_key = mqtt_config.get("accessKey")
            encrypted_secret_key = mqtt_config.get("secretKey")

            if not encrypted_access_key or not encrypted_secret_key:
                _LOGGER.warning("MQTT config missing accessKey or secretKey")
                return False

            # Decrypt credentials (C extension, run in thread for async safety)
            access_key = await asyncio.to_thread(
                decrypt_mqtt_credential, encrypted_access_key
            )
            secret_key = await asyncio.to_thread(
                decrypt_mqtt_credential, encrypted_secret_key
            )

            # Get biz_id from config entry data
            biz_id = self.config_entry.data.get(CONF_BIZ_ID)
            if not biz_id:
                # Try to get from user_id (fallback)
                user_id = self.config_entry.data.get(CONF_USER_ID)
                if user_id is not None:
                    biz_id = str(user_id)
                else:
                    _LOGGER.warning("No biz_id available for MQTT")
                    return False

            # Remove 'lip_' prefix if present
            biz_id = biz_id.removeprefix("lip_")

            self._biz_id = biz_id
            phone_id = self.config_entry.data.get(CONF_PHONE_ID, "")

            # Create MQTT client
            self._mqtt_client = LiproMqttClient(
                access_key=access_key,
                secret_key=secret_key,
                biz_id=biz_id,
                phone_id=phone_id,
                on_message=self._on_mqtt_message,
                on_connect=self._on_mqtt_connect,
                on_disconnect=self._on_mqtt_disconnect,
            )

            # Get device IDs to subscribe
            # For mesh groups: use their serial (mesh_group_xxx) as the topic
            # For non-group devices: use their serial directly
            # Note: iot_device_id is an alias for serial, so we always use serial
            device_ids = list(self._devices.keys())

            for dev in self._devices.values():
                if dev.is_group:
                    _LOGGER.debug(
                        "MQTT: subscribing to mesh group %s",
                        dev.serial,
                    )

            # Start MQTT client
            await self._mqtt_client.start(device_ids)
            _LOGGER.info(
                "MQTT client setup complete, subscribing to %d devices",
                len(device_ids),
            )
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
        if self._post_command_refresh_task and not self._post_command_refresh_task.done():
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
        relaxed = base * _MQTT_POLLING_MULTIPLIER
        self.update_interval = timedelta(seconds=relaxed)
        _LOGGER.info("MQTT connected, polling interval relaxed to %ds", relaxed)

    def _on_mqtt_disconnect(self) -> None:
        """Handle MQTT disconnection."""
        self._mqtt_connected = False
        if self._mqtt_disconnect_time is None:
            self._mqtt_disconnect_time = monotonic()
        # Restore normal polling frequency
        base = self._base_scan_interval
        self.update_interval = timedelta(seconds=base)
        _LOGGER.warning("MQTT disconnected, polling interval restored to %ds", base)

    def _check_mqtt_disconnect_notification(self) -> None:
        """Send persistent notification if MQTT has been disconnected too long."""
        if (
            not self._mqtt_enabled
            or self._mqtt_connected
            or self._mqtt_disconnect_time is None
            or self._mqtt_disconnect_notified
        ):
            return

        elapsed = monotonic() - self._mqtt_disconnect_time
        if elapsed >= MQTT_DISCONNECT_NOTIFY_THRESHOLD:
            self._mqtt_disconnect_notified = True
            minutes = int(elapsed // 60)
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
        # Find device using IoT ID mapping
        device = self.get_device_by_id(device_id)

        if not device:
            _LOGGER.debug("MQTT message for unknown device: %s...", device_id[:8])
            return

        # Deduplication: check if this is a duplicate message
        current_time = monotonic()
        # Use hash of sorted items tuple for fast dedup (no JSON serialization needed)
        try:
            props_hash = hash(tuple(sorted(properties.items())))
        except TypeError:
            # Properties contain unhashable values, skip dedup
            _LOGGER.debug(
                "MQTT: cannot hash properties for %s, skipping dedup", device.name
            )
            props_hash = None

        # Only perform deduplication if we have a valid hash
        if props_hash is not None:
            cache_key = f"{device_id}:{props_hash}"
            last_time = self._mqtt_message_cache.get(cache_key)

            if last_time is not None:
                if current_time - last_time < self._mqtt_dedup_window:
                    # Duplicate message within dedup window, skip
                    if self._debug_mode:
                        _LOGGER.debug(
                            "MQTT: skipping duplicate message for %s (%.2fs ago)",
                            device.name,
                            current_time - last_time,
                        )
                    return

            # Update cache
            self._mqtt_message_cache[cache_key] = current_time

            # Periodic cleanup: only run when cache exceeds threshold
            if len(self._mqtt_message_cache) > MAX_MQTT_CACHE_SIZE:
                self._cleanup_mqtt_cache(current_time)

        self._apply_properties_update(device, properties)

        if properties:
            # Force notify all listeners of the update
            # Note: async_set_updated_data won't trigger updates when always_update=False
            # and the same dict object is passed, so we use async_update_listeners directly
            self.async_update_listeners()

            # Fallback: when a device comes back online, schedule an immediate
            # REST API refresh to reconcile state. In mesh groups, sub-devices
            # may reconnect with a different state than the group reports.
            connect_state = properties.get(PROP_CONNECT_STATE)
            if device.is_group and _is_online_connect_state(connect_state):
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
        # Remove stale entries
        self._mqtt_message_cache = {
            k: t
            for k, t in self._mqtt_message_cache.items()
            if current_time - t <= _MQTT_CACHE_STALE_SECONDS
        }

        # Hard cap: if cache still exceeds limit, keep newest half
        if len(self._mqtt_message_cache) > MAX_MQTT_CACHE_SIZE:
            sorted_items = sorted(self._mqtt_message_cache.items(), key=lambda x: x[1])
            self._mqtt_message_cache = dict(sorted_items[len(sorted_items) // 2 :])

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

            # Fetch device list if we don't have devices yet or refresh was forced
            if not self._devices or self._force_device_refresh:
                self._force_device_refresh = False
                await self._fetch_devices()
                # Load product configs and apply color temp ranges
                await self._load_product_configs()

            # Query device status
            await self._update_device_status()

            # Ensure MQTT client is running (retry if previous setup failed)
            # Only if MQTT is enabled in options
            if (
                self._mqtt_enabled
                and not self._mqtt_client
                and not self._mqtt_setup_in_progress
                and self._devices
            ):
                self._mqtt_setup_in_progress = True
                self.hass.async_create_task(self._async_setup_mqtt_safe())

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

        previous_serials = set(self._devices)
        devices_data = await self._fetch_all_device_pages()
        snapshot = self._build_fetched_device_snapshot(devices_data)
        self._apply_fetched_device_snapshot(snapshot)
        await self._record_devices_for_anonymous_share()
        await self._reconcile_stale_devices(previous_serials)

        if self._mqtt_client and self._mqtt_connected:
            await self._sync_mqtt_subscriptions()

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

    def _build_fetched_device_snapshot(
        self,
        devices_data: list[dict[str, Any]],
    ) -> _FetchedDeviceSnapshot:
        """Build refreshed device indexes from API payload."""
        new_devices: dict[str, LiproDevice] = {}
        new_device_by_id: dict[str, LiproDevice] = {}
        new_iot_ids: list[str] = []
        new_group_ids: list[str] = []
        new_outlet_ids: list[str] = []

        for device_data in devices_data:
            try:
                device = LiproDevice.from_api_data(device_data)
            except (TypeError, ValueError, AttributeError):
                _LOGGER.debug("Skipping malformed device payload row")
                continue

            if not isinstance(device.serial, str) or not device.serial.strip():
                _LOGGER.debug("Skipping device with invalid serial type/value")
                continue

            try:
                is_gateway = device.is_gateway
            except (TypeError, ValueError):
                _LOGGER.debug("Skipping device with malformed category payload")
                continue

            if is_gateway:
                _LOGGER.debug("Skipping gateway device: %s", device.name)
                continue

            new_devices[device.serial] = device
            _register_lookup_id(new_device_by_id, device.serial, device)

            if device.is_group:
                new_group_ids.append(device.serial)
                continue

            if not device.has_valid_iot_id:
                _LOGGER.debug(
                    "Device %s has unexpected IoT ID format: %s",
                    device.name,
                    device.serial,
                )
            new_iot_ids.append(device.iot_device_id)

            try:
                is_outlet = device.category == DeviceCategory.OUTLET
            except (TypeError, ValueError):
                _LOGGER.debug("Skipping outlet categorization for malformed device")
                is_outlet = False

            if is_outlet:
                new_outlet_ids.append(device.iot_device_id)

        return _FetchedDeviceSnapshot(
            devices=new_devices,
            device_by_id=new_device_by_id,
            iot_ids=new_iot_ids,
            group_ids=new_group_ids,
            outlet_ids=new_outlet_ids,
        )

    def _apply_fetched_device_snapshot(self, snapshot: _FetchedDeviceSnapshot) -> None:
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

        tracked_missing_serials = set(self._missing_device_cycles)
        stale_serials = (previous_serials | tracked_missing_serials) - current_serials
        for serial in current_serials:
            self._missing_device_cycles.pop(serial, None)

        if not stale_serials:
            return

        removable: set[str] = set()
        for serial in stale_serials:
            miss_count = self._missing_device_cycles.get(serial, 0) + 1
            self._missing_device_cycles[serial] = miss_count
            if miss_count >= _STALE_DEVICE_REMOVE_THRESHOLD:
                removable.add(serial)

        if not removable:
            return

        await self._async_remove_stale_devices(removable)
        for serial in removable:
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
            # Get groupId directly from response
            group_id = status_data.get("groupId")
            if not group_id:
                _LOGGER.warning(
                    "Missing groupId in mesh group status response: %s",
                    list(status_data.keys()),
                )
                continue

            device = self._devices.get(group_id)
            if not device:
                _LOGGER.debug(
                    "Unknown group in status response: %s",
                    group_id,
                )
                continue

            # Save gateway device ID for API-level lookups
            # Note: MQTT messages use mesh_group_xxx topics, not gateway IDs
            gateway_id = status_data.get("gatewayDeviceId")
            if gateway_id:
                device.extra_data["gateway_device_id"] = gateway_id
                # Map gateway ID -> device for API responses that reference it
                _register_lookup_id(self._device_by_id, gateway_id, device)

            # Map group member IDs -> group device. Real API control often accepts
            # group-level commands only, so member IDs should resolve to the group.
            members = status_data.get("devices")
            member_ids: list[str] = []
            if isinstance(members, list):
                for member in members:
                    if not isinstance(member, dict):
                        continue
                    member_id = member.get("deviceId")
                    if isinstance(member_id, str) and member_id.strip():
                        member_ids.append(member_id.strip())
                    _register_lookup_id(self._device_by_id, member_id, device)
            device.extra_data["group_member_ids"] = member_ids
            device.extra_data["group_member_count"] = len(member_ids)

            # Parse group-level properties (powerState, brightness, etc.)
            properties = parse_properties_list(status_data.get("properties", []))
            self._apply_properties_update(device, properties)

    async def _query_outlet_power(self) -> None:
        """Query power information for outlet devices.

        The API returns aggregated data (single nowPower + energyList) for all
        requested devices, so we query each outlet individually to get accurate
        per-device power data. Queries run concurrently for better performance.
        """
        if not self._outlet_ids_to_query:
            return

        async def _query_single_outlet(device_id: str) -> None:
            """Query power for a single outlet."""
            try:
                power_data = await self.client.fetch_outlet_power_info([device_id])
                if not power_data:
                    return
                device = self.get_device_by_id(device_id)
                if device:
                    device.extra_data["power_info"] = power_data
                    _LOGGER.debug(
                        "Updated power info for %s: nowPower=%s",
                        device.name,
                        power_data.get("nowPower"),
                    )
            except LiproApiError as err:
                # Auth/connection errors must bubble up so _async_update_data can
                # trigger reauth or mark update failed.
                if isinstance(err, (LiproAuthError, LiproConnectionError)):
                    raise
                _LOGGER.debug("Failed to query power for %s: %s", device_id, err)

        await asyncio.gather(
            *(_query_single_outlet(did) for did in self._outlet_ids_to_query),
        )

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

    @staticmethod
    def _extract_property_keys(
        properties: list[dict[str, str]] | None,
    ) -> list[str]:
        """Extract command property keys for trace logging."""
        return [
            key
            for item in (properties or [])
            if isinstance((key := item.get("key")), str)
        ]

    def _build_command_trace(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
    ) -> dict[str, Any]:
        """Build initial command trace payload."""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "device_id": _redact_identifier(device.serial),
            "is_group": device.is_group,
            "iot_name": device.iot_name,
            "device_type": device.device_type,
            "physical_model": device.physical_model,
            "requested_command": command,
            "requested_property_count": len(properties or []),
            "requested_property_keys": self._extract_property_keys(properties),
            "requested_fallback_device_id": _redact_identifier(fallback_device_id),
        }

    def _resolve_command_request(
        self,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        fallback_device_id: str | None,
    ) -> tuple[str, str, list[dict[str, str]] | None, str | None]:
        """Resolve command payload and route policy for one command call."""
        member_fallback_id = _resolve_group_fallback_member_id(device, fallback_device_id)
        if not device.is_group:
            return "device_direct", command, properties, member_fallback_id

        route = "group_direct"
        if (
            isinstance(fallback_device_id, str)
            and fallback_device_id.strip()
            and fallback_device_id.strip().lower() != device.serial.lower()
            and member_fallback_id is None
        ):
            _LOGGER.debug(
                "Ignoring member fallback %s for group %s "
                "(requires single-member mesh group)",
                fallback_device_id,
                device.serial,
            )

        actual_command, actual_properties = _normalize_group_power_command(
            command,
            properties,
        )
        if actual_command != command:
            _LOGGER.debug(
                "Normalized group command %s to %s for %s",
                command,
                actual_command,
                device.serial,
            )
        return route, actual_command, actual_properties, member_fallback_id

    async def _dispatch_command(
        self,
        *,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
        route: str,
        member_fallback_id: str | None,
    ) -> tuple[Any, str]:
        """Execute direct/group command send with fallback routing."""
        if not device.is_group:
            result = await self._send_member_command(
                member_id=device.serial,
                device=device,
                command=command,
                properties=properties,
            )
            return result, route

        try:
            result = await self.client.send_group_command(
                device.serial,
                command,
                device.device_type,
                properties,
                device.iot_name,
            )
        except LiproApiError as err:
            if not member_fallback_id:
                raise
            route = "group_error_fallback_member"
            _LOGGER.warning(
                "Group command %s to %s failed (%s), fallback to member %s",
                command,
                device.serial,
                err,
                member_fallback_id,
            )
            result = await self._send_member_command(
                member_id=member_fallback_id,
                device=device,
                command=command,
                properties=properties,
            )

        if (
            member_fallback_id
            and isinstance(result, dict)
            and result.get("pushSuccess") is False
        ):
            route = "group_push_fail_fallback_member"
            _LOGGER.warning(
                "Group command %s to %s returned pushSuccess=false, "
                "fallback to member %s",
                command,
                device.serial,
                member_fallback_id,
            )
            result = await self._send_member_command(
                member_id=member_fallback_id,
                device=device,
                command=command,
                properties=properties,
            )

        return result, route

    async def _send_member_command(
        self,
        *,
        member_id: str,
        device: LiproDevice,
        command: str,
        properties: list[dict[str, str]] | None,
    ) -> Any:
        """Send a command to a specific member device."""
        return await self.client.send_command(
            member_id,
            command,
            device.device_type,
            properties,
            device.iot_name,
        )

    def _update_trace_with_response(self, trace: dict[str, Any], result: Any) -> None:
        """Attach API response metadata to command trace."""
        if not isinstance(result, dict):
            return

        trace["push_success"] = result.get("pushSuccess")
        trace["response_code"] = result.get("code") or result.get("errorCode")
        trace["response_message"] = result.get("message")
        trace["response_msg_sn"] = result.get("msgSn")
        trace["response_push_timestamp"] = result.get("pushTimestamp")

    def _record_push_failure_trace(
        self,
        trace: dict[str, Any],
        route: str,
        command: str,
        device_name: str,
    ) -> None:
        """Record failed command push result as a trace event."""
        trace["route"] = route
        trace["success"] = False
        trace["error"] = "PushFailed"
        trace["error_message"] = "pushSuccess=false"
        self._record_command_trace(trace)
        _LOGGER.warning(
            "Command %s sent to %s but push failed (device may be offline)",
            command,
            device_name,
        )

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
        skip_immediate_refresh = _should_skip_immediate_post_refresh(command, properties)
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

    def _record_command_exception_trace(
        self,
        trace: dict[str, Any],
        route: str,
        err: LiproApiError,
    ) -> None:
        """Record failed command trace from API exception."""
        trace["route"] = route
        trace["success"] = False
        trace["error"] = type(err).__name__
        trace["error_message"] = str(err)
        trace["error_code"] = err.code
        self._record_command_trace(trace)

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
        trace = self._build_command_trace(
            device,
            command,
            properties,
            fallback_device_id,
        )
        route = "device_direct"

        try:
            await self.auth_manager.ensure_valid_token()
            self._clear_auth_issues()

            (
                route,
                actual_command,
                actual_properties,
                member_fallback_id,
            ) = self._resolve_command_request(
                device,
                command,
                properties,
                fallback_device_id,
            )
            trace["effective_fallback_device_id"] = _redact_identifier(
                member_fallback_id
            )
            trace["resolved_command"] = actual_command
            trace["resolved_property_count"] = len(actual_properties or [])
            trace["resolved_property_keys"] = self._extract_property_keys(
                actual_properties
            )

            result, route = await self._dispatch_command(
                device=device,
                command=actual_command,
                properties=actual_properties,
                route=route,
                member_fallback_id=member_fallback_id,
            )

            self._update_trace_with_response(trace, result)
            if isinstance(result, dict) and result.get("pushSuccess") is False:
                self._record_push_failure_trace(
                    trace=trace,
                    route=route,
                    command=command,
                    device_name=device.name,
                )
                return False

            self._finalize_successful_command(
                device=device,
                command=actual_command,
                properties=actual_properties,
                route=route,
                trace=trace,
            )

            return True

        except LiproRefreshTokenExpiredError as err:
            self._record_command_exception_trace(trace, route, err)
            _LOGGER.warning(
                "Refresh token expired while sending command to %s", device.name
            )
            await self._trigger_reauth("auth_expired")
            return False
        except LiproAuthError as err:
            self._record_command_exception_trace(trace, route, err)
            _LOGGER.warning(
                "Auth error sending command to %s, triggering reauth", device.name
            )
            await self._trigger_reauth("auth_error")
            return False
        except LiproApiError as err:
            self._record_command_exception_trace(trace, route, err)
            _LOGGER.warning("Failed to send command to %s: %s", device.name, err)
            return False

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
        if self._post_command_refresh_task and not self._post_command_refresh_task.done():
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
