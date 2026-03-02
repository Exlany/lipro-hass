"""Anonymous device information sharing for Lipro integration.

Collects anonymous device information and error reports to help improve
the integration. All data collection is opt-in and privacy-preserving.

This module allows users to voluntarily share their device information
to help developers support more device types and fix issues.
"""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from inspect import isawaitable
import json
import logging
from pathlib import Path
import re
import time
from typing import TYPE_CHECKING, Any, Final

import aiohttp

from ...const import (
    PROP_ACTIVATED,
    PROP_AERATION_GEAR,
    PROP_BATTERY,
    PROP_BODY_REACTIVE,
    PROP_BRIGHTNESS,
    PROP_DARK,
    PROP_DOOR_OPEN,
    PROP_FADE_STATE,
    PROP_FAN_GEAR,
    PROP_FAN_MODE,
    PROP_FOCUS_MODE,
    PROP_HEATER_MODE,
    PROP_LIGHT_MODE,
    PROP_POSITION,
    PROP_SLEEP_AID_ENABLE,
    PROP_TEMPERATURE,
    PROP_WAKE_UP_ENABLE,
    PROP_WIND_GEAR,
    VERSION,
)

if TYPE_CHECKING:
    from ..device import LiproDevice

_LOGGER = logging.getLogger(__name__)

# Pre-compiled patterns for sensitive data detection and sanitization
_RE_MAC_ADDRESS = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
_RE_MAC_EXACT = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
# Compact MAC-like identifiers seen in payloads (e.g., rcList.address).
_RE_MAC_COMPACT = re.compile(r"\b[0-9A-Fa-f]{12}\b")
_RE_MAC_COMPACT_EXACT = re.compile(r"^[0-9A-Fa-f]{12}$")
_RE_IP_ADDRESS = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
_RE_IP_EXACT = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
_RE_DEVICE_ID = re.compile(r"03ab[0-9a-f]{12}", re.IGNORECASE)
_RE_DEVICE_ID_EXACT = re.compile(r"^03ab[0-9a-f]{12}$", re.IGNORECASE)
_RE_TOKEN_LIKE = re.compile(r"^[a-zA-Z0-9_-]{32,}$")
_RE_TOKEN_EMBEDDED = re.compile(r"\b[a-zA-Z0-9_-]{32,}\b")
_RE_AUTH_BEARER = re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;\"']+")
_RE_SECRET_KV = re.compile(
    r"(?i)\b(access[_-]?token|refresh[_-]?token|api[_-]?key|secret|password)\b"
    r"(\s*[:=]\s*)([^\s,;\"']+)"
)

# Anonymous share server endpoints
#
# NOTE: `X-API-Key` is a *public* client identifier used for coarse attribution
# and anti-abuse shaping on the Worker side (not a secret).
SHARE_BASE_URL: Final = "https://lipro-share.lany.me"
SHARE_REPORT_URL: Final = f"{SHARE_BASE_URL}/api/report"
SHARE_TOKEN_REFRESH_URL: Final = f"{SHARE_BASE_URL}/api/token/refresh"
SHARE_API_KEY: Final = "lipro-ha-share-2026"

# Keys to always redact from reports
REDACT_KEYS: Final = frozenset(
    {
        "deviceId",
        "serial",
        "mac",
        "ip",
        "wifi_ssid",
        "wifiSsid",
        "bleMac",
        "deviceName",
        "roomName",
        "roomId",
        "userId",
        "bizId",
        "access_token",
        "refresh_token",
        "phone",
        "password",
        "gatewayDeviceId",
    }
)

# Pre-computed lowercase version for efficient lookups in sanitization
_REDACT_KEYS_LOWER: Final[frozenset[str]] = frozenset(k.lower() for k in REDACT_KEYS)
_SENSITIVE_KEY_RULES: Final[tuple[frozenset[str], ...]] = (_REDACT_KEYS_LOWER,)
_SANITIZE_STRING_RULES: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (_RE_AUTH_BEARER, r"\1[TOKEN]"),
    (_RE_SECRET_KV, r"\1\2[REDACTED]"),
    (_RE_TOKEN_EMBEDDED, "[TOKEN]"),
    (_RE_MAC_ADDRESS, "[MAC]"),
    (_RE_MAC_COMPACT, "[MAC]"),
    (_RE_IP_ADDRESS, "[IP]"),
    (_RE_DEVICE_ID, "[DEVICE_ID]"),
)
_SENSITIVE_VALUE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    _RE_MAC_EXACT,
    _RE_MAC_COMPACT_EXACT,
    _RE_IP_EXACT,
    _RE_DEVICE_ID_EXACT,
    _RE_TOKEN_LIKE,
)

# Maximum items to keep in memory before forcing upload
MAX_PENDING_ERRORS: Final = 50
MAX_PENDING_DEVICES: Final = 20

