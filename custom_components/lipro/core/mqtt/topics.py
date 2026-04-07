"""MQTT topic helpers for Lipro integration."""

from __future__ import annotations

from ...const.api import MQTT_TOPIC_PREFIX
from ..protocol.boundary.mqtt_decoder import (
    decode_mqtt_topic_payload,
    normalize_mqtt_biz_id,
)


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
    """Extract device ID from MQTT topic through the formal boundary authority."""
    canonical = decode_mqtt_topic_payload(
        topic,
        expected_biz_id=expected_biz_id,
    ).canonical
    device_id = canonical.get("deviceId")
    return device_id if isinstance(device_id, str) and device_id else None


__all__ = ["build_topic", "normalize_mqtt_biz_id", "parse_topic"]
