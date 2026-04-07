"""MQTT setup preparation helpers for coordinator orchestration."""

from __future__ import annotations

from collections.abc import Mapping

from ....const.config import CONF_BIZ_ID, CONF_USER_ID
from ...device.device import LiproDevice
from ...mqtt.topics import normalize_mqtt_biz_id
from ..types import PropertyValue


def extract_mqtt_encrypted_credentials(
    mqtt_config: Mapping[str, PropertyValue],
) -> tuple[str, str] | None:
    """Extract encrypted MQTT credentials from API payload."""
    encrypted_access_key = mqtt_config.get("accessKey")
    encrypted_secret_key = mqtt_config.get("secretKey")
    if not encrypted_access_key or not encrypted_secret_key:
        return None
    if not isinstance(encrypted_access_key, str) or not isinstance(
        encrypted_secret_key, str
    ):
        return None
    return encrypted_access_key, encrypted_secret_key


def resolve_mqtt_biz_id(config_entry_data: Mapping[str, PropertyValue]) -> str | None:
    """Resolve MQTT biz ID from config entry data with user_id fallback."""
    biz_id = config_entry_data.get(CONF_BIZ_ID)
    if biz_id is None or str(biz_id).strip() == "":
        user_id = config_entry_data.get(CONF_USER_ID)
        if user_id is None:
            return None
        biz_id = user_id
    return normalize_mqtt_biz_id(biz_id)


def _dedupe_serials(serials: list[str]) -> list[str]:
    """Return serials in stable order without duplicates."""
    deduped: list[str] = []
    seen: set[str] = set()
    for serial in serials:
        if not serial or serial in seen:
            continue
        seen.add(serial)
        deduped.append(serial)
    return deduped


def build_mqtt_subscription_device_ids(
    devices: Mapping[str, LiproDevice],
) -> list[str]:
    """Build MQTT subscription targets, preferring mesh-group topics."""
    mesh_group_serials = _dedupe_serials(
        [dev.serial for dev in devices.values() if dev.is_group]
    )
    if mesh_group_serials:
        return mesh_group_serials
    return _dedupe_serials([dev.serial for dev in devices.values()])


def iter_mesh_group_serials(devices: Mapping[str, LiproDevice]) -> list[str]:
    """Return mesh-group serials for setup-time diagnostics."""
    return [dev.serial for dev in devices.values() if dev.is_group]