# Minimum interval between uploads (seconds)
MIN_UPLOAD_INTERVAL: Final = 3600  # 1 hour

# Sanitization limits for privacy-preserving data truncation
_MAX_LIST_ITEMS: Final = 50  # Max items when sanitizing lists
_MAX_DICT_ITEMS: Final = 100  # Max key/value pairs when sanitizing mappings
_MAX_NESTED_DEPTH: Final = 8  # Max recursive depth when preserving structure
_MAX_STRING_LENGTH: Final = 500  # Strings longer than this are truncated
_TRUNCATED_STRING_PREFIX_LENGTH: Final = 200  # Keep this many chars when truncating

# Auto-upload interval: force upload if no upload in 24 hours
AUTO_UPLOAD_INTERVAL: Final = MIN_UPLOAD_INTERVAL * 24  # 24 hours

_LIGHT_PRIMARY_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_BRIGHTNESS, "brightness"),
    (PROP_TEMPERATURE, "color_temp"),
)

_LIGHT_SECONDARY_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_FADE_STATE, "fade"),
    (PROP_FOCUS_MODE, "focus_mode"),
    (PROP_SLEEP_AID_ENABLE, "sleep_aid"),
    (PROP_WAKE_UP_ENABLE, "wake_up"),
)

_FAN_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_FAN_GEAR, "fan_speed"),
    (PROP_FAN_MODE, "fan_mode"),
)

_SENSOR_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_BATTERY, "battery"),
    (PROP_DOOR_OPEN, "door_sensor"),
    (PROP_DARK, "light_sensor"),
)

_HEATER_PROPERTY_CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    (PROP_HEATER_MODE, "heater_mode"),
    (PROP_WIND_GEAR, "wind_speed"),
    (PROP_AERATION_GEAR, "aeration"),
    (PROP_LIGHT_MODE, "heater_light"),
)

_MOTION_SENSOR_TRIGGER_PROPERTIES: Final[frozenset[str]] = frozenset(
    {PROP_BODY_REACTIVE, PROP_ACTIVATED}
)


def _is_sensitive_key(key: Any) -> bool:
    """Return True when a key should be dropped from anonymized payloads."""
    if not isinstance(key, str):
        return False
    lowered = key.lower()
    return any(lowered in key_set for key_set in _SENSITIVE_KEY_RULES)


@dataclass
class SharedError:
    """Represents a collected error.

    Flattened format for Worker API compatibility.
    """

    error_type: str
    message: str = ""
    endpoint: str = ""
    iot_name: str = ""
    device_type: str = ""
    timestamp: float = field(default_factory=time.time)
    count: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        message = self.message
        if self.count > 1:
            message = f"{message} (x{self.count})"
        return {
            "type": self.error_type,
            "message": message,
            "endpoint": self.endpoint,
            "iot_name": self.iot_name,
            "device_type": self.device_type,
            "timestamp": datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat(),
        }


@dataclass
class SharedDevice:
    """Represents collected device information."""

    physical_model: str | None
    iot_name: str
    device_type: int
    product_id: int | None
    is_group: bool
    category: str
    firmware_version: str | None
    property_keys: list[str]
    properties: dict[str, Any]  # Sanitized property values (preserves structure)
    # New fields for device capabilities
    min_color_temp_kelvin: int = 0
    max_color_temp_kelvin: int = 0
    has_gear_presets: bool = False
    gear_count: int = 0
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "physical_model": self.physical_model,
            "iot_name": self.iot_name,
            "device_type": self.device_type,
            "product_id": self.product_id,
            "is_group": self.is_group,
            "category": self.category,
            "firmware_version": self.firmware_version,
            "property_keys": self.property_keys,
            "properties": self.properties,
            # New fields
            "min_color_temp_kelvin": self.min_color_temp_kelvin,
            "max_color_temp_kelvin": self.max_color_temp_kelvin,
            "has_gear_presets": self.has_gear_presets,
            "gear_count": self.gear_count,
            "capabilities": self.capabilities,
        }


