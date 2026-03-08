"""MQTT topic helpers for Lipro integration."""

from __future__ import annotations

from ...const.api import MQTT_TOPIC_PREFIX


def normalize_mqtt_biz_id(value: object) -> str | None:
    """Normalize MQTT biz ID, tolerating whitespace and `lip_` prefix."""
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None
    if normalized[:4].casefold() == "lip_":
        normalized = normalized[4:]
    if not normalized or not all(c.isalnum() or c in "-_" for c in normalized):
        return None
    return normalized


def build_topic(biz_id: str, device_id: str) -> str:
    """Build MQTT topic for device status subscription.

    Format: Topic_Device_State/{bizId}/{deviceId}
    """
    normalized_biz_id = normalize_mqtt_biz_id(biz_id)
    if normalized_biz_id is None:
        msg = f"Invalid biz_id format: {biz_id}"
        raise ValueError(msg)
    if not device_id or not all(c.isalnum() or c in "-_" for c in device_id):
        msg = f"Invalid device_id format: {device_id}"
        raise ValueError(msg)

    return f"{MQTT_TOPIC_PREFIX}/{normalized_biz_id}/{device_id}"


def parse_topic(topic: str, *, expected_biz_id: str | None = None) -> str | None:
    """Extract device ID from MQTT topic, optionally validating biz ID."""
    parts = topic.split("/")
    if len(parts) != 3:
        return None
    if parts[0] != MQTT_TOPIC_PREFIX:
        return None

    normalized_biz_id = normalize_mqtt_biz_id(parts[1])
    device_id = parts[2]
    if normalized_biz_id is None:
        return None
    if not device_id or not all(c.isalnum() or c in "-_" for c in device_id):
        return None
    if expected_biz_id is not None:
        normalized_expected = normalize_mqtt_biz_id(expected_biz_id)
        if normalized_expected is None or normalized_biz_id != normalized_expected:
            return None
    return device_id


__all__ = ["build_topic", "normalize_mqtt_biz_id", "parse_topic"]
