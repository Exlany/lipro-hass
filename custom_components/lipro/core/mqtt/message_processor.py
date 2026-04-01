"""MQTT message parsing helpers extracted from the client."""

from __future__ import annotations

from collections.abc import Callable
import json
import logging
from typing import TYPE_CHECKING, Any

from ..protocol.boundary.mqtt_decoder import decode_mqtt_topic_payload
from ..telemetry.models import (
    OperationOutcome,
    build_operation_outcome,
    build_operation_outcome_from_exception,
)
from ..utils.redaction import redact_identifier as _redact_identifier
from .payload import (
    _MAX_MQTT_LOG_CHARS,
    _MAX_MQTT_PAYLOAD_BYTES,
    _format_mqtt_payload_for_log,
)

if TYPE_CHECKING:
    import aiomqtt

_LOGGER = logging.getLogger(__package__ or __name__)
_MQTT_PROCESSOR_ORIGIN = "mqtt.message_processor"

type MqttPayload = dict[str, Any]
type ParsePayloadCallback = Callable[[object], MqttPayload]
type MessageCallback = Callable[[str, MqttPayload], None]


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

    def _resolve_device_id(self, topic: str) -> str | None:
        result = decode_mqtt_topic_payload(
            topic,
            expected_biz_id=self._biz_id,
        )
        device_id = result.canonical.get("deviceId")
        return device_id if isinstance(device_id, str) and device_id else None

    def _topic_context(self, topic: str) -> tuple[str | None, str]:
        device_id = self._resolve_device_id(topic)
        topic_context = (
            f"device={_redact_identifier(device_id) or '***'}"
            if device_id
            else f"invalid_topic_len={len(topic)}"
        )
        return device_id, topic_context

    def _invalid_topic_outcome(self, topic: str) -> OperationOutcome:
        self.log_invalid_topic(topic)
        return build_operation_outcome(
            kind="skipped",
            reason_code="invalid_topic",
        )

    def _load_payload_mapping(
        self,
        raw_payload: object,
        *,
        device_id: str,
    ) -> MqttPayload | OperationOutcome:
        device_id_log = _redact_identifier(device_id) or "***"
        if not raw_payload:
            _LOGGER.debug("MQTT [%s]: empty payload, skipping", device_id_log)
            return build_operation_outcome(
                kind="skipped",
                reason_code="empty_payload",
            )

        payload_text = decode_payload_text(raw_payload, device_id)
        if payload_text is None:
            return build_operation_outcome(
                kind="skipped",
                reason_code="payload_unavailable",
            )

        payload = json.loads(payload_text)
        if not isinstance(payload, dict):
            _LOGGER.debug(
                "MQTT [%s]: unexpected payload type %s, skipping",
                device_id_log,
                type(payload).__name__,
            )
            return build_operation_outcome(
                kind="skipped",
                reason_code="unexpected_payload_type",
            )

        if _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug(
                "MQTT [%s]: %s",
                device_id_log,
                _format_mqtt_payload_for_log(payload)[:_MAX_MQTT_LOG_CHARS],
            )
        return payload

    def _parse_properties(
        self,
        payload: MqttPayload,
        *,
        parse_payload: Callable[[Any], dict[str, Any]],
        clear_last_error: Callable[[], None],
    ) -> dict[str, Any] | OperationOutcome:
        properties = parse_payload(payload)
        if properties:
            return properties
        clear_last_error()
        return build_operation_outcome(
            kind="skipped",
            reason_code="empty_properties",
        )

    def _dispatch_message(
        self,
        *,
        device_id: str,
        properties: dict[str, Any],
        on_message: Callable[[str, dict[str, Any]], None] | None,
        invoke_callback: Callable[..., bool],
        clear_last_error: Callable[[], None],
    ) -> OperationOutcome:
        if not invoke_callback(
            on_message,
            "on_message",
            device_id,
            properties,
        ):
            return build_operation_outcome(
                kind="failed",
                reason_code="callback_failed",
            )

        clear_last_error()
        return build_operation_outcome(
            kind="success",
            reason_code="processed",
        )

    def _process_message_core(
        self,
        message: aiomqtt.Message,
        *,
        parse_payload: ParsePayloadCallback,
        on_message: MessageCallback | None,
        invoke_callback: Callable[..., bool],
        clear_last_error: Callable[[], None],
    ) -> OperationOutcome:
        topic = str(message.topic)
        device_id = self._resolve_device_id(topic)
        if device_id is None:
            return self._invalid_topic_outcome(topic)

        payload_or_outcome = self._load_payload_mapping(
            message.payload,
            device_id=device_id,
        )
        if isinstance(payload_or_outcome, OperationOutcome):
            return payload_or_outcome

        properties_or_outcome = self._parse_properties(
            payload_or_outcome,
            parse_payload=parse_payload,
            clear_last_error=clear_last_error,
        )
        if isinstance(properties_or_outcome, OperationOutcome):
            return properties_or_outcome

        return self._dispatch_message(
            device_id=device_id,
            properties=properties_or_outcome,
            on_message=on_message,
            invoke_callback=invoke_callback,
            clear_last_error=clear_last_error,
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
    ) -> OperationOutcome:
        """Parse one MQTT message and forward flattened properties."""
        try:
            return self._process_message_core(
                message,
                parse_payload=parse_payload,
                on_message=on_message,
                invoke_callback=invoke_callback,
                clear_last_error=clear_last_error,
            )
        except (json.JSONDecodeError, UnicodeError) as err:
            set_last_error(err)
            _LOGGER.exception("Failed to decode MQTT payload")
            return build_operation_outcome_from_exception(
                err,
                kind="failed",
                reason_code="payload_decode_error",
                failure_origin=_MQTT_PROCESSOR_ORIGIN,
                failure_category="protocol",
                handling_policy="inspect",
            )
        except (
            AttributeError,
            LookupError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as err:
            set_last_error(err)
            topic = str(getattr(message, "topic", "unknown"))
            _device_id, topic_context = self._topic_context(topic)
            _LOGGER.exception(
                "Error processing MQTT message (%s, error=%s)",
                topic_context,
                type(err).__name__,
            )
            return build_operation_outcome_from_exception(
                err,
                kind="failed",
                reason_code="message_processing_error",
                failure_origin=_MQTT_PROCESSOR_ORIGIN,
                handling_policy="inspect",
            )


__all__ = ["MqttMessageProcessor", "decode_payload_text"]
