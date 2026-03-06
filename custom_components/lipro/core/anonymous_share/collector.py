"""Anonymous share collection logic (devices, errors, unknowns)."""

from __future__ import annotations

from collections import deque
import time
from typing import TYPE_CHECKING, Any

from .capabilities import detect_device_capabilities
from .const import MAX_PENDING_ERRORS
from .models import SharedDevice, SharedError
from .sanitize import is_sensitive_key, sanitize_properties, sanitize_string

if TYPE_CHECKING:
    from ..device import LiproDevice


class AnonymousShareCollector:
    """Collects pending devices and errors for anonymous sharing."""

    def __init__(self) -> None:
        """Initialize the collector."""
        self._enabled = False
        self._error_reporting_enabled = False
        self.devices: dict[str, SharedDevice] = {}  # Keyed by anonymized ID
        self.errors: deque[SharedError] = deque(maxlen=MAX_PENDING_ERRORS)
        self.unknown_properties: set[tuple[str, str]] = set()  # (device_type, key)
        self.unknown_device_types: set[tuple[str | None, int]] = set()

    def set_enabled(self, enabled: bool, *, error_reporting: bool = True) -> None:
        """Enable/disable collection and optionally error reporting."""
        self._enabled = enabled
        self._error_reporting_enabled = error_reporting
        if not enabled:
            self.clear()

    @property
    def is_enabled(self) -> bool:
        """Return whether collection is enabled."""
        return self._enabled

    @property
    def pending_count(self) -> tuple[int, int]:
        """Return count of pending items (devices, errors)."""
        return len(self.devices), len(self.errors)

    def clear(self) -> None:
        """Clear all pending data (does not clear reported-device cache)."""
        self.devices.clear()
        self.errors.clear()
        self.unknown_properties.clear()
        self.unknown_device_types.clear()

    def _can_record_error(self) -> bool:
        """Return whether error collection is currently enabled."""
        return self._enabled and self._error_reporting_enabled

    def record_device(
        self, device: LiproDevice, *, reported_device_keys: set[str]
    ) -> None:
        """Record device information (only if model not already reported)."""
        if not self._enabled:
            return

        if device.has_unknown_physical_model:
            self.record_unknown_device_type(
                device.physical_model,
                device.device_type,
                device.iot_name,
            )

        # 按 iot_name 去重（同款设备只存一份）；空值统一占位，避免上报不可匹配键。
        normalized_iot_name = device.iot_name or "unknown"
        device_key = normalized_iot_name

        if device_key in reported_device_keys:
            return

        sanitized_props = sanitize_properties(device.properties)
        capabilities = detect_device_capabilities(device)

        gear_list = device.gear_list
        has_gear_presets = bool(gear_list)
        gear_count = len(gear_list) if gear_list else 0

        property_keys = [key for key in device.properties if not is_sensitive_key(key)]

        self.devices[device_key] = SharedDevice(
            physical_model=device.physical_model,
            iot_name=normalized_iot_name,
            device_type=device.device_type,
            product_id=device.product_id,
            is_group=device.is_group,
            category=str(device.category.value),
            firmware_version=device.firmware_version,
            property_keys=property_keys,
            properties=sanitized_props,
            min_color_temp_kelvin=device.min_color_temp_kelvin,
            max_color_temp_kelvin=device.max_color_temp_kelvin,
            has_gear_presets=has_gear_presets,
            gear_count=gear_count,
            capabilities=capabilities,
        )

    def record_devices(
        self, devices: list[LiproDevice], *, reported_device_keys: set[str]
    ) -> None:
        """Record multiple devices."""
        for device in devices:
            self.record_device(device, reported_device_keys=reported_device_keys)

    def record_unknown_property(
        self,
        device_type: str,
        key: str,
        value: Any,
    ) -> None:
        """Record an unknown property key."""
        if not self._can_record_error():
            return

        if (device_type, key) in self.unknown_properties:
            return
        self.unknown_properties.add((device_type, key))

        self._add_error(
            error_type="unknown_property",
            message=f"key={key}, value_type={type(value).__name__}",
            device_type=device_type,
        )

    def record_unknown_device_type(
        self,
        physical_model: str | None,
        type_id: int,
        iot_name: str = "",
    ) -> None:
        """Record an unknown device type."""
        if not self._can_record_error():
            return

        if (physical_model, type_id) in self.unknown_device_types:
            return
        self.unknown_device_types.add((physical_model, type_id))

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
        """Record an API error."""
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
        """Record a parsing error."""
        if not self._can_record_error():
            return

        exc_type = type(exception).__name__
        exc_msg = str(exception)[:200]
        sample = ""
        if input_sample:
            sample = f" input_len={len(input_sample)}"

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
        """Record a command execution error."""
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
        """Add an error to the collection, merging duplicates by count."""
        sanitized_message = sanitize_string(message)
        sanitized_endpoint = sanitize_string(endpoint)
        sanitized_iot_name = sanitize_string(iot_name)
        sanitized_device_type = sanitize_string(device_type)

        msg_prefix = sanitized_message[:80]
        for existing in self.errors:
            if (
                existing.error_type == error_type
                and existing.message[:80] == msg_prefix
            ):
                existing.count += 1
                existing.timestamp = time.time()
                return

        self.errors.append(
            SharedError(
                error_type=error_type,
                message=sanitized_message,
                endpoint=sanitized_endpoint,
                iot_name=sanitized_iot_name,
                device_type=sanitized_device_type,
            )
        )
