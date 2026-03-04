"""MQTT topic helpers for Lipro integration."""

from __future__ import annotations

from ...const.api import MQTT_TOPIC_PREFIX


def build_topic(biz_id: str, device_id: str) -> str:
    """Build MQTT topic for device status subscription.

    Format: Topic_Device_State/{bizId}/{deviceId}
    """
    if not biz_id or not all(c.isalnum() or c in "-_" for c in biz_id):
        msg = f"Invalid biz_id format: {biz_id}"
        raise ValueError(msg)
    if not device_id or not all(c.isalnum() or c in "-_" for c in device_id):
        msg = f"Invalid device_id format: {device_id}"
        raise ValueError(msg)

    return f"{MQTT_TOPIC_PREFIX}/{biz_id}/{device_id}"


def parse_topic(topic: str) -> str | None:
    """Extract device ID from MQTT topic."""
    parts = topic.split("/")
    if len(parts) != 3:
        return None
    if parts[0] != MQTT_TOPIC_PREFIX:
        return None
    biz_id = parts[1]
    device_id = parts[2]
    if not biz_id or not all(c.isalnum() or c in "-_" for c in biz_id):
        return None
    if not device_id or not all(c.isalnum() or c in "-_" for c in device_id):
        return None
    return device_id


__all__ = ["build_topic", "parse_topic"]
