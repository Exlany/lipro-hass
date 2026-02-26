"""MQTT setup preparation helpers for coordinator orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..const import CONF_BIZ_ID, CONF_USER_ID
from .device import LiproDevice


def extract_mqtt_encrypted_credentials(
    mqtt_config: Mapping[str, Any],
) -> tuple[Any, Any] | None:
    """Extract encrypted MQTT credentials from API payload."""
    encrypted_access_key = mqtt_config.get("accessKey")
    encrypted_secret_key = mqtt_config.get("secretKey")
    if not encrypted_access_key or not encrypted_secret_key:
        return None
    return encrypted_access_key, encrypted_secret_key


def resolve_mqtt_biz_id(config_entry_data: Mapping[str, Any]) -> str | None:
    """Resolve MQTT biz ID from config entry data with user_id fallback."""
    biz_id = config_entry_data.get(CONF_BIZ_ID)
    if not biz_id:
        user_id = config_entry_data.get(CONF_USER_ID)
        if user_id is None:
            return None
        biz_id = str(user_id)
    return biz_id.removeprefix("lip_")


def build_mqtt_subscription_device_ids(
    devices: Mapping[str, LiproDevice],
) -> list[str]:
    """Build MQTT subscription targets (device serial list)."""
    return list(devices.keys())


def iter_mesh_group_serials(devices: Mapping[str, LiproDevice]) -> list[str]:
    """Return mesh-group serials for setup-time diagnostics."""
    return [dev.serial for dev in devices.values() if dev.is_group]
