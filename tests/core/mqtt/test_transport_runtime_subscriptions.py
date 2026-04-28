"""Tests for Lipro MQTT transport."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock

import aiomqtt
import pytest

from custom_components.lipro.core.mqtt.transport import MqttTransport


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
