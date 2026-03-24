"""MQTT topic helpers for Lipro integration."""

from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from typing import TYPE_CHECKING, Protocol, cast

from ...const.api import MQTT_TOPIC_PREFIX

if TYPE_CHECKING:
    from custom_components.lipro.core.protocol.boundary import BoundaryDecodeResult


class _BoundaryDecoderModule(Protocol):
    """Typed view of the lazily imported boundary module."""

    def decode_mqtt_topic_payload(
        self,
        payload: object,
        *,
        expected_biz_id: str | None = None,
    ) -> BoundaryDecodeResult[dict[str, str]]: ...


@lru_cache(maxsize=1)
def _boundary_decoder_module() -> _BoundaryDecoderModule:
    """Resolve the protocol-boundary module lazily to avoid import cycles."""
    return cast(
        _BoundaryDecoderModule,
        import_module("custom_components.lipro.core.protocol.boundary"),
    )


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
    """Extract device ID from MQTT topic through the formal boundary authority."""
    canonical = _boundary_decoder_module().decode_mqtt_topic_payload(
        topic,
        expected_biz_id=expected_biz_id,
    ).canonical
    device_id = canonical.get("deviceId")
    return device_id if isinstance(device_id, str) and device_id else None


__all__ = ["build_topic", "normalize_mqtt_biz_id", "parse_topic"]
