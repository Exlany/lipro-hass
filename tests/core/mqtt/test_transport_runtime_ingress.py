"""Tests for Lipro MQTT transport."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from custom_components.lipro.core.mqtt.payload import _MAX_MQTT_PAYLOAD_BYTES
from custom_components.lipro.core.mqtt.transport import MqttTransport


class TestMqttTransportIngress:
    """Tests for MqttTransport class."""

    def test_process_message(self):
        """Test message processing."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        # Create mock message
        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b'{"light": {"powerState": "1"}}'

        client._process_message(message)

        on_message.assert_called_once()
        call_args = on_message.call_args
        assert call_args[0][0] == "03ab5ccd7cxxxxxx"
        assert call_args[0][1]["powerState"] == "1"

    def test_process_message_memoryview_payload(self):
        """Test message processing with memoryview payload."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = memoryview(b'{"light": {"powerState": "1"}}')

        client._process_message(message)

        on_message.assert_called_once()
        call_args = on_message.call_args
        assert call_args[0][0] == "03ab5ccd7cxxxxxx"
        assert call_args[0][1]["powerState"] == "1"

    def test_process_message_ignores_mismatched_biz_id(self):
        """Messages for a different biz ID should be ignored."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz123/03ab5ccd7cxxxxxx"
        message.payload = b'{"light": {"powerState": "1"}}'

        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_invalid_json(self):
        """Test message processing with invalid JSON."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b"not valid json"

        # Should not raise, just log error
        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_invalid_topic(self, caplog):
        """Test message processing with invalid topic."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "invalid"
        message.payload = b'{"light": {"powerState": "1"}}'

        with caplog.at_level(logging.DEBUG):
            client._process_message(message)

        on_message.assert_not_called()
        assert "Invalid topic format (count=1, len=7), skipping message" in caplog.text
        assert "topic=invalid" not in caplog.text

    def test_process_message_invalid_topic_warns_when_debug_disabled(self, caplog):
        """Non-debug invalid topic path should emit warning without topic content."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "invalid"
        message.payload = b'{"light": {"powerState": "1"}}'

        with caplog.at_level(logging.WARNING):
            client._process_message(message)

        on_message.assert_not_called()
        assert "Invalid topic format, skipping message (count=1)" in caplog.text
        assert "topic=invalid" not in caplog.text

    def test_process_message_empty_properties(self):
        """Test message processing with empty properties."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b"{}"

        client._process_message(message)

        # Should not call callback for empty properties
        on_message.assert_not_called()

    def test_process_message_payload_not_object(self):
        """Test message processing ignores JSON payloads that are not objects."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b'["not", "an", "object"]'

        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_redacts_sensitive_debug_payload(self, caplog):
        """Debug payload log should redact sensitive fields and identifiers."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = (
            b'{"common":{"wifi_ssid":"MyHome","ip":"192.168.1.8","mac":"AA:BB:CC:DD:EE:FF"},'
            b'"light":{"accessToken":"very-secret-token-value-123456","powerState":"1"}}'
        )

        with caplog.at_level(logging.DEBUG):
            client._process_message(message)

        payload_logs = [
            rec.message
            for rec in caplog.records
            if rec.name == "custom_components.lipro.core.mqtt"
            and "MQTT [" in rec.message
        ]
        assert payload_logs
        combined = "\n".join(payload_logs)
        assert "MyHome" not in combined
        assert "192.168.1.8" not in combined
        assert "AA:BB:CC:DD:EE:FF" not in combined
        assert "very-secret-token-value-123456" not in combined

    def test_process_message_skips_oversized_payload(self):
        """Oversized MQTT payloads should be dropped defensively."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        oversize_blob = "x" * (_MAX_MQTT_PAYLOAD_BYTES + 1024)
        message.payload = (
            f'{{"light":{{"powerState":"1","blob":"{oversize_blob}"}}}}'
        ).encode()

        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_skips_oversized_unicode_string_payload(self):
        """Oversized unicode string payloads should be checked by UTF-8 byte size."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        oversize_blob = "中" * ((_MAX_MQTT_PAYLOAD_BYTES // 3) + 1024)
        message.payload = f'{{"light":{{"powerState":"1","blob":"{oversize_blob}"}}}}'

        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_empty_payload(self):
        """Empty payload should be skipped early."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b""

        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_unexpected_exception(self, caplog):
        """Unexpected errors should be swallowed and logged."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b'{"light":{"powerState":"1"}}'

        with (
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.parse_mqtt_payload",
                side_effect=RuntimeError("boom"),
            ),
            caplog.at_level(logging.ERROR),
        ):
            client._process_message(message)

        on_message.assert_not_called()
        assert "Topic_Device_State/biz001/03ab5ccd7cxxxxxx" not in caplog.text
        assert "device=03ab***xxxx" in caplog.text

    def test_process_message_callback_error_sets_last_error_and_calls_error_hook(self):
        """Callback exceptions should be observable via last_error and on_error."""
        on_message = MagicMock(side_effect=RuntimeError("message boom"))
        on_error = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
            on_error=on_error,
        )
        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b'{"light":{"powerState":"1"}}'

        client._process_message(message)

        assert isinstance(client.last_error, RuntimeError)
        on_error.assert_called_once()

    def test_process_message_error_hook_failure_is_swallowed(self):
        """Error hook failures should not replace original callback exception."""
        on_message = MagicMock(side_effect=ValueError("message failed"))
        on_error = MagicMock(side_effect=RuntimeError("hook failed"))
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
            on_error=on_error,
        )
        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b'{"light":{"powerState":"1"}}'

        client._process_message(message)

        assert isinstance(client.last_error, ValueError)
        on_error.assert_called_once()

    def test_process_message_success_clears_last_error(self):
        """Successful message processing should clear stale error state."""
        on_message = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )
        client._last_error = RuntimeError("stale")
        message = MagicMock()
        message.topic = "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"
        message.payload = b'{"light":{"powerState":"1"}}'

        client._process_message(message)

        assert client.last_error is None


class TestDecodePayload:
    """Tests for connect/listen and payload decoding paths."""

    def test_decode_payload_text_string(self):
        """String payload should pass through unchanged when size is valid."""
        decoded = MqttTransport._decode_payload_text("{}", "dev1")
        assert decoded == "{}"

    def test_decode_payload_text_unexpected_type(self):
        """Unexpected payload types should be ignored."""
        decoded = MqttTransport._decode_payload_text(123, "dev1")
        assert decoded is None
