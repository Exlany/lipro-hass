"""Tests for Lipro MQTT client."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.mqtt import (
    LiproMqttClient,
    MqttCredentials,
    build_topic,
    decrypt_mqtt_credential,
    parse_mqtt_payload,
    parse_topic,
)


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


class TestMqttCredentials:
    """Tests for MqttCredentials class."""

    def test_create_credentials(self):
        """Test creating MQTT credentials."""
        creds = MqttCredentials.create(
            access_key="test_access_key",
            secret_key="test_secret_key",
            biz_id="lip_biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Client ID format: GID_App@@@{bizId}-android-{phoneId}
        assert creds.client_id.startswith("GID_App@@@lip_biz001-android-")
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
        topic = build_topic("lip_biz001", "03ab5ccd7cxxxxxx")

        assert topic == "Topic_Device_State/lip_biz001/03ab5ccd7cxxxxxx"

    def test_build_topic_with_special_chars(self):
        """Test building topic with various IDs."""
        topic = build_topic("lip_biz001", "mesh_group_10001")

        assert topic == "Topic_Device_State/lip_biz001/mesh_group_10001"


class TestParseTopic:
    """Tests for topic parsing."""

    def test_parse_topic_valid(self):
        """Test parsing valid topic."""
        device_id = parse_topic("Topic_Device_State/lip_biz001/03ab5ccd7cxxxxxx")

        assert device_id == "03ab5ccd7cxxxxxx"

    def test_parse_topic_invalid(self):
        """Test parsing invalid topic."""
        assert parse_topic("invalid") is None
        assert parse_topic("only/two") is None
        assert parse_topic("") is None

    def test_parse_topic_extra_parts(self):
        """Test parsing topic with extra parts."""
        device_id = parse_topic("Topic_Device_State/biz/device/extra/parts")

        # Should still return the device ID (third part)
        assert device_id == "device"


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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_disconnect=on_disconnect,
        )
        client._connected = True
        client._client = MagicMock()

        client._handle_disconnect("Test reason")

        assert client._connected is False
        assert client._client is None
        on_disconnect.assert_called_once()

    def test_process_message(self):
        """Test message processing."""
        on_message = MagicMock()
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="lip_biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        # Create mock message
        message = MagicMock()
        message.topic = "Topic_Device_State/biz123/03ab5ccd7cxxxxxx"
        message.payload = b'{"light": {"powerState": "1"}}'

        client._process_message(message)

        on_message.assert_called_once()
        call_args = on_message.call_args
        assert call_args[0][0] == "03ab5ccd7cxxxxxx"
        assert call_args[0][1]["powerState"] == "1"

    def test_process_message_invalid_json(self):
        """Test message processing with invalid JSON."""
        on_message = MagicMock()
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="lip_biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/lip_biz001/03ab5ccd7cxxxxxx"
        message.payload = b"not valid json"

        # Should not raise, just log error
        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_invalid_topic(self):
        """Test message processing with invalid topic."""
        on_message = MagicMock()
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="lip_biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "invalid"
        message.payload = b'{"light": {"powerState": "1"}}'

        client._process_message(message)

        on_message.assert_not_called()

    def test_process_message_empty_properties(self):
        """Test message processing with empty properties."""
        on_message = MagicMock()
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="lip_biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
            on_message=on_message,
        )

        message = MagicMock()
        message.topic = "Topic_Device_State/lip_biz001/03ab5ccd7cxxxxxx"
        message.payload = b"{}"

        client._process_message(message)

        # Should not call callback for empty properties
        on_message.assert_not_called()


class TestLiproMqttClientProperties:
    """Tests for MQTT client properties."""

    def test_is_connected(self):
        """Test is_connected property."""
        client = LiproMqttClient(
            access_key="access",
            secret_key="secret",
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
            biz_id="lip_biz001",
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
