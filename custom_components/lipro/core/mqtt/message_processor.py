"""MQTT message parsing helpers extracted from the client."""

from __future__ import annotations

from collections.abc import Callable
import json
import logging
from typing import TYPE_CHECKING, Any

from ..utils.redaction import redact_identifier as _redact_identifier
from .payload import (
    _MAX_MQTT_LOG_CHARS,
    _MAX_MQTT_PAYLOAD_BYTES,
    _format_mqtt_payload_for_log,
)
from .topics import parse_topic

if TYPE_CHECKING:
    import aiomqtt

_LOGGER = logging.getLogger(__package__ or __name__)


def decode_payload_text(raw_payload: object, device_id: str) -> str | None:
    """Decode MQTT payload to UTF-8 text with size/type checks."""
    if isinstance(raw_payload, memoryview):
        raw_payload = raw_payload.tobytes()

    if isinstance(raw_payload, (bytes, bytearray)):
        raw_bytes = bytes(raw_payload)
        payload_size = len(raw_bytes)
        if payload_size > _MAX_MQTT_PAYLOAD_BYTES:
            _LOGGER.warning(
                "MQTT [%s]: payload too large (%d bytes), skipping",
                _redact_identifier(device_id) or "***",
                payload_size,
            )
            return None
        return raw_bytes.decode("utf-8")

    if isinstance(raw_payload, str):
        payload_size = len(raw_payload.encode("utf-8"))
        if payload_size > _MAX_MQTT_PAYLOAD_BYTES:
            _LOGGER.warning(
                "MQTT [%s]: payload too large (%d bytes), skipping",
                _redact_identifier(device_id) or "***",
                payload_size,
            )
            return None
        return raw_payload

    _LOGGER.debug(
        "MQTT [%s]: unexpected payload type %s, skipping",
        _redact_identifier(device_id) or "***",
        type(raw_payload).__name__,
    )
    return None


class MqttMessageProcessor:
    """Process MQTT messages without coupling to connection lifecycle."""

    def __init__(self, biz_id: str) -> None:
        """Store the business identifier used for topic validation."""
        self._biz_id = biz_id
        self._invalid_topic_count = 0

    def log_invalid_topic(self, topic: str) -> None:
        """Record and log invalid topic metadata without exposing topic content."""
        self._invalid_topic_count += 1
        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug(
                "Invalid topic format (count=%d, len=%d), skipping message",
                self._invalid_topic_count,
                len(topic),
            )
            return
        _LOGGER.warning(
            "Invalid topic format, skipping message (count=%d)",
            self._invalid_topic_count,
        )

    def process_message(
        self,
        message: aiomqtt.Message,
        *,
        parse_payload: Callable[[Any], dict[str, Any]],
        on_message: Callable[[str, dict[str, Any]], None] | None,
        invoke_callback: Callable[..., bool],
        set_last_error: Callable[[Exception], None],
        clear_last_error: Callable[[], None],
    ) -> None:
        """Parse one MQTT message and forward flattened properties."""
        try:
            topic = str(message.topic)
            device_id = parse_topic(topic, expected_biz_id=self._biz_id)

            if not device_id:
                self.log_invalid_topic(topic)
                return

            device_id_log = _redact_identifier(device_id) or "***"
            if not message.payload:
                _LOGGER.debug("MQTT [%s]: empty payload, skipping", device_id_log)
                return

            payload_text = decode_payload_text(message.payload, device_id)
            if payload_text is None:
                return

            payload = json.loads(payload_text)
            if not isinstance(payload, dict):
                _LOGGER.debug(
                    "MQTT [%s]: unexpected payload type %s, skipping",
                    device_id_log,
                    type(payload).__name__,
                )
                return

            if _LOGGER.isEnabledFor(logging.DEBUG):
                _LOGGER.debug(
                    "MQTT [%s]: %s",
                    device_id_log,
                    _format_mqtt_payload_for_log(payload)[:_MAX_MQTT_LOG_CHARS],
                )

            properties = parse_payload(payload)
            if properties and not invoke_callback(
                on_message,
                "on_message",
                device_id,
                properties,
            ):
                return

            clear_last_error()
        except (json.JSONDecodeError, UnicodeError) as err:
            set_last_error(err)
            _LOGGER.exception("Failed to decode MQTT payload")
        except Exception as err:
            set_last_error(err)
            topic = str(getattr(message, "topic", "unknown"))
            device_id = parse_topic(topic, expected_biz_id=self._biz_id)
            topic_context = (
                f"device={_redact_identifier(device_id) or '***'}"
                if device_id
                else f"invalid_topic_len={len(topic)}"
            )
            _LOGGER.exception(
                "Error processing MQTT message (%s, error=%s)",
                topic_context,
                type(err).__name__,
            )


__all__ = ["MqttMessageProcessor", "decode_payload_text"]
