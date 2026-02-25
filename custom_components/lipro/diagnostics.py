"""Diagnostics support for Lipro integration."""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.diagnostics import async_redact_data

from .const import (
    CONF_PHONE,
    CONF_PHONE_ID,
    DOMAIN,
    PROP_BLE_MAC,
    PROP_IP,
    PROP_MAC,
    PROP_WIFI_SSID,
)
from .core.anonymous_share import get_anonymous_share_manager

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceEntry

    from . import LiproConfigEntry
    from .core.device import LiproDevice

# Keys to redact from diagnostics
# Note: Both snake_case (internal storage) and camelCase (API response) formats
# are included because async_redact_data may encounter either format.
TO_REDACT: Final = {
    # Auth & identity
    CONF_PHONE,
    CONF_PHONE_ID,
    "password",
    "password_hash",
    "access_token",
    "refresh_token",
    # User ID (API: userId, internal: user_id)
    "user_id",
    "userId",
    # Business ID (API: bizId, internal: biz_id)
    "biz_id",
    "bizId",
    # Device identifiers
    "serial",
    "device_id",
    "deviceId",
    "iot_device_id",
    "iotDeviceId",
    "groupId",
    "iotName",
    "gatewayDeviceId",
}

# Keys to redact from device properties
PROPERTY_KEYS_TO_REDACT: Final = {
    PROP_MAC,
    PROP_IP,
    PROP_BLE_MAC,
    PROP_WIFI_SSID,
    "wifiSsid",
    "macAddress",
    "ipAddress",
}

# Pre-computed lowercase set for efficient lookup
_PROPERTY_KEYS_LOWER: Final = frozenset(key.lower() for key in PROPERTY_KEYS_TO_REDACT)

_NESTED_KEYS_TO_REDACT_LOWER: Final = _PROPERTY_KEYS_LOWER | frozenset(
    {
        "deviceid",
        "serial",
        "iotdeviceid",
        "iot_device_id",
        "groupid",
        "gatewaydeviceid",
    }
)

_MAC_LITERAL_RE: Final = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")
_IPV4_LITERAL_RE: Final = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_DEVICE_ID_LITERAL_RE: Final = re.compile(
    r"^03ab[0-9a-f]{12}$",
    re.IGNORECASE,
)
_MAC_EMBEDDED_RE: Final = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")
_IPV4_EMBEDDED_RE: Final = re.compile(r"\d{1,3}(\.\d{1,3}){3}")
_DEVICE_ID_EMBEDDED_RE: Final = re.compile(
    r"03ab[0-9a-f]{12}",
    re.IGNORECASE,
)


def _redact_property_value(value: Any, key: str | None = None) -> Any:
    """Recursively redact sensitive values in property payloads."""
    if key is not None and key.lower() in _NESTED_KEYS_TO_REDACT_LOWER:
        return "**REDACTED**"

    if isinstance(value, dict):
        return {
            k: _redact_property_value(v, str(k))
            for k, v in value.items()
        }

    if isinstance(value, list):
        return [_redact_property_value(item) for item in value]

    if isinstance(value, str):
        stripped = value.strip()

        # deviceInfo/deviceExtra payloads may embed JSON as strings.
        if stripped and stripped[0] in "{[":
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError):
                pass
            else:
                redacted = _redact_property_value(parsed)
                if isinstance(redacted, (dict, list)):
                    return json.dumps(
                        redacted, ensure_ascii=False, separators=(",", ":")
                    )

        if (
            _MAC_LITERAL_RE.fullmatch(stripped)
            or _IPV4_LITERAL_RE.fullmatch(stripped)
            or _DEVICE_ID_LITERAL_RE.fullmatch(stripped)
        ):
            return "**REDACTED**"

        sanitized = _MAC_EMBEDDED_RE.sub("**REDACTED**", value)
        sanitized = _IPV4_EMBEDDED_RE.sub("**REDACTED**", sanitized)
        sanitized = _DEVICE_ID_EMBEDDED_RE.sub("**REDACTED**", sanitized)
        if sanitized != value:
            return sanitized

    return value


def _redact_device_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from device properties."""
    return {
        k: _redact_property_value(v, k)
        for k, v in properties.items()
    }


def _build_device_diagnostics(device: LiproDevice) -> dict[str, Any]:
    """Build redacted diagnostics payload for a single device."""
    device_info: dict[str, Any] = {
        "name": "**REDACTED**",
        "device_type": device.device_type,
        "device_type_hex": device.device_type_hex,
        "category": device.category.value,
        "physical_model": device.physical_model,
        "is_group": device.is_group,
        "room_name": "**REDACTED**",
        "available": device.available,
        "is_connected": device.is_connected,
        "properties": _redact_device_properties(device.properties),
    }
    # Add network info (non-sensitive)
    if device.firmware_version:
        device_info["firmware_version"] = device.firmware_version
    if device.wifi_rssi is not None:
        device_info["wifi_rssi"] = device.wifi_rssi
    if device.net_type:
        device_info["net_type"] = device.net_type
    # Add Mesh info
    if device.mesh_address is not None:
        device_info["mesh_address"] = device.mesh_address
    if device.mesh_type is not None:
        device_info["mesh_type"] = device.mesh_type
    if device.is_mesh_gateway:
        device_info["is_mesh_gateway"] = True

    # Add extra_data (redact device identifiers, keep power info)
    if device.extra_data:
        safe_extra: dict[str, Any] = {}
        if "power_info" in device.extra_data:
            safe_extra["power_info"] = device.extra_data["power_info"]
        if "gateway_device_id" in device.extra_data:
            safe_extra["gateway_device_id"] = "**REDACTED**"
        if safe_extra:
            device_info["extra_data"] = safe_extra

    return device_info


def _extract_device_serial(device: DeviceEntry) -> str | None:
    """Extract Lipro serial from device identifiers."""
    for domain, identifier in device.identifiers:
        if domain == DOMAIN:
            return identifier
    return None


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    # Collect device information (redacted)
    devices_info = [
        _build_device_diagnostics(device) for device in coordinator.devices.values()
    ]

    # Get anonymous share status
    share_manager = get_anonymous_share_manager(hass)
    device_count, error_count = share_manager.pending_count
    anonymous_share_info = {
        "enabled": share_manager.is_enabled,
        "pending_devices": device_count,
        "pending_errors": error_count,
    }

    return {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": entry.options,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "device_count": len(coordinator.devices),
            "mqtt_connected": coordinator.mqtt_connected,
        },
        "anonymous_share": anonymous_share_info,
        "devices": devices_info,
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a single device entry."""
    coordinator = entry.runtime_data
    serial = _extract_device_serial(device)
    if serial is None:
        return {"error": "device_not_in_lipro_domain"}

    lipro_device = coordinator.get_device(serial)
    if lipro_device is None:
        return {"error": "device_not_found"}

    return {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": entry.options,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "device_count": len(coordinator.devices),
            "mqtt_connected": coordinator.mqtt_connected,
        },
        "device": _build_device_diagnostics(lipro_device),
    }
