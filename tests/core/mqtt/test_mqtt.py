"""Tests for Lipro MQTT client."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock, patch

import aiomqtt
from Crypto.Cipher import AES
import pytest

from custom_components.lipro.const.api import MQTT_AES_KEY
from custom_components.lipro.core.mqtt.mqtt_client import LiproMqttClient
from custom_components.lipro.core.mqtt.credentials import (
    MqttCredentials,
    decrypt_mqtt_credential,
)
from custom_components.lipro.core.mqtt.payload import (
    _MAX_MQTT_PAYLOAD_BYTES,
    _sanitize_mqtt_log_value,
    parse_mqtt_payload,
)
from custom_components.lipro.core.mqtt.topics import build_topic, parse_topic


class TestDecryptMqttCredential:
    """Tests for MQTT credential decryption."""

    def test_decrypt_valid_credential(self):
        """Test decrypting a valid credential."""
        # This test uses a known encrypted value
        # In real tests, you'd use actual encrypted values from the API
        # For now, we test the function structure
        with pytest.raises(ValueError):
            # Invalid hex should raise ValueError
            decrypt_mqtt_credential("invalid_hex")

    def test_decrypt_empty_credential(self):
        """Test decrypting empty credential raises ValueError (not IndexError)."""
        # After fix: IndexError from empty decrypt is caught and wrapped as ValueError
        with pytest.raises(ValueError, match="Failed to decrypt"):
            decrypt_mqtt_credential("")

    def test_decrypt_short_hex_credential(self):
        """Test decrypting very short hex that produces empty decrypt output."""
        # "00" is valid hex but too short for valid AES — triggers padding error
        with pytest.raises(ValueError):
            decrypt_mqtt_credential("00")

    def test_decrypt_odd_length_hex(self):
        """Test decrypting odd-length hex string."""
        with pytest.raises(ValueError):
            decrypt_mqtt_credential("abc")  # Odd length

    def test_decrypt_non_utf8_credential(self):
        """Test decrypting payload with valid padding but invalid UTF-8 bytes."""
        plaintext = (b"\xff" * 15) + b"\x01"
        cipher = AES.new(MQTT_AES_KEY.encode("utf-8"), AES.MODE_ECB)
        encrypted_hex = cipher.encrypt(plaintext).hex()

        with pytest.raises(ValueError, match="Failed to decrypt"):
            decrypt_mqtt_credential(encrypted_hex)

    def test_decrypt_invalid_padding_length(self):
        """Invalid PKCS5 padding length should raise ValueError."""
        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = b"invalid\x00"

        with (
            patch(
                "custom_components.lipro.core.mqtt.credentials.AES.new",
                return_value=mock_cipher,
            ),
            pytest.raises(ValueError, match="Invalid PKCS5 padding length"),
        ):
            decrypt_mqtt_credential("00")

    def test_decrypt_invalid_padding_bytes(self):
        """Mismatched PKCS5 padding bytes should raise ValueError."""
        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = b"invalid\x01\x02"

        with (
            patch(
                "custom_components.lipro.core.mqtt.credentials.AES.new",
                return_value=mock_cipher,
            ),
            pytest.raises(ValueError, match="Invalid PKCS5 padding bytes"),
        ):
            decrypt_mqtt_credential("00")


class TestMqttCredentials:
    """Tests for MqttCredentials class."""

    def test_create_credentials(self):
        """Test creating MQTT credentials."""
        creds = MqttCredentials.create(
            access_key="test_access_key",
            secret_key="test_secret_key",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Client ID format: GID_App@@@{bizId}-android-{phoneId}
        assert creds.client_id.startswith("GID_App@@@biz001-android-")
        assert len(creds.client_id) <= 64

        # Username format: Signature|{accessKey}|{instanceId}
        assert creds.username.startswith("Signature|test_access_key|")

        # Password is base64 encoded HMAC-SHA1
        assert len(creds.password) > 0

    def test_create_credentials_truncates_client_id(self):
        """Test that client ID is truncated to 64 chars."""
        creds = MqttCredentials.create(
            access_key="key",
            secret_key="secret",
            biz_id="very_long_biz_id_that_exceeds_normal_length",
            phone_id="very-long-phone-uuid-that-also-exceeds-normal-length-1234567890",
        )

        assert len(creds.client_id) == 64


class TestBuildTopic:
    """Tests for topic building."""

    def test_build_topic(self):
        """Test building MQTT topic."""
        topic = build_topic("biz001", "03ab5ccd7cxxxxxx")

        assert topic == "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"

    def test_build_topic_with_special_chars(self):
        """Test building topic with various IDs."""
        topic = build_topic("biz001", "mesh_group_10001")

        assert topic == "Topic_Device_State/biz001/mesh_group_10001"

    def test_build_topic_invalid_biz_id_raises(self):
        """Invalid biz_id should be rejected."""
        with pytest.raises(ValueError, match="Invalid biz_id format"):
            build_topic("biz/invalid", "03ab5ccd7cxxxxxx")


class TestMqttLogSanitization:
    """Tests for MQTT payload log sanitization."""

    def test_sanitize_list_payload(self):
        """List payloads should be sanitized recursively."""
        payload = [{"accessToken": "secret-token"}, {"nested": {"ip": "192.168.0.2"}}]

        sanitized = _sanitize_mqtt_log_value(payload)

        assert isinstance(sanitized, list)
        assert sanitized[0]["accessToken"] == "***"
        assert sanitized[1]["nested"]["ip"] == "***"

    def test_sanitize_json_string_payload(self):
        """JSON string payloads should be parsed and sanitized."""
        raw = '{"accessToken":"secret-token","nested":{"mac":"AA:BB:CC:DD:EE:FF"}}'

        sanitized = _sanitize_mqtt_log_value(raw)

        assert isinstance(sanitized, str)
        assert "secret-token" not in sanitized
        assert "AA:BB:CC:DD:EE:FF" not in sanitized
        assert "***" in sanitized

    def test_sanitize_non_string_value_passthrough(self):
        """Non-container, non-string values should pass through unchanged."""
        assert _sanitize_mqtt_log_value(42) == 42


class TestParseTopic:
    """Tests for topic parsing."""

    def test_parse_topic_valid(self):
        """Test parsing valid topic."""
        device_id = parse_topic("Topic_Device_State/biz001/03ab5ccd7cxxxxxx")

        assert device_id == "03ab5ccd7cxxxxxx"
        assert (
            parse_topic(
                "Topic_Device_State/biz001/03ab5ccd7cxxxxxx",
                expected_biz_id="lip_biz001",
            )
            == "03ab5ccd7cxxxxxx"
        )

    def test_parse_topic_invalid(self):
        """Test parsing invalid topic."""
        assert parse_topic("invalid") is None
        assert parse_topic("only/two") is None
        assert parse_topic("") is None
        # Wrong prefix should also return None
        assert parse_topic("Wrong_Prefix/biz/device") is None

    def test_parse_topic_extra_parts(self):
        """Topic with extra segments should be rejected."""
        assert parse_topic("Topic_Device_State/biz/device/extra/parts") is None

    def test_parse_topic_invalid_biz_or_device(self):
        """Topic should reject invalid biz/device segment characters."""
        assert parse_topic("Topic_Device_State/biz$/device") is None
        assert parse_topic("Topic_Device_State/biz/device#1") is None


    def test_parse_topic_rejects_mismatched_expected_biz(self):
        """Expected biz ID mismatch should reject the topic."""
        assert (
            parse_topic(
                "Topic_Device_State/biz123/03ab5ccd7cxxxxxx",
                expected_biz_id="biz001",
            )
            is None
        )


class TestParseMqttPayload:
    """Tests for MQTT payload parsing."""

    def test_parse_light_payload(self):
        """Test parsing light device payload."""
        payload = {
            "common": {
                "connectState": "1",
            },
            "light": {
                "powerState": "1",
                "brightness": "80",
                "temperature": "4000",
            },
        }

        result = parse_mqtt_payload(payload)

        assert result["connectState"] == "1"
        assert result["powerState"] == "1"
        assert result["brightness"] == "80"
        assert result["temperature"] == "4000"

    def test_parse_fan_light_payload(self):
        """Test parsing fan light payload with key mapping."""
        payload = {
            "fanLight": {
                "fanOnOff": "1",  # MQTT uses fanOnOff
                "fanGear": "5",
                "fanMode": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        # Should be mapped to REST API key
        assert result["fanOnoff"] == "1"  # REST uses fanOnoff
        assert result["fanGear"] == "5"
        assert result["fanMode"] == "1"

    def test_parse_curtain_payload(self):
        """Test parsing curtain payload with key mapping."""
        payload = {
            "curtain": {
                "progress": "50",  # MQTT uses progress
                "state": "1",  # MQTT uses state
            },
        }

        result = parse_mqtt_payload(payload)

        # Should be mapped to REST API keys
        assert result["position"] == "50"  # REST uses position
        assert result["moving"] == "1"  # REST uses moving

    def test_parse_empty_payload(self):
        """Test parsing empty payload."""
        result = parse_mqtt_payload({})

        assert result == {}

    def test_parse_payload_wrapper_fallback(self):
        """Wrapper payloads should fall back to nested data/payload dicts."""
        result = parse_mqtt_payload({"data": {"light": {"powerState": "1"}}})
        assert result["powerState"] == "1"

        nested = parse_mqtt_payload({"payload": {"common": {"connectState": "1"}}})
        assert nested["connectState"] == "1"


    def test_parse_non_dict_payload(self):
        """Test parsing payload safely ignores non-dict JSON types."""
        assert parse_mqtt_payload([]) == {}
        assert parse_mqtt_payload("not-an-object") == {}
        assert parse_mqtt_payload(None) == {}

    def test_parse_payload_with_unknown_groups(self):
        """Test parsing payload ignores unknown groups."""
        payload = {
            "unknown_group": {
                "key": "value",
            },
            "light": {
                "powerState": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        assert "key" not in result
        assert result["powerState"] == "1"

    def test_parse_payload_with_non_dict_group(self):
        """Test parsing payload handles non-dict groups."""
        payload = {
            "light": "not_a_dict",
            "common": {
                "connectState": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        assert result == {"connectState": "1"}

    def test_parse_real_light_payload(self):
        """Test parsing real MQTT payload captured from Lipro 20X1 light.

        This payload was captured from a real device after POWER_ON command.
        Noise values like "-1" and "" should be filtered out.
        """
        payload = {
            "common": {
                "connectState": "1",
                "deviceInfo": '{"wifi_ssid":"Tide IoT","wifi_rssi":-80}',
                "devicePhysicalMode": "light",
                "latestSyncTimestamp": "1770854728432",
                "version": "11.2.54",
            },
            "light": {
                "beepSwitch": "-1",
                "brightness": "50",
                "brightnessDecimal": "-1",
                "fadeState": "1",
                "gearList": '[{"temperature":0,"brightness":50}]',
                "ldrAutoSwitch": "-1",
                "powerState": "1",
                "seatSwitch": "-1",
                "temperature": "30",
                "upperLed": "",
            },
        }

        result = parse_mqtt_payload(payload)

        # Real values should be present
        assert result["connectState"] == "1"
        assert result["powerState"] == "1"
        assert result["brightness"] == "50"
        assert result["temperature"] == "30"
        assert result["fadeState"] == "1"
        assert result["version"] == "11.2.54"
        assert result["devicePhysicalMode"] == "light"

        # Noise values ("-1" and "") should be filtered out
        assert "beepSwitch" not in result
        assert "brightnessDecimal" not in result
        assert "ldrAutoSwitch" not in result
        assert "seatSwitch" not in result
        assert "upperLed" not in result

    def test_parse_payload_filters_numeric_and_whitespace_noise_values(self):
        """Noise values can be numeric -1 or strings with extra whitespace."""
        payload = {
            "common": {
                "connectState": 1,
            },
            "light": {
                "beepSwitch": -1,
                "seatSwitch": " -1 ",
                "upperLed": " ",
                "powerState": "1",
            },
        }

        result = parse_mqtt_payload(payload)

        assert result["connectState"] == 1
        assert result["powerState"] == "1"
        assert "beepSwitch" not in result
        assert "seatSwitch" not in result
        assert "upperLed" not in result

    def test_parse_payload_preserves_zero_values(self):
        """Test that "0" values are NOT filtered (they are valid states)."""
        payload = {
            "light": {
                "powerState": "0",  # Off — valid
                "brightness": "0",  # Min brightness — valid
            },
        }

        result = parse_mqtt_payload(payload)

        assert result["powerState"] == "0"
        assert result["brightness"] == "0"


class TestLiproMqttClient:
    """Tests for LiproMqttClient class."""

    def test_init(self):
        """Test client initialization."""
        client = LiproMqttClient(
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

        client = LiproMqttClient(
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
        """Test starting MQTT client."""
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        """Test stopping MQTT client."""
        client = LiproMqttClient(
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
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._client = cast(aiomqtt.Client | None, MagicMock())

        client._handle_disconnect("Test reason")

        assert client._connected is False
        assert client._client is None
        on_disconnect.assert_called_once()

    def test_handle_disconnect_callback_failure_sets_last_error(self, caplog):
        """Disconnect callback exceptions should be captured as last_error."""
        on_disconnect = MagicMock(side_effect=RuntimeError("boom"))
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._client = MagicMock()

        with caplog.at_level(logging.ERROR):
            client._handle_disconnect("Test reason")

        assert isinstance(client.last_error, RuntimeError)
        assert str(client.last_error) == "boom"

    def test_process_message(self):
        """Test message processing."""
        on_message = MagicMock()
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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

        assert LiproMqttClient._consume_task_exception(task) is None

    def test_process_message_redacts_sensitive_debug_payload(self, caplog):
        """Debug payload log should redact sensitive fields and identifiers."""
        on_message = MagicMock()
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
                "custom_components.lipro.core.mqtt.client_runtime.parse_mqtt_payload",
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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


class TestLiproMqttClientProperties:
    """Tests for MQTT client properties."""

    def test_is_connected(self):
        """Test is_connected property."""
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
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
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        client._client = mock_mqtt
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
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        client._client = mock_mqtt
        client._connected = True
        client._subscribed_devices = {f"old_{idx}" for idx in range(55)}

        await client.sync_subscriptions({f"new_{idx}" for idx in range(55)})

        assert mock_mqtt.subscribe.await_count == 2
        assert mock_mqtt.unsubscribe.await_count == 2
        assert client._subscribed_devices == {f"new_{idx}" for idx in range(55)}

    @pytest.mark.asyncio
    async def test_sync_connected_skips_invalid_device_id(self, caplog):
        """Test sync skips invalid topic IDs without breaking valid subscriptions."""
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        client._client = mock_mqtt
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
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        mock_mqtt.subscribe.side_effect = aiomqtt.MqttError("subscribe failed")
        client._client = mock_mqtt
        client._connected = True

        await client.sync_subscriptions({"dev_new"})

        mock_mqtt.subscribe.assert_called_once()
        assert client._subscribed_devices == set()

    @pytest.mark.asyncio
    async def test_sync_connected_unsubscribe_invalid_id_skips(self):
        """Invalid unsubscribe device IDs should be skipped safely."""
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._client = AsyncMock()
        client._connected = True
        client._subscribed_devices = {"bad/dev"}

        await client.sync_subscriptions(set())

        assert client._subscribed_devices == set()

    @pytest.mark.asyncio
    async def test_sync_connected_unsubscribe_mqtt_error_keeps_running(self):
        """Unsubscribe errors should not break synchronization."""
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        mock_mqtt = AsyncMock()
        mock_mqtt.unsubscribe.side_effect = aiomqtt.MqttError("unsubscribe failed")
        client._client = mock_mqtt
        client._connected = True
        client._subscribed_devices = {"dev_old"}

        await client.sync_subscriptions(set())

        mock_mqtt.unsubscribe.assert_called_once()
        assert client._subscribed_devices == set()


class TestConnectAndDecode:
    """Tests for connect/listen and payload decoding paths."""

    @pytest.mark.asyncio
    async def test_connect_and_listen_subscribes_and_processes_messages(self, caplog):
        """Connect/listen should subscribe valid IDs, skip invalid ones, and process stream.

        Also verifies TLS context is cached across reconnects to avoid rebuilding it.
        """
        on_connect = MagicMock()
        client = LiproMqttClient(
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
                "custom_components.lipro.core.mqtt.client_runtime.ssl.create_default_context"
            ) as mock_tls,
            patch(
                "custom_components.lipro.core.mqtt.client_runtime.aiomqtt.Client"
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
        client = LiproMqttClient(
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
            "custom_components.lipro.core.mqtt.client_runtime.aiomqtt.Client"
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
        client = LiproMqttClient(
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
            "custom_components.lipro.core.mqtt.client_runtime.aiomqtt.Client"
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
        decoded = LiproMqttClient._decode_payload_text("{}", "dev1")
        assert decoded == "{}"

    def test_decode_payload_text_unexpected_type(self):
        """Unexpected payload types should be ignored."""
        decoded = LiproMqttClient._decode_payload_text(123, "dev1")
        assert decoded is None


class TestConnectionLoop:
    """Tests for reconnection loop with backoff/jitter."""

    @pytest.mark.asyncio
    async def test_connection_loop_retries_after_mqtt_error(self):
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )
        client._running = True
        client._connected = True
        client._client = MagicMock()

        with (
            patch.object(
                client,
                "_connect_and_listen",
                side_effect=[aiomqtt.MqttError("boom"), asyncio.CancelledError()],
            ),
            patch(
                "custom_components.lipro.core.mqtt.client_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.client_runtime.asyncio.sleep",
                new_callable=AsyncMock,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_awaited_once()
        assert client._connected is False
        assert client._client is None

    @pytest.mark.asyncio
    async def test_connection_loop_handles_oserror(self):
        client = LiproMqttClient(
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
                "custom_components.lipro.core.mqtt.client_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.client_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_connection_loop_handles_value_error(self):
        client = LiproMqttClient(
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
                "custom_components.lipro.core.mqtt.client_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.client_runtime.asyncio.sleep",
                side_effect=_sleep_and_stop,
            ) as sleep,
        ):
            await client._connection_loop()

        sleep.assert_called_once()
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_connection_loop_handles_unexpected_exception(self):
        client = LiproMqttClient(
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
                "custom_components.lipro.core.mqtt.client_runtime.random.uniform",
                return_value=0.0,
            ),
            patch(
                "custom_components.lipro.core.mqtt.client_runtime.asyncio.sleep",
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
        client = LiproMqttClient(
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
