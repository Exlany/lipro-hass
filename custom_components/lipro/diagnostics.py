"""Diagnostics support for Lipro integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.diagnostics import async_redact_data

from .const import (
    CONF_PHONE,
    CONF_PHONE_ID,
    PROP_BLE_MAC,
    PROP_IP,
    PROP_MAC,
    PROP_WIFI_SSID,
)
from .core.anonymous_share import get_anonymous_share_manager

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import LiproConfigEntry

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
    "macAddress",
    "ipAddress",
}

# Pre-computed lowercase set for efficient lookup
_PROPERTY_KEYS_LOWER: Final = frozenset(key.lower() for key in PROPERTY_KEYS_TO_REDACT)


def _redact_device_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from device properties."""
    return {
        k: "**REDACTED**" if k.lower() in _PROPERTY_KEYS_LOWER else v
        for k, v in properties.items()
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: LiproConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    # Collect device information (redacted)
    devices_info = []
    for device in coordinator.devices.values():
        device_info = {
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

        devices_info.append(device_info)

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