class AnonymousShareManager:
    """Collects anonymous device information and error reports.

    All collection is opt-in and respects user privacy.
    Only collects NEW devices that haven't been reported before.
    """

    def __init__(self) -> None:
        """Initialize the share manager."""
        self._enabled = False
        self._error_reporting_enabled = False
        self._devices: dict[str, SharedDevice] = {}  # Keyed by anonymized ID
        self._errors: deque[SharedError] = deque(maxlen=MAX_PENDING_ERRORS)
        self._unknown_properties: set[tuple[str, str]] = set()  # (device_type, key)
        self._unknown_device_types: set[tuple[str | None, int]] = set()
        self._last_upload_time: float = 0
        self._upload_lock = asyncio.Lock()
        self._installation_id: str | None = None
        self._ha_version: str | None = None
        # Install token state (Worker-side install token, unrelated to Lipro API tokens)
        self._install_token: str | None = None
        self._token_expires_at: int = 0  # epoch seconds
        self._token_refresh_after: int = 0  # epoch seconds
        self._next_upload_attempt_at: float = 0.0
        # Track already reported devices to avoid duplicates
        self._reported_device_keys: set[str] = set()
        self._storage_path: str | None = None
        self._cache_loaded: bool = True  # True = no load needed

    def set_enabled(
        self,
        enabled: bool,
        error_reporting: bool = True,
        installation_id: str | None = None,
        storage_path: str | None = None,
        ha_version: str | None = None,
    ) -> None:
        """Enable or disable anonymous sharing.

        Args:
            enabled: Whether to enable device info sharing.
            error_reporting: Whether to enable error reporting.
            installation_id: Anonymous installation ID for deduplication.
            storage_path: Path to store reported device cache.
            ha_version: Home Assistant version string.

        """
        self._enabled = enabled
        self._error_reporting_enabled = error_reporting
        self._installation_id = installation_id
        self._storage_path = storage_path
        self._ha_version = ha_version
        if enabled and storage_path:
            # Defer loading to async context to avoid blocking the event loop
            self._cache_loaded = False
        if not enabled:
            self.clear()

    @property
    def is_enabled(self) -> bool:
        """Return whether anonymous sharing is enabled."""
        return self._enabled

    @property
    def pending_count(self) -> tuple[int, int]:
        """Return count of pending items (devices, errors)."""
        return len(self._devices), len(self._errors)

    def clear(self) -> None:
        """Clear all pending data (does not clear reported device cache)."""
        self._devices.clear()
        self._errors.clear()
        self._unknown_properties.clear()
        self._unknown_device_types.clear()

    async def async_ensure_loaded(self) -> None:
        """Load reported device cache in a thread to avoid blocking the event loop."""
        if self._cache_loaded:
            return
        # Mark loaded after the actual load completes to avoid race conditions
        # where a concurrent caller skips loading before data is ready.
        await asyncio.to_thread(self._load_reported_devices)
        self._cache_loaded = True

    def _load_reported_devices(self) -> None:
        """Load previously reported device keys from storage."""
        if not self._storage_path:
            return
        cache_file = Path(self._storage_path) / ".lipro_reported_devices.json"
        try:
            if cache_file.exists():
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                self._reported_device_keys = set(data.get("devices", []))
                _LOGGER.debug(
                    "Loaded %d reported device keys from cache",
                    len(self._reported_device_keys),
                )
        except (OSError, json.JSONDecodeError, TypeError) as err:
            _LOGGER.warning("Failed to load reported devices cache: %s", err)

    def _save_reported_devices(self) -> None:
        """Save reported device keys to storage."""
        if not self._storage_path:
            return
        cache_file = Path(self._storage_path) / ".lipro_reported_devices.json"
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(
                json.dumps({"devices": list(self._reported_device_keys)}),
                encoding="utf-8",
            )
        except OSError as err:
            _LOGGER.warning("Failed to save reported devices cache: %s", err)

    # =========================================================================
    # Device Information Collection
    # =========================================================================

    def record_device(self, device: LiproDevice) -> None:
        """Record device information (only if model not already reported).

        Args:
            device: The device to record.

        """
        if not self._enabled:
            return

        # 按 iot_name 去重（同款设备只存一份）；空值统一占位，避免上报不可匹配键。
        normalized_iot_name = device.iot_name or "unknown"
        device_key = normalized_iot_name

        # Skip if model already reported
        if device_key in self._reported_device_keys:
            return

        # Sanitize properties
        sanitized_props = self._sanitize_properties(device.properties)

        # Collect device capabilities
        capabilities = self._detect_capabilities(device)

        # Get gear list info
        gear_list = device.gear_list
        has_gear_presets = bool(gear_list)
        gear_count = len(gear_list) if gear_list else 0

        self._devices[device_key] = SharedDevice(
            physical_model=device.physical_model,
            iot_name=normalized_iot_name,
            device_type=device.device_type,
            product_id=device.product_id,
            is_group=device.is_group,
            category=str(device.category.value),
            firmware_version=device.firmware_version,
            property_keys=list(device.properties.keys()),
            properties=sanitized_props,
            # New fields
            min_color_temp_kelvin=device.min_color_temp_kelvin,
            max_color_temp_kelvin=device.max_color_temp_kelvin,
            has_gear_presets=has_gear_presets,
            gear_count=gear_count,
            capabilities=capabilities,
        )

    @staticmethod
    def _append_capabilities_for_properties(
        capabilities: list[str],
        properties: dict[str, Any],
        mappings: tuple[tuple[str, str], ...],
    ) -> None:
        """Append capabilities for present property keys in declared order."""
        for prop_key, capability in mappings:
            if prop_key in properties:
                capabilities.append(capability)

    @staticmethod
    def _has_any_property(
        properties: dict[str, Any],
        candidates: frozenset[str],
    ) -> bool:
        """Return True when at least one candidate property is present."""
        return any(prop_key in properties for prop_key in candidates)

    def _detect_capabilities(self, device: LiproDevice) -> list[str]:
        """Detect device capabilities from properties and category.

        Args:
            device: The device to analyze.

        Returns:
            List of capability strings.

        """
        caps: list[str] = []
        props = device.properties

        if device.is_light:
            caps.append("light")
            self._append_capabilities_for_properties(
                caps,
                props,
                _LIGHT_PRIMARY_PROPERTY_CAPABILITIES,
            )
            if device.has_gear_presets:
                caps.append("gear_presets")
            self._append_capabilities_for_properties(
                caps,
                props,
                _LIGHT_SECONDARY_PROPERTY_CAPABILITIES,
            )

        if device.is_fan_light:
            caps.append("fan")
            self._append_capabilities_for_properties(
                caps,
                props,
                _FAN_PROPERTY_CAPABILITIES,
            )

        if device.is_curtain:
            caps.append("cover")
            if PROP_POSITION in props:
                caps.append("position")

        if device.is_sensor:
            caps.append("sensor")
            self._append_capabilities_for_properties(
                caps,
                props,
                _SENSOR_PROPERTY_CAPABILITIES,
            )
            if self._has_any_property(props, _MOTION_SENSOR_TRIGGER_PROPERTIES):
                caps.append("motion_sensor")

        if device.is_heater:
            caps.append("heater")
            self._append_capabilities_for_properties(
                caps,
                props,
                _HEATER_PROPERTY_CAPABILITIES,
            )

        if device.is_switch or device.is_outlet:
            caps.append("switch")

        return caps

    def record_devices(self, devices: list[LiproDevice]) -> None:
        """Record multiple devices.

        Args:
            devices: List of devices to record.

        """
        for device in devices:
            self.record_device(device)

    # =========================================================================
    # Error Collection
    # =========================================================================

    def _can_record_error(self) -> bool:
        """Return whether error collection is currently enabled."""
        return self._enabled and self._error_reporting_enabled

    def record_unknown_property(
        self,
        device_type: str,
        key: str,
        value: Any,
    ) -> None:
        """Record an unknown property key.

        Args:
            device_type: The device type (physical_model or category).
            key: The unknown property key.
            value: The property value (will be sanitized).

        """
        if not self._can_record_error():
            return

        # Deduplicate
        if (device_type, key) in self._unknown_properties:
            return
        self._unknown_properties.add((device_type, key))

        self._add_error(
            error_type="unknown_property",
            message=f"key={key}, value={self._sanitize_value(value)}",
            device_type=device_type,
        )

    def record_unknown_device_type(
        self,
        physical_model: str | None,
        type_id: int,
        iot_name: str = "",
    ) -> None:
        """Record an unknown device type.

        Args:
            physical_model: The physical model string.
            type_id: The numeric type ID.
            iot_name: The IoT name/model.

        """
        if not self._can_record_error():
            return

        # Deduplicate
        if (physical_model, type_id) in self._unknown_device_types:
            return
        self._unknown_device_types.add((physical_model, type_id))

        self._add_error(
            error_type="unknown_device_type",
            message=f"type={type_id}, model={physical_model}",
            iot_name=iot_name,
        )

    def record_api_error(
        self,
        endpoint: str,
        code: str | int,
        message: str,
        method: str = "",
    ) -> None:
        """Record an API error.

        Args:
            endpoint: The API endpoint that failed.
            code: The error code.
            message: The error message.
            method: The HTTP method (e.g., "POST").

        """
        if not self._can_record_error():
            return

        prefix = f"[{code}] "
        if method:
            prefix += f"{method} "
        self._add_error(
            error_type="api_error",
            message=f"{prefix}{endpoint}: {message[:200]}",
            endpoint=endpoint,
        )

    def record_parse_error(
        self,
        location: str,
        exception: Exception,
        input_sample: str | None = None,
    ) -> None:
        """Record a parsing error.

        Args:
            location: Code location (e.g., "device.py:parse_properties").
            exception: The exception that occurred.
            input_sample: Optional sample of input that caused the error.

        """
        if not self._can_record_error():
            return

        exc_type = type(exception).__name__
        exc_msg = str(exception)[:200]
        sample = ""
        if input_sample:
            sample = f" input={self._sanitize_string(input_sample)[:300]}"

        self._add_error(
            error_type="parse_error",
            message=f"[{exc_type}] {exc_msg}{sample}",
            endpoint=location,
        )

    def record_command_error(
        self,
        command: str,
        device_type: str,
        code: str | int,
        message: str,
        params: str = "",
    ) -> None:
        """Record a command execution error.

        Args:
            command: The command that failed.
            device_type: The device type.
            code: The error code.
            message: The error message.
            params: Command parameters summary.

        """
        if not self._can_record_error():
            return

        cmd = f"{command}({params})" if params else command
        self._add_error(
            error_type="command_error",
            message=f"[{code}] {cmd}: {message[:200]}",
            device_type=device_type,
        )

    def _add_error(
        self,
        error_type: str,
        message: str = "",
        endpoint: str = "",
        iot_name: str = "",
        device_type: str = "",
    ) -> None:
        """Add an error to the collection, merging duplicates by count.

        Args:
            error_type: Type of error.
            message: Error message.
            endpoint: API endpoint (if applicable).
            iot_name: Device IoT name (if applicable).
            device_type: Device type (if applicable).

        """
        sanitized_message = self._sanitize_string(message)
        sanitized_endpoint = self._sanitize_string(endpoint)
        sanitized_iot_name = self._sanitize_string(iot_name)
        sanitized_device_type = self._sanitize_string(device_type)

        # Try to merge with existing error of same type and message prefix
        msg_prefix = sanitized_message[:80]
        for existing in self._errors:
            if (
                existing.error_type == error_type
                and existing.message[:80] == msg_prefix
            ):
                existing.count += 1
                existing.timestamp = time.time()
                return

        # deque(maxlen=MAX_PENDING_ERRORS) auto-evicts oldest on overflow
        self._errors.append(
            SharedError(
                error_type=error_type,
                message=sanitized_message,
                endpoint=sanitized_endpoint,
                iot_name=sanitized_iot_name,
                device_type=sanitized_device_type,
            )
        )

    # =========================================================================
    # Data Sanitization
    # =========================================================================

    def _sanitize_properties(self, properties: dict[str, Any]) -> dict[str, Any]:
        """Sanitize device properties for reporting.

        Keeps most property values intact for debugging, only redacts
        truly sensitive data like MAC addresses, IPs, and device IDs.

        Args:
            properties: Raw properties.

        Returns:
            Sanitized properties with sensitive values removed.

        """
        result = {}
        for key, value in properties.items():
            # Skip known sensitive keys
            if _is_sensitive_key(key):
                continue
            # Keep the value, only sanitize if it looks sensitive
            result[key] = self._sanitize_value(value, preserve_structure=True)
        return result

    def _sanitize_mapping(
        self,
        value: dict[Any, Any],
        *,
        depth: int,
    ) -> dict[str, Any]:
        """Sanitize mapping values while preserving structure and limits."""
        result: dict[str, Any] = {}
        for key, item in value.items():
            if len(result) >= _MAX_DICT_ITEMS:
                break
            if _is_sensitive_key(key):
                continue
            result[str(key)] = self._sanitize_value(
                item,
                preserve_structure=True,
                _depth=depth + 1,
            )
        return result

    def _sanitize_list(self, value: list[Any], *, depth: int) -> list[Any]:
        """Sanitize list values while preserving order and limits."""
        return [
            self._sanitize_value(
                item,
                preserve_structure=True,
                _depth=depth + 1,
            )
            for item in value[:_MAX_LIST_ITEMS]
        ]

    def _sanitize_json_string(self, value: str, *, depth: int) -> str | None:
        """Sanitize JSON string payloads recursively when parseable."""
        stripped = value.strip()
        if not stripped or stripped[0] not in "{[":
            return None
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return None
        if not isinstance(parsed, (dict, list)):
            return None
        sanitized = self._sanitize_value(
            parsed,
            preserve_structure=True,
            _depth=depth + 1,
        )
        return json.dumps(
            sanitized,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def _sanitize_value(
        self,
        value: Any,
        preserve_structure: bool = False,
        *,
        _depth: int = 0,
    ) -> Any:
        """Sanitize a single value.

        Args:
            value: The value to sanitize.
            preserve_structure: If True, preserve lists/dicts structure.

        Returns:
            Sanitized value (keeps original type when possible).

        """
        if value is None:
            return None

        # Preserve structure for complex types
        if preserve_structure:
            if _depth >= _MAX_NESTED_DEPTH:
                return {}
            if isinstance(value, dict):
                return self._sanitize_mapping(value, depth=_depth)
            if isinstance(value, list):
                return self._sanitize_list(value, depth=_depth)

        if isinstance(value, str):
            # Some payload fields (e.g., deviceInfo/rcList) are JSON strings.
            # Parse and sanitize recursively to avoid leaking nested identifiers.
            if preserve_structure:
                sanitized_json = self._sanitize_json_string(value, depth=_depth)
                if sanitized_json is not None:
                    return sanitized_json

        str_value = str(value)

        # Check for potential sensitive patterns
        if self._looks_sensitive(str_value):
            return "[redacted]"

        sanitized_value = self._sanitize_string(str_value)
        if sanitized_value != str_value:
            return sanitized_value

        # Keep numeric values as-is
        # Note: isinstance() does not accept PEP604 unions at runtime.
        if isinstance(value, (bool, int, float)):
            return value

        # Truncate very long strings
        if len(str_value) > _MAX_STRING_LENGTH:
            return str_value[:_TRUNCATED_STRING_PREFIX_LENGTH] + "...[truncated]"

        return value

    def _sanitize_string(self, value: str) -> str:
        """Sanitize a string, removing potential sensitive data.

        Args:
            value: The string to sanitize.

        Returns:
            Sanitized string.

        """
        result = value
        for pattern, replacement in _SANITIZE_STRING_RULES:
            result = pattern.sub(replacement, result)
        return result

    def _looks_sensitive(self, value: str) -> bool:
        """Check if a value looks like sensitive data.

        Args:
            value: The value to check.

        Returns:
            True if the value appears sensitive.

        """
        return any(pattern.match(value) for pattern in _SENSITIVE_VALUE_PATTERNS)

    # =========================================================================
    # Report Generation and Upload
    # =========================================================================

    def build_report(self) -> dict[str, Any]:
        """Build the anonymous share report.

        Returns:
            Complete report ready for submission.

        """
        return {
            "report_version": "1.1",
            "integration_version": VERSION,
            "ha_version": self._ha_version,
            "generated_at": datetime.now(UTC).isoformat(),
            "installation_id": self._installation_id,
            "device_count": len(self._devices),
            "error_count": len(self._errors),
            "devices": [d.to_dict() for d in self._devices.values()],
            "errors": [e.to_dict() for e in self._errors],
        }

    def get_pending_report(self) -> dict[str, Any] | None:
        """Get pending report data for user review.

        Returns:
            Report data or None if nothing to report.

        """
        if not self._devices and not self._errors:
            return None
        return self.build_report()

    def _build_developer_feedback_report(
        self,
        feedback: dict[str, Any],
    ) -> dict[str, Any]:
        """Build one developer-feedback report payload.

        The payload reuses the same endpoint/protocol as anonymous share reports
        so server-side collection remains centralized.
        """
        sanitized_feedback = self._sanitize_value(feedback, preserve_structure=True)
        if not isinstance(sanitized_feedback, dict):
            sanitized_feedback = {"value": sanitized_feedback}

        return {
            "report_version": "1.2",
            "integration_version": VERSION,
            "ha_version": self._ha_version,
            "generated_at": datetime.now(UTC).isoformat(),
            "installation_id": self._installation_id or "manual",
            "device_count": 0,
            "error_count": 0,
            "devices": [],
            "errors": [],
            "developer_feedback": sanitized_feedback,
        }

    @staticmethod
    def _build_upload_headers(*, install_token: str | None = None) -> dict[str, str]:
        """Build common headers for share uploads."""
        headers = {
            "User-Agent": f"HomeAssistant/Lipro {VERSION}",
            "X-API-Key": SHARE_API_KEY,
        }
        if install_token:
            headers["Authorization"] = f"Bearer {install_token}"
        return headers

    @staticmethod
    def _parse_retry_after(headers: Any) -> float | None:
        """Parse Retry-After seconds (best-effort)."""
        try:
            value = headers.get("Retry-After") or headers.get("retry-after")
            if not value:
                return None
            seconds = float(str(value).strip())
            if seconds <= 0:
                return 0.1
            return seconds
        except (AttributeError, TypeError, ValueError):
            return None

    def _clear_install_token(self) -> None:
        """Clear local install-token state."""
        self._install_token = None
        self._token_expires_at = 0
        self._token_refresh_after = 0

    def _apply_token_payload(self, payload: dict[str, Any]) -> bool:
        """Update local token state from response payload."""
        token = payload.get("install_token")
        if not isinstance(token, str) or not token:
            return False
        self._install_token = token
        self._token_expires_at = int(payload.get("token_expires_at") or 0)
        self._token_refresh_after = int(payload.get("token_refresh_after") or 0)
        return True

    @staticmethod
    def _build_lite_report(report: dict[str, Any]) -> dict[str, Any]:
        """Build a smaller report variant for 413 retries."""
        lite: dict[str, Any] = {
            "report_version": report.get("report_version"),
            "integration_version": report.get("integration_version"),
            "ha_version": report.get("ha_version"),
            "generated_at": report.get("generated_at"),
            "installation_id": report.get("installation_id"),
            "device_count": report.get("device_count"),
            "error_count": report.get("error_count"),
        }

        devices = report.get("devices")
        if isinstance(devices, list):
            compact_devices: list[dict[str, Any]] = []
            for item in devices[:10]:
                if not isinstance(item, dict):
                    continue
                compact_devices.append(
                    {
                        "physical_model": item.get("physical_model"),
                        "iot_name": item.get("iot_name"),
                        "device_type": item.get("device_type"),
                        "product_id": item.get("product_id"),
                        "is_group": item.get("is_group"),
                        "category": item.get("category"),
                        "firmware_version": item.get("firmware_version"),
                        "capabilities": item.get("capabilities"),
                        "has_gear_presets": item.get("has_gear_presets"),
                        "gear_count": item.get("gear_count"),
                        "min_color_temp_kelvin": item.get("min_color_temp_kelvin"),
                        "max_color_temp_kelvin": item.get("max_color_temp_kelvin"),
                    }
                )
            lite["devices"] = compact_devices

        errors = report.get("errors")
        if isinstance(errors, list):
            lite["errors"] = [e for e in errors[:10] if isinstance(e, dict)]

        if "developer_feedback" in report:
            feedback = report.get("developer_feedback")
            if isinstance(feedback, str):
                lite["developer_feedback"] = feedback[:2000]
            else:
                lite["developer_feedback"] = feedback

        return lite

    async def _safe_read_json(
        self,
        response: aiohttp.ClientResponse,
    ) -> dict[str, Any] | None:
        """Best-effort JSON parsing for Worker responses."""
        try:
            json_reader = getattr(response, "json", None)
            if not callable(json_reader):
                return None
            result = response.json(content_type=None)
            data = await result if isawaitable(result) else result
        except (
            AttributeError,
            aiohttp.ContentTypeError,
            json.JSONDecodeError,
            ValueError,
        ):
            return None
        return data if isinstance(data, dict) else None

    async def _refresh_install_token(self, session: aiohttp.ClientSession) -> bool:
        """Refresh install token via /api/token/refresh when needed."""
        if not self._install_token:
            return False
        if time.time() < self._next_upload_attempt_at:
            return False

        try:
            async with session.post(
                SHARE_TOKEN_REFRESH_URL,
                headers=self._build_upload_headers(install_token=self._install_token),
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                payload = await self._safe_read_json(response)
                if response.status == 200 and payload:
                    if self._apply_token_payload(payload):
                        return True

                code = payload.get("code") if payload else None
                if response.status == 401 and code in {
                    "TOKEN_EXPIRED",
                    "TOKEN_REVOKED",
                    "TOKEN_VERSION_REVOKED",
                    "TOKEN_KEY_NOT_FOUND",
                    "TOKEN_SIGNATURE_INVALID",
                    "TOKEN_CLAIMS_INVALID",
                    "TOKEN_STATE_MISSING",
                }:
                    self._clear_install_token()
                    return False

                if response.status == 429:
                    retry_after = self._parse_retry_after(response.headers)
                    if retry_after is not None:
                        self._next_upload_attempt_at = time.time() + min(
                            60.0, retry_after
                        )
                    return False

                return False
        except TimeoutError:
            return False
        except aiohttp.ClientError:
            return False
        except (OSError, ValueError):
            return False

    async def _submit_share_payload(
        self,
        session: aiohttp.ClientSession,
        report: dict[str, Any],
        *,
        label: str,
    ) -> bool:
        """Submit one payload to share endpoint with unified error handling."""
        await self.async_ensure_loaded()

        if time.time() < self._next_upload_attempt_at:
            return False

        installation_id = report.get("installation_id")
        if not isinstance(installation_id, str) or not installation_id:
            _LOGGER.warning("%s upload skipped: missing installation_id", label)
            return False

        # Refresh token proactively when we're past refresh window / near expiry.
        if self._install_token:
            now_sec = int(time.time())
            if (self._token_refresh_after and now_sec >= self._token_refresh_after) or (
                self._token_expires_at and (self._token_expires_at - now_sec) <= 60
            ):
                await self._refresh_install_token(session)

        # Try token mode first when available, then fall back to bootstrap.
        token_attempts: list[str | None] = (
            [self._install_token, None] if self._install_token else [None]
        )

        try:
            payload_variants = [report, self._build_lite_report(report)]

            last_status: int | None = None
            for variant_index, report_variant in enumerate(payload_variants):
                for token in token_attempts:
                    async with session.post(
                        SHARE_REPORT_URL,
                        json=report_variant,
                        headers=self._build_upload_headers(install_token=token),
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        last_status = response.status
                        payload = await self._safe_read_json(response)

                        if response.status == 200:
                            if payload:
                                self._apply_token_payload(payload)
                            return True

                        code = payload.get("code") if payload else None

                        if response.status == 429:
                            retry_after = self._parse_retry_after(response.headers)
                            if retry_after is not None:
                                self._next_upload_attempt_at = time.time() + min(
                                    60.0, retry_after
                                )
                            return False

                        if response.status == 413 and variant_index == 0:
                            # Retry once with a smaller payload.
                            break

                        if response.status == 401 and code in {
                            "TOKEN_VERSION_REVOKED",
                            "TOKEN_REVOKED",
                            "TOKEN_EXPIRED",
                            "TOKEN_REQUIRED",
                            "TOKEN_MISSING",
                            "TOKEN_STATE_MISSING",
                            "TOKEN_KEY_NOT_FOUND",
                            "TOKEN_SIGNATURE_INVALID",
                            "TOKEN_CLAIMS_INVALID",
                            "TOKEN_INSTALLATION_MISMATCH",
                        }:
                            # Token no longer usable; clear and retry bootstrap once.
                            if token:
                                self._clear_install_token()
                                continue
                            return False

                        if response.status == 400 and code == "INVALID_SCHEMA":
                            return False

                # continue to next variant

            _LOGGER.warning(
                "%s upload failed with status %s",
                label,
                last_status if last_status is not None else "?",
            )
            return False
        except TimeoutError:
            _LOGGER.warning("%s upload timed out", label)
            return False
        except aiohttp.ClientError as err:
            _LOGGER.warning("%s upload failed: %s", label, err)
            return False
        except (OSError, ValueError):
            _LOGGER.exception("Unexpected error during %s upload", label.lower())
            return False

    async def submit_developer_feedback(
        self,
        session: aiohttp.ClientSession,
        feedback: dict[str, Any],
    ) -> bool:
        """Submit one developer-feedback payload immediately.

        This is an explicit user action from service call, so it does not
        depend on anonymous-share opt-in switches.
        """
        async with self._upload_lock:
            report = self._build_developer_feedback_report(feedback)
            if not await self._submit_share_payload(
                session,
                report,
                label="Developer feedback",
            ):
                return False
            _LOGGER.info("Developer feedback report submitted")
            return True

    async def submit_report(
        self,
        session: aiohttp.ClientSession,
        force: bool = False,
    ) -> bool:
        """Submit the anonymous share report to the server.

        Args:
            session: aiohttp session (should be HA-injected session).
            force: Force upload even if interval hasn't passed.

        Returns:
            True if successful.

        """
        if not self._enabled:
            return False

        # Check if we have anything to report
        if not self._devices and not self._errors:
            _LOGGER.debug("No anonymous share data to report")
            return True

        # Check upload interval (unless forced)
        if not force:
            elapsed = time.time() - self._last_upload_time
            if elapsed < MIN_UPLOAD_INTERVAL:
                _LOGGER.debug(
                    "Skipping anonymous share upload, last upload was %d seconds ago",
                    int(elapsed),
                )
                return True

        async with self._upload_lock:
            report = self.build_report()
            if not await self._submit_share_payload(
                session,
                report,
                label="Anonymous share",
            ):
                return False
            _LOGGER.info(
                "Anonymous share report submitted: %d devices, %d errors",
                len(self._devices),
                len(self._errors),
            )
            self._last_upload_time = time.time()
            # Mark device models as reported
            for device in self._devices.values():
                self._reported_device_keys.add(device.iot_name)
            await asyncio.to_thread(self._save_reported_devices)
            # Clear pending data
            self.clear()
            return True

    async def submit_if_needed(self, session: aiohttp.ClientSession) -> bool:
        """Submit report if thresholds are met.

        Args:
            session: aiohttp session (should be HA-injected session).

        Returns:
            True if submitted successfully or no submission needed.

        """
        if not self._enabled:
            return True

        # Check if we have enough data to warrant an upload
        device_count = len(self._devices)
        error_count = len(self._errors)

        should_upload = (
            device_count >= MAX_PENDING_DEVICES
            or error_count >= MAX_PENDING_ERRORS
            or (time.time() - self._last_upload_time) > AUTO_UPLOAD_INTERVAL
        )

        if should_upload:
            return await self.submit_report(session)

        return True


# Global anonymous share manager instance
_share_manager: AnonymousShareManager | None = None


def get_anonymous_share_manager(
    hass: Any = None,
) -> AnonymousShareManager:
    """Get the anonymous share manager for the given hass instance.

    When hass is provided, the manager is stored in hass.data[DOMAIN]
    and follows the config entry lifecycle. Falls back to a module-level
    instance for contexts without hass (e.g. tests).

    Args:
        hass: Home Assistant instance (optional).

    Returns:
        The anonymous share manager.

    """
    global _share_manager  # noqa: PLW0603

    if hass is not None:
        from ...const import DOMAIN  # noqa: PLC0415

        domain_data = hass.data.setdefault(DOMAIN, {})
        manager: AnonymousShareManager | None = domain_data.get(
            "anonymous_share_manager"
        )
        if manager is None:
            manager = AnonymousShareManager()
            domain_data["anonymous_share_manager"] = manager
        # Keep global in sync so callers without hass (api.py, device.py)
        # use the same instance managed by hass.data lifecycle.
        _share_manager = manager
        return manager

    # Fallback for contexts without hass (tests, standalone usage)
    if _share_manager is None:
        _share_manager = AnonymousShareManager()
    return _share_manager
