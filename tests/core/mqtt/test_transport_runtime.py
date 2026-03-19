"""Tests for Lipro MQTT transport."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock, patch

import aiomqtt
import pytest

from custom_components.lipro.core.mqtt.payload import _MAX_MQTT_PAYLOAD_BYTES
from custom_components.lipro.core.mqtt.transport import MqttTransport


class TestMqttTransport:
    """Tests for MqttTransport class."""

    def test_init(self):
        """Test client initialization."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert client.is_connected is False
        assert client.subscribed_count == 0

    def test_init_with_callbacks(self):
        """Test client initialization with callbacks."""
        on_message = MagicMock()
        on_connect = MagicMock()
        on_disconnect = MagicMock()

        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
            on_connect=on_connect,
            on_disconnect=on_disconnect,
        )

        assert client._on_message is on_message
        assert client._on_connect is on_connect
        assert client._on_disconnect is on_disconnect

    @pytest.mark.asyncio
    async def test_start(self):
        """Test starting MQTT transport."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        device_ids = ["03ab5ccd7cxxxxxx", "03ab5ccd7cyyyyyy"]

        with patch.object(client, "_connection_loop", new_callable=AsyncMock):
            await client.start(device_ids)

            assert client._running is True
            assert client._subscribed_devices == set(device_ids)
            assert client.subscribed_count == 2

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test starting already running client."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        with patch.object(
            client, "_connection_loop", new_callable=AsyncMock
        ) as mock_loop:
            await client.start(["device1"])

            # Should not start again
            mock_loop.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping MQTT transport."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True
        client._connected = True

        # Create a proper async task mock
        async def dummy_task():
            pass

        import asyncio

        client._task = asyncio.create_task(dummy_task())
        # Wait for dummy task to complete
        await asyncio.sleep(0)

        await client.stop()

        assert client._running is False
        assert client._connected is False
        assert client._task is None

    def test_handle_disconnect(self):
        """Test disconnect handling."""
        on_disconnect = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._broker_client = cast(aiomqtt.Client | None, MagicMock())

        client._handle_disconnect("Test reason")

        assert client._connected is False
        assert client._broker_client is None
        on_disconnect.assert_called_once()

    def test_handle_disconnect_callback_failure_sets_last_error(self, caplog):
        """Disconnect callback exceptions should be captured as last_error."""
        on_disconnect = MagicMock(side_effect=RuntimeError("boom"))
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._broker_client = MagicMock()

        with caplog.at_level(logging.ERROR):
            client._handle_disconnect("Test reason")

        assert isinstance(client.last_error, RuntimeError)
        assert str(client.last_error) == "boom"

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

    @pytest.mark.asyncio
    async def test_consume_task_exception_cancelled_returns_none(self):
        """Cancelled background tasks should not be treated as errors."""

        async def _long_task() -> None:
            await asyncio.sleep(10)

        task = asyncio.create_task(_long_task())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert MqttTransport._consume_task_exception(task) is None

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

class TestMqttTransportProperties:
    """Tests for MQTT transport properties."""

    def test_is_connected(self):
        """Test is_connected property."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert client.is_connected is False

        client._connected = True
        assert client.is_connected is True

    def test_subscribed_count(self):
        """Test subscribed_count property."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert client.subscribed_count == 0

        client._subscribed_devices = {"device1", "device2", "device3"}
        assert client.subscribed_count == 3

    def test_subscribed_devices_returns_copy(self):
        """Test subscribed_devices returns a copy, not the internal set."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._subscribed_devices = {"device1", "device2"}

        snapshot = client.subscribed_devices
        snapshot.add("injected")

        # Internal set must not be affected
        assert "injected" not in client._subscribed_devices
        assert len(client._subscribed_devices) == 2

class TestSyncSubscriptions:
    """Tests for sync_subscriptions method."""

    @pytest.mark.asyncio
    async def test_sync_add_devices(self):
        """Test adding new device subscriptions."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        # Not connected — devices should be recorded for later subscription
        await client.sync_subscriptions({"dev_a", "dev_b"})

        assert client._subscribed_devices == {"dev_a", "dev_b"}

    @pytest.mark.asyncio
    async def test_sync_remove_devices(self):
        """Test removing device subscriptions."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._subscribed_devices = {"dev_a", "dev_b", "dev_c"}

        await client.sync_subscriptions({"dev_a"})

        assert client._subscribed_devices == {"dev_a"}

    @pytest.mark.asyncio
    async def test_sync_no_change(self):
        """Test sync with no changes is a no-op."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._subscribed_devices = {"dev_a", "dev_b"}

        await client.sync_subscriptions({"dev_a", "dev_b"})

        assert client._subscribed_devices == {"dev_a", "dev_b"}

    @pytest.mark.asyncio
    async def test_sync_add_and_remove(self):
        """Test simultaneous add and remove."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._subscribed_devices = {"dev_a", "dev_b"}

        await client.sync_subscriptions({"dev_b", "dev_c"})

        assert client._subscribed_devices == {"dev_b", "dev_c"}

    @pytest.mark.asyncio
    async def test_sync_connected_subscribes_to_broker(self):
        """Test sync actually subscribes/unsubscribes when connected."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        client._broker_client = mock_mqtt
        client._connected = True
        client._subscribed_devices = {"dev_old"}

        await client.sync_subscriptions({"dev_new"})

        # Should subscribe to new and unsubscribe from old
        mock_mqtt.subscribe.assert_called_once()
        mock_mqtt.unsubscribe.assert_called_once()
        assert client._subscribed_devices == {"dev_new"}

    @pytest.mark.asyncio
    async def test_sync_connected_batches_broker_updates(self):
        """Large syncs should batch subscribe/unsubscribe requests."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        client._broker_client = mock_mqtt
        client._connected = True
        client._subscribed_devices = {f"old_{idx}" for idx in range(55)}

        await client.sync_subscriptions({f"new_{idx}" for idx in range(55)})

        assert mock_mqtt.subscribe.await_count == 2
        assert mock_mqtt.unsubscribe.await_count == 2
        assert client._subscribed_devices == {f"new_{idx}" for idx in range(55)}

    @pytest.mark.asyncio
    async def test_sync_connected_skips_invalid_device_id(self, caplog):
        """Test sync skips invalid topic IDs without breaking valid subscriptions."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        client._broker_client = mock_mqtt
        client._connected = True

        with caplog.at_level(logging.WARNING):
            await client.sync_subscriptions({"valid_dev", "bad/dev"})

        mock_mqtt.subscribe.assert_called_once()
        assert client._subscribed_devices == {"valid_dev"}
        assert "bad/dev" not in caplog.text
        assert "invalid characters" in caplog.text

    @pytest.mark.asyncio
    async def test_sync_connected_subscribe_mqtt_error_keeps_running(self):
        """Subscribe errors should be logged without breaking sync flow."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        mock_mqtt.subscribe.side_effect = aiomqtt.MqttError("subscribe failed")
        client._broker_client = mock_mqtt
        client._connected = True

        await client.sync_subscriptions({"dev_new"})

        mock_mqtt.subscribe.assert_called_once()
        assert client._subscribed_devices == set()

    @pytest.mark.asyncio
    async def test_sync_connected_unsubscribe_invalid_id_skips(self):
        """Invalid unsubscribe device IDs should be skipped safely."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._broker_client = AsyncMock()
        client._connected = True
        client._subscribed_devices = {"bad/dev"}

        await client.sync_subscriptions(set())

        assert client._subscribed_devices == set()

    @pytest.mark.asyncio
    async def test_sync_connected_unsubscribe_mqtt_error_keeps_running(self):
        """Unsubscribe errors should not break synchronization."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        mock_mqtt.unsubscribe.side_effect = aiomqtt.MqttError("unsubscribe failed")
        client._broker_client = mock_mqtt
        client._connected = True
        client._subscribed_devices = {"dev_old"}

        await client.sync_subscriptions(set())

        mock_mqtt.unsubscribe.assert_called_once()
        assert client._subscribed_devices == {"dev_old"}
        assert client._pending_unsubscribe == {"dev_old"}

    @pytest.mark.asyncio
    async def test_sync_connected_retries_pending_unsubscribe_until_success(self):
        """Failed live unsubscribes should retry on later sync calls in the same session."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        mock_mqtt.unsubscribe.side_effect = [
            aiomqtt.MqttError("unsubscribe failed"),
            None,
        ]
        client._broker_client = mock_mqtt
        client._connected = True
        client._subscribed_devices = {"dev_old"}

        await client.sync_subscriptions(set())
        await client.sync_subscriptions(set())

        assert mock_mqtt.unsubscribe.await_count == 2
        assert client._subscribed_devices == set()
        assert client._pending_unsubscribe == set()

class TestConnectAndDecode:
    """Tests for connect/listen and payload decoding paths."""

    @pytest.mark.asyncio
    async def test_connect_and_listen_subscribes_and_processes_messages(self, caplog):
        """Connect/listen should subscribe valid IDs, skip invalid ones, and process stream.

        Also verifies TLS context is cached across reconnects to avoid rebuilding it.
        """
        on_connect = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_connect=on_connect,
        )
        client._subscribed_devices = {"valid_dev", "bad/dev"}

        async def _messages():
            yield MagicMock(topic="Topic_Device_State/biz001/valid_dev")

        mqtt_client_1 = AsyncMock()
        mqtt_client_1.messages = _messages()
        mqtt_client_2 = AsyncMock()
        mqtt_client_2.messages = _messages()

        with (
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.ssl.create_default_context"
            ) as mock_tls,
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.aiomqtt.Client"
            ) as mock_client_cls,
            patch.object(client, "_process_message") as mock_process,
        ):
            context_manager_1 = AsyncMock()
            context_manager_1.__aenter__.return_value = mqtt_client_1
            context_manager_1.__aexit__.return_value = False
            context_manager_2 = AsyncMock()
            context_manager_2.__aenter__.return_value = mqtt_client_2
            context_manager_2.__aexit__.return_value = False
            mock_client_cls.side_effect = [context_manager_1, context_manager_2]

            # Connect twice to simulate reconnects: TLS context should be reused.
            with caplog.at_level(logging.WARNING):
                await client._connect_and_listen()
                await client._connect_and_listen()

        mock_tls.assert_called_once()
        assert mock_client_cls.call_count == 2
        assert (
            mock_client_cls.call_args_list[0].kwargs["tls_context"]
            is mock_client_cls.call_args_list[1].kwargs["tls_context"]
        )
        assert (
            mock_tls.return_value
            is mock_client_cls.call_args_list[0].kwargs["tls_context"]
        )
        assert on_connect.call_count == 2
        mqtt_client_1.subscribe.assert_called_once()
        mqtt_client_2.subscribe.assert_called_once()
        assert mock_process.call_count == 2
        assert "bad/dev" not in client._subscribed_devices
        # Message stream ends after one yielded message; client should no longer
        # report itself connected once _connect_and_listen returns.
        assert client.is_connected is False
        assert "bad/dev" not in caplog.text
        assert "invalid characters" in caplog.text

    @pytest.mark.asyncio
    async def test_connect_and_listen_batches_pending_and_current_topics(self):
        """Connect/listen should batch queued unsubscribes and subscriptions."""
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._pending_unsubscribe = {f"old_{idx}" for idx in range(55)}
        client._subscribed_devices = {f"new_{idx}" for idx in range(55)}

        async def _messages():
            if TYPE_CHECKING:
                yield None

        mqtt_client = AsyncMock()
        mqtt_client.messages = _messages()

        with patch(
            "custom_components.lipro.core.mqtt.transport_runtime.aiomqtt.Client"
        ) as mock_client_cls:
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mqtt_client
            context_manager.__aexit__.return_value = False
            mock_client_cls.return_value = context_manager

            await client._connect_and_listen()

        assert mqtt_client.unsubscribe.await_count == 2
        assert mqtt_client.subscribe.await_count == 2
        assert client._pending_unsubscribe == set()
        assert client._subscribed_devices == {f"new_{idx}" for idx in range(55)}

    @pytest.mark.asyncio
    async def test_connect_and_listen_keeps_last_error_when_on_connect_fails(self):
        """on_connect callback failures should remain observable via last_error."""
        on_connect = MagicMock(side_effect=RuntimeError("callback boom"))
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_connect=on_connect,
        )

        async def _messages():
            if TYPE_CHECKING:
                yield None

        mqtt_client = AsyncMock()
        mqtt_client.messages = _messages()

        with patch(
            "custom_components.lipro.core.mqtt.transport_runtime.aiomqtt.Client"
        ) as mock_client_cls:
            context_manager = AsyncMock()
            context_manager.__aenter__.return_value = mqtt_client
            context_manager.__aexit__.return_value = False
            mock_client_cls.return_value = context_manager

            await client._connect_and_listen()

        assert isinstance(client.last_error, RuntimeError)
        assert str(client.last_error) == "callback boom"

    def test_decode_payload_text_string(self):
        """String payload should pass through unchanged when size is valid."""
        decoded = MqttTransport._decode_payload_text("{}", "dev1")
        assert decoded == "{}"

    def test_decode_payload_text_unexpected_type(self):
        """Unexpected payload types should be ignored."""
        decoded = MqttTransport._decode_payload_text(123, "dev1")
        assert decoded is None

class TestConnectionLoop:
    """Tests for reconnection loop with backoff/jitter."""

    @pytest.mark.asyncio
    async def test_connection_loop_retries_after_mqtt_error(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True
        client._connected = True
        client._broker_client = MagicMock()

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=[aiomqtt.MqttError("boom"), asyncio.CancelledError()],
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                new_callable=AsyncMock,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_awaited_once()
        assert client._connected is False
        assert client._broker_client is None

    @pytest.mark.asyncio
    async def test_connection_loop_handles_oserror(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        async def _sleep_and_stop(_: float) -> None:
            client._running = False

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=OSError("network down"),
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_connection_loop_handles_value_error(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        async def _sleep_and_stop(_: float) -> None:
            client._running = False

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=ValueError("invalid topic"),
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_connection_loop_handles_unexpected_exception(self):
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True

        async def _sleep_and_stop(_: float) -> None:
            client._running = False

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=RuntimeError("unexpected"),
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.transport_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_finalize_connection_task_sets_last_error_and_calls_error_hook(self):
        """Background connection task failures should be observable."""
        on_error = MagicMock()
        client = MqttTransport(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_error=on_error,
        )

        async def _boom() -> None:
            raise RuntimeError("loop boom")

        task = asyncio.create_task(_boom())
        await asyncio.gather(task, return_exceptions=True)
        client._task = cast(asyncio.Task[None] | None, task)

        client._async_finalize_connection_task(task)

        assert client._task is None
        assert isinstance(client.last_error, RuntimeError)
        on_error.assert_called_once()
